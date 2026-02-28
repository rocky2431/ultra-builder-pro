#!/usr/bin/env python3
"""
Post Edit Guard - Unified PostToolUse Hook
Replaces: code_quality.py, mock_detector.py, security_scan.py

Runs all three checkers in a single process with one stdin parse and one file read.
Decision priority: any block from any checker -> overall block.
"""

import sys
import json
import re
import os


# -- Shared Utilities --

def get_line_number(content, match_pos):
    """Get 1-based line number from character position."""
    return content[:match_pos].count('\n') + 1


def is_test_file(file_path):
    path_lower = file_path.lower()
    return any(ind in path_lower for ind in [
        '/test/', '/tests/', '/__tests__/',
        '/spec/', '/specs/',
        '.test.', '.spec.',
        '_test.', '_spec.',
    ])


def is_config_file(file_path):
    for pattern in [r'\.config\.', r'config/', r'constants\.', r'\.env\.', r'settings\.', r'\.d\.ts$']:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def is_generated_file(file_path):
    """Generated/vendor files - skip code quality checks."""
    indicators = [
        '/node_modules/', '/dist/', '/build/', '/.next/',
        '/coverage/', '.min.js', '.bundle.js', '.generated.',
        '/.claude/hooks/',
    ]
    return any(ind in file_path for ind in indicators)


def is_hook_file(file_path):
    """Hook files - skip security self-detection."""
    return '/.claude/hooks/' in file_path


def is_example_or_docs(file_path):
    path_lower = file_path.lower()
    return any(ind in path_lower for ind in [
        '/examples/', '/example/',
        '/docs/', '/documentation/',
        'readme', '.md',
    ])


def is_in_comment(line_content):
    stripped = line_content.lstrip()
    return stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('*')


# -- Extension Sets --

CODE_QUALITY_EXT = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.py', '.go', '.rs', '.java'}
MOCK_DETECTOR_EXT = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}
SECURITY_EXT = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.py', '.go', '.rs', '.java', '.rb', '.php'}
ALL_CODE_EXT = CODE_QUALITY_EXT | SECURITY_EXT


# -- Code Quality Patterns --

