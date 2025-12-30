---
description: Comprehensive testing (six-dimensional coverage + Core Web Vitals)
argument-hint: [scope]
allowed-tools: TodoWrite, Bash, Read, Write, Task, Grep, Glob
---

# /ultra-test

## Purpose

Execute comprehensive testing with six-dimensional coverage and Core Web Vitals monitoring.

## Pre-Execution Checks

- Check for code changes via `git status`
- Assess existing test coverage (read coverage report if available)
- Detect frontend vs backend: Frontend requires Core Web Vitals testing
- Verify test frameworks configured

## Workflow

### 0. Test Authenticity Analysis (TAS)

**⚠️ MANDATORY: Execute BEFORE running tests to detect fake tests early.**

**Auto-triggered by**: `guarding-test-quality` skill

**Analysis Process**:
1. **Scan test files**: `**/*.test.ts`, `**/*.spec.ts`, `**/*.test.js`, `**/*.spec.js`
2. **Calculate TAS** for each file (4 components):

| Component | Weight | Detection |
|-----------|--------|-----------|
| Mock Ratio | 25% | Internal mocks (`jest.mock('../')`) vs total imports |
| Assertion Quality | 35% | Behavioral (`toBe`, `toEqual`) vs mock-only (`toHaveBeenCalled`) |
| Real Execution | 25% | Real code lines vs mock-driven lines |
| Pattern Compliance | 15% | 100 - (anti-patterns × 15) |

3. **Grade each file**:
   - A (85-100): ✅ High quality
   - B (70-84): ✅ Pass with minor issues
   - C (50-69): ❌ **BLOCKED** - Needs improvement
   - D/F (<50): ❌ **BLOCKED** - Fake tests detected

**Anti-Pattern Detection** (Critical):
```regex
# Tautology tests (CRITICAL - automatic F grade)
expect\((true|false|1|0)\)\.toBe\((true|false|1|0)\)

# Empty test body (CRITICAL)
it\([^)]+,\s*(async\s*)?\(\)\s*=>\s*\{\s*\}\)

# Over-mocking internal modules (WARNING)
jest\.mock\(['"]\.\./
vi\.mock\(['"]\.\./

# Mock-only assertions (WARNING)
\.toHaveBeenCalled\(\)(?!With)
```

**Output** (Chinese at runtime):
```
📊 Test Authenticity Analysis Report
===================================
Project TAS: 78% (Grade: B)

Files Analyzed: 15
- A Grade (85+): 8 files
- B Grade (70-84): 5 files
- C Grade (50-69): 2 files ❌ BLOCKED
- D/F Grade (<50): 0 files

Issues Found:
- src/services/auth.test.ts: TAS 62% (C)
  - Issue: 8 internal module mocks, only 2 behavioral assertions
  - Recommendation: Remove internal mocks, test real AuthService

Quality Gate: ❌ BLOCKED (2 files below 70%)
```

**Blocking Conditions**:
- ❌ Any file TAS < 70% → Tests BLOCKED
- ❌ Tautology detected (`expect(true).toBe(true)`) → Tests BLOCKED
- ❌ Empty test body detected → Tests BLOCKED

**Codex Test Generation** (auto-triggered when TAS critically low):
```
If project average TAS < 50%:
  Trigger codex-test-gen skill to regenerate tests with 6D coverage.
  See skills/codex-test-gen/SKILL.md for detailed requirements.
```

**Reference**: `guidelines/ultra-testing-philosophy.md` for anti-pattern examples and fixes

---

### 0.5: Codex Test Generation (Dual-Engine)

**Before Claude Code writes tests, optionally let Codex generate test cases.**

**When to Use**:
- Coverage gap detected (< 80%)
- Complex logic requires edge case coverage
- Security-critical code needs penetration tests

**Codex Test Generation**:
```bash
# Generate comprehensive tests for a file
codex -q <<EOF
Generate comprehensive test cases for the following code:
$(cat {target_file})

Requirements:
1. Cover all branches and paths
2. Include boundary tests (null, empty, max, min)
3. Include exception tests (error handling)
4. Include security tests (injection, XSS)
5. Use vitest/jest syntax
6. Mock only external dependencies (DB, API)
7. Each test must have meaningful assertions

Output complete test file code.
EOF
```

