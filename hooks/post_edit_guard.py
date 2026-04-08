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
TDD_SOURCE_EXT = {'.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.rb'}
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


# -- Scope Reduction Patterns (WARN only, non-test source files) --

SCOPE_REDUCTION_PATTERNS = [
    (r'(?:simplified|basic)\s+(?:version|implementation|approach)',
     'Scope reduction language - implement full spec or split task'),
    (r'(?:static|hardcoded)\s+for\s+now',
     'Scope deferral - implement dynamic per spec'),
    (r'\bplaceholder\b',
     'Placeholder detected - complete implementation per spec'),
    (r'\bv1\b.*(?:later|future|next|v2)',
     'Scope versioning (v1/v2) - deliver full spec or propose task split'),
    (r'(?:will\s+be|to\s+be)\s+(?:wired|connected|integrated)\s+later',
     'Deferred wiring - integrate now or flag as blocked'),
    (r'(?:future|later)\s+(?:enhancement|improvement|phase|iteration)',
     'Scope deferral to future - deliver now or split task'),
    (r'\bminimal\s+(?:implementation|version|viable)',
     'Minimal implementation - deliver full spec scope'),
    (r'\bskip(?:ped|ping)?\s+for\s+now',
     'Skipped scope - implement or flag as blocked'),
    (r'\bstub(?:bed)?\b(?!\s*(?:test|spec|mock))',
     'Stub detected - complete implementation'),
    (r'\bnot\s+(?:wired|connected|hooked)\s+(?:to|up|yet)',
     'Unwired code - integrate before commit'),
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


# -- Checker: Scope Reduction Detection --

def check_scope_reduction(file_path, content, lines):
    """Detect scope reduction language in non-test source files. Returns warnings list."""
    if is_test_file(file_path) or is_config_file(file_path):
        return []
    if is_generated_file(file_path) or is_hook_file(file_path):
        return []
    if is_example_or_docs(file_path):
        return []

    warnings = []
    for pattern, message in SCOPE_REDUCTION_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = get_line_number(content, match.start())
            line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ''
            # Only flag if the pattern appears in comments or string literals
            # (scope reduction language is typically in code comments, not variable names)
            if is_in_comment(line_content) or re.search(r'["\'].*' + re.escape(match.group(0)[:20]) + r'.*["\']', line_content):
                warnings.append({'line': line_num, 'message': message, 'code': line_content[:80]})
    return warnings


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


# -- Checker: TDD Test File Pairing --

# Directories that indicate source code (not config, not generated)
_SOURCE_DIRS = {'src', 'lib', 'app', 'pkg', 'internal', 'services', 'domain', 'core', 'modules'}

# Test file search patterns per language
_TEST_PATTERNS = {
    '.ts': ['.test.ts', '.spec.ts', '_test.ts'],
    '.tsx': ['.test.tsx', '.spec.tsx'],
    '.js': ['.test.js', '.spec.js', '_test.js'],
    '.jsx': ['.test.jsx', '.spec.jsx'],
    '.py': ['_test.py', 'test_'],
    '.go': ['_test.go'],
    '.rs': [],  # Rust tests are inline (#[cfg(test)])
    '.java': ['Test.java'],
    '.rb': ['_test.rb', '_spec.rb'],
}


def check_test_file_exists(file_path):
    """Check if a source file has a corresponding test file. Returns warning string or None."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in TDD_SOURCE_EXT:
        return None

    # Skip test files, config files, generated files, hook files
    if is_test_file(file_path) or is_config_file(file_path):
        return None
    if is_generated_file(file_path) or is_hook_file(file_path):
        return None

    # Skip files not in recognizable source directories
    path_parts = file_path.replace('\\', '/').lower().split('/')
    if not any(d in path_parts for d in _SOURCE_DIRS):
        return None

    # Rust uses inline tests - skip
    if ext == '.rs':
        return None

    basename = os.path.splitext(os.path.basename(file_path))[0]
    dirpath = os.path.dirname(file_path)
    patterns = _TEST_PATTERNS.get(ext, [])

    # Search in same dir, test/ sibling, tests/ sibling, __tests__/ sibling
    search_dirs = [dirpath]
    parent = os.path.dirname(dirpath)
    for test_dir_name in ['test', 'tests', '__tests__', 'spec']:
        candidate = os.path.join(parent, test_dir_name)
        if os.path.isdir(candidate):
            search_dirs.append(candidate)
        # Also check test dir mirroring source structure
        rel = os.path.relpath(dirpath, parent)
        candidate_mirror = os.path.join(parent, test_dir_name, rel)
        if os.path.isdir(candidate_mirror):
            search_dirs.append(candidate_mirror)

    for search_dir in search_dirs:
        for pat in patterns:
            if ext == '.py' and pat == 'test_':
                test_path = os.path.join(search_dir, f"test_{basename}.py")
            elif ext == '.java':
                test_path = os.path.join(search_dir, f"{basename}Test.java")
            else:
                test_path = os.path.join(search_dir, f"{basename}{pat}")
            if os.path.exists(test_path):
                return None

    fname = os.path.basename(file_path)
    return f"[TDD] No test file found for {fname}"


# -- Checker: Silent Catch Detection --

SILENT_CATCH_PATTERN = re.compile(
    r'except\s*(?:\([^)]*\)|[\w.,\s]*)?\s*(?:as\s+\w+)?\s*:\s*\n'
    r'\s+(?:pass|return\s*$|return\s+None|\.\.\.)',
    re.MULTILINE
)


def check_silent_catches(file_path, content, lines):
    """Detect except blocks that swallow errors silently."""
    if is_hook_file(file_path) or is_test_file(file_path):
        return []

    violations = []
    for match in SILENT_CATCH_PATTERN.finditer(content):
        line_num = get_line_number(content, match.start())
        snippet = match.group(0).strip().split('\n')[0][:80]
        violations.append((line_num, snippet))
    return violations


# -- Checker: Blast Radius --

def check_blast_radius(file_path):
    """Find files that import/reference the edited file. Returns list of dependent paths."""
    basename = os.path.basename(file_path)
    module_name = os.path.splitext(basename)[0]

    if not module_name or module_name.startswith('.'):
        return []

    # Only check for Python files in hooks dir or source files in project
    parent_dir = os.path.dirname(file_path)
    if not parent_dir:
        return []

    dependents = []
    try:
        for fname in os.listdir(parent_dir):
            fpath = os.path.join(parent_dir, fname)
            if fpath == file_path or not fname.endswith('.py'):
                continue
            # Skip test files and __pycache__
            if '/tests/' in fpath or '__pycache__' in fpath:
                continue
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    head = f.read(5000)  # Only scan first 5KB for imports
                if re.search(rf'\bimport\s+{re.escape(module_name)}\b|from\s+{re.escape(module_name)}\b', head):
                    dependents.append(fname)
            except (OSError, UnicodeDecodeError):
                pass
    except OSError:
        pass

    return dependents


# -- Checker: Test File Reminder --

def check_test_reminder(file_path):
    """If edited file has a corresponding test file, remind to run it."""
    if is_test_file(file_path) or is_config_file(file_path):
        return None

    basename = os.path.basename(file_path)
    name_no_ext = os.path.splitext(basename)[0]
    parent = os.path.dirname(file_path)

    # Check common test file locations
    candidates = [
        os.path.join(parent, 'tests', f'test_{basename}'),
        os.path.join(parent, 'tests', f'test_{name_no_ext}.py'),
        os.path.join(parent, f'{name_no_ext}.test.ts'),
        os.path.join(parent, f'{name_no_ext}.spec.ts'),
        os.path.join(parent, '__tests__', f'{name_no_ext}.test.ts'),
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


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


def _fmt_scope_reduction(file_path, warnings):
    if not warnings:
        return []
    fname = os.path.basename(file_path)
    out = []
    for w in warnings[:5]:
        out.append(f"[SCOPE:WARN] {fname}:{w['line']} {w['message']}")
    if len(warnings) > 5:
        out.append(f"[SCOPE] +{len(warnings)-5} more")
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

    # Skip very large files to avoid OOM on regex scanning
    try:
        if os.path.getsize(file_path) > 5_000_000:
            print(json.dumps({}))
            return
    except OSError:
        pass

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

    # 4. Scope reduction detection (source files only, warn not block)
    if ext in CODE_QUALITY_EXT and not is_generated_file(file_path):
        scope_warnings = check_scope_reduction(file_path, content, lines)
        scope_section = _fmt_scope_reduction(file_path, scope_warnings)
        if scope_section:
            if all_issues:
                all_issues.append("")
            all_issues.extend(scope_section)

    # 5. TDD test file pairing (source files only, warn not block)
    tdd_warning = check_test_file_exists(file_path)
    if tdd_warning:
        if all_issues:
            all_issues.append("")
        all_issues.append(tdd_warning)

    # 6. Silent catch detection (block)
    if ext == '.py' and not is_hook_file(file_path):
        silent_violations = check_silent_catches(file_path, content, lines)
        if silent_violations:
            if all_issues:
                all_issues.append("")
            all_issues.append("[SILENT-CATCH:BLOCK] Silent exception handlers detected:")
            for line_num, snippet in silent_violations[:5]:
                all_issues.append(f"  L{line_num}: {snippet}")
            all_issues.append("  → Add logging or handle the error explicitly.")
            has_blocks = True

    # 7. Blast radius (info via stderr, never blocks)
    dependents = check_blast_radius(file_path)
    if dependents:
        short = os.path.basename(file_path)
        dep_list = ", ".join(dependents[:8])
        extra = f" +{len(dependents)-8} more" if len(dependents) > 8 else ""
        print(f"[Impact] {short} is imported by: {dep_list}{extra}", file=sys.stderr)

    # 8. Test reminder (info via stderr, never blocks)
    test_file = check_test_reminder(file_path)
    if test_file:
        rel_test = os.path.relpath(test_file)
        print(f"[Test] Run: pytest {rel_test}", file=sys.stderr)

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
