#!/usr/bin/env python3
"""Ultra Memory DB v2 - SQLite FTS5 + Chroma vector storage for session memory.

Schema v2 changes:
- sessions: added content_session_id (real hook session ID), initial_request
- session_summaries: structured fields (request/completed/learned/next_steps)
  with status/source tracking. Replaces sessions.summary for new data.
- observations: lightweight tool-use capture (Write/Edit/test failures)
- summaries_fts: FTS5 on structured summary fields

Backward compat: old sessions.summary column preserved, read ops check both.

Dual-use: importable library AND CLI tool.

CLI usage:
  python3 memory_db.py search "keyword" [--limit N]
  python3 memory_db.py semantic "query" [--limit N]
  python3 memory_db.py hybrid "query" [--limit N]
  python3 memory_db.py recent [N]
  python3 memory_db.py latest
  python3 memory_db.py date 2026-02-15
  python3 memory_db.py save-summary SESSION_ID "summary text"
  python3 memory_db.py add-tags SESSION_ID "tag1,tag2"
  python3 memory_db.py reindex-chroma
  python3 memory_db.py cleanup [--days N]
  python3 memory_db.py stats
  python3 memory_db.py migrate
"""

import hashlib
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
SCHEMA_VERSION = 2


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

_KNOWN_TABLES = {"sessions", "session_summaries", "observations"}


