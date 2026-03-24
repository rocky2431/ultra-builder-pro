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

COMPLIANCE_CHECKLIST = """
## Completion Compliance Check

Before stopping, verify ALL of the following:

1. **Goal Check**: Re-read the user's original request. Is it FULLY achieved? Not partially — DONE.
2. **Verification**: Did you actually run tests and show passing output? "Should work" is not evidence.
3. **Loose Ends**: Any TODO/FIXME/placeholder? Any promised tests not written? Any skipped edge cases?
4. **Task List**: Are ALL tasks marked completed? Check with TaskList.

The following are NOT valid reasons to stop:
- "made good progress" / "mostly done" / "diminishing returns"
- "would require broader architectural changes"
- "the rest can be done manually"
- "beyond the scope of this session"
- "should work based on the pattern" / "I'm confident"

If ANY check fails → continue working. Stop ONLY when everything is verifiably complete.
""".strip()


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


def get_git_toplevel() -> str:
    """Get git repo root, or empty string."""
    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=GIT_TIMEOUT
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        pass
    return ""


def check_workflow_state() -> str | None:
    """Check .ultra/workflow-state.json for incomplete workflow."""
    try:
        toplevel = get_git_toplevel()
        if not toplevel:
            return None
        state_path = os.path.join(toplevel, ".ultra", "workflow-state.json")
        if not os.path.exists(state_path):
            return None
        with open(state_path) as f:
            state = json.load(f)
        status = state.get("status", "")
        if status in ("committed", "completed", "done"):
            return None
        step = state.get("step", "unknown")
        command = state.get("command", "unknown")
        return f"Active workflow '{command}' at step {step} (status: {status})"
    except Exception:
        return None


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

    # Collect block reasons from multiple layers
    reasons = []

    # Layer 1: Source files changed → suggest code-reviewer
    source_files = get_changed_source_files()
    if source_files:
        lines = [f"[Pre-Stop] {len(source_files)} source file(s) changed but not reviewed:"]
        for f in source_files[:8]:
            lines.append(f"  - {f}")
        if len(source_files) > 8:
            lines.append(f"  ... and {len(source_files) - 8} more")
        lines.append("Action: Run code-reviewer agent before stopping.")
        reasons.append("\n".join(lines))

    # Layer 2: Incomplete workflow state
    workflow_issue = check_workflow_state()
    if workflow_issue:
        reasons.append(f"[Pre-Stop] {workflow_issue} — complete the workflow before stopping.")

    if not reasons:
        allow_stop()
        return

    # Append compliance checklist to any block
    full_reason = "\n\n".join(reasons) + "\n\n" + COMPLIANCE_CHECKLIST
    block_stop(session_id, full_reason)


if __name__ == '__main__':
    main()
