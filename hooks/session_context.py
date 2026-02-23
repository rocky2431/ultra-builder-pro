#!/usr/bin/env python3
"""
Session Context Hook - SessionStart
Loads development context at session start.

Provides:
- Current git branch and recent commits
- Modified files status
- Last session one-liner from memory DB (~50 tokens)
"""

import sys
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path


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


def get_last_session_oneliner() -> str:
    """Get a one-liner about the last session from memory DB.

    Returns empty string if DB doesn't exist or has no records.
    Adds ~50 tokens to context. Fails silently.
    """
    try:
        result = subprocess.run(
            ["python3", str(Path(__file__).parent / "memory_db.py"), "oneliner"],
            capture_output=True, text=True, timeout=3,
            cwd=os.getcwd()
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return ""


def get_branch_memory(branch: str) -> list:
    """Query memory DB directly for recent sessions with summaries on this branch.

    Returns up to 3 session summaries for context continuity.
    Adds ~150 tokens. Fails silently.
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
               ORDER BY last_active DESC LIMIT 3""",
            (branch,)
        ).fetchall()
        conn.close()

        lines = []
        for row in rows:
            date = row["last_active"][:10]
            summary = row["summary"]
            # Take first line/sentence, truncate to 120 chars
            short = summary.split("\n")[0].strip()
            if short.startswith("- "):
                short = short[2:]
            if short.startswith("## "):
                # Structured summary - grab first bullet instead
                for s_line in summary.split("\n"):
                    s_line = s_line.strip()
                    if s_line.startswith("- ") and len(s_line) > 5:
                        short = s_line[2:]
                        break
            if len(short) > 120:
                short = short[:117] + "..."
            lines.append(f"  - [{date}] {short}")

        return lines
    except Exception:
        pass
    return []


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

    # Add last session one-liner from memory DB
    last_session = get_last_session_oneliner()
    if last_session:
        context_lines.append("")
        context_lines.append(last_session)

    # Add branch-relevant memory (recent sessions on same branch)
    branch = ''
    for line in git_ctx:
        if line.startswith("Branch:"):
            branch = line.replace("Branch:", "").strip()
            break

    branch_mem = get_branch_memory(branch)
    if branch_mem:
        context_lines.append("")
        context_lines.append("Related sessions on this branch:")
        context_lines.extend(branch_mem)

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
