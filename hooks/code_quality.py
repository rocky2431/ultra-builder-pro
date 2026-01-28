#!/usr/bin/env python3
"""
Code Quality Hook - PostToolUse
Enforces CLAUDE.md forbidden_patterns (lines 89-92)

BLOCK patterns:
- // TODO: / // FIXME: / // XXX: / // HACK:
- throw NotImplementedError / raise NotImplementedError

WARN patterns (stderr, don't block):
- console.log/warn/error/debug()
- Hardcoded localhost URLs
- Hardcoded port numbers
"""

import sys
import json
import re
import os

# BLOCKING patterns - code cannot proceed
BLOCK_PATTERNS = [
    (r'//\s*TODO\s*:', 'TODO comment - Complete or remove before commit'),
    (r'//\s*FIXME\s*:', 'FIXME comment - Fix the issue before commit'),
    (r'//\s*XXX\s*:', 'XXX comment - Address before commit'),
    (r'//\s*HACK\s*:', 'HACK comment - Implement properly before commit'),
    (r'#\s*TODO\s*:', 'TODO comment - Complete or remove before commit'),
    (r'#\s*FIXME\s*:', 'FIXME comment - Fix the issue before commit'),
    (r'throw\s+(?:new\s+)?NotImplementedError', 'NotImplementedError - Complete implementation'),
    (r'raise\s+NotImplementedError', 'NotImplementedError - Complete implementation'),
    (r'throw\s+(?:new\s+)?Error\s*\(\s*[\'"]Not\s+implemented', 'Not implemented error - Complete implementation'),
]

# WARNING patterns - alert but don't block
WARN_PATTERNS = [
    (r'\bconsole\.(log|warn|error|debug|info)\s*\(', 'console.{} - Use structured logger in production'),
    (r'localhost:\d+', 'Hardcoded localhost URL - Use environment variable'),
    (r'127\.0\.0\.1:\d+', 'Hardcoded localhost URL - Use environment variable'),
    (r'["\']http://localhost', 'Hardcoded localhost URL - Use environment variable'),
]

# File extensions to check
CODE_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.py', '.go', '.rs', '.java'}


def get_line_number(content: str, match_pos: int) -> int:
    """Get line number from character position."""
    return content[:match_pos].count('\n') + 1


def check_file(file_path: str, content: str) -> tuple:
    """Check file content for quality issues. Returns (blocks, warnings)."""
    blocks = []
    warnings = []

    # Check blocking patterns
    for pattern, message in BLOCK_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = get_line_number(content, match.start())
            lines = content.split('\n')
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            blocks.append({
                'line': line_num,
                'message': message,
                'code': line_content[:80]
            })

    # Check warning patterns
    for pattern, message in WARN_PATTERNS:
        for match in re.finditer(pattern, content):
            line_num = get_line_number(content, match.start())
            lines = content.split('\n')
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            warnings.append({
                'line': line_num,
                'message': message.format(match.group(1) if match.lastindex else ''),
                'code': line_content[:80]
            })

    return blocks, warnings


def is_generated_file(file_path: str) -> bool:
    """Check if file is auto-generated or should be skipped."""
    indicators = [
        '/node_modules/',
        '/dist/',
        '/build/',
        '/.next/',
        '/coverage/',
        '.min.js',
        '.bundle.js',
        '.generated.',
        '/.claude/hooks/',  # Skip hook files themselves (contain pattern descriptions)
    ]
    return any(ind in file_path for ind in indicators)


def main():
    # Read stdin for hook input
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except json.JSONDecodeError:
        print(input_data)
        return

    tool_name = hook_input.get('tool_name')  # 官方文档：字段名是 tool_name
    tool_input = hook_input.get('tool_input', {})

    # Only check Edit and Write tools
    if tool_name not in ('Edit', 'Write'):
        print(input_data)
        return

    file_path = tool_input.get('file_path', '')

    # Skip generated files
    if is_generated_file(file_path):
        print(input_data)
        return

    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in CODE_EXTENSIONS:
        print(input_data)
        return

    # Read file content
    if not os.path.exists(file_path):
        print(input_data)
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        print(input_data)
        return

    # Check for issues
    blocks, warnings = check_file(file_path, content)

    # Build warning message for AI
    all_issues = []

    if blocks:
        all_issues.append(f"[CODE QUALITY CRITICAL] {file_path}")
        all_issues.append("CLAUDE.md forbidden_patterns (lines 63-65) violated:")
        for b in blocks[:5]:
            all_issues.append(f"  Line {b['line']}: {b['message']}")
            all_issues.append(f"    > {b['code']}")
        if len(blocks) > 5:
            all_issues.append(f"  ... and {len(blocks) - 5} more")
        all_issues.append("")
        all_issues.append("Red flags (CLAUDE.md lines 72-88):")
        all_issues.append("  - 'Write TODO, improve later' -> Later = never")
        all_issues.append("  - 'Just MVP/prototype' -> MVP is production code")
        all_issues.append("Complete the implementation NOW or don't commit.")

    if warnings:
        if all_issues:
            all_issues.append("")
        all_issues.append(f"[CODE QUALITY WARNING] {file_path}")
        for w in warnings[:5]:
            all_issues.append(f"  Line {w['line']}: {w['message']}")
            all_issues.append(f"    > {w['code']}")
        if len(warnings) > 5:
            all_issues.append(f"  ... and {len(warnings) - 5} more")
        all_issues.append("")
        all_issues.append("Use structured logger (CLAUDE.md logging lines 111-127):")
        all_issues.append("  logger.info('message', { context, traceId })")

    if all_issues:
        all_issues.append("")
        all_issues.append("ACTION: Complete implementations before continuing.")
        warning_message = "\n".join(all_issues)

        # BLOCK patterns (TODO/FIXME) block execution, WARN patterns only warn
        if blocks:
            result = {
                "decision": "block",
                "reason": warning_message,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": warning_message
                }
            }
        else:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": warning_message
                }
            }
        print(json.dumps(result))
    else:
        # Pass through
        print(json.dumps({}))


if __name__ == '__main__':
    main()
