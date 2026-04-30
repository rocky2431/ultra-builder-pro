#!/usr/bin/env python3
"""Shared utilities for Claude Code hooks.

Provides common functions to avoid duplication across hook files:
- Git repository detection and commands
- Project-level path resolution
- Workflow state management
- v7: north-star + task progress (Goal-Always-Present + Incremental Validation)
"""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

GIT_TIMEOUT = 3

# v7 evidence dimensions tracked by progress.json
EVIDENCE_DIMENSIONS = (
    "tests_written",
    "tests_passed",
    "persistence_real",
    "feature_flags_audit",
    "vertical_slice",
    "spec_trace",
)
MAX_ADVISORIES_PER_TASK = 50


def get_git_toplevel() -> str:
    """Get git repository root, or empty string if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=GIT_TIMEOUT,
            cwd=os.getcwd()
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def run_git(*args, timeout: int = GIT_TIMEOUT) -> str:
    """Run git command, return stdout or empty string."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=timeout,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def get_project_path(subpath: str, fallback_base: str = "~/.claude") -> Path:
    """Resolve project-level path: {git_toplevel}/.ultra/{subpath}.

    Falls back to {fallback_base}/{subpath} if not in a git repo.
    """
    toplevel = get_git_toplevel()
    if toplevel:
        return Path(toplevel) / ".ultra" / subpath
    return Path(fallback_base).expanduser() / subpath


def get_snapshot_path() -> Path:
    """Get compact snapshot path (.ultra/compact-snapshot.md)."""
    toplevel = get_git_toplevel()
    if toplevel:
        return Path(toplevel) / ".ultra" / "compact-snapshot.md"
    return Path.home() / ".claude" / "compact-snapshot.md"


def get_workflow_state() -> dict | None:
    """Read active workflow state from .ultra/workflow-state.json."""
    state_file = Path.cwd() / ".ultra" / "workflow-state.json"
    if not state_file.exists():
        return None
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# -- v7: Goal-Always-Present + Incremental Validation helpers --

def get_active_task() -> dict | None:
    """Return the in_progress task dict from .ultra/tasks/tasks.json (or None)."""
    toplevel = get_git_toplevel()
    if not toplevel:
        return None
    tasks_path = Path(toplevel) / ".ultra" / "tasks" / "tasks.json"
    if not tasks_path.exists():
        return None
    try:
        data = json.loads(tasks_path.read_text(encoding="utf-8"))
        for t in data.get("tasks", []):
            if t.get("status") == "in_progress":
                return t
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _init_progress(task_id: str) -> dict:
    """Initial progress.json shape. evidence_score 0-100 per dimension."""
    return {
        "task_id": task_id,
        "evidence_score": {dim: 0 for dim in EVIDENCE_DIMENSIONS},
        "files_touched": [],
        "advisories": [],
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def get_progress_path(task_id: str) -> Path | None:
    """Path to .ultra/tasks/progress/task-<id>.json (creates parent dir if needed)."""
    toplevel = get_git_toplevel()
    if not toplevel:
        return None
    path = Path(toplevel) / ".ultra" / "tasks" / "progress" / f"task-{task_id}.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    return path


def update_task_progress(file_path: str, advisories: list | None = None) -> None:
    """v7 Incremental Validation: maintain progress.json on PostToolUse.

    Best-effort: silent on any error. Looks up the in_progress task, appends the
    edited file to files_touched, and records advisory entries (capped).

    Evidence dimension scores are not auto-derived here — they are updated by
    purpose-built sensors (test runner, persistence detector, etc.) which will
    be added incrementally. This helper just keeps the file fresh + tracks
    surface signal so agent and user can read 'how far from done' anytime.
    """
    task = get_active_task()
    if not task:
        return
    tid = task.get("id")
    if not tid:
        return
    progress_path = get_progress_path(tid)
    if progress_path is None:
        return

    if progress_path.exists():
        try:
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            progress = _init_progress(tid)
    else:
        progress = _init_progress(tid)

    # Heal missing dimensions from older runs
    progress.setdefault("evidence_score", {})
    for dim in EVIDENCE_DIMENSIONS:
        progress["evidence_score"].setdefault(dim, 0)
    progress.setdefault("files_touched", [])
    progress.setdefault("advisories", [])

    # Touch tracking
    toplevel = get_git_toplevel()
    if toplevel:
        try:
            rel = os.path.relpath(file_path, toplevel)
        except ValueError:
            rel = file_path
    else:
        rel = file_path
    if rel not in progress["files_touched"]:
        progress["files_touched"].append(rel)

    # Advisory log (capped)
    if advisories:
        now = datetime.now(timezone.utc).isoformat()
        for msg in advisories:
            progress["advisories"].append({
                "at": now,
                "file": rel,
                "msg": str(msg)[:240],
            })
        progress["advisories"] = progress["advisories"][-MAX_ADVISORIES_PER_TASK:]

    progress["last_updated"] = datetime.now(timezone.utc).isoformat()

    try:
        progress_path.write_text(
            json.dumps(progress, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        pass


def get_distance_to_done(task_id: str) -> str:
    """Human-readable summary of evidence_score for advisory injection."""
    progress_path = get_progress_path(task_id)
    if progress_path is None or not progress_path.exists():
        return ""
    try:
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    scores = progress.get("evidence_score", {})
    completed = sum(1 for v in scores.values() if v >= 80)
    total = len(EVIDENCE_DIMENSIONS)
    pending = [d for d in EVIDENCE_DIMENSIONS if scores.get(d, 0) < 80]
    parts = [f"{completed}/{total} evidence dimensions ≥80%"]
    if pending:
        parts.append(f"pending: {', '.join(pending[:3])}")
    return "; ".join(parts)