def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Check if a column exists in a table. Table must be in allowlist."""
    if table not in _KNOWN_TABLES:
        raise ValueError(f"Unknown table: {table}")
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(c[1] == column for c in cols)



def _migrate_v2(conn: sqlite3.Connection) -> None:
    """Migrate schema from v1 to v2. Safe to call multiple times."""
    # Add columns to sessions
    if not _has_column(conn, "sessions", "content_session_id"):
        conn.execute(
            "ALTER TABLE sessions ADD COLUMN content_session_id TEXT DEFAULT ''"
        )
    if not _has_column(conn, "sessions", "initial_request"):
        conn.execute(
            "ALTER TABLE sessions ADD COLUMN initial_request TEXT DEFAULT ''"
        )

    # Create session_summaries table
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS session_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            source TEXT NOT NULL DEFAULT 'model',
            model TEXT DEFAULT '',
            request TEXT DEFAULT '',
            completed TEXT DEFAULT '',
            learned TEXT DEFAULT '',
            next_steps TEXT DEFAULT '',
            summary_hash TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(session_id)
        );

        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT DEFAULT '',
            tool_name TEXT DEFAULT '',
            files TEXT DEFAULT '[]',
            content_hash TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_obs_session
            ON observations(session_id);
        CREATE INDEX IF NOT EXISTS idx_obs_kind
            ON observations(kind);
        CREATE INDEX IF NOT EXISTS idx_summaries_session
            ON session_summaries(session_id);
    """)

    # Create FTS5 on structured summary fields
    existing_fts = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' "
        "AND name='summaries_fts'"
    ).fetchone()[0]
    if not existing_fts:
        conn.executescript("""
            CREATE VIRTUAL TABLE summaries_fts USING fts5(
                session_id UNINDEXED,
                request,
                completed,
                learned,
                next_steps,
                content=session_summaries,
                content_rowid=rowid
            );

            CREATE TRIGGER IF NOT EXISTS summaries_fts_ai
                AFTER INSERT ON session_summaries BEGIN
                INSERT INTO summaries_fts(
                    rowid, session_id, request, completed, learned, next_steps
                ) VALUES (
                    new.rowid, new.session_id,
                    new.request, new.completed, new.learned, new.next_steps
                );
            END;

            CREATE TRIGGER IF NOT EXISTS summaries_fts_ad
                AFTER DELETE ON session_summaries BEGIN
                INSERT INTO summaries_fts(
                    summaries_fts, rowid, session_id,
                    request, completed, learned, next_steps
                ) VALUES (
                    'delete', old.rowid, old.session_id,
                    old.request, old.completed, old.learned, old.next_steps
                );
            END;

            CREATE TRIGGER IF NOT EXISTS summaries_fts_au
                AFTER UPDATE ON session_summaries BEGIN
                INSERT INTO summaries_fts(
                    summaries_fts, rowid, session_id,
                    request, completed, learned, next_steps
                ) VALUES (
                    'delete', old.rowid, old.session_id,
                    old.request, old.completed, old.learned, old.next_steps
                );
                INSERT INTO summaries_fts(
                    rowid, session_id, request, completed, learned, next_steps
                ) VALUES (
                    new.rowid, new.session_id,
                    new.request, new.completed, new.learned, new.next_steps
                );
            END;
        """)

    conn.commit()


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialize database with tables, FTS5, and v2 migration."""
    if db_path is None:
        db_path = get_db_path()

    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")

    # v1 base schema
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

    # v2 migration (safe to re-run)
    _migrate_v2(conn)

    return conn


# -- Write Operations --

def upsert_session(conn: sqlite3.Connection, branch: str, cwd: str,
                   files_modified: list,
                   content_session_id: str = "",
                   merge_window_min: int = DEFAULT_MERGE_WINDOW_MIN) -> str:
    """Insert or update session record.

    If content_session_id is provided, use it as the identity key.
    Otherwise fall back to branch+cwd+time merge window (v1 compat).

    Returns session ID (our internal timestamp-based ID).
    """
    now = datetime.now(timezone.utc)

    # v2 path: use real session_id from hook protocol
    if content_session_id:
        row = conn.execute(
            "SELECT id, files_modified, stop_count FROM sessions "
            "WHERE content_session_id = ?",
            (content_session_id,)
        ).fetchone()

        if row:
            existing_files = json.loads(row["files_modified"])
            merged_files = sorted(set(existing_files + files_modified))
            # Backfill branch/cwd if the shell was created without them
            conn.execute(
                "UPDATE sessions SET last_active = ?, files_modified = ?, "
                "stop_count = ?, "
                "branch = CASE WHEN branch = '' OR branch IS NULL THEN ? ELSE branch END, "
                "cwd = CASE WHEN cwd = '' OR cwd IS NULL THEN ? ELSE cwd END "
                "WHERE id = ?",
                (now.isoformat(), json.dumps(merged_files),
                 row["stop_count"] + 1, branch, cwd, row["id"])
            )
            conn.commit()
            return row["id"]

        session_id = now.strftime("%Y%m%d-%H%M%S") + f"-{now.microsecond // 1000:03d}"
        conn.execute(
            "INSERT INTO sessions "
            "(id, started_at, last_active, branch, cwd, files_modified, "
            " content_session_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, now.isoformat(), now.isoformat(),
             branch, cwd, json.dumps(files_modified), content_session_id)
        )
        conn.commit()
        return session_id

    # v1 fallback: merge window
    cutoff = (now - timedelta(minutes=merge_window_min)).isoformat()
    row = conn.execute(
        "SELECT id, files_modified, stop_count FROM sessions "
        "WHERE branch = ? AND cwd = ? AND last_active > ? "
        "ORDER BY last_active DESC LIMIT 1",
        (branch, cwd, cutoff)
    ).fetchone()

    if row:
        existing_files = json.loads(row["files_modified"])
        merged_files = sorted(set(existing_files + files_modified))
        conn.execute(
            "UPDATE sessions SET last_active = ?, files_modified = ?, "
            "stop_count = ? WHERE id = ?",
            (now.isoformat(), json.dumps(merged_files),
             row["stop_count"] + 1, row["id"])
        )
        conn.commit()
        return row["id"]

    session_id = now.strftime("%Y%m%d-%H%M%S") + f"-{now.microsecond // 1000:03d}"
    conn.execute(
        "INSERT INTO sessions "
        "(id, started_at, last_active, branch, cwd, files_modified) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, now.isoformat(), now.isoformat(),
         branch, cwd, json.dumps(files_modified))
    )
    conn.commit()
    return session_id


def update_summary(conn: sqlite3.Connection, session_id: str,
                   summary: str) -> bool:
    """Update legacy summary field for a session (v1 compat)."""
    cursor = conn.execute(
        "UPDATE sessions SET summary = ? WHERE id = ?",
        (summary, session_id)
    )
    conn.commit()
    return cursor.rowcount > 0


def save_structured_summary(conn: sqlite3.Connection, session_id: str,
                            request: str, completed: str,
                            learned: str, next_steps: str,
                            source: str = "model",
                            model: str = "") -> bool:
    """Save structured summary to session_summaries table.

    Also updates the legacy sessions.summary field for backward compat.
    Returns True if saved, False if hash matches existing (dedup).
    """
    now = datetime.now(timezone.utc).isoformat()
    content = f"{request}{completed}{learned}{next_steps}"
    summary_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    # Dedup: skip if same content hash
    existing = conn.execute(
        "SELECT summary_hash FROM session_summaries WHERE session_id = ?",
        (session_id,)
    ).fetchone()
    if existing and existing["summary_hash"] == summary_hash:
        return False

    # Determine status
    total_len = len(request) + len(completed) + len(learned) + len(next_steps)
    status = "ready" if total_len >= 100 else "failed"

    conn.execute(
        "INSERT INTO session_summaries "
        "(session_id, status, source, model, request, completed, "
        " learned, next_steps, summary_hash, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(session_id) DO UPDATE SET "
        "status=excluded.status, source=excluded.source, "
        "model=excluded.model, request=excluded.request, "
        "completed=excluded.completed, learned=excluded.learned, "
        "next_steps=excluded.next_steps, summary_hash=excluded.summary_hash, "
        "created_at=excluded.created_at",
        (session_id, status, source, model, request, completed,
         learned, next_steps, summary_hash, now)
    )

    # Also update legacy summary for backward compat
    legacy = f"## Accomplished\n{completed}"
    if learned:
        legacy += f"\n\n## Decisions\n{learned}"
    if next_steps:
        legacy += f"\n\n## Unfinished\n{next_steps}"
    conn.execute(
        "UPDATE sessions SET summary = ? WHERE id = ?",
        (legacy, session_id)
    )

    conn.commit()
    return True


def save_observation(conn: sqlite3.Connection, session_id: str,
                     kind: str, title: str, detail: str = "",
                     tool_name: str = "", files: list | None = None) -> bool:
    """Save a lightweight observation. Returns False if dedup match."""
    now = datetime.now(timezone.utc).isoformat()
    files_json = json.dumps(files or [])
    content = f"{session_id}{kind}{title}{detail}"
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    # Dedup: skip if same hash within same session
    existing = conn.execute(
        "SELECT id FROM observations "
        "WHERE session_id = ? AND content_hash = ?",
        (session_id, content_hash)
    ).fetchone()
    if existing:
        return False

    conn.execute(
        "INSERT INTO observations "
        "(session_id, kind, title, detail, tool_name, files, "
        " content_hash, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, kind, title, detail, tool_name, files_json,
         content_hash, now)
    )
    conn.commit()
    return True


def set_initial_request(conn: sqlite3.Connection, session_id: str,
                        request: str) -> bool:
    """Store the initial user prompt for a session."""
    cursor = conn.execute(
        "UPDATE sessions SET initial_request = ? "
        "WHERE id = ? AND (initial_request = '' OR initial_request IS NULL)",
        (request[:2000], session_id)
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

    # Collect IDs to delete from Chroma before removing from SQLite
    expired_ids = [
        r[0] for r in conn.execute(
            "SELECT id FROM sessions WHERE last_active < ?", (cutoff,)
        ).fetchall()
    ]

    cursor = conn.execute(
        "DELETE FROM sessions WHERE last_active < ?", (cutoff,)
    )
    # Cascade deletes summaries and observations via app logic
    conn.execute(
        "DELETE FROM session_summaries WHERE session_id NOT IN "
        "(SELECT id FROM sessions)"
    )
    conn.execute(
        "DELETE FROM observations WHERE session_id NOT IN "
        "(SELECT id FROM sessions)"
    )
    conn.commit()

    # Clean up Chroma embeddings for expired sessions
    if expired_ids:
        try:
            collection = get_chroma_collection()
            collection.delete(ids=expired_ids)
        except Exception:
            pass  # Chroma cleanup is best-effort

    # Trim JSONL backup: keep only entries newer than cutoff
    try:
        jsonl_path = get_jsonl_path()
        if jsonl_path.exists():
            kept = []
            for line in jsonl_path.read_text(encoding="utf-8").splitlines():
                try:
                    entry = json.loads(line)
                    if entry.get("ts", "") >= cutoff:
                        kept.append(line)
                except (json.JSONDecodeError, ValueError):
                    pass
            jsonl_path.write_text("\n".join(kept) + "\n" if kept else "",
                                 encoding="utf-8")
    except OSError:
        pass  # JSONL cleanup is best-effort

    return cursor.rowcount


# -- Read Operations --

def search(conn: sqlite3.Connection, query: str, limit: int = 10) -> list:
    """FTS5 search across sessions (v1) and structured summaries (v2)."""
    safe_query = query.replace('"', '""')

    # Search both old sessions_fts and new summaries_fts
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

    results = {r["id"]: dict(r) for r in rows}

    # Also search structured summaries
    try:
        rows2 = conn.execute(
            """SELECT ss.session_id, s.started_at, s.last_active, s.branch,
                      s.cwd, s.files_modified, s.summary, s.tags, s.stop_count
               FROM summaries_fts sf
               JOIN session_summaries ss ON sf.rowid = ss.rowid
               JOIN sessions s ON ss.session_id = s.id
               WHERE summaries_fts MATCH ?
               ORDER BY rank
               LIMIT ?""",
            (f'"{safe_query}"', limit)
        ).fetchall()
        for r in rows2:
            sid = r["session_id"]
            if sid not in results:
                results[sid] = dict(r)
                results[sid]["id"] = sid
    except sqlite3.OperationalError:
        pass  # summaries_fts may not exist yet

    return list(results.values())[:limit]


def get_recent(conn: sqlite3.Connection, limit: int = 5) -> list:
    """Get most recent sessions with structured summary if available."""
    rows = conn.execute(
        """SELECT s.id, s.started_at, s.last_active, s.branch, s.cwd,
                  s.files_modified, s.summary, s.tags, s.stop_count,
                  ss.request as ss_request, ss.completed as ss_completed,
                  ss.learned as ss_learned, ss.next_steps as ss_next_steps,
                  ss.status as ss_status
           FROM sessions s
           LEFT JOIN session_summaries ss ON s.id = ss.session_id
           ORDER BY s.last_active DESC
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
        """SELECT s.id, s.started_at, s.last_active, s.branch, s.cwd,
                  s.files_modified, s.summary, s.tags, s.stop_count,
                  ss.request as ss_request, ss.completed as ss_completed,
                  ss.learned as ss_learned, ss.next_steps as ss_next_steps
           FROM sessions s
           LEFT JOIN session_summaries ss ON s.id = ss.session_id
           WHERE s.started_at LIKE ?
           ORDER BY s.started_at DESC""",
        (f"{date_str}%",)
    ).fetchall()

    return [dict(r) for r in rows]


