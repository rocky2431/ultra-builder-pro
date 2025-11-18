---
name: guarding-test-coverage
description: "Ensures 6-dimensional test coverage (Functional, Boundary, Exception, Performance, Security, Compatibility). TRIGGERS: Running /ultra-test, executing test commands (npm test, pytest, go test), marking tasks complete, discussing test coverage or gaps. CHECKS: Overall ≥80%, critical paths 100%, branch ≥75%. DO NOT TRIGGER: For documentation updates, config changes without code, read-only file operations."
allowed-tools: Read, Bash, Grep, Glob
---

# Test Strategy Guardian

## Purpose
Verify six-dimensional test coverage before completion.

## Configuration

**Load from `.ultra/config.json`**:
```json
{
  "quality_gates": {
    "test_coverage": {
      "overall": 0.80,
      "critical_paths": 1.00,
      "branch": 0.75,
      "function": 0.85
    }
  }
}
```

**Loading config in runtime** (TypeScript example):
```typescript
// Load config from project
const configPath = '.ultra/config.json';
const config = JSON.parse(await Read(configPath));

// Extract test coverage thresholds
const overallThreshold = config.quality_gates.test_coverage.overall;          // 0.80 (80%)
const criticalThreshold = config.quality_gates.test_coverage.critical_paths;  // 1.00 (100%)
const branchThreshold = config.quality_gates.test_coverage.branch;            // 0.75 (75%)
const functionThreshold = config.quality_gates.test_coverage.function;        // 0.85 (85%)

// Use in coverage validation
if (actualCoverage < overallThreshold) {
  // BLOCK: Coverage insufficient
}
```

## When
- Running /ultra-test or marking features complete
- Discussing test coverage
- Before merging to main

## Do
- Map existing tests to 6 dimensions
- Identify coverage gaps
- Recommend test types (unit/integration/E2E)
- Verify overall coverage meets {overall * 100}% threshold (from config)
- Check critical paths meet {critical_paths * 100}% threshold
- Verify branch coverage meets {branch * 100}% threshold

## Six Dimensions Required
1. Functional - Core features work correctly
2. Boundary - Edge cases (empty, max values, special chars)
3. Exception - Error handling (network failures, timeouts)
4. Performance - Response time, memory, no leaks
5. Security - XSS, SQL injection, auth checks
6. Compatibility - Cross-browser, mobile, platforms

**Details**: See `guidelines/quality-standards.md#six-dimensional-test-coverage`

## Don't
- Do not block execution, provide clear next steps
- Do not require 100% coverage for non-critical code

## Outputs
- Coverage summary with gaps identified
- Test recommendations by dimension
- Language: Chinese (simplified) at runtime
