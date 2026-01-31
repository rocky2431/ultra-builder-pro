#!/usr/bin/env python3
"""
Block Dangerous Commands Hook - PreToolUse
Prevents destructive shell operations before execution.

BLOCK patterns:
- rm -rf ~ / rm -rf /
- Fork bombs
- chmod 777
- Force push to main/master
- git reset --hard on main
- Direct writes to system directories
"""

import sys
import json
import re

# Dangerous command patterns with explanations
DANGEROUS_PATTERNS = [
    # Destructive file operations - only block truly dangerous patterns
    (r'\brm\s+-[rf]*\s*-[rf]*\s+~\s*$', 'Recursive delete on home directory'),
    (r'\brm\s+-[rf]*\s*-[rf]*\s+/\s*$', 'Recursive delete on root directory'),
    (r'\brm\s+-[rf]*\s+--no-preserve-root', 'Dangerous rm with --no-preserve-root'),
    (r'\brm\s+-[rf]+\s+/(?!Users|home)', 'Recursive delete on system directory'),

    # Fork bombs
    (r':\(\)\s*\{\s*:\|:\s*&\s*\}\s*;?\s*:', 'Fork bomb detected'),
    (r'\.\s*/dev/null\s*\|', 'Potential fork bomb pattern'),

    # Dangerous permissions
    (r'\bchmod\s+777\b', 'chmod 777 is insecure - use specific permissions'),
    (r'\bchmod\s+-R\s+777\b', 'Recursive chmod 777 is dangerous'),

    # Dangerous git operations on main
    (r'\bgit\s+push\s+.*--force.*\b(main|master)\b', 'Force push to main/master blocked'),
    (r'\bgit\s+push\s+-f\s+.*\b(main|master)\b', 'Force push to main/master blocked'),
    (r'\bgit\s+reset\s+--hard\b', 'git reset --hard can lose work'),
    (r'\bgit\s+clean\s+-fd', 'git clean -fd removes untracked files'),

    # System directory writes
    (r'\b(cat|echo|tee)\s+.*>\s*/etc/', 'Direct write to /etc blocked'),
    (r'\b(cat|echo|tee)\s+.*>\s*/usr/', 'Direct write to /usr blocked'),
    (r'\b(cat|echo|tee)\s+.*>\s*/bin/', 'Direct write to /bin blocked'),

    # Dangerous curl/wget pipes
    (r'\bcurl\s+.*\|\s*(sudo\s+)?(ba)?sh\b', 'Piping curl to shell is dangerous'),
    (r'\bwget\s+.*\|\s*(sudo\s+)?(ba)?sh\b', 'Piping wget to shell is dangerous'),

    # Database drops
    (r'\bDROP\s+DATABASE\b', 'DROP DATABASE blocked'),
    (r'\bDROP\s+TABLE\b.*\*', 'DROP TABLE with wildcard blocked'),
]

# Warning patterns (allow but warn)
WARNING_PATTERNS = [
    (r'\bsudo\s+', 'Command uses sudo - ensure this is intentional'),
    (r'\bgit\s+checkout\s+\.', 'git checkout . discards changes'),
    (r'\bgit\s+stash\s+drop', 'git stash drop removes stashed changes'),
]


def check_command(command: str) -> tuple:
    """Check command for dangerous patterns. Returns (should_block, message)."""
    for pattern, message in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, message

    warnings = []
    for pattern, message in WARNING_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            warnings.append(message)

    if warnings:
        return False, '; '.join(warnings)

    return False, None


def main():
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[block_dangerous_commands] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    tool_name = hook_input.get('tool_name')
    tool_input = hook_input.get('tool_input', {})

    # Only check Bash tool
    if tool_name != 'Bash':
        print(json.dumps({}))
        return

    command = tool_input.get('command', '')
    if not command:
        print(json.dumps({}))
        return

    should_block, message = check_command(command)

    if should_block:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"[BLOCKED] {message}\nCommand: {command[:100]}"
            }
        }
        print(json.dumps(result))
    elif message:
        # Warning only
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"[WARNING] {message}"
            }
        }
        print(json.dumps(result))
    else:
        print(json.dumps({}))


if __name__ == '__main__':
    main()