**Codex Test Review**:
```bash
# Review existing tests for quality
codex -q <<EOF
Review the following test file for quality issues:
$(cat {test_file})

Check for:
1. Tautology tests (expect(true).toBe(true))
2. Over-mocking (internal modules mocked)
3. Missing edge cases
4. Weak assertions (only toHaveBeenCalled)

Provide specific improvements with code.
EOF
```

**Integration with TAS**:
- Codex-generated tests are validated by TAS
- TAS ≥ 70% required for generated tests
- Regenerate if TAS < 70%

---

### 1. Design Test Strategy

Design comprehensive strategy covering all six dimensions:
**Functional, Boundary, Exception, Performance, Security, Compatibility**

**Reference**: See `guidelines/quality-standards.md#six-dimensional-test-coverage` for complete details.

### 2. Execute Tests

**Unit/Integration** (Built-in Bash):
```bash
npm test -- --coverage  # JavaScript/TypeScript (≥80% coverage)
pytest --cov=src --cov-report=html  # Python
go test -coverprofile=coverage.out ./...  # Go
```

**E2E Testing** (Playwright Skill auto-activates):
When you mention "E2E test" or "browser automation":
1. Playwright Skill generates test code (TypeScript)
2. Run tests: `npx playwright test`
3. Reports results in Chinese

**Performance** (Frontend only - Lighthouse CLI):
```bash
lighthouse http://localhost:3000 --only-categories=performance --output=json
```

**Reference**: `@config/ultra-mcp-guide.md` for complete testing tools guide

### 3. Analyze Results

- Collect metrics from all test types
- Identify failures and root causes
- Generate fix recommendations

---

### 3.5 Test Coverage Gap Analysis (AI Automated)

**AI Workflow** (executes automatically after test execution):

```typescript
// Step 1: Find all exported functions, classes, and methods
const exports = Grep({
  pattern: "export (function|const|class)",
  path: "src/",
  type: "ts",
  output_mode: "content",
  "-n": true
});

// Step 2: Extract symbol names
// Example matches:
// - "export function login(" → "login"
// - "export class UserService" → "UserService"
// - "export const getUserById =" → "getUserById"
const symbolNames = [];
exports.split('\n').forEach(line => {
  const match = line.match(/export\s+(function|const|class)\s+(\w+)/);
  if (match) symbolNames.push(match[2]);
});

// Step 3: Search for each symbol in test files
const gaps = [];
for (const symbol of symbolNames) {
  const testMatches = Grep({
    pattern: symbol,
    path: "**/*.test.ts",
    output_mode: "count"
  });

  if (testMatches === 0) {
    gaps.push({
      symbol,
      file: extractFileFromGrep(symbol),  // Helper to get file path
      status: 'UNTESTED'
    });
  }
}

// Step 4: Generate gap report
const gapReport = `
# Test Coverage Gaps Report

Generated: ${new Date().toISOString()}

## Summary
- Total Exported Symbols: ${symbolNames.length}
- Untested Symbols: ${gaps.length}
- Coverage: ${((1 - gaps.length / symbolNames.length) * 100).toFixed(1)}%

## Untested Methods/Functions

${gaps.map(gap => `- ❌ **${gap.symbol}** (\`${gap.file}\`) - 0 test cases found`).join('\n')}

## Recommendations

${gaps.slice(0, 5).map(gap => `
### ${gap.symbol}
**File**: \`${gap.file}\`
**Priority**: ${gap.symbol.includes('delete') || gap.symbol.includes('remove') ? 'HIGH' : 'MEDIUM'}
**Suggested Test Dimensions**:
1. Functional: Core logic validation
2. Boundary: Edge cases (null, empty, max values)
3. Exception: Error handling
4. Security: Input validation
`).join('\n')}
`;

Write(".ultra/docs/test-coverage-gaps.md", gapReport);
```

**Output**: `.ultra/docs/test-coverage-gaps.md`

**Accuracy**: ~90%
- ✅ Detects most untested exports
- ⚠️ May miss: Methods inside classes (requires deeper analysis), private functions (not exported), dynamic exports

**Token cost**: ~8000 tokens

