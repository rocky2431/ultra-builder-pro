#!/usr/bin/env python3
"""Session Journal Hook - Stop

Records session events to SQLite + JSONL for cross-session memory.
Debounced: merges entries within 30-minute windows for same branch+cwd.

Layer 2: Auto-generates summary from recent git commits (no AI).
Layer 3: Reminds Claude to save a detailed summary when substantive changes exist.

Execution target: < 100ms (no AI, no network calls).
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import shared memory_db module
sys.path.insert(0, str(Path(__file__).parent))
import memory_db

GIT_TIMEOUT = 3
COMMIT_WINDOW_MIN = 30


def run_git(*args) -> str:
    """Run git command, return stdout or empty string."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def get_modified_files() -> list:
    """Get list of modified/staged files from git status."""
    status = run_git("status", "--porcelain")
    if not status:
        return []

    files = []
    for line in status.split("\n"):
        if not line or len(line) < 4:
            continue
        filepath = line[3:].strip()
        if " -> " in filepath:
            filepath = filepath.split(" -> ")[1]
        files.append(filepath)

    return files


def get_recent_commits() -> str:
    """Extract recent commit messages as auto-summary.

    Uses --since to scope to the merge window. Returns a compact
    summary string, or empty if no recent commits.
    """
    log = run_git(
        "log", "--oneline",
        f"--since={COMMIT_WINDOW_MIN} minutes ago",
        "--no-merges",
        "--format=%s"
    )
    if not log:
        return ""

    messages = log.split("\n")
    # Deduplicate and limit
    seen = set()
    unique = []
    for msg in messages:
        msg = msg.strip()
        if msg and msg not in seen:
            seen.add(msg)
            unique.append(msg)

    if not unique:
        return ""

    # Join with " + ", truncate to 200 chars
    summary = " + ".join(unique)
    if len(summary) > 200:
        summary = summary[:197] + "..."

    return summary


def main():
    # Consume stdin (required by hook protocol)
    try:
        sys.stdin.read()
    except Exception:
        pass

    # Must be in a git repo
    branch = run_git("branch", "--show-current")
    if not branch:
        print(json.dumps({}))
        return

    cwd = os.getcwd()
    files_modified = get_modified_files()

    # Layer 2: Auto-generate summary from recent git commits
    auto_summary = get_recent_commits()

    # Write to SQLite (with 30-min merge window)
    session_id = None
    try:
        conn = memory_db.init_db()
        session_id = memory_db.upsert_session(
            conn, branch, cwd, files_modified
        )

        # Auto-fill summary if empty and we have commit messages
        if auto_summary and session_id:
            current = memory_db.get_latest(conn)
            if current and not current.get("summary"):
                memory_db.update_summary(conn, session_id, auto_summary)

        conn.close()
    except Exception as e:
        print(f"[session_journal] DB error: {e}", file=sys.stderr)

    # Append to JSONL (backup + human-readable)
    try:
        jsonl_path = memory_db.get_jsonl_path()
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "sid": session_id,
            "branch": branch,
            "cwd": cwd,
            "files": files_modified,
            "auto_summary": auto_summary,
        }
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[session_journal] JSONL error: {e}", file=sys.stderr)

    # Output: no block, no context (Stop hook doesn't support additionalContext)
    print(json.dumps({}))


if __name__ == "__main__":
    main()
