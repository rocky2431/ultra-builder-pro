---
description: Pre-delivery quality audit (Anti-Pattern + Coverage Gap + E2E + Performance + Security)
argument-hint: [scope]
allowed-tools: TodoWrite, Bash, Read, Write, Task, Grep, Glob
---

# /ultra-test

## Purpose

Pre-delivery quality audit. Validates test health, coverage gaps, E2E functionality, performance, and security.

**Note**: This is NOT for running unit tests (that's `/ultra-dev` Step 3-4). This is for auditing overall project quality before `/ultra-deliver`.

---

## Pre-Execution Checks

1. **Detect project type** (for test command reference):
   - Node.js: `package.json` → read `scripts.test`
   - Python: `pyproject.toml` or `pytest.ini` → pytest
   - Go: `go.mod` → `go test`
   - Rust: `Cargo.toml` → `cargo test`

2. **Check prerequisites**:
   - At least one task completed in `.ultra/tasks/tasks.json`
   - Test files exist (`**/*.test.*` or `**/*.spec.*` or `**/test_*.py`)

---

## Workflow

### Step 1: Anti-Pattern Detection

**Purpose**: Detect fake/meaningless tests before they waste CI time.

**Scan patterns** (auto-detect based on project type):
- TypeScript/JavaScript: `**/*.test.ts`, `**/*.spec.ts`, `**/*.test.js`, `**/*.spec.js`
- Python: `**/test_*.py`, `**/*_test.py`
- Go: `**/*_test.go`

**Detection Rules**:

| Pattern | Severity | Regex | Example |
|---------|----------|-------|---------|
| Tautology | CRITICAL | `expect\((true|false|1|0)\)\.toBe\(\1\)` | `expect(true).toBe(true)` |
| Empty test | CRITICAL | `(it|test)\([^)]+,\s*\(\)\s*=>\s*\{\s*\}\)` | `it('does something', () => {})` |
| Core logic mock | CRITICAL | `(mock|jest\.mock)\(['"]\./(domain|core|services)/` | `mock('./domain/user')` |
| No assertion | WARNING | Test function without `expect`/`assert` | `it('test', () => { doThing() })` |

**Process**:
1. Use Grep to scan test files for each pattern
2. Count matches per pattern
3. Report findings

**Result**:
- ❌ **BLOCKED**: Any CRITICAL pattern found → must fix before delivery
- ⚠️ **WARNING**: Only WARNING patterns found → can proceed with note
- ✅ **PASS**: No anti-patterns detected

---

### Step 2: Coverage Gap Analysis

**Purpose**: Find untested code that coverage % misses.

**Process**:
1. Find all exported symbols: `export (function|const|class)`
2. Search for each symbol in test files
3. Report symbols with 0 test references

**Output**: `.ultra/docs/test-coverage-gaps.md`

```markdown
# Test Coverage Gaps Report

## Summary
- Exported Symbols: 45
- Untested: 8
- Symbol Coverage: 82%

## Untested Functions
- ❌ `deleteUser` (src/services/user.ts) - HIGH priority
- ❌ `validateInput` (src/utils/validation.ts) - MEDIUM priority
```

---

### Step 3: E2E Testing (if applicable)

**Trigger**: Project has frontend or web application

**Method**: Claude Code native Chrome capability (`mcp__claude-in-chrome__*`)

**Process**:
1. Start dev server (auto-detect from package.json)
2. Navigate to key pages
3. Verify critical elements render (`read_page`, `find`)
4. Check for console errors (`read_console_messages`)
5. Test primary user flows (form submission, navigation, etc.)
6. Take screenshots for verification (`computer` action=screenshot)

**Result**:
- ✅ **PASS**: All pages load, no console errors, flows complete
- ❌ **BLOCKED**: Critical pages fail to load or major console errors

---

### Step 4: Performance Testing (frontend only)

**Trigger**: Project has frontend (React/Vue/Next.js/etc.)

**Core Web Vitals targets**:

| Metric | Target | Tool |
|--------|--------|------|
| LCP (Largest Contentful Paint) | <2.5s | Lighthouse |
| INP (Interaction to Next Paint) | <200ms | Lighthouse |
| CLS (Cumulative Layout Shift) | <0.1 | Lighthouse |

**Process**:
1. Detect dev server port from `package.json` (`scripts.dev` or `scripts.start`)
2. Start dev server if not running
3. Run Lighthouse:
   ```bash
   lighthouse http://localhost:{detected-port} --only-categories=performance --output=json
   ```
4. Parse results and compare against targets

---

### Step 5: Security Audit

**Process**:
1. Run dependency audit
2. Check for known vulnerabilities
3. Report findings

**Auto-detect commands**:
```bash
# Node.js
npm audit --json

# Python
pip-audit --format json

# Go
govulncheck ./...
```

**Severity handling**:
- Critical/High: ❌ BLOCKED
- Medium: ⚠️ Warning
- Low: ℹ️ Info

---

## Quality Gates

All must pass for `/ultra-deliver`:

| Gate | Requirement |
|------|-------------|
| Anti-Pattern | No CRITICAL patterns detected |
| Coverage Gaps | No HIGH priority untested functions |
| E2E | All tests pass (if applicable) |
| Performance | Core Web Vitals pass (if frontend) |
| Security | No critical/high vulnerabilities |

---

## Output

**Quality Audit Report** (Chinese at runtime):

```
🧪 Quality Audit Report
========================

📊 Anti-Pattern Detection: ✅ PASS
   - 15 test files scanned
   - 0 CRITICAL patterns
   - 1 WARNING (no assertion in 1 test)

📈 Coverage Gaps: 3 untested functions ⚠️
   - HIGH: 1 (deleteUser)
   - MEDIUM: 2

🌐 E2E Tests: 12/12 passed ✅
   - Method: Playwright

⚡ Performance:
   - LCP: 1.8s ✅
   - INP: 150ms ✅
   - CLS: 0.05 ✅

🔒 Security: 0 critical, 2 medium ⚠️

Overall: ⚠️ PASS with warnings
Action: Fix coverage gaps before /ultra-deliver
```

---

## Integration

- **Prerequisites**: At least one task completed via `/ultra-dev`
- **Input**: Test files, source code, package configs
- **Output**:
  - `.ultra/docs/test-coverage-gaps.md`
  - Quality report (terminal)
- **Next**: `/ultra-deliver` (if all gates pass)

---

## Comparison with /ultra-dev

| Aspect | /ultra-dev | /ultra-test |
|--------|------------|-------------|
| When | Per task | Before delivery |
| Focus | TDD for single task | Project-wide audit |
| Unit tests | Run & write | Detect anti-patterns |
| E2E | ❌ | ✅ (Chrome MCP) |
| Performance | ❌ | ✅ (Lighthouse) |
| Security | ❌ | ✅ (Dependency audit) |

---

## Output Format

**Command icon**: 🧪
