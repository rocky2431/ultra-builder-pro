#!/usr/bin/env python3
"""
Security Scan Hook - PostToolUse
Enforces CLAUDE.md security rules (lines 180-186)

CRITICAL (BLOCK):
- Hardcoded secrets: sk-xxx, ghp_xxx, api_key=xxx
- SQL string concatenation
- Dangerous functions: eval(), exec()
- Empty catch blocks

HIGH (WARN + suggest security-reviewer):
- innerHTML with dynamic values
- SSL verification disabled
- Security rule disable comments
"""

import sys
import json
import re
import os

# CRITICAL patterns - BLOCK
CRITICAL_PATTERNS = [
    # API Keys and Secrets
    (r'["\']sk-[a-zA-Z0-9]{20,}["\']', 'Hardcoded OpenAI API key'),
    (r'["\']ghp_[a-zA-Z0-9]{36,}["\']', 'Hardcoded GitHub token'),
    (r'["\']gho_[a-zA-Z0-9]{36,}["\']', 'Hardcoded GitHub OAuth token'),
    (r'["\']ghu_[a-zA-Z0-9]{36,}["\']', 'Hardcoded GitHub user-to-server token'),
    (r'["\']ghs_[a-zA-Z0-9]{36,}["\']', 'Hardcoded GitHub server-to-server token'),
    (r'["\']ghr_[a-zA-Z0-9]{36,}["\']', 'Hardcoded GitHub refresh token'),
    (r'["\']xox[baprs]-[a-zA-Z0-9-]{10,}["\']', 'Hardcoded Slack token'),
    (r'["\']AKIA[A-Z0-9]{16}["\']', 'Hardcoded AWS Access Key ID'),
    (r'api[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'Hardcoded API key'),
    (r'secret[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'Hardcoded secret key'),
    (r'password\s*[=:]\s*["\'][^"\']{8,}["\'](?!\s*(?://|#)\s*(?:example|demo|test|placeholder))', 'Hardcoded password'),

    # SQL Injection
    (r'["\']SELECT\s+.+FROM\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'["\']INSERT\s+INTO\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'["\']UPDATE\s+.+SET\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'["\']DELETE\s+FROM\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'`SELECT\s+.+\$\{', 'SQL template literal with interpolation - Use parameterized queries'),
    (r'f["\']SELECT\s+.+\{', 'SQL f-string with interpolation - Use parameterized queries'),

    # Dangerous functions
    (r'\beval\s*\([^)]*\buser', 'eval() with user input - Code injection risk'),
    (r'\bexec\s*\([^)]*\buser', 'exec() with user input - Code injection risk'),
    (r'Function\s*\([^)]*\buser', 'Function() constructor with user input'),

    # Empty catch blocks (silent error swallowing)
    (r'catch\s*\([^)]*\)\s*\{\s*\}', 'Empty catch block - Never silently swallow errors'),
    (r'except\s*:\s*pass\s*$', 'Bare except with pass - Never silently swallow errors'),
    (r'except\s+\w+\s*:\s*pass\s*$', 'Exception swallowed with pass - Log or re-raise'),
]

# HIGH patterns - WARN and suggest security-reviewer
HIGH_PATTERNS = [
    (r'\.innerHTML\s*=\s*(?![\'"<])', 'Dynamic innerHTML assignment - XSS risk'),
    (r'dangerouslySetInnerHTML\s*=\s*\{', 'dangerouslySetInnerHTML - XSS risk, ensure sanitization'),
    (r'verify\s*[=:]\s*False', 'SSL verification disabled'),
    (r'rejectUnauthorized\s*:\s*false', 'SSL verification disabled'),
    (r'NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*["\']?0', 'TLS verification disabled'),
    (r'#\s*nosec', 'Security rule disabled'),
    (r'//\s*eslint-disable.*security', 'Security ESLint rule disabled'),
    (r'@SuppressWarnings.*security', 'Security warning suppressed'),
    (r'subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True', 'Shell injection risk - use shell=False'),
]

# File extensions to check
CODE_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.py', '.go', '.rs', '.java', '.rb', '.php'}


def get_line_number(content: str, match_pos: int) -> int:
    """Get line number from character position."""
    return content[:match_pos].count('\n') + 1


def is_test_file(file_path: str) -> bool:
    """Check if file is a test file (more lenient security checks)."""
    path_lower = file_path.lower()
    return any(indicator in path_lower for indicator in [
        '/test/', '/tests/', '/__tests__/',
        '/spec/', '/specs/',
        '.test.', '.spec.',
        '_test.', '_spec.',
        '/fixtures/', '/mocks/'
    ])


def is_example_or_docs(file_path: str) -> bool:
    """Check if file is example/documentation."""
    path_lower = file_path.lower()
    return any(indicator in path_lower for indicator in [
        '/examples/', '/example/',
        '/docs/', '/documentation/',
        'readme', '.md'
    ])


def check_file(file_path: str, content: str) -> tuple:
    """Check file content for security issues. Returns (critical, high)."""
    critical = []
    high = []

    is_test = is_test_file(file_path)
    is_example = is_example_or_docs(file_path)

    # Check critical patterns (always block, except in tests/examples for some)
    for pattern, message in CRITICAL_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            line_num = get_line_number(content, match.start())
            lines = content.split('\n')
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            # Skip test files for empty catch blocks (may be intentional)
            if is_test and 'catch' in message.lower():
                continue

            # Skip example files for hardcoded secrets (may be placeholders)
            if is_example and 'Hardcoded' in message:
                continue

            critical.append({
                'line': line_num,
                'message': message,
                'code': line_content[:80]
            })

    # Check high patterns (warn, don't block in tests)
    for pattern, message in HIGH_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            if is_test:
                continue  # Skip warnings in test files

            line_num = get_line_number(content, match.start())
            lines = content.split('\n')
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            high.append({
                'line': line_num,
                'message': message,
                'code': line_content[:80]
            })

    return critical, high


def main():
    # Read stdin for hook input
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except json.JSONDecodeError:
        print(input_data)
        return

    tool_name = hook_input.get('tool')
    tool_input = hook_input.get('tool_input', {})

    # Only check Edit and Write tools
    if tool_name not in ('Edit', 'Write'):
        print(input_data)
        return

    file_path = tool_input.get('file_path', '')

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

    # Check for security issues
    critical, high = check_file(file_path, content)

    # Output high-severity warnings
    if high:
        print(f"[SECURITY WARNING] Potential issues in {file_path}", file=sys.stderr)
        for h in high[:5]:
            print(f"  Line {h['line']}: {h['message']}", file=sys.stderr)
            print(f"    > {h['code']}", file=sys.stderr)
        if len(high) > 5:
            print(f"  ... and {len(high) - 5} more warnings", file=sys.stderr)
        print("", file=sys.stderr)
        print("[Agent Reminder] Consider running security-reviewer agent", file=sys.stderr)
        print("", file=sys.stderr)

    # Block on critical issues
    if critical:
        print(f"[BLOCKED] Security vulnerabilities in {file_path}", file=sys.stderr)
        print("", file=sys.stderr)
        print("CLAUDE.md security rules (security:180-186) violated", file=sys.stderr)
        print("", file=sys.stderr)

        for c in critical[:5]:
            print(f"  Line {c['line']}: {c['message']}", file=sys.stderr)
            print(f"    > {c['code']}", file=sys.stderr)

        if len(critical) > 5:
            print(f"  ... and {len(critical) - 5} more vulnerabilities", file=sys.stderr)

        print("", file=sys.stderr)
        print("Solutions:", file=sys.stderr)
        print("  - Secrets: Use environment variables or secret manager", file=sys.stderr)
        print("  - SQL: Use parameterized queries ($1, ?, :param)", file=sys.stderr)
        print("  - Errors: Log with context, then re-throw or handle", file=sys.stderr)
        print("", file=sys.stderr)

        result = {
            "blocked": True,
            "reason": f"Security vulnerabilities: {len(critical)} critical issues found"
        }
        print(json.dumps(result))
    else:
        # Pass through
        print(input_data)


if __name__ == '__main__':
    main()
