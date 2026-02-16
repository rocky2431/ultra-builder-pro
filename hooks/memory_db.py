#!/usr/bin/env python3
"""Ultra Memory DB - SQLite FTS5 storage for session memory.

Dual-use: importable library AND CLI tool.

CLI usage:
  python3 memory_db.py search "keyword" [--limit N]
  python3 memory_db.py recent [N]
  python3 memory_db.py latest
  python3 memory_db.py date 2026-02-15
  python3 memory_db.py save-summary SESSION_ID "summary text"
  python3 memory_db.py add-tags SESSION_ID "tag1,tag2"
  python3 memory_db.py cleanup [--days N]
  python3 memory_db.py stats
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

GIT_TIMEOUT = 3
DEFAULT_MERGE_WINDOW_MIN = 30
DEFAULT_RETENTION_DAYS = 90


# -- Path Resolution --

def get_git_toplevel() -> str:
    """Get git repository root, or empty string if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def get_db_path() -> Path:
    """Get project-level DB path (.ultra/memory/memory.db).

    Falls back to ~/.claude/memory/memory.db if not in a git repo.
    """
    toplevel = get_git_toplevel()
    if toplevel:
        return Path(toplevel) / ".ultra" / "memory" / "memory.db"
    return Path.home() / ".claude" / "memory" / "memory.db"


def get_jsonl_path() -> Path:
    """Get JSONL path alongside the DB."""
    return get_db_path().with_name("sessions.jsonl")


# -- Database Init --

def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialize database with tables and FTS5 index."""
    if db_path is None:
        db_path = get_db_path()

    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            last_active TEXT NOT NULL,
            branch TEXT DEFAULT '',
            cwd TEXT DEFAULT '',
            files_modified TEXT DEFAULT '[]',
            summary TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            stop_count INTEGER DEFAULT 1
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
            id UNINDEXED,
            branch,
            files_modified,
            summary,
            tags,
            content=sessions,
            content_rowid=rowid
        );

        CREATE TRIGGER IF NOT EXISTS sessions_ai AFTER INSERT ON sessions BEGIN
            INSERT INTO sessions_fts(rowid, id, branch, files_modified, summary, tags)
            VALUES (new.rowid, new.id, new.branch, new.files_modified, new.summary, new.tags);
        END;

        CREATE TRIGGER IF NOT EXISTS sessions_ad AFTER DELETE ON sessions BEGIN
            INSERT INTO sessions_fts(sessions_fts, rowid, id, branch, files_modified, summary, tags)
            VALUES ('delete', old.rowid, old.id, old.branch, old.files_modified, old.summary, old.tags);
        END;

        CREATE TRIGGER IF NOT EXISTS sessions_au AFTER UPDATE ON sessions BEGIN
            INSERT INTO sessions_fts(sessions_fts, rowid, id, branch, files_modified, summary, tags)
            VALUES ('delete', old.rowid, old.id, old.branch, old.files_modified, old.summary, old.tags);
            INSERT INTO sessions_fts(rowid, id, branch, files_modified, summary, tags)
            VALUES (new.rowid, new.id, new.branch, new.files_modified, new.summary, new.tags);
        END;
    """)

    conn.commit()
    return conn


# -- Write Operations --

def upsert_session(conn: sqlite3.Connection, branch: str, cwd: str,
                   files_modified: list,
                   merge_window_min: int = DEFAULT_MERGE_WINDOW_MIN) -> str:
    """Insert or update session record.

    If a recent entry (within merge_window_min) exists for same branch+cwd,
    update it (merge files, bump stop_count). Otherwise create new.

    Returns session ID.
    """
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(minutes=merge_window_min)).isoformat()

    row = conn.execute(
        """SELECT id, files_modified, stop_count FROM sessions
           WHERE branch = ? AND cwd = ? AND last_active > ?
           ORDER BY last_active DESC LIMIT 1""",
        (branch, cwd, cutoff)
    ).fetchone()

    if row:
        existing_files = json.loads(row["files_modified"])
        merged_files = sorted(set(existing_files + files_modified))

        conn.execute(
            """UPDATE sessions
               SET last_active = ?, files_modified = ?, stop_count = ?
               WHERE id = ?""",
            (now.isoformat(), json.dumps(merged_files),
             row["stop_count"] + 1, row["id"])
        )
        conn.commit()
        return row["id"]

    session_id = now.strftime("%Y%m%d-%H%M%S")
    conn.execute(
        """INSERT INTO sessions
           (id, started_at, last_active, branch, cwd, files_modified)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session_id, now.isoformat(), now.isoformat(),
         branch, cwd, json.dumps(files_modified))
    )
    conn.commit()
    return session_id


def update_summary(conn: sqlite3.Connection, session_id: str,
                   summary: str) -> bool:
    """Update summary for a session."""
    cursor = conn.execute(
        "UPDATE sessions SET summary = ? WHERE id = ?",
        (summary, session_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def add_tags(conn: sqlite3.Connection, session_id: str,
             new_tags: str) -> bool:
    """Add tags to a session (comma-separated)."""
    row = conn.execute(
        "SELECT tags FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    if not row:
        return False

    existing = set(t.strip() for t in row["tags"].split(",") if t.strip())
    incoming = set(t.strip() for t in new_tags.split(",") if t.strip())
    merged = ",".join(sorted(existing | incoming))

    conn.execute(
        "UPDATE sessions SET tags = ? WHERE id = ?", (merged, session_id)
    )
    conn.commit()
    return True


def cleanup(conn: sqlite3.Connection,
            days: int = DEFAULT_RETENTION_DAYS) -> int:
    """Delete sessions older than N days. Returns count deleted."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    cursor = conn.execute(
        "DELETE FROM sessions WHERE last_active < ?", (cutoff,)
    )
    conn.commit()
    return cursor.rowcount


