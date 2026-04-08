---
description: Pre-delivery quality audit (Anti-Pattern + Coverage Gap + E2E + Performance + Security)
argument-hint: [scope]
allowed-tools: Bash, Read, Write, Edit, Task, Grep, Glob, AskUserQuestion
model: opus
---

# /ultra-test

## Workflow Tracking (MANDATORY)

**On command start**, create tasks for each major step using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 0 | Pre-Execution Check | Checking prerequisites... |
| 1 | Anti-Pattern Detection | Detecting anti-patterns... |
| 2 | Coverage Gap Analysis | Analyzing coverage gaps... |
| 3 | E2E Testing | Running E2E tests... |
| 4 | Performance Testing | Testing performance... |
| 5 | Security Audit | Auditing security... |
| 6 | Auto-Fix Loop | Auto-fixing issues... |
| 7 | Persist Results | Persisting results... |

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**On context recovery**: `TaskList` → resume from last incomplete step

---

Pre-delivery quality audit. Validates test health, coverage gaps, E2E functionality, performance, and security.

**Note**: This is NOT for running unit tests (that's `/ultra-dev`). This is for auditing overall project quality before `/ultra-deliver`.

---

## Pre-Execution

1. Detect project type from config files (package.json, Cargo.toml, go.mod, pyproject.toml, etc.)
2. Verify at least one task completed in `.ultra/tasks/tasks.json`
3. Verify test files exist

---

## Workflow

### Step 1: Anti-Pattern Detection

**Purpose**: Detect fake/meaningless tests before they waste CI time.

**What to detect**:
1. **Tautology**: Assertions that always pass (e.g., `assert True`, `expect(true).toBe(true)`)
2. **Empty test**: Test functions with no logic inside
3. **Core logic mock**: Mocking domain/core/services code (violates test authenticity)

**How**:
1. Identify test file patterns for detected language
2. Construct appropriate regex for each anti-pattern
3. Use Grep to scan and count matches

**Result**:
- ❌ BLOCKED: Any critical anti-pattern found
- ⚠️ WARNING: Minor issues found
- ✅ PASS: No anti-patterns

---

### Step 2: Coverage Gap Analysis

**Purpose**: Find exported functions/classes not referenced in any test file.

**What to do**:
1. Find all exported/public symbols in source code
2. Search for each symbol name in test files
3. Report symbols with 0 test references

**Output**: `.ultra/docs/test-coverage-gaps.md`

**Priority**:
- HIGH: Core business logic untested
- MEDIUM: Utility functions untested
- LOW: Config/constants untested

### Step 2.5: Wiring Verification

**Purpose**: Detect orphaned code — files that exist and pass tests but are not connected to anything.

**What to do**:
1. Find all exported symbols in source files (functions, classes, constants)
2. For each export, search ALL non-test source files for imports of that symbol
3. Report exports with 0 non-test imports as orphaned

**Wiring Patterns to Verify** (when applicable):
- **Component → API**: Components with fetch/axios calls should target existing API routes
- **API → Database**: Route handlers should import and use DB clients (prisma, db, mongoose)
- **Form → Handler**: onSubmit handlers should have real logic (not empty `() => {}`)
- **State → Render**: State variables should appear in JSX/template output

**Stub Detection** (Level 2 — Substantive):
- Functions returning empty arrays `return []` or `return {}` without DB/API calls
- Functions with only `console.log()` as body
- Event handlers that only call `e.preventDefault()` with no further logic
- Components returning only `<div>Placeholder</div>` or similar static text

**Output**: Append to `.ultra/docs/test-coverage-gaps.md` under "## Wiring Gaps" section

**Priority**:
- HIGH: Orphaned exports in core business logic
- HIGH: Stub implementations (empty returns, log-only handlers)
- MEDIUM: Orphaned utility functions
- LOW: Orphaned type definitions

---

### Step 3: E2E Testing

**Trigger**: Project has web UI or API endpoints

**Method**: Claude Code native Chrome capability (`mcp__claude-in-chrome__*`)

**What to do**:
1. Start dev server (detect start command from project config)
2. Navigate to key pages/endpoints
3. Verify elements render correctly
4. Check for console errors
5. Test primary user flows

**Result**:
- ✅ PASS: All pages load, no errors, flows complete
- ❌ BLOCKED: Critical pages fail or major errors

---

### Step 4: Performance Testing

**Trigger**: Project has frontend

**What to measure** (Core Web Vitals):
- LCP (Largest Contentful Paint): <2.5s
- INP (Interaction to Next Paint): <200ms
- CLS (Cumulative Layout Shift): <0.1

**How**: Run Lighthouse on dev server URL

---

### Step 5: Security Audit

**What to do**: Run dependency vulnerability scan using project's package manager audit command.

**Severity handling**:
- Critical/High: ❌ BLOCKED
- Medium: ⚠️ Warning
- Low: ℹ️ Info

---

## Quality Gates

All must pass for `/ultra-deliver`:

| Gate | Requirement |
|------|-------------|
| Anti-Pattern | No critical patterns detected |
| Coverage Gaps | No HIGH priority untested functions |
| E2E | All tests pass (if applicable) |
| Performance | Core Web Vitals pass (if frontend) |
| Security | No critical/high vulnerabilities |

**Pass Condition**: All gates pass → Proceed to Output

---

## Output

### 1. Persist Results

Update `.ultra/test-report.json`:

```json
{
  "timestamp": "2025-01-01T03:00:00Z",
  "git_commit": "abc123",
  "passed": false,
  "run_count": 1,
  "gates": {
    "anti_pattern": { "passed": true, "critical": 0, "warning": 1 },
    "coverage_gaps": { "passed": false, "high": 2, "medium": 3 },
    "e2e": { "passed": true, "skipped": false },
    "performance": { "passed": true, "lcp": 1.8, "inp": 150, "cls": 0.05 },
    "security": { "passed": true, "critical": 0, "high": 0, "medium": 2 }
  },
  "blocking_issues": [
    "Coverage Gap: deleteUser (src/services/user.ts) - HIGH"
  ]
}
```

**Rules**:
- If file exists, increment `run_count`
- `passed` = all gates passed
- `blocking_issues` = list of reasons for failure

---

## Auto-Fix Loop

If any gate fails, attempt automatic fix:

```
Loop (max 5 attempts):
  1. Analyze blocking_issues
  2. Fix issues → re-run tests → update run_count
  3. If external dependency issue → break and report
  4. If all gates pass → done
```

**Auto-fix all code issues**:
- Coverage Gap → Write missing tests
- Anti-Pattern → Fix test code
- E2E errors → Fix code
- Performance → Optimize code (splitting, lazy loading, etc.)

**External dependency issues** (cannot auto-fix):
- Security CVE in third-party package → Requires upstream fix or user decision to upgrade

**If max attempts reached**:
- Report remaining issues to user
- Explain what was attempted

### 2. Display Report

---

## Output Format

> Claude responds in Chinese per CLAUDE.md.

**Command icon**: 🧪
