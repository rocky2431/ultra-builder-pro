#!/usr/bin/env python3
"""
Mock Detector Hook - PostToolUse
Enforces CLAUDE.md testing rules (lines 60-68) and forbidden_patterns (lines 84-88)

BLOCK patterns:
- jest.fn() / vi.fn()
- jest.mock() / vi.mock()
- .mockResolvedValue() / .mockReturnValue()
- class InMemoryXxxRepository
- class MockXxx / class FakeXxx
- sinon.stub/spy/mock

ALLOW exceptions:
- Files with '// Test Double rationale:' comment (external API mocks)
"""

import sys
import json
import re
import os

# Forbidden mock patterns
FORBIDDEN_PATTERNS = [
    (r'\bjest\.fn\s*\(', 'jest.fn() - Use real implementation or Testcontainers'),
    (r'\bvi\.fn\s*\(', 'vi.fn() - Use real implementation or Testcontainers'),
    (r'\bjest\.mock\s*\(', 'jest.mock() - Test real modules'),
    (r'\bvi\.mock\s*\(', 'vi.mock() - Test real modules'),
    (r'\.mockResolvedValue\s*\(', '.mockResolvedValue() - Use real async behavior'),
    (r'\.mockReturnValue\s*\(', '.mockReturnValue() - Use real return values'),
    (r'\.mockImplementation\s*\(', '.mockImplementation() - Use real implementation'),
    (r'\bclass\s+InMemory\w*Repository', 'InMemoryRepository - Use Testcontainers with real DB'),
    (r'\bclass\s+Mock\w+', 'Mock class - Use real implementation'),
    (r'\bclass\s+Fake\w+', 'Fake class - Use real implementation'),
    (r'\bsinon\.stub\s*\(', 'sinon.stub() - Use real implementation'),
    (r'\bsinon\.spy\s*\(', 'sinon.spy() - Use real implementation'),
    (r'\bsinon\.mock\s*\(', 'sinon.mock() - Use real implementation'),
    (r'\bspyOn\s*\([^)]+\)\.and\.returnValue', 'spyOn().and.returnValue - Use real implementation'),
]

# Exception: Test Double rationale comment
RATIONALE_PATTERN = r'//\s*Test\s+Double\s+rationale:'

# File extensions to check
TEST_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}


def is_test_file(file_path: str) -> bool:
    """Check if file is a test file."""
    path_lower = file_path.lower()
    return any(indicator in path_lower for indicator in [
        '/test/', '/tests/', '/__tests__/',
        '/spec/', '/specs/',
        '.test.', '.spec.',
        '_test.', '_spec.'
    ])


def has_rationale_comment(content: str, pattern_match_line: int) -> bool:
    """Check if there's a Test Double rationale comment near the violation."""
    lines = content.split('\n')
    # Check 5 lines before and 2 lines after the match
    start = max(0, pattern_match_line - 5)
    end = min(len(lines), pattern_match_line + 3)

    for i in range(start, end):
        if re.search(RATIONALE_PATTERN, lines[i], re.IGNORECASE):
            return True
    return False


def get_line_number(content: str, match_pos: int) -> int:
    """Get line number from character position."""
    return content[:match_pos].count('\n') + 1


def check_file(file_path: str, content: str) -> list:
    """Check file content for forbidden mock patterns."""
    violations = []

    # Skip if file has global rationale at top (first 20 lines)
    first_lines = '\n'.join(content.split('\n')[:20])
    if re.search(RATIONALE_PATTERN, first_lines, re.IGNORECASE):
        return violations

    for pattern, message in FORBIDDEN_PATTERNS:
        for match in re.finditer(pattern, content):
            line_num = get_line_number(content, match.start())

            # Check for nearby rationale comment
            if has_rationale_comment(content, line_num - 1):
                continue

            # Get the offending line
            lines = content.split('\n')
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            violations.append({
                'line': line_num,
                'pattern': message,
                'code': line_content[:80]
            })

    return violations


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

    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in TEST_EXTENSIONS:
        print(input_data)
        return

    # Only check test files (mocks should only appear in tests)
    if not is_test_file(file_path):
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

    # Check for violations
    violations = check_file(file_path, content)

    if violations:
        # Build warning message
        warning_lines = [
            f"[MOCK WARNING] Forbidden mock patterns detected in {file_path}",
            "",
            "CLAUDE.md forbids mocking internal code. You MUST fix these violations:",
            ""
        ]

        for v in violations[:5]:
            warning_lines.append(f"  Line {v['line']}: {v['pattern']}")
            warning_lines.append(f"    > {v['code']}")

        if len(violations) > 5:
            warning_lines.append(f"  ... and {len(violations) - 5} more violations")

        warning_lines.extend([
            "",
            "Solutions: Use Testcontainers, or add '// Test Double rationale: [reason]' for external APIs.",
            "ACTION REQUIRED: Fix the mock patterns above before continuing."
        ])

        warning_message = "\n".join(warning_lines)

        # Output JSON with decision: block to ensure Claude sees the warning
        result = {
            "decision": "block",
            "reason": warning_message,
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": warning_message
            }
        }
        print(json.dumps(result))
    else:
        # Pass through original input
        print(input_data)


if __name__ == '__main__':
    main()
