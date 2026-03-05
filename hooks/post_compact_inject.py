#!/usr/bin/env python3
"""Post-Compact Context Injection — SessionStart(compact)

Triggered after auto-compact via SessionStart matcher="compact".
Reads compact-snapshot.md and workflow-state.json, injects ~800 tokens
of recovery context so Claude retains critical working state.

Complements session_context.py (which provides base git/project/memory context).
This hook provides the detailed recovery: tasks, workflow step, key files, decisions.
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_utils import get_snapshot_path, get_workflow_state

GIT_TIMEOUT = 3
COMPACT_MARKER = f".claude_compact_ts_{os.getuid()}"
SNAPSHOT_MAX_AGE = 3600  # 1 hour — ignore stale snapshots
MAX_INJECT_CHARS = 3200  # ~800 tokens budget


def check_freshness(snapshot_path: Path) -> bool:
    """Check if the snapshot is fresh enough to use.

    Checks marker file first (written by PreCompact), falls back to mtime.
    """
    marker_path = os.path.join(tempfile.gettempdir(), COMPACT_MARKER)

    # Prefer marker timestamp (written by PreCompact right before compact)
    try:
        if os.path.exists(marker_path):
            marker_age = time.time() - os.path.getmtime(marker_path)
            if marker_age < SNAPSHOT_MAX_AGE:
                return True
    except OSError:
        pass

    # Fallback to snapshot file mtime
    try:
        if snapshot_path.exists():
            file_age = time.time() - snapshot_path.stat().st_mtime
            return file_age < SNAPSHOT_MAX_AGE
    except OSError:
        pass

    return False


def parse_snapshot(snapshot_path: Path) -> dict:
    """Parse compact-snapshot.md into structured sections.

    Returns dict with keys: git_state, tasks, workflow, memory, raw.
    """
    result = {
        "git_state": "",
        "tasks": "",
        "workflow": "",
        "memory": "",
        "raw": "",
    }

    try:
        content = snapshot_path.read_text(encoding="utf-8")
        result["raw"] = content
    except OSError:
        return result

    current_section = ""
    section_lines: dict[str, list[str]] = {
        "git_state": [],
        "tasks": [],
        "workflow": [],
        "memory": [],
    }

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## Git State"):
            current_section = "git_state"
            continue
        elif stripped.startswith("## Active Tasks"):
            current_section = "tasks"
            continue
        elif stripped.startswith("## Active Workflow"):
            current_section = "workflow"
            continue
        elif stripped.startswith("## Session Memory"):
            current_section = "memory"
            continue
        elif stripped.startswith("## Recovery"):
            current_section = ""
            continue
        elif stripped.startswith("## ") or stripped.startswith("# "):
            current_section = ""
            continue

        if current_section and stripped:
            section_lines[current_section].append(line)

    for key, lines in section_lines.items():
        result[key] = "\n".join(lines).strip()

    return result


def build_injection(sections: dict, workflow: dict | None) -> str:
    """Build the recovery context string within token budget."""
    parts = ["[Post-Compact Recovery]"]

    # Git state: extract branch and file count
    git = sections.get("git_state", "")
    if git:
        for line in git.split("\n"):
            if line.startswith("Branch:"):
                parts.append(line.strip())
                break

        # Count modified files
        file_lines = [l for l in git.split("\n")
                      if l.strip().startswith(("M ", "A ", "D ", "?? ", "R "))]
        if file_lines:
            parts.append(f"Modified files: {len(file_lines)}")
            # Show first 8 files
            for fl in file_lines[:8]:
                parts.append(f"  {fl.strip()}")
            if len(file_lines) > 8:
                parts.append(f"  ... and {len(file_lines) - 8} more")

    # Active workflow (highest priority)
    if workflow:
        cmd = workflow.get("command", "?")
        task_id = workflow.get("task_id", "?")
        step = workflow.get("step", "?")
        status = workflow.get("status", "?")
        parts.append("")
        parts.append(f"Active Workflow: {cmd} task {task_id} at step {step} ({status})")
        if workflow.get("review_session"):
            parts.append(f"  Review session: {workflow['review_session']}")
        if workflow.get("commit"):
            parts.append(f"  Last commit: {workflow['commit']}")
        parts.append(f"  Resume: Read `.ultra/workflow-state.json` and continue from step {step}")
    elif sections.get("workflow"):
        parts.append("")
        parts.append("Active Workflow:")
        for line in sections["workflow"].split("\n")[:5]:
            parts.append(f"  {line.strip()}")

    # Active tasks
    tasks = sections.get("tasks", "")
    if tasks:
        parts.append("")
        parts.append("Active Tasks:")
        for line in tasks.split("\n")[:6]:
            if line.strip():
                parts.append(f"  {line.strip()}")

    # Session memory (brief)
    memory = sections.get("memory", "")
    if memory:
        parts.append("")
        parts.append("Session Memory:")
        mem_lines = [l for l in memory.split("\n") if l.strip().startswith("- ")]
        for line in mem_lines[:3]:
            # Truncate long summaries
            text = line.strip()
            if len(text) > 150:
                text = text[:147] + "..."
            parts.append(f"  {text}")

    # Recovery pointer
    snapshot_path = get_snapshot_path()
    parts.append("")
    parts.append(f"Full context: `Read {snapshot_path}`")

    result = "\n".join(parts)

    # Enforce budget
    if len(result) > MAX_INJECT_CHARS:
        result = result[:MAX_INJECT_CHARS - 50] + "\n\n[truncated — read full snapshot]"

    return result


def main():
    # Consume stdin
    try:
        sys.stdin.read()
    except Exception:
        pass

    snapshot_path = get_snapshot_path()

    # Check if snapshot exists and is fresh
    if not snapshot_path.exists():
        print(json.dumps({}))
        return

    if not check_freshness(snapshot_path):
        # Stale snapshot — inject minimal hint only
        hint = f"[Post-Compact] Snapshot exists but may be stale. Read `{snapshot_path}` to recover context."
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": hint
            }
        }
        print(json.dumps(output))
        return

    # Parse snapshot and build injection
    sections = parse_snapshot(snapshot_path)
    workflow = get_workflow_state()
    injection = build_injection(sections, workflow)

    if not injection or len(injection) < 30:
        print(json.dumps({}))
        return

    # Clean up marker file (one-time use)
    marker_path = os.path.join(tempfile.gettempdir(), COMPACT_MARKER)
    try:
        if os.path.exists(marker_path):
            os.unlink(marker_path)
    except OSError:
        pass

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": injection
        }
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
