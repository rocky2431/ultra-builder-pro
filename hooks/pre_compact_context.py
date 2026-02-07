#!/usr/bin/env python3
"""PreCompact hook: preserve critical context before compaction.

Outputs additionalContext with current task state and key decisions
so that compaction doesn't lose active work context.

Usage:
  python3 pre_compact_context.py  # called by PreCompact hook
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def get_git_context():
    """Get current git branch and recent activity."""
    import subprocess

    ctx = {}
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            ctx["branch"] = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "--cached"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            ctx["staged_changes"] = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return ctx


def get_task_context():
    """Read any active task files from .ultra/tasks/ if they exist."""
    task_dir = Path.cwd() / ".ultra" / "tasks"
    if not task_dir.exists():
        return None

    active_tasks = []
    for f in sorted(task_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        # Extract first line as task title
        first_line = content.split("\n", 1)[0].strip().lstrip("#").strip()
        if first_line:
            active_tasks.append(first_line)

    return active_tasks if active_tasks else None


def main():
    context_parts = []

    context_parts.append(
        f"[PreCompact] Compaction at {datetime.now(timezone.utc).isoformat()}"
    )

    git_ctx = get_git_context()
    if git_ctx.get("branch"):
        context_parts.append(f"Branch: {git_ctx['branch']}")
    if git_ctx.get("staged_changes"):
        context_parts.append(f"Staged changes:\n{git_ctx['staged_changes']}")

    tasks = get_task_context()
    if tasks:
        context_parts.append("Active tasks:\n" + "\n".join(f"  - {t}" for t in tasks))

    # Output as hook response with additionalContext
    output = {
        "additionalContext": "\n".join(context_parts)
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
