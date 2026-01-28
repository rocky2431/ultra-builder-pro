#!/usr/bin/env python3
"""
Pre-Stop Check Hook - Stop
Checks for unreviewed code changes before session ends

Reminds to:
- Run pr-review-toolkit:code-reviewer for uncommitted changes
- Run tests before completing

This is a reminder only, does not block.
"""

import sys
import json
import subprocess
import os


def get_git_status() -> dict:
    """Get current git status."""
    result = {
        'has_changes': False,
        'staged': [],
        'unstaged': [],
        'untracked': []
    }

    try:
        # Check if in a git repo
        proc = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if proc.returncode != 0:
            return result

        # Get status
        proc = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if proc.returncode != 0:
            return result

        for line in proc.stdout.strip().split('\n'):
            if not line:
                continue

            status = line[:2]
            filepath = line[3:]

            if status[0] in 'MADRC':  # Staged
                result['staged'].append(filepath)
            if status[1] in 'MD':  # Unstaged modifications
                result['unstaged'].append(filepath)
            if status == '??':  # Untracked
                result['untracked'].append(filepath)

        result['has_changes'] = bool(result['staged'] or result['unstaged'])

    except Exception:
        pass

    return result


def get_code_files(files: list) -> list:
    """Filter to code files only."""
    code_extensions = {'.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.sol', '.rb'}
    return [f for f in files if os.path.splitext(f)[1].lower() in code_extensions]


def main():
    # Read stdin for hook input
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except json.JSONDecodeError:
        print(input_data)
        return

    # Check git status
    git_status = get_git_status()

    reminders = []

    # Check for uncommitted changes
    if git_status['has_changes']:
        all_changed = git_status['staged'] + git_status['unstaged']
        code_files = get_code_files(all_changed)

        if code_files:
            reminders.append({
                'type': 'Code Review',
                'message': f'{len(code_files)} code file(s) changed but not reviewed',
                'action': 'Run pr-review-toolkit:code-reviewer agent before completing',
                'files': code_files[:5]  # Show max 5
            })

    # Check for security-sensitive files
    security_patterns = ['auth', 'login', 'password', 'payment', 'secret', 'token']
    if git_status['has_changes']:
        all_files = git_status['staged'] + git_status['unstaged']
        security_files = [f for f in all_files
                        if any(p in f.lower() for p in security_patterns)]

        if security_files:
            reminders.append({
                'type': 'Security Review',
                'message': 'Security-sensitive files changed',
                'action': 'Run pr-review-toolkit:code-reviewer (MANDATORY)',
                'files': security_files[:5]
            })

    # Output reminders
    if reminders:
        print("", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("[Pre-Stop Check] Recommendations before ending session:", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        for reminder in reminders:
            print("", file=sys.stderr)
            print(f"[{reminder['type']}] {reminder['message']}", file=sys.stderr)
            print(f"  Action: {reminder['action']}", file=sys.stderr)
            if reminder.get('files'):
                print("  Files:", file=sys.stderr)
                for f in reminder['files']:
                    print(f"    - {f}", file=sys.stderr)

        print("", file=sys.stderr)
        print("Use Task tool with appropriate subagent_type to invoke agents.", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("", file=sys.stderr)

    # Always pass through (reminder only)
    print(input_data)


if __name__ == '__main__':
    main()
