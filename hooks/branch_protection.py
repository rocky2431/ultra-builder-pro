#!/usr/bin/env python3
"""
Branch Protection Hook - PreToolUse
Asks for confirmation when editing on protected branches (main/master).

Prompts user to approve or reject the edit.
Excludes config directories like ~/.claude/
"""

import sys
import json
import subprocess
import os

PROTECTED_BRANCHES = {'main', 'master', 'production', 'prod'}


def is_config_path(file_path: str) -> bool:
    """Check if path is a config directory (excluded from branch protection)."""
    excluded = [
        '/.claude/',
        '/.git/',
        '/.vscode/',
        '/.idea/',
    ]
    return any(ex in file_path for ex in excluded)


def get_current_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ''


def main():
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    tool_name = hook_input.get('tool_name')
    tool_input = hook_input.get('tool_input', {})

    # Only check Edit and Write tools
    if tool_name not in ('Edit', 'Write'):
        print(json.dumps({}))
        return

    # Skip config directories
    file_path = tool_input.get('file_path', '')
    if is_config_path(file_path):
        print(json.dumps({}))
        return

    current_branch = get_current_branch()

    if current_branch in PROTECTED_BRANCHES:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"Editing on protected branch '{current_branch}'. Allow this edit or create a feature branch first?"
            }
        }
        print(json.dumps(result))
    else:
        print(json.dumps({}))


if __name__ == '__main__':
    main()