def get_observations(conn: sqlite3.Connection, session_id: str) -> list:
    """Get observations for a session."""
    rows = conn.execute(
        "SELECT * FROM observations WHERE session_id = ? "
        "ORDER BY created_at",
        (session_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_session_by_content_id(conn: sqlite3.Connection,
                              content_session_id: str) -> dict | None:
    """Look up session by Claude Code's content_session_id."""
    row = conn.execute(
        "SELECT * FROM sessions WHERE content_session_id = ?",
        (content_session_id,)
    ).fetchone()
    return dict(row) if row else None


def get_subagent_observations(conn: sqlite3.Connection,
                               session_id: str,
                               kinds: list | None = None,
                               limit: int = 20) -> list:
    """Get observations from the current session, useful for subagent context.

    Allows a subagent to see what the main agent (or prior subagents)
    have done: file edits, test results, etc.
    """
    if kinds:
        placeholders = ",".join("?" for _ in kinds)
        rows = conn.execute(
            f"SELECT kind, title, detail, tool_name, files, created_at "
            f"FROM observations WHERE session_id = ? AND kind IN ({placeholders}) "
            f"ORDER BY created_at DESC LIMIT ?",
            (session_id, *kinds, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT kind, title, detail, tool_name, files, created_at "
            "FROM observations WHERE session_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def get_session_context_for_subagent(conn: sqlite3.Connection,
                                     content_session_id: str) -> dict | None:
    """Get session context suitable for injection into subagent prompts.

    Returns session info + recent observations for cross-agent awareness.
    """
    row = conn.execute(
        "SELECT id, branch, initial_request FROM sessions "
        "WHERE content_session_id = ? LIMIT 1",
        (content_session_id,)
    ).fetchone()
    if not row:
        return None

    obs = get_subagent_observations(conn, row["id"], limit=10)
    return {
        "session_id": row["id"],
        "branch": row["branch"],
        "initial_request": row["initial_request"] or "",
        "recent_observations": obs,
    }


def get_stats(conn: sqlite3.Connection) -> dict:
    """Get memory database statistics."""
    total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    with_legacy = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE summary != ''"
    ).fetchone()[0]

    with_structured = 0
    try:
        with_structured = conn.execute(
            "SELECT COUNT(*) FROM session_summaries WHERE status = 'ready'"
        ).fetchone()[0]
    except sqlite3.OperationalError:
        pass

    obs_count = 0
    try:
        obs_count = conn.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]
    except sqlite3.OperationalError:
        pass

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
        "with_legacy_summary": with_legacy,
        "with_structured_summary": with_structured,
        "total_observations": obs_count,
        "oldest": oldest[0][:10] if oldest else None,
        "newest": newest[0][:10] if newest else None,
        "branches": [r[0] for r in branches],
        "db_path": str(get_db_path()),
        "schema_version": SCHEMA_VERSION,
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

    # Prefer structured summary
    if s.get("ss_completed") or s.get("ss_request"):
        if s.get("ss_request"):
            lines.append(f"  Request: {s['ss_request']}")
        if s.get("ss_completed"):
            lines.append(f"  Completed: {s['ss_completed']}")
        if s.get("ss_learned"):
            lines.append(f"  Learned: {s['ss_learned']}")
        if s.get("ss_next_steps"):
            lines.append(f"  Next: {s['ss_next_steps']}")
    elif s.get("summary"):
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

    # Prefer structured summary
    text = ""
    if s.get("ss_completed"):
        text = s["ss_completed"]
    elif s.get("summary"):
        text = s["summary"]

    if text:
        if len(text) > 60:
            text = text[:57] + "..."
        return f"Last session: {date} | {branch} | {file_count} files | \"{text}\""

    return f"Last session: {date} | {branch} | {file_count} files modified"


# -- Chroma Vector Search --


def get_chroma_dir() -> Path:
    """Get Chroma storage directory (.ultra/memory/chroma/)."""
    toplevel = get_git_toplevel()
    if toplevel:
        return Path(toplevel) / ".ultra" / "memory" / "chroma"
    return Path.home() / ".claude" / "memory" / "chroma"


def get_chroma_collection():
    """Get or create the sessions Chroma collection.

    Uses PersistentClient with local ONNX embedding (ONNXMiniLM_L6_V2).
    No API key required.
    """
    import chromadb

    chroma_dir = get_chroma_dir()
    chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_dir))
    return client.get_or_create_collection(
        name="sessions",
        metadata={"hnsw:space": "cosine"}
    )


