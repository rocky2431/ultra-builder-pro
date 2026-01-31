#!/usr/bin/env python3
"""
Pre-Stop Check Hook - Stop
Checks for unreviewed code changes before session ends

Reminds to:
- Run pr-review-toolkit:code-reviewer for uncommitted changes
- Run tests before completing

Uses a marker file to track review completion, preventing infinite loops.
First trigger: blocks and reminds. After review completes, marker file is
created, and subsequent triggers allow stop.

Marker file: /tmp/.claude_review_done_<git_hash>
The hash is based on the set of changed files, so new changes invalidate it.
"""

import sys
import json
import subprocess
import os
import hashlib
import tempfile


MARKER_PREFIX = ".claude_review_done_"


def get_git_status() -> dict:
    """Get current git status."""
    result = {
        'has_changes': False,
        'staged': [],
        'unstaged': [],
        'untracked': []
    }

    try:
        proc = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if proc.returncode != 0:
            return result

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

            if status[0] in 'MADRC':
                result['staged'].append(filepath)
            if status[1] in 'MD':
                result['unstaged'].append(filepath)
            if status == '??':
                result['untracked'].append(filepath)

        result['has_changes'] = bool(result['staged'] or result['unstaged'])

    except Exception:
        pass

    return result


def get_code_files(files: list) -> list:
    """Filter to code files only."""
    code_extensions = {'.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.sol', '.rb'}
    return [f for f in files if os.path.splitext(f)[1].lower() in code_extensions]


def get_changes_hash(files: list) -> str:
    """Generate a hash based on the set of changed files."""
    content = "\n".join(sorted(files))
    return hashlib.md5(content.encode()).hexdigest()[:12]


def get_marker_path(changes_hash: str) -> str:
    """Get the marker file path for a given changes hash."""
    return os.path.join(tempfile.gettempdir(), f"{MARKER_PREFIX}{changes_hash}")


def is_review_done(changes_hash: str) -> bool:
    """Check if review has been completed for this set of changes."""
    return os.path.exists(get_marker_path(changes_hash))


def mark_review_blocked(changes_hash: str) -> None:
    """Mark that we've blocked once for this set of changes.

    On the first block, create a marker file. On the next stop attempt,
    the hook will see the marker and allow stop (review was presumably done).
    """
    marker_path = get_marker_path(changes_hash)
    with open(marker_path, 'w') as f:
        f.write("blocked_once")


def main():
    input_data = ""
    try:
        input_data = sys.stdin.read()
        json.loads(input_data)
    except json.JSONDecodeError:
        print(input_data)
        return

    git_status = get_git_status()

    reminders = []

    if git_status['has_changes']:
        all_changed = git_status['staged'] + git_status['unstaged']
        code_files = get_code_files(all_changed)

        if code_files:
            reminders.append({
                'type': 'Code Review',
                'message': f'{len(code_files)} code file(s) changed but not reviewed',
                'action': 'Run pr-review-toolkit:code-reviewer agent before completing',
                'files': code_files[:5]
            })

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

    has_security_files = any(r['type'] == 'Security Review' for r in reminders)

    if reminders:
        all_changed = git_status['staged'] + git_status['unstaged']
        changes_hash = get_changes_hash(all_changed)

        lines = ["[Pre-Stop Check] Before ending session:"]

        for reminder in reminders:
            lines.append(f"  [{reminder['type']}] {reminder['message']}")
            lines.append(f"    Action: {reminder['action']}")
            if reminder.get('files'):
                for f in reminder['files'][:3]:
                    lines.append(f"      - {f}")

        lines.append("")
        lines.append("Use Task tool with subagent_type to invoke agents.")

        message = "\n".join(lines)

        if has_security_files and not is_review_done(changes_hash):
            # First time: block and create marker
            mark_review_blocked(changes_hash)
            result = {
                "decision": "block",
                "reason": message
            }
            print(json.dumps(result))
        else:
            # Either: no security files, or review marker exists (already blocked once)
            print(message, file=sys.stderr)
            print(json.dumps({}))
    else:
        print(json.dumps({}))


if __name__ == '__main__':
    main()
