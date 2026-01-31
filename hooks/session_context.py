#!/usr/bin/env python3
"""
Session Context Hook - SessionStart
Loads development context at session start.

Provides:
- Current git branch and recent commits
- Modified files status
"""

import sys
import json
import subprocess
import os
from datetime import datetime


def run_cmd(cmd: list, cwd: str = '') -> str:
    """Run command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd(),
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"[session_context] Command failed: {' '.join(cmd)}: {e}", file=sys.stderr)
    return ''


def get_git_context() -> list:
    """Get git repository context."""
    context = []

    # Check if in git repo
    if not run_cmd(['git', 'rev-parse', '--is-inside-work-tree']):
        return context

    # Current branch
    branch = run_cmd(['git', 'branch', '--show-current'])
    if branch:
        context.append(f"Branch: {branch}")

    # Recent commits (last 3)
    log = run_cmd(['git', 'log', '--oneline', '-3'])
    if log:
        context.append("Recent commits:")
        for line in log.split('\n'):
            context.append(f"  {line}")

    # Modified files
    status = run_cmd(['git', 'status', '--short'])
    if status:
        lines = status.split('\n')
        context.append(f"Modified files: {len(lines)}")
        for line in lines[:5]:
            context.append(f"  {line}")
        if len(lines) > 5:
            context.append(f"  ... and {len(lines) - 5} more")

    return context


def get_project_context() -> list:
    """Get project-specific context."""
    context = []

    # Check for package.json
    if os.path.exists('package.json'):
        try:
            with open('package.json', 'r') as f:
                pkg = json.load(f)
                name = pkg.get('name', 'unknown')
                context.append(f"Project: {name} (Node.js)")
        except Exception:
            pass

    # Check for pyproject.toml
    elif os.path.exists('pyproject.toml'):
        context.append("Project: Python (pyproject.toml)")

    # Check for Cargo.toml
    elif os.path.exists('Cargo.toml'):
        context.append("Project: Rust (Cargo.toml)")

    # Check for go.mod
    elif os.path.exists('go.mod'):
        context.append("Project: Go (go.mod)")

    return context


def main():
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[session_context] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    source = hook_input.get('source', 'startup')

    # Build context
    context_lines = [
        f"[Session Context] {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Session type: {source}",
        ""
    ]

    # Add git context
    git_ctx = get_git_context()
    if git_ctx:
        context_lines.extend(git_ctx)
        context_lines.append("")

    # Add project context
    proj_ctx = get_project_context()
    if proj_ctx:
        context_lines.extend(proj_ctx)

    # Output context for AI
    result = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(context_lines)
        }
    }
    print(json.dumps(result))


if __name__ == '__main__':
    main()