def upsert_embedding(session_id: str, summary: str, branch: str,
                     files: list) -> bool:
    """Write session embedding to Chroma."""
    try:
        file_list = ", ".join(files[:5]) if files else ""
        doc = f"Branch: {branch}\nFiles: {file_list}\nSummary: {summary}"
        if len(doc) > 900:
            doc = doc[:900]

        collection = get_chroma_collection()
        collection.upsert(
            ids=[session_id],
            documents=[doc],
            metadatas=[{
                "branch": branch,
                "file_count": str(len(files)),
                "summary": summary[:500]
            }]
        )
        return True
    except Exception:
        return False


def semantic_search(query: str, limit: int = 10,
                    conn: sqlite3.Connection | None = None) -> list:
    """Pure vector semantic search via Chroma."""
    try:
        collection = get_chroma_collection()
        results = collection.query(
            query_texts=[query],
            n_results=limit
        )

        owns_conn = conn is None
        if owns_conn:
            conn = init_db()
        sessions = []
        if results and results["ids"] and results["ids"][0]:
            for sid in results["ids"][0]:
                row = conn.execute(
                    """SELECT id, started_at, last_active, branch, cwd,
                              files_modified, summary, tags, stop_count
                       FROM sessions WHERE id = ?""",
                    (sid,)
                ).fetchone()
                if row:
                    sessions.append(dict(row))
        if owns_conn:
            conn.close()
        return sessions
    except Exception:
        return []


