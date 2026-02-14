#!/usr/bin/env python3
"""Subagent lifecycle tracker.

Logs SubagentStart/Stop events to ~/.claude/debug/subagent-log.jsonl
for debugging and cost analysis.

Usage:
  python3 subagent_tracker.py start  # called by SubagentStart hook
  python3 subagent_tracker.py stop   # called by SubagentStop hook
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_log_dir() -> Path:
    """Get project-level log directory (.ultra/debug/ relative to git toplevel).

    Falls back to ~/.claude/debug/ if not in a git repo.
    """
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return Path(proc.stdout.strip()) / ".ultra" / "debug"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return Path.home() / ".claude" / "debug"


LOG_DIR = get_log_dir()
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
        if not isinstance(hook_input, dict):
            hook_input = {}
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

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        sys.exit(0)


if __name__ == "__main__":
    main()
