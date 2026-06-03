#!/usr/bin/env python3
"""
Session Context Hook - SessionStart (v7.0 — Goal-Always-Present substrate)

Loads development context at session start.

Provides:
- Current git branch and recent commits
- Modified files status
- v7: tools status (.ultra availability) — quick situational awareness
- v7: north-star (project goal + active task acceptance criteria) — Goal-Always-Present

Memory归位 (2026-06-02): cross-session recall (last session, related/semantic
sessions, learnings) is no longer read from the self-built memory.db (removed).
L3 raw observations are owned by the claude-mem plugin; L3 refined knowledge by
the file-based memory under projects/.../memory/. This hook intentionally injects
ONLY live state (git + .ultra goal), never historical summaries — so no
stale-replay guard is needed here (historical injection now lives in claude-mem).
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
            timeout=3
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


def _extract_md_section(content: str, header: str, max_chars: int = 300) -> str:
    """Extract first non-placeholder content from a markdown section header to next `---`.

    Properly handles multi-line HTML comments, blockquotes, and placeholder markers.
    """
    if header not in content:
        return ""
    section = content.split(header, 1)[1].split('\n---\n', 1)[0]
    out = []
    in_comment = False
    for line in section.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        # Track multi-line HTML comments (line may contain both open and close)
        if '<!--' in stripped and '-->' not in stripped:
            in_comment = True
            continue
        if in_comment:
            if '-->' in stripped:
                in_comment = False
            continue
        # Single-line comment
        if stripped.startswith('<!--') and stripped.endswith('-->'):
            continue
        if stripped.startswith('>'):
            stripped = stripped[1:].strip()
        if not stripped:
            continue
        # Skip placeholder markers like _(not yet defined)_ or _(criterion 1)_
        if stripped.startswith('_(') and stripped.endswith(')_'):
            continue
        # Skip checklist markers without content
        if stripped in ('- [ ]', '- [x]'):
            continue
        out.append(stripped)
        if sum(len(s) for s in out) > max_chars:
            break
    result = ' '.join(out)
    return result[:max_chars].strip()


def get_tools_status() -> list:
    """v7: report harness tool availability. Minimal — keep token cost low."""
    lines = []
    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=1
        )
        if proc.returncode == 0 and proc.stdout.strip():
            ultra = Path(proc.stdout.strip()) / '.ultra'
            if ultra.exists():
                phil = ultra / 'PHILOSOPHY.md'
                ns = ultra / 'north-star.md'
                lines.append(
                    f"  .ultra: ✓ {'philosophy' if phil.exists() else 'no-philosophy'} | "
                    f"{'north-star' if ns.exists() else 'no-north-star'}"
                )
    except Exception:
        pass

    return ["[Tools]"] + lines if lines else []


def get_north_star_context() -> list:
    """v7 Goal-Always-Present: inject project + active task north-star at SessionStart."""
    lines = []
    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=1
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return []
        root = Path(proc.stdout.strip())
        ns_path = root / '.ultra' / 'north-star.md'
        if not ns_path.exists():
            return []

        content = ns_path.read_text(encoding='utf-8')
        one_line = _extract_md_section(content, '## One-line', max_chars=250)
        hard = _extract_md_section(content, '## Hard Constraints', max_chars=400)

        if one_line:
            lines.append(f"  Goal: {one_line}")
        if hard:
            lines.append(f"  Hard constraints: {hard}")

        # Active task acceptance criteria
        tasks_path = root / '.ultra' / 'tasks' / 'tasks.json'
        if tasks_path.exists():
            try:
                tasks_data = json.loads(tasks_path.read_text(encoding='utf-8'))
                in_progress = [
                    t for t in tasks_data.get('tasks', [])
                    if t.get('status') == 'in_progress'
                ]
                if in_progress:
                    t = in_progress[0]
                    tid = t.get('id', '?')
                    title = t.get('title', '?')
                    lines.append(f"  Active task {tid}: {title}")
                    ctx_file = root / '.ultra' / 'tasks' / 'contexts' / f"task-{tid}.md"
                    if ctx_file.exists():
                        ctx_md = ctx_file.read_text(encoding='utf-8')
                        ac = _extract_md_section(ctx_md, '## Acceptance Criteria', max_chars=300)
                        if ac:
                            lines.append(f"  Acceptance: {ac}")
            except Exception:
                pass
    except Exception:
        pass

    return ["[North Star]"] + lines if lines else []


def main():
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[session_context] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    if not isinstance(hook_input, dict):
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

    # v7: tools status (.ultra availability)
    tools_lines = get_tools_status()
    if tools_lines:
        context_lines.append("")
        context_lines.extend(tools_lines)

    # v7: north-star (Goal-Always-Present substrate — every session sees the goal)
    ns_lines = get_north_star_context()
    if ns_lines:
        context_lines.append("")
        context_lines.extend(ns_lines)

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
