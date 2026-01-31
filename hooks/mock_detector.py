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

# Forbidden mock patterns for Repository/Service/Domain (CLAUDE.md lines 48-52)
# UI component mocks (onClick, onChange, etc.) are allowed
FORBIDDEN_PATTERNS = [
    # Mock functions - forbidden for internal code
    (r'\bjest\.fn\s*\(', 'jest.fn() for internal code'),
    (r'\bvi\.fn\s*\(', 'vi.fn() for internal code'),
    (r'\bjest\.mock\s*\(', 'jest.mock() - Test real module collaboration'),
    (r'\bvi\.mock\s*\(', 'vi.mock() - Test real module collaboration'),
    (r'\.mockResolvedValue\s*\(', '.mockResolvedValue() - Use real async behavior'),
    (r'\.mockReturnValue\s*\(', '.mockReturnValue() - Use real return values'),
    (r'\.mockImplementation\s*\(', '.mockImplementation() - Use real implementation'),
    # Mock classes - always forbidden
    (r'\bclass\s+InMemory\w*Repository', 'InMemoryRepository class - Use Testcontainers'),
    (r'\bclass\s+Mock\w+', 'Mock class - Use real implementation'),
    (r'\bclass\s+Fake\w+', 'Fake class - Use real implementation'),
    # Other mock libraries
    (r'\bsinon\.stub\s*\(', 'sinon.stub() - Use real implementation'),
    (r'\bsinon\.spy\s*\(', 'sinon.spy() - Use real implementation'),
    (r'\bsinon\.mock\s*\(', 'sinon.mock() - Use real implementation'),
    (r'\bspyOn\s*\([^)]+\)\.and\.returnValue', 'spyOn().and.returnValue - Use real implementation'),
    # Skipped tests - "too slow" is not valid (CLAUDE.md line 52)
    (r'\bit\.skip\s*\(\s*[\'"][^\'"]*(?:database|db|slow|integration)[^\'"]*[\'"]', 'it.skip for DB/slow tests - "too slow" is not valid excuse'),
    (r'\btest\.skip\s*\(\s*[\'"][^\'"]*(?:database|db|slow|integration)[^\'"]*[\'"]', 'test.skip for DB/slow tests - "too slow" is not valid excuse'),
    (r'\bdescribe\.skip\s*\(\s*[\'"][^\'"]*(?:database|db|integration)[^\'"]*[\'"]', 'describe.skip for DB tests - Use Testcontainers'),
]

# Allowed mock patterns (UI event handlers, external callbacks)
ALLOWED_MOCK_CONTEXTS = [
    r'on[A-Z]\w*\s*[:=]\s*(?:jest|vi)\.fn',  # onClick, onChange, etc.
    r'handler\s*[:=]\s*(?:jest|vi)\.fn',      # event handlers
    r'callback\s*[:=]\s*(?:jest|vi)\.fn',     # callbacks
    r'mock(?:Fn|Handler|Callback)\s*=',       # explicitly named UI mocks
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


def is_allowed_mock_context(line_content: str) -> bool:
    """Check if the mock is in an allowed context (UI handlers, callbacks)."""
    for allowed_pattern in ALLOWED_MOCK_CONTEXTS:
        if re.search(allowed_pattern, line_content):
            return True
    return False


def check_file(file_path: str, content: str) -> list:
    """Check file content for forbidden mock patterns."""
    violations = []
    lines = content.split('\n')

    # Skip if file has global rationale at top (first 20 lines)
    first_lines = '\n'.join(lines[:20])
    if re.search(RATIONALE_PATTERN, first_lines, re.IGNORECASE):
        return violations

    for pattern, message in FORBIDDEN_PATTERNS:
        for match in re.finditer(pattern, content):
            line_num = get_line_number(content, match.start())
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            # Check for nearby rationale comment
            if has_rationale_comment(content, line_num - 1):
                continue

            # Check if it's an allowed mock context (UI handlers)
            if is_allowed_mock_context(line_content):
                continue

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
    except (json.JSONDecodeError, Exception) as e:
        print(f"[mock_detector] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    tool_name = hook_input.get('tool_name')
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
        # Build warning message with specific guidance
        warning_lines = [
            f"[MOCK VIOLATION] {file_path}",
            "",
            "CLAUDE.md (lines 48-52) forbids mocking Repository/Service/Domain.",
            ""
        ]

        for v in violations[:5]:
            warning_lines.append(f"  Line {v['line']}: {v['pattern']}")
            warning_lines.append(f"    > {v['code']}")

        if len(violations) > 5:
            warning_lines.append(f"  ... and {len(violations) - 5} more violations")

        warning_lines.extend([
            "",
            "SOLUTIONS by layer:",
            "  1. Functional Core (Domain): Test pure functions directly (input->output), no mocks needed",
            "  2. Imperative Shell (Repository/Service): Use Testcontainers with real DB",
            "  3. External APIs ONLY: Add '// Test Double rationale: [specific reason]'",
            "",
            "Allowed: UI event handlers (onClick, onChange) can use mocks.",
            "Forbidden: 'it.skip' for slow/database tests - use Testcontainers instead.",
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