def hybrid_search(conn: sqlite3.Connection, query: str,
                  limit: int = 10, k: int = 60) -> list:
    """Hybrid search: FTS5 + Chroma semantic, merged via RRF."""
    fts_results = search(conn, query, limit=limit * 2)
    fts_ids = [s["id"] for s in fts_results]

    sem_results = semantic_search(query, limit=limit * 2)
    sem_ids = [s["id"] for s in sem_results]

    scores: dict[str, float] = {}
    for rank, sid in enumerate(fts_ids):
        scores[sid] = scores.get(sid, 0.0) + 1.0 / (k + rank + 1)
    for rank, sid in enumerate(sem_ids):
        scores[sid] = scores.get(sid, 0.0) + 1.0 / (k + rank + 1)

    sorted_ids = sorted(
        scores.keys(), key=lambda x: scores[x], reverse=True
    )[:limit]

    session_map: dict[str, dict] = {}
    for s in fts_results + sem_results:
        if s["id"] not in session_map:
            session_map[s["id"]] = s

    return [session_map[sid] for sid in sorted_ids if sid in session_map]


def reindex_chroma(conn: sqlite3.Connection) -> int:
    """Reindex all sessions with summaries into Chroma.

    Indexes both legacy summaries and structured summaries (v2).
    Structured summaries take priority when both exist.
    """
    # Build summary text for each session: prefer structured over legacy
    rows = conn.execute(
        """SELECT s.id, s.branch, s.files_modified, s.summary,
                  ss.completed, ss.learned
           FROM sessions s
           LEFT JOIN session_summaries ss ON s.id = ss.session_id
           WHERE s.summary != '' OR ss.completed IS NOT NULL"""
    ).fetchall()

    count = 0
    for row in rows:
        # Prefer structured summary (richer content)
        if row["completed"]:
            summary = row["completed"]
            if row["learned"]:
                summary += " | " + row["learned"]
        else:
            summary = row["summary"] or ""

        if not summary:
            continue

        files = json.loads(row["files_modified"])
        if upsert_embedding(row["id"], summary, row["branch"], files):
            count += 1

    return count


