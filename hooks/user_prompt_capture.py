#!/usr/bin/env python3
"""UserPromptSubmit Hook - Capture initial user request.

Stores the first user prompt of each session in sessions.initial_request.
Only writes once per session (ignores subsequent prompts).

Execution target: < 50ms (single DB write, no AI processing).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import memory_db


def main():
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        pass

    if not raw or not raw.strip():
        print(json.dumps({}))
        return

    try:
        data = json.loads(raw.strip())
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({}))
        return

    if not isinstance(data, dict):
        print(json.dumps({}))
        return

    prompt = data.get("prompt", "").strip()
    session_id = data.get("session_id", "").strip()

    if not prompt or not session_id:
        print(json.dumps({}))
        return

    # Store initial request (only first prompt per session)
    try:
        db_path = memory_db.get_db_path()
        if not db_path.exists():
            print(json.dumps({}))
            return

        conn = memory_db.init_db(db_path)

        # Find session by content_session_id
        row = conn.execute(
            "SELECT id, initial_request FROM sessions "
            "WHERE content_session_id = ? LIMIT 1",
            (session_id,)
        ).fetchone()

        if row:
            # Session exists — fill initial_request if empty
            if not row["initial_request"]:
                memory_db.set_initial_request(conn, row["id"], prompt)
        else:
            # Session not yet created by Stop hook — create minimal shell.
            # Stop hook's upsert_session will find and merge via content_session_id.
            now = datetime.now(timezone.utc)
            sid = now.strftime("%Y%m%d-%H%M%S") + f"-{now.microsecond // 1000:03d}"
            conn.execute(
                "INSERT INTO sessions "
                "(id, started_at, last_active, content_session_id, initial_request) "
                "VALUES (?, ?, ?, ?, ?)",
                (sid, now.isoformat(), now.isoformat(),
                 session_id, prompt[:2000])
            )
            conn.commit()

        conn.close()
    except Exception:
        print("[user_prompt_capture] DB error", file=sys.stderr)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
