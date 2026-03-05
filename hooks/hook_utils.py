#!/usr/bin/env python3
"""Shared utilities for Claude Code hooks.

Provides common functions to avoid duplication across hook files:
- Git repository detection and commands
- Project-level path resolution
- Workflow state management
"""

import json
import os
import subprocess
from pathlib import Path

GIT_TIMEOUT = 3


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
