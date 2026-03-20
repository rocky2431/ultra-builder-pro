#!/usr/bin/env python3
"""
Pre-Stop Check Hook - Stop
Checks for unreviewed source code changes before session ends.

Simple two-layer logic:
0. Fast path: stop_hook_active or circuit breaker → allow stop
1. Source files changed → block + suggest code-reviewer

Complex audits (security, full pipeline) are the user's responsibility
via /ultra-review. This hook only catches "forgot to review" scenarios.

Counter file: /tmp/.claude_stop_count_<session_id>
"""

import sys
import json
import subprocess
import os
import tempfile
import time
import glob as glob_module


STOP_COUNT_PREFIX = ".claude_stop_count_"
MAX_STOP_BLOCKS = 2
GIT_TIMEOUT = 3
COUNTER_MAX_AGE = 86400

SOURCE_EXTENSIONS = {
    '.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java',
    '.sol', '.rb', '.vue', '.svelte', '.css', '.scss', '.html', '.sh',
}


def cleanup_old_counters() -> None:
    try:
        tmp_dir = tempfile.gettempdir()
        now = time.time()
        for path in glob_module.glob(os.path.join(tmp_dir, f"{STOP_COUNT_PREFIX}*")):
            try:
                if now - os.path.getmtime(path) > COUNTER_MAX_AGE:
                    os.unlink(path)
            except OSError:
                pass
    except Exception:
        pass


def get_stop_count(session_id: str) -> int:
    try:
        path = os.path.join(tempfile.gettempdir(), f"{STOP_COUNT_PREFIX}{session_id}")
        with open(path) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def increment_stop_count(session_id: str) -> int:
    count = get_stop_count(session_id) + 1
    path = os.path.join(tempfile.gettempdir(), f"{STOP_COUNT_PREFIX}{session_id}")
    try:
        with open(path, 'w') as f:
            f.write(str(count))
        os.chmod(path, 0o600)
    except OSError:
        pass
    return count


def get_changed_source_files() -> list[str]:
    """Return source files with staged or unstaged changes."""
    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True, text=True, timeout=GIT_TIMEOUT
        )
        if proc.returncode != 0:
            return []

        proc = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, timeout=GIT_TIMEOUT
        )
        if proc.returncode != 0:
            return []

        files = []
        for line in proc.stdout.rstrip('\n').split('\n'):
            if not line:
                continue
            status = line[:2]
            filepath = line[3:]
            if status[0] in 'MADRC' or status[1] in 'MD':
                ext = os.path.splitext(filepath)[1].lower()
                if ext in SOURCE_EXTENSIONS:
                    files.append(filepath)
        return files

    except (subprocess.TimeoutExpired, Exception):
        return []


def allow_stop() -> None:
    print(json.dumps({}))


def block_stop(session_id: str, reason: str) -> None:
    if session_id:
        count = increment_stop_count(session_id)
        print(f"[pre_stop_check] Block #{count}/{MAX_STOP_BLOCKS}", file=sys.stderr)
    print(json.dumps({"decision": "block", "reason": reason}))


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        allow_stop()
        return

    session_id = hook_data.get("session_id", "")

    cleanup_old_counters()

    # Layer 0a: stop_hook_active → already continued once, allow stop
    if hook_data.get("stop_hook_active", False):
        allow_stop()
        return

    # Layer 0b: Circuit breaker → prevent infinite block loop
    if session_id and get_stop_count(session_id) >= MAX_STOP_BLOCKS:
        allow_stop()
        return

    # Layer 1: Source files changed → suggest code-reviewer
    source_files = get_changed_source_files()
    if not source_files:
        allow_stop()
        return

    lines = [f"[Pre-Stop Check] {len(source_files)} source file(s) changed but not reviewed:"]
    for f in source_files[:8]:
        lines.append(f"  - {f}")
    if len(source_files) > 8:
        lines.append(f"  ... and {len(source_files) - 8} more")
    lines.append("")
    lines.append("Action: Run code-reviewer agent before stopping.")

    block_stop(session_id, "\n".join(lines))


if __name__ == '__main__':
    main()
