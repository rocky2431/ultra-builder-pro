---
name: guarding-test-quality
description: "Detects fake/useless tests through static analysis. TRIGGERS when: running /ultra-test, editing test files, marking tasks complete. Keywords: test quality, TAS score, mock ratio, fake tests, assertion count."
allowed-tools: Read, Grep, Glob
---

# Test Quality Guardian

## Purpose

Detect and prevent fake tests that achieve coverage without testing real behavior. Calculates Test Authenticity Score (TAS) to measure test meaningfulness.

## When

**Auto-triggers when**:
- `/ultra-test` execution starts
- Test files modified (`*.test.ts`, `*.spec.ts`, `*.test.js`, `*.spec.js`)
- Task marked complete with tests
- Keywords: "test quality", "TAS score", "mock ratio", "fake tests"

**Do NOT trigger for**:
- Reading test files for understanding
- Documentation-only changes
- Non-test code changes

## Do

### 1. Calculate Test Authenticity Score (TAS)

For each test file, analyze four components:

| Component | Weight | Detection |
|-----------|--------|-----------|
| Mock Ratio | 25% | Internal mocks / total imports |
| Assertion Quality | 35% | Behavioral / total assertions |
| Real Execution | 25% | Real code lines / total lines |
| Pattern Compliance | 15% | 100 - (anti-patterns * 15) |

### 2. Detection Patterns

**Mock Analysis** (Grep patterns):
```
# Internal module mocking (high risk)
jest\.mock\(['"]\.\./
vi\.mock\(['"]\.\./

# Mock function count
jest\.fn\(\)
vi\.fn\(\)

# Factory mock pattern
jest\.mock\([^)]+,\s*\(\)\s*=>
```

**Assertion Analysis**:
```
# Total assertions
expect\(

# Mock-only assertions (problematic)
\.toHaveBeenCalled\(\)(?!With)
\.toHaveBeenCalledTimes\(

# Behavioral assertions (good)
\.toBe\(
\.toEqual\(
\.toContain\(
\.toThrow\(
```

**Anti-Pattern Detection**:
```
# Tautology tests (CRITICAL)
expect\((true|false|1|0)\)\.toBe\((true|false|1|0)\)

# Empty test body (CRITICAL)
it\([^)]+,\s*(async\s*)?\(\)\s*=>\s*\{\s*\}\)

# Skipped tests
it\.skip\(|xit\(|test\.skip\(

# Commented assertions
//\s*expect\(
```

### 3. TAS Calculation

```typescript
function calculateTAS(testFile: string): TASResult {
  const mockRatio = analyzeInternalMocks(testFile);      // 0-100
  const assertionQuality = analyzeAssertions(testFile);  // 0-100
  const realExecution = analyzeRealCode(testFile);       // 0-100
  const patternScore = detectAntiPatterns(testFile);     // 0-100

  const overall =
    mockRatio * 0.25 +
    assertionQuality * 0.35 +
    realExecution * 0.25 +
    patternScore * 0.15;

  return {
    overall,
    grade: getGrade(overall),
    components: { mockRatio, assertionQuality, realExecution, patternScore }
  };
}

function getGrade(score: number): string {
  if (score >= 85) return 'A';
  if (score >= 70) return 'B';
  if (score >= 50) return 'C';
  if (score >= 30) return 'D';
  return 'F';
}
```

### 4. Enforce Quality Gates

| Gate | Threshold | Action |
|------|-----------|--------|
| TAS Score | >= 70% | Pass (Grade A/B) |
| TAS Score | < 70% | **BLOCK** task completion |
| Zero-Assertion Tests | 0 | Pass |
| Critical Anti-Patterns | 0 | Pass |
| Mock Ratio | <= 50% | Pass |

### 5. Generate Report

**Output** (Chinese at runtime):
```
Test Quality Analysis Report

Project TAS: {score}% (Grade: {grade})

Files Analyzed: {count}
- A Grade (85+): {count} files
- B Grade (70-84): {count} files
- C Grade (50-69): {count} files (blocked)
- D/F Grade (<50): {count} files (blocked)

Issues Found:
- {file}: TAS {score}% ({grade})
  - Issue: {description}
  - Recommendation: {fix}

Quality Gate Result: {PASS/BLOCK}
```

## Don't

- Do not trigger for non-test files
- Do not block if only warnings (Grade B)
- Do not count external module mocks as violations
- Do not flag integration tests with real database usage

## Outputs

**Language**: Chinese (simplified) at runtime

**Report Location**: Displayed inline before coverage report

**Blocking Conditions**:
- TAS < 70% on any test file
- Critical anti-patterns detected (tautology, empty tests)
- Zero assertions in test file

---

## Configuration

Thresholds configurable in `.ultra/config.json`:

```json
{
  "testQuality": {
    "minTAS": 70,
    "maxMockRatio": 0.5,
    "minAssertionsPerTest": 1,
    "blockGrade": "C"
  }
}
```

---

## Reference

See `guidelines/ultra-testing-philosophy.md` for:
- Core testing philosophy
- Mock boundary definitions
- 10 anti-pattern examples with fixes

---

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**