**When to use**:
- After running `npm test -- --coverage`
- Before marking task as complete
- During /ultra-test Phase 3

**Optional: User Review for Higher Accuracy**:
- Review AI-generated gap report
- Compare with coverage report HTML for detailed line-by-line coverage
- Add missed methods identified by AI to test suite

---

### 4. Fix and Retest

Iterate until all tests pass and metrics meet baselines.

### 5. Update Feature Status (MANDATORY)

**⚠️ CRITICAL: This step is NON-OPTIONAL. Execute AFTER all test results are collected.**

**Status Mapping**:
| Condition | Status |
|-----------|--------|
| All tests pass AND coverage ≥80% | "pass" |
| Any test fails OR coverage <80% | "fail" |

**Step 1: Identify tested tasks**
Read completed tasks from tasks.json that need status update:
```bash
cat .ultra/tasks/tasks.json | jq '.tasks[] | select(.status == "completed")'
```

**Step 2: Read existing feature status**
```bash
cat .ultra/docs/feature-status.json
```

**Step 3: Update each task's feature status** (execute, not just describe)
For each completed task:
1. Find entry in feature-status.json by taskId
2. If found → Update existing entry:
   - `status`: "pass" or "fail" (based on test results)
   - `testedAt`: current ISO timestamp
   - `coverage`: percentage from test run
   - `coreWebVitals`: {lcp, inp, cls} (frontend only)
3. If NOT found → Create new entry with test results

**Step 4: Write updated feature-status.json**

**Step 5: Verify update succeeded**
```bash
cat .ultra/docs/feature-status.json | grep "testedAt"
# Must show updated timestamps
```

**Output Format** (Chinese at runtime):
```
Test completion message including:
   - Feature status updates: feat-{id} ({name}): pass/fail (coverage: X%)
   - Test summary: Unit tests X/Y passed, E2E tests X/Y passed
   - Total coverage: X%
   - Core Web Vitals: LCP, INP, CLS values
   - Issues to fix (if any): Coverage below 80%
```

**Failure Handling**:
If feature-status.json update fails:
1. Display warning (Chinese at runtime)
2. Log error to .ultra/docs/status-sync.log
3. Continue with test report (do NOT block)
4. syncing-status Skill will auto-fix on next trigger

**Benefits**:
- Track pass/fail status per feature
- Historical verification records
- Commit traceability for debugging

## Quality Gates (All Must Pass)

### Test Authenticity (NEW - Mandatory)
- ✅ **TAS ≥70%** for ALL test files (Grade A/B pass)
- ✅ **No tautologies** (`expect(true).toBe(true)` = instant fail)
- ✅ **No empty tests** (test body must have assertions)
- ✅ **Mock ratio ≤50%** (internal modules should NOT be mocked)

### Coverage & Execution
- ✅ Unit coverage ≥80%
- ✅ All E2E tests pass
- ✅ All 6 dimensions covered (Functional, Boundary, Exception, Performance, Security, Compatibility)

### Frontend Only (Core Web Vitals)
- ✅ LCP (Largest Contentful Paint) <2.5s
- ✅ INP (Interaction to Next Paint) <200ms
- ✅ CLS (Cumulative Layout Shift) <0.1

### Security
- ✅ No critical security issues

**References**:
- `@guidelines/ultra-quality-standards.md` - Detailed requirements
- `@guidelines/ultra-testing-philosophy.md` - Anti-pattern examples

## Integration

- **Skills**:
  - **guarding-test-quality** (TAS analysis, anti-pattern detection)
  - **codex-test-gen** (Codex test generation and review)
  - guarding-quality (six-dimensional coverage enforcement)
  - automating-e2e-tests (E2E testing, auto-activates on keywords)
- **Dual-Engine**: Claude Code (test design) + Codex (test generation/review)
- **Next**: `/ultra-deliver` for deployment prep

## Output Format

**Standard output structure**: See `@config/ultra-command-output-template.md` for the complete 6-section format.

**Command icon**: 🧪

**Example output**: See template Section 7.5 for ultra-test specific example.

## References

- @guidelines/ultra-quality-standards.md - Complete testing standards
- @config/ultra-mcp-guide.md - Testing tools and strategy guide