# -- CLI Interface --

def cli_main():
    """CLI entry point for direct invocation."""
    if len(sys.argv) < 2:
        print("Usage: memory_db.py <command> [args]")
        print("Commands: search, semantic, hybrid, recent, latest, date, "
              "save-summary, add-tags, reindex-chroma, cleanup, stats, migrate")
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
                  f"({stats['with_legacy_summary']} legacy, "
                  f"{stats['with_structured_summary']} structured)")
            print(f"Observations: {stats['total_observations']}")
            if stats["oldest"]:
                print(f"Range: {stats['oldest']} -> {stats['newest']}")
            print(f"Branches: {', '.join(stats['branches']) or 'none'}")
            print(f"Schema: v{stats['schema_version']}")
            print(f"DB: {stats['db_path']}")

        elif cmd == "oneliner":
            result = get_latest(conn)
            if result:
                print(format_oneliner(result))

        elif cmd == "semantic":
            if len(sys.argv) < 3:
                print("Usage: memory_db.py semantic <query> [--limit N]")
                sys.exit(1)
            query = sys.argv[2]
            limit = 10
            if "--limit" in sys.argv:
                idx = sys.argv.index("--limit")
                if idx + 1 < len(sys.argv):
                    limit = int(sys.argv[idx + 1])

            results = semantic_search(query, limit)
            if not results:
                print(f"No semantic results for: {query}")
            else:
                print(f"Found {len(results)} session(s) semantically "
                      f"matching '{query}':\n")
                for s in results:
                    print(format_session(s, verbose=True))
                    print()

        elif cmd == "hybrid":
            if len(sys.argv) < 3:
                print("Usage: memory_db.py hybrid <query> [--limit N]")
                sys.exit(1)
            query = sys.argv[2]
            limit = 10
            if "--limit" in sys.argv:
                idx = sys.argv.index("--limit")
                if idx + 1 < len(sys.argv):
                    limit = int(sys.argv[idx + 1])

            results = hybrid_search(conn, query, limit)
            if not results:
                print(f"No hybrid results for: {query}")
            else:
                print(f"Found {len(results)} session(s) (hybrid "
                      f"FTS5+semantic) for '{query}':\n")
                for s in results:
                    print(format_session(s, verbose=True))
                    print()

        elif cmd == "reindex-chroma":
            count = reindex_chroma(conn)
            print(f"Reindexed {count} session(s) into Chroma")

        elif cmd == "migrate":
            print(f"Schema v{SCHEMA_VERSION} migration complete.")
            stats = get_stats(conn)
            print(f"Sessions: {stats['total_sessions']}")
            print(f"Structured summaries: {stats['with_structured_summary']}")
            print(f"Observations: {stats['total_observations']}")

        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    cli_main()