CQ_BLOCK_PATTERNS = [
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

CQ_WARN_PATTERNS = [
    (r'\bconsole\.(log|warn|error|debug|info)\s*\(', 'console.{} - Use structured logger in production'),
    (r'localhost:\d+', 'Hardcoded localhost - Use process.env.HOST'),
    (r'127\.0\.0\.1:\d+', 'Hardcoded localhost - Use process.env.HOST'),
    (r'["\']http://localhost', 'Hardcoded localhost URL - Use process.env.API_URL'),
    (r'(?:port|PORT)\s*[=:]\s*\d{4,5}(?!\d)', 'Hardcoded port - Use process.env.PORT'),
    (r'["\']https?://(?!localhost)[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}[^"\']*["\']',
     'Hardcoded URL - Use environment variable'),
    (r'\bstatic\s+(?:let|var|readonly)\s+\w*(?:state|data|cache|store|queue|buffer)\b',
     'Static variable for state - Persist to DB/KV store'),
    (r'\bstatic\s+\w+\s*:\s*(?:Map|Set|Array|Object)\s*[<\[]',
     'Static collection for state - Use external storage'),
    (r'fs\.(?:writeFileSync?|appendFileSync?)\s*\([^)]*(?:user|order|payment|transaction|customer|account)',
     'Local file for business data - Use DB or object storage'),
    (r'(?:writeFile|saveFile)\s*\([^)]*(?:\.json|\.csv)[^)]*(?:user|order|payment)',
     'Local file for business data - Use DB or object storage'),
]


# -- Mock Detector Patterns --

MOCK_FORBIDDEN_PATTERNS = [
    (r'\bjest\.fn\s*\(', 'jest.fn() for internal code'),
    (r'\bvi\.fn\s*\(', 'vi.fn() for internal code'),
    (r'\bjest\.mock\s*\(', 'jest.mock() - Test real module collaboration'),
    (r'\bvi\.mock\s*\(', 'vi.mock() - Test real module collaboration'),
    (r'\.mockResolvedValue\s*\(', '.mockResolvedValue() - Use real async behavior'),
    (r'\.mockReturnValue\s*\(', '.mockReturnValue() - Use real return values'),
    (r'\.mockImplementation\s*\(', '.mockImplementation() - Use real implementation'),
    (r'\bclass\s+InMemory\w*Repository', 'InMemoryRepository class - Use Testcontainers'),
    (r'\bclass\s+Mock\w+', 'Mock class - Use real implementation'),
    (r'\bclass\s+Fake\w+', 'Fake class - Use real implementation'),
    (r'\bsinon\.stub\s*\(', 'sinon.stub() - Use real implementation'),
    (r'\bsinon\.spy\s*\(', 'sinon.spy() - Use real implementation'),
    (r'\bsinon\.mock\s*\(', 'sinon.mock() - Use real implementation'),
    (r'\bspyOn\s*\([^)]+\)\.and\.returnValue', 'spyOn().and.returnValue - Use real implementation'),
    (r'\bit\.skip\s*\(\s*[\'"][^\'"]*(?:database|db|slow|integration)[^\'"]*[\'"]',
     'it.skip for DB/slow tests - "too slow" is not valid excuse'),
    (r'\btest\.skip\s*\(\s*[\'"][^\'"]*(?:database|db|slow|integration)[^\'"]*[\'"]',
     'test.skip for DB/slow tests - "too slow" is not valid excuse'),
    (r'\bdescribe\.skip\s*\(\s*[\'"][^\'"]*(?:database|db|integration)[^\'"]*[\'"]',
     'describe.skip for DB tests - Use Testcontainers'),
]

MOCK_ALLOWED_CONTEXTS = [
    r'on[A-Z]\w*\s*[:=]\s*(?:jest|vi)\.fn',
    r'handler\s*[:=]\s*(?:jest|vi)\.fn',
    r'callback\s*[:=]\s*(?:jest|vi)\.fn',
    r'mock(?:Fn|Handler|Callback)\s*=',
]

MOCK_RATIONALE_RE = r'//\s*Test\s+Double\s+rationale:'


# -- Security Patterns --

SEC_CRITICAL_PATTERNS = [
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
    (r'password\s*[=:]\s*["\'][^"\']{8,}["\'](?!\s*(?://|#)\s*(?:example|demo|test|placeholder))',
     'Hardcoded password'),
    (r'["\']SELECT\s+.+FROM\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'["\']INSERT\s+INTO\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'["\']UPDATE\s+.+SET\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'["\']DELETE\s+FROM\s+.+["\']\s*\+\s*', 'SQL string concatenation - Use parameterized queries'),
    (r'`SELECT\s+.+\$\{', 'SQL template literal with interpolation - Use parameterized queries'),
    (r'f["\']SELECT\s+.+\{', 'SQL f-string with interpolation - Use parameterized queries'),
    (r'\beval\s*\([^)]*\buser', 'Dynamic code evaluation with user input - Injection risk'),
    (r'\bexec\s*\([^)]*\buser', 'Dynamic code execution with user input - Injection risk'),
    (r'Function\s*\([^)]*\buser', 'Function() constructor with user input'),
    (r'catch\s*\([^)]*\)\s*\{\s*\}', 'Empty catch block - Log with context and re-throw or handle'),
    (r'catch\s*\([^)]*\)\s*\{\s*return\s+null\s*;?\s*\}',
     'catch returning null - Converts error to invalid state'),
    (r'catch\s*\([^)]*\)\s*\{\s*console\.log\s*\([^)]*\)\s*;?\s*\}',
     'catch with only console.log - Logging without handling'),
    (r'except\s*:\s*pass\s*$', 'Bare except with pass - Never silently swallow errors'),
    (r'except\s+\w+\s*:\s*pass\s*$', 'Exception swallowed with pass - Log or re-raise'),
    (r'throw\s+new\s+Error\s*\(\s*[\'"](?:Error|error|ERROR)[\'"]',
     'Generic Error message - Include what failed, why, and input'),
    (r'throw\s+new\s+Error\s*\(\s*[\'"][\'"]',
     'Empty Error message - Include what failed, why, and input'),
    (r'raise\s+Exception\s*\(\s*[\'"](?:Error|error)[\'"]',
     'Generic Exception message - Include context'),
]

SEC_HIGH_PATTERNS = [
    (r'\.innerHTML\s*=\s*(?![\'"<])', 'Dynamic innerHTML assignment - XSS risk'),
    (r'dangerouslySetInnerHTML\s*=\s*\{', 'dangerouslySetInnerHTML usage - XSS risk, ensure sanitization'),
    (r'verify\s*[=:]\s*False', 'SSL verification disabled'),
    (r'rejectUnauthorized\s*:\s*false', 'SSL verification disabled'),
    (r'NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*["\']?0', 'TLS verification disabled'),
    (r'#\s*nosec', 'Security rule disabled'),
    (r'//\s*eslint-disable.*security', 'Security ESLint rule disabled'),
    (r'@SuppressWarnings.*security', 'Security warning suppressed'),
    (r'subprocess\.(?:call|run|Popen)\s*\([^)]*shell\s*=\s*True',
     'Shell injection risk - use shell=False'),
]


# -- Checker: Code Quality --

def check_code_quality(_file_path, content, lines):
    """Returns (blocks, warnings). WARN patterns deferred to review-code agent."""
    blocks = []

    for pattern, message in CQ_BLOCK_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = get_line_number(content, match.start())
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''
            # All TODO/FIXME/XXX/HACK are forbidden per CLAUDE.md - no exceptions
            blocks.append({'line': line_num, 'message': message, 'code': line_content[:80]})

    # WARN patterns deferred to review-code agent (reduces PostToolUse noise)
    return blocks, []


# -- Checker: Mock Detector --

def _has_rationale_comment(lines, match_line_idx):
    """Check for Test Double rationale comment near violation (5 before, 2 after)."""
    start = max(0, match_line_idx - 5)
    end = min(len(lines), match_line_idx + 3)
    for i in range(start, end):
        if re.search(MOCK_RATIONALE_RE, lines[i], re.IGNORECASE):
            return True
    return False


def _is_allowed_mock_context(line_content):
    return any(re.search(p, line_content) for p in MOCK_ALLOWED_CONTEXTS)


def check_mocks(_file_path, content, lines):
    """Returns list of violations. Only called for test files."""
    violations = []

    # Skip if global rationale in first 20 lines
    first_lines = '\n'.join(lines[:20])
    if re.search(MOCK_RATIONALE_RE, first_lines, re.IGNORECASE):
        return violations

    for pattern, message in MOCK_FORBIDDEN_PATTERNS:
        for match in re.finditer(pattern, content):
            line_num = get_line_number(content, match.start())
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            if _has_rationale_comment(lines, line_num - 1):
                continue
            if _is_allowed_mock_context(line_content):
                continue

            violations.append({'line': line_num, 'pattern': message, 'code': line_content[:80]})

    return violations


# -- Checker: Security Scan --

def check_security(file_path, content, lines):
    """Returns (critical, high). HIGH patterns deferred to review-code agent."""
    critical = []
    _is_test = is_test_file(file_path)
    _is_example = is_example_or_docs(file_path)

    for pattern, message in SEC_CRITICAL_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            line_num = get_line_number(content, match.start())
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''

            if _is_test and 'catch' in message.lower():
                continue
            if _is_example and 'Hardcoded' in message:
                continue

            critical.append({'line': line_num, 'message': message, 'code': line_content[:80]})

    # HIGH patterns deferred to review-code agent (reduces PostToolUse noise)
    return critical, []


# -- Output Formatting --

def _fmt_code_quality(file_path, blocks, warnings):
    out = []
    fname = os.path.basename(file_path)
    for b in blocks[:5]:
        out.append(f"[CQ:BLOCK] {fname}:{b['line']} {b['message']}")
    for w in warnings[:3]:
        out.append(f"[CQ:WARN] {fname}:{w['line']} {w['message']}")
    if len(blocks) > 5:
        out.append(f"[CQ] +{len(blocks)-5} more blocks")
    return out


def _fmt_mock_violations(file_path, violations):
    if not violations:
        return []
    fname = os.path.basename(file_path)
    out = []
    for v in violations[:5]:
        out.append(f"[MOCK:BLOCK] {fname}:{v['line']} {v['pattern']}")
    if len(violations) > 5:
        out.append(f"[MOCK] +{len(violations)-5} more")
    return out


def _fmt_security(file_path, critical, high):
    out = []
    fname = os.path.basename(file_path)
    for c in critical[:5]:
        out.append(f"[SEC:CRIT] {fname}:{c['line']} {c['message']}")
    for h in high[:3]:
        out.append(f"[SEC:HIGH] {fname}:{h['line']} {h['message']}")
    return out


# -- Main --

def main():
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[post_edit_guard] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    if not isinstance(hook_input, dict):
        print(json.dumps({}))
        return

    tool_name = hook_input.get('tool_name')
    tool_input = hook_input.get('tool_input', {})

    if tool_name not in ('Edit', 'Write'):
        print(json.dumps({}))
        return

    file_path = tool_input.get('file_path', '')
    ext = os.path.splitext(file_path)[1].lower()

    if ext not in ALL_CODE_EXT:
        print(json.dumps({}))
        return

    if not os.path.exists(file_path):
        print(json.dumps({}))
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        print(json.dumps({}))
        return

    lines = content.split('\n')
    all_issues = []
    has_blocks = False

    # 1. Code quality (skip generated files including hook files)
    if ext in CODE_QUALITY_EXT and not is_generated_file(file_path):
        cq_blocks, cq_warnings = check_code_quality(file_path, content, lines)
        section = _fmt_code_quality(file_path, cq_blocks, cq_warnings)
        if section:
            all_issues.extend(section)
        if cq_blocks:
            has_blocks = True

    # 2. Mock detector (test files only)
    if ext in MOCK_DETECTOR_EXT and is_test_file(file_path):
        mock_violations = check_mocks(file_path, content, lines)
        section = _fmt_mock_violations(file_path, mock_violations)
        if section:
            if all_issues:
                all_issues.append("")
            all_issues.extend(section)
            has_blocks = True

    # 3. Security scan (skip hook files only)
    if ext in SECURITY_EXT and not is_hook_file(file_path):
        sec_critical, sec_high = check_security(file_path, content, lines)
        section = _fmt_security(file_path, sec_critical, sec_high)
        if section:
            if all_issues:
                all_issues.append("")
            all_issues.extend(section)
        if sec_critical:
            has_blocks = True

    if all_issues:
        warning_message = "\n".join(all_issues)

        if has_blocks:
            result = {
                "decision": "block",
                "reason": warning_message,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": warning_message,
                },
            }
        else:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": warning_message,
                },
            }
        print(json.dumps(result))
    else:
        print(json.dumps({}))


if __name__ == '__main__':
    main()