# -- Read Operations --

def search(conn: sqlite3.Connection, query: str, limit: int = 10) -> list:
    """FTS5 search across sessions."""
    safe_query = query.replace('"', '""')

    rows = conn.execute(
        """SELECT s.id, s.started_at, s.last_active, s.branch, s.cwd,
                  s.files_modified, s.summary, s.tags, s.stop_count
           FROM sessions_fts f
           JOIN sessions s ON f.rowid = s.rowid
           WHERE sessions_fts MATCH ?
           ORDER BY rank
           LIMIT ?""",
        (f'"{safe_query}"', limit)
    ).fetchall()

    return [dict(r) for r in rows]


def get_recent(conn: sqlite3.Connection, limit: int = 5) -> list:
    """Get most recent sessions."""
    rows = conn.execute(
        """SELECT id, started_at, last_active, branch, cwd,
                  files_modified, summary, tags, stop_count
           FROM sessions
           ORDER BY last_active DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()

    return [dict(r) for r in rows]


def get_latest(conn: sqlite3.Connection) -> dict | None:
    """Get the most recent session."""
    results = get_recent(conn, 1)
    return results[0] if results else None


def get_by_date(conn: sqlite3.Connection, date_str: str) -> list:
    """Get sessions from a specific date (YYYY-MM-DD)."""
    rows = conn.execute(
        """SELECT id, started_at, last_active, branch, cwd,
                  files_modified, summary, tags, stop_count
           FROM sessions
           WHERE started_at LIKE ?
           ORDER BY started_at DESC""",
        (f"{date_str}%",)
    ).fetchall()

    return [dict(r) for r in rows]


def get_stats(conn: sqlite3.Connection) -> dict:
    """Get memory database statistics."""
    total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    with_summary = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE summary != ''"
    ).fetchone()[0]

    oldest = conn.execute(
        "SELECT started_at FROM sessions ORDER BY started_at ASC LIMIT 1"
    ).fetchone()
    newest = conn.execute(
        "SELECT last_active FROM sessions ORDER BY last_active DESC LIMIT 1"
    ).fetchone()

    branches = conn.execute(
        "SELECT DISTINCT branch FROM sessions"
    ).fetchall()

    return {
        "total_sessions": total,
        "with_summary": with_summary,
        "without_summary": total - with_summary,
        "oldest": oldest[0][:10] if oldest else None,
        "newest": newest[0][:10] if newest else None,
        "branches": [r[0] for r in branches],
        "db_path": str(get_db_path()),
    }


# -- Formatting --

def format_session(s: dict, verbose: bool = False) -> str:
    """Format a session record for display."""
    files = json.loads(s.get("files_modified", "[]"))

    started = s.get("started_at", "")[:19].replace("T", " ")
    last = s.get("last_active", "")[:19].replace("T", " ")

    lines = [f"**[{s['id']}]** {started} -> {last}"]
    lines.append(
        f"  Branch: `{s.get('branch', '?')}` | "
        f"Dir: `{s.get('cwd', '?')}` | "
        f"Stops: {s.get('stop_count', 1)}"
    )

    if s.get("summary"):
        lines.append(f"  Summary: {s['summary']}")

    if s.get("tags"):
        lines.append(f"  Tags: {s['tags']}")

    if files:
        if verbose:
            for f in files[:15]:
                lines.append(f"  - {f}")
            if len(files) > 15:
                lines.append(f"  ... and {len(files) - 15} more")
        else:
            display = ", ".join(files[:5])
            lines.append(f"  Files ({len(files)}): {display}")
            if len(files) > 5:
                lines.append(f"  ... and {len(files) - 5} more")

    return "\n".join(lines)


def format_oneliner(s: dict) -> str:
    """Format a session as a single line for SessionStart injection."""
    files = json.loads(s.get("files_modified", "[]"))
    date = s.get("last_active", "")[:16].replace("T", " ")
    branch = s.get("branch", "?")
    file_count = len(files)

    summary = s.get("summary", "")
    if summary:
        # Truncate to 60 chars
        if len(summary) > 60:
            summary = summary[:57] + "..."
        return f"Last session: {date} | {branch} | {file_count} files | \"{summary}\""

    return f"Last session: {date} | {branch} | {file_count} files modified"


# -- CLI Interface --

def cli_main():
    """CLI entry point for direct invocation."""
    if len(sys.argv) < 2:
        print("Usage: memory_db.py <command> [args]")
        print("Commands: search, recent, latest, date, "
              "save-summary, add-tags, cleanup, stats")
        sys.exit(1)

    cmd = sys.argv[1]
    conn = init_db()

    try:
        if cmd == "search":
            if len(sys.argv) < 3:
                print("Usage: memory_db.py search <query> [--limit N]")
                sys.exit(1)
            query = sys.argv[2]
            limit = 10
            if "--limit" in sys.argv:
                idx = sys.argv.index("--limit")
                if idx + 1 < len(sys.argv):
                    limit = int(sys.argv[idx + 1])

            results = search(conn, query, limit)
            if not results:
                print(f"No results for: {query}")
            else:
                print(f"Found {len(results)} session(s) matching '{query}':\n")
                for s in results:
                    print(format_session(s, verbose=True))
                    print()

        elif cmd == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            results = get_recent(conn, limit)
            if not results:
                print("No sessions recorded yet.")
            else:
                print(f"Recent {len(results)} session(s):\n")
                for s in results:
                    print(format_session(s))
                    print()

        elif cmd == "latest":
            result = get_latest(conn)
            if not result:
                print("No sessions recorded yet.")
            else:
                print(format_session(result, verbose=True))

        elif cmd == "date":
            if len(sys.argv) < 3:
                print("Usage: memory_db.py date <YYYY-MM-DD>")
                sys.exit(1)
            results = get_by_date(conn, sys.argv[2])
            if not results:
                print(f"No sessions on {sys.argv[2]}")
            else:
                print(f"Sessions on {sys.argv[2]}:\n")
                for s in results:
                    print(format_session(s, verbose=True))
                    print()

        elif cmd == "save-summary":
            if len(sys.argv) < 4:
                print("Usage: memory_db.py save-summary <session_id> "
                      "<summary>")
                sys.exit(1)
            if update_summary(conn, sys.argv[2], sys.argv[3]):
                print(f"Summary saved for session {sys.argv[2]}")
            else:
                print(f"Session {sys.argv[2]} not found")
                sys.exit(1)

        elif cmd == "add-tags":
            if len(sys.argv) < 4:
                print("Usage: memory_db.py add-tags <session_id> "
                      "<tag1,tag2,...>")
                sys.exit(1)
            if add_tags(conn, sys.argv[2], sys.argv[3]):
                print(f"Tags added to session {sys.argv[2]}")
            else:
                print(f"Session {sys.argv[2]} not found")
                sys.exit(1)

        elif cmd == "cleanup":
            days = DEFAULT_RETENTION_DAYS
            if "--days" in sys.argv:
                idx = sys.argv.index("--days")
                if idx + 1 < len(sys.argv):
                    days = int(sys.argv[idx + 1])
            deleted = cleanup(conn, days)
            print(f"Cleaned up {deleted} session(s) older than {days} days")

        elif cmd == "stats":
            stats = get_stats(conn)
            print(f"Sessions: {stats['total_sessions']} total "
                  f"({stats['with_summary']} with summary)")
            if stats["oldest"]:
                print(f"Range: {stats['oldest']} -> {stats['newest']}")
            print(f"Branches: {', '.join(stats['branches']) or 'none'}")
            print(f"DB: {stats['db_path']}")

        elif cmd == "oneliner":
            result = get_latest(conn)
            if result:
                print(format_oneliner(result))

        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    cli_main()
