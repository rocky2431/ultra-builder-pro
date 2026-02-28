#!/usr/bin/env python3
"""PreCompact hook: preserve critical context before compaction.

Two-layer strategy:
1. additionalContext → guides the compactor on what to preserve in summary
2. Disk file (~/.claude/compact-snapshot.md) → full context recoverable via Read tool

Usage:
  python3 pre_compact_context.py  # called by PreCompact hook
"""

import json
import subprocess
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

GIT_TIMEOUT = 3


def get_snapshot_path() -> Path:
    """Get project-level snapshot path (.ultra/compact-snapshot.md).

    Falls back to ~/.claude/compact-snapshot.md if not in a git repo.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()) / ".ultra" / "compact-snapshot.md"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return Path.home() / ".claude" / "compact-snapshot.md"


SNAPSHOT_PATH = get_snapshot_path()


def run_git(*args):
    """Run git command with timeout, return stdout or empty string."""
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


def get_git_context():
    """Get git state: branch, recent commits, modified files."""
    ctx = {}
    ctx["branch"] = run_git("branch", "--show-current")
    ctx["log"] = run_git("log", "--oneline", "-5")
    ctx["status"] = run_git("status", "--short")
    ctx["staged"] = run_git("diff", "--stat", "--cached")
    return {k: v for k, v in ctx.items() if v}


def get_task_context():
    """Read active task files from .ultra/tasks/ if they exist."""
    task_dir = Path.cwd() / ".ultra" / "tasks"
    if not task_dir.exists():
        return []

    tasks = []
    for f in sorted(task_dir.glob("*.md")):
        try:
            content = f.read_text(encoding="utf-8")
            first_line = content.split("\n", 1)[0].strip().lstrip("#").strip()
            if first_line:
                tasks.append(first_line)
        except OSError:
            pass
    return tasks


def get_native_tasks():
    """Read native Claude Code task list files if they exist."""
    todos_dir = Path.home() / ".claude" / "todos"
    if not todos_dir.exists():
        return []

    tasks = []
    for f in sorted(todos_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for task in data:
                    if isinstance(task, dict) and task.get("status") != "completed":
                        subject = task.get("subject", "")
                        status = task.get("status", "pending")
                        if subject:
                            tasks.append(f"[{status}] {subject}")
            if tasks:
                break  # only read most recent task file
        except (json.JSONDecodeError, OSError):
            pass
    return tasks


def get_cwd_info():
    """Get current working directory project info."""
    cwd = Path.cwd()
    info = str(cwd)
    for marker in ["package.json", "pyproject.toml", "Cargo.toml", "go.mod"]:
        if (cwd / marker).exists():
            info += f" ({marker})"
            break
    return info


def get_branch_memory(branch: str) -> list:
    """Query memory DB directly for recent sessions with summaries on this branch.

    Returns formatted summary lines for inclusion in compact snapshot.
    """
    if not branch:
        return []

    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import memory_db

        db_path = memory_db.get_db_path()
        if not db_path.exists():
            return []

        conn = memory_db.init_db(db_path)
        rows = conn.execute(
            """SELECT id, last_active, summary FROM sessions
               WHERE branch = ? AND summary != ''
               ORDER BY last_active DESC LIMIT 5""",
            (branch,)
        ).fetchall()
        conn.close()

        lines = []
        for row in rows:
            date = row["last_active"][:10]
            summary = row["summary"]
            # Truncate to keep compact
            if len(summary) > 200:
                summary = summary[:197] + "..."
            lines.append(f"- [{date}] {summary}")

        return lines
    except Exception:
        pass
    return []


def get_workflow_state():
    """Read active workflow state from .ultra/workflow-state.json."""
    state_file = Path.cwd() / ".ultra" / "workflow-state.json"
    if not state_file.exists():
        return None
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def build_snapshot(git_ctx, ultra_tasks, native_tasks, timestamp):
    """Build the full snapshot content for disk persistence."""
    lines = [
        f"# Compact Snapshot",
        f"*Generated: {timestamp}*",
        f"*Working dir: {get_cwd_info()}*",
        "",
    ]

    if git_ctx.get("branch"):
        lines.append(f"## Git State")
        lines.append(f"Branch: `{git_ctx['branch']}`")
        if git_ctx.get("log"):
            lines.append(f"\nRecent commits:")
            for commit in git_ctx["log"].split("\n")[:5]:
                lines.append(f"  {commit}")
        if git_ctx.get("status"):
            lines.append(f"\nModified files:")
            for f in git_ctx["status"].split("\n")[:15]:
                lines.append(f"  {f}")
            status_lines = git_ctx["status"].split("\n")
            if len(status_lines) > 15:
                lines.append(f"  ... and {len(status_lines) - 15} more")
        if git_ctx.get("staged"):
            lines.append(f"\nStaged changes:\n{git_ctx['staged']}")
        lines.append("")

    if ultra_tasks or native_tasks:
        lines.append("## Active Tasks")
        for t in (native_tasks or ultra_tasks):
            lines.append(f"- {t}")
        lines.append("")

    # Inject active workflow state
    workflow = get_workflow_state()
    if workflow:
        lines.append("## Active Workflow")
        lines.append(f"- Command: {workflow.get('command', '?')}")
        lines.append(f"- Task: {workflow.get('task_id', '?')}")
        lines.append(f"- Step: {workflow.get('step', '?')} ({workflow.get('status', '?')})")
        if workflow.get('review_session'):
            lines.append(f"- Review: {workflow['review_session']}")
        lines.append(f"- Resume: Read `.ultra/workflow-state.json` and skip to step {workflow.get('step', '?')}")
        lines.append("")

    # Inject branch-relevant session memory
    branch = git_ctx.get("branch", "")
    branch_mem = get_branch_memory(branch)
    if branch_mem:
        lines.append("## Session Memory (this branch)")
        lines.append("Recent session summaries for context continuity:")
        lines.extend(branch_mem)
        lines.append("")

    lines.append("## Recovery Instructions")
    lines.append("After compact, read this file to restore context:")
    lines.append(f"`Read {SNAPSHOT_PATH}`")
    lines.append("")

    return "\n".join(lines)


def build_compact_hint(git_ctx, ultra_tasks, native_tasks):
    """Build concise additionalContext for the compactor (keep short)."""
    parts = []

    if git_ctx.get("branch"):
        parts.append(f"Branch: {git_ctx['branch']}")

    if git_ctx.get("status"):
        file_count = len(git_ctx["status"].split("\n"))
        parts.append(f"Modified files: {file_count}")

    all_tasks = native_tasks or ultra_tasks
    if all_tasks:
        parts.append(f"Active tasks: {len(all_tasks)}")
        for t in all_tasks[:3]:
            parts.append(f"  - {t}")

    workflow = get_workflow_state()
    if workflow:
        parts.append(f"RESUME: ultra-dev task {workflow.get('task_id')} at step {workflow.get('step')}")

    parts.append(f"Full context saved to: {SNAPSHOT_PATH}")

    return "\n".join(parts)


def main():
    # Consume stdin to avoid broken pipe
    try:
        sys.stdin.read()
    except Exception:
        pass

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    git_ctx = get_git_context()
    ultra_tasks = get_task_context()
    native_tasks = get_native_tasks()

    # Layer 1: Write full snapshot to disk
    snapshot = build_snapshot(git_ctx, ultra_tasks, native_tasks, timestamp)
    try:
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(snapshot, encoding="utf-8")
    except OSError as e:
        print(f"[pre_compact] Failed to write snapshot: {e}", file=sys.stderr)

    # Layer 2: Output concise hint as additionalContext for compactor
    hint = build_compact_hint(git_ctx, ultra_tasks, native_tasks)
    output = {
        "additionalContext": f"[PreCompact {timestamp}]\n{hint}"
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
