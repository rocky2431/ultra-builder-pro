#!/usr/bin/env python3
"""Subagent lifecycle tracker.

Logs SubagentStart/Stop events to ~/.claude/debug/subagent-log.jsonl
for debugging and cost analysis.

Usage:
  python3 subagent_tracker.py start  # called by SubagentStart hook
  python3 subagent_tracker.py stop   # called by SubagentStop hook
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / ".claude" / "debug"
LOG_FILE = LOG_DIR / "subagent-log.jsonl"


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    action = sys.argv[1]
    if action not in ("start", "stop"):
        sys.exit(0)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Read hook input from stdin (JSON with agent info)
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": f"subagent_{action}",
        "agent_name": hook_input.get("agent_name", "unknown"),
        "session_id": hook_input.get("session_id", "unknown"),
    }

    # For stop events, try to capture duration info
    if action == "stop":
        entry["turns_used"] = hook_input.get("turns_used", None)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
