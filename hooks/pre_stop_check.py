#!/usr/bin/env python3
"""
Pre-Stop Check Hook - Stop (v7.0 sensor mode)
Emits advisory via stderr; never blocks.

Layers:
0. Fast path: stop_hook_active → allow stop (already past)
1. Source files changed → stderr advisory, allow stop
2. Workflow incomplete → stderr advisory, allow stop

v7.0 design notes:
- Old block-mode caused over-correction loops (agents edited tests/specs to
  escape, drifting from user intent). Sensor mode prevents that by design.
- The pre-v7 circuit breaker (MAX_STOP_BLOCKS=2 + counter files in /tmp) was
  removed: it was an architectural admission that block-loops were harmful
  rather than a fix. PHILOSOPHY.md C3 — sensors not blockers.
"""

import sys
import json
import subprocess
import os


GIT_TIMEOUT = 3

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


def main():
    """v7.0: sensor mode — advisory via stderr, never block.

    See module docstring for the full rationale (over-correction loop, removal
    of pre-v7 circuit breaker). This function only emits advisories and always
    allows stop.
    """
    try:
        hook_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        allow_stop()
        return

    # Fast path: agent has already continued past one stop in this session,
    # don't re-emit advisories on subsequent stops.
    if hook_data.get("stop_hook_active", False):
        allow_stop()
        return

    advisories = []

    # Layer 1: Source files changed → advisory (was: block)
    source_files = get_changed_source_files()
    if source_files:
        lines = [f"[Pre-Stop Advisory] {len(source_files)} source file(s) changed but not reviewed:"]
        for f in source_files[:8]:
            lines.append(f"  - {f}")
        if len(source_files) > 8:
            lines.append(f"  ... and {len(source_files) - 8} more")
        lines.append("Recommended: code-reviewer agent (not blocking — stop allowed).")
        advisories.append("\n".join(lines))

    # Layer 2: Incomplete workflow state → advisory (was: block)
    workflow_issue = check_workflow_state()
    if workflow_issue:
        advisories.append(f"[Pre-Stop Advisory] {workflow_issue} — consider resuming, not blocking.")

    if advisories:
        # Emit compliance checklist via stderr only — do NOT block
        full_advisory = "\n\n".join(advisories) + "\n\n" + COMPLIANCE_CHECKLIST
        print(full_advisory, file=sys.stderr)

    # Always allow stop in sensor mode
    allow_stop()


if __name__ == '__main__':
    main()
