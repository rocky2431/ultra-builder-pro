#!/usr/bin/env python3
"""PreToolUse Hook - Mid-Workflow Memory Recall.

When editing source files that have past observations (test failures, learned
lessons from previous sessions), injects concise historical context via stderr.

Fires on: Write|Edit
Performance: <50ms common case (no matches), <100ms with injection
Rate-limited: once per file per session, max 10 injections per session
"""

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_INJECTIONS = 10
GIT_TIMEOUT = 3

SOURCE_EXTENSIONS = {
    '.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java',
    '.sol', '.rb', '.vue', '.svelte', '.sh',
}


def get_db_path() -> Path | None:
    """Get memory.db path. Returns None if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0 and result.stdout.strip():
            db = Path(result.stdout.strip()) / ".ultra" / "memory" / "memory.db"
            if db.exists():
                return db
    except Exception:
        pass
    fallback = Path.home() / ".claude" / "memory" / "memory.db"
    return fallback if fallback.exists() else None


def get_tracker_path(session_id: str) -> str:
    return os.path.join(tempfile.gettempdir(), f".claude_recall_{session_id}")


def load_recalled(session_id: str) -> set:
    try:
        with open(get_tracker_path(session_id)) as f:
            return set(line.strip() for line in f if line.strip())
    except (OSError, FileNotFoundError):
        return set()


def mark_recalled(session_id: str, file_path: str) -> None:
    tracker = get_tracker_path(session_id)
    try:
        with open(tracker, 'a') as f:
            f.write(file_path + '\n')
        os.chmod(tracker, 0o600)
    except OSError:
        pass


def query_file_observations(db_path: Path, filename: str,
                            content_session_id: str) -> dict:
    """Query past observations for a file from other sessions.

    Returns dict with 'test_failures' and 'edit_history' lists.
    """
    result = {"test_failures": [], "edit_history": []}
    try:
        conn = sqlite3.connect(str(db_path), timeout=1)
        conn.row_factory = sqlite3.Row

        # Test failures (highest priority signal)
        rows = conn.execute(
            """SELECT o.kind, o.title, o.detail, o.created_at, s.branch
               FROM observations o
               JOIN sessions s ON o.session_id = s.id
               WHERE o.files LIKE ?
               AND o.kind = 'test_failure'
               AND s.content_session_id != ?
               ORDER BY o.created_at DESC
               LIMIT 3""",
            (f'%{filename}%', content_session_id)
        ).fetchall()
        result["test_failures"] = [dict(r) for r in rows]

        # Cross-session edit history (useful context even without test failures)
        rows = conn.execute(
            """SELECT o.title, o.created_at, s.branch,
                      ss.request as session_request
               FROM observations o
               JOIN sessions s ON o.session_id = s.id
               LEFT JOIN session_summaries ss ON o.session_id = ss.session_id
               WHERE o.files LIKE ?
               AND o.kind = 'edit'
               AND s.content_session_id != ?
               ORDER BY o.created_at DESC
               LIMIT 3""",
            (f'%{filename}%', content_session_id)
        ).fetchall()
        result["edit_history"] = [dict(r) for r in rows]

        conn.close()
    except Exception:
        pass
    return result


def query_learned_lessons(db_path: Path, filename: str) -> list:
    """Query past session learnings and completions mentioning this file."""
    try:
        conn = sqlite3.connect(str(db_path), timeout=1)
        conn.row_factory = sqlite3.Row
        # Search both learned AND completed fields for file mentions
        rows = conn.execute(
            """SELECT ss.learned, ss.completed, s.started_at, s.branch
               FROM session_summaries ss
               JOIN sessions s ON ss.session_id = s.id
               WHERE (ss.learned LIKE ? OR ss.completed LIKE ?)
               AND (ss.learned != '' OR ss.completed != '')
               ORDER BY s.started_at DESC
               LIMIT 2""",
            (f'%{filename}%', f'%{filename}%')
        ).fetchall()
        results = [dict(r) for r in rows]
        conn.close()
        return results
    except Exception:
        return []


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({}))
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "")

    if tool_name not in ("Write", "Edit"):
        print(json.dumps({}))
        return

    file_path = tool_input.get("file_path", "")
    if not file_path:
        print(json.dumps({}))
        return

    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SOURCE_EXTENSIONS:
        print(json.dumps({}))
        return

    # Rate limit: skip if already recalled or quota exhausted
    if session_id:
        recalled = load_recalled(session_id)
        if file_path in recalled or len(recalled) >= MAX_INJECTIONS:
            print(json.dumps({}))
            return

    db_path = get_db_path()
    if not db_path:
        print(json.dumps({}))
        return

    obs_data = query_file_observations(db_path, filename, session_id or "")
    lessons = query_learned_lessons(db_path, filename)

    test_failures = obs_data.get("test_failures", [])
    edit_history = obs_data.get("edit_history", [])

    if not test_failures and not edit_history and not lessons:
        print(json.dumps({}))
        return

    # Format concise injection
    lines = [f"[Memory: {filename}]"]

    # Test failures (highest priority)
    for obs in test_failures[:2]:
        date = obs["created_at"][:10]
        branch = obs.get("branch", "")
        prefix = f"({date}" + (f", {branch}" if branch else "") + ")"
        lines.append(f"  Test failure {prefix}: {obs['title'][:120]}")
        if obs.get("detail"):
            lines.append(f"    cmd: {obs['detail'][:80]}")

    # Cross-session edit history (only if no test failures, to keep it concise)
    if not test_failures and edit_history:
        seen_branches = set()
        for edit in edit_history[:2]:
            branch = edit.get("branch", "")
            if branch in seen_branches:
                continue
            seen_branches.add(branch)
            date = edit["created_at"][:10]
            ctx = edit.get("session_request", "")
            if ctx:
                ctx = f" — {ctx[:60]}"
            lines.append(f"  Previously edited ({date}, {branch}){ctx}")

    # Learned lessons / completed context
    for lesson in lessons[:1]:
        learned = lesson.get("learned", "")
        if learned:
            lines.append(f"  Learned ({lesson['started_at'][:10]}): {learned.replace('|', ', ')[:150]}")
        elif lesson.get("completed"):
            lines.append(f"  Context ({lesson['started_at'][:10]}): {lesson['completed'].replace('|', ', ')[:150]}")

    print("\n".join(lines), file=sys.stderr)

    if session_id:
        mark_recalled(session_id, file_path)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
