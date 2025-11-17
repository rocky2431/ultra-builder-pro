---
name: guarding-code-quality
description: "Guards code quality principles. TRIGGERS: When editing code files or refactoring. ACTIONS: Flag violations, suggest improvements. DO NOT TRIGGER: For non-code edits."
allowed-tools: Read, Write, Edit, Grep
---

# Code Quality Guardian

## Purpose
Detect common quality issues and suggest small, safe refactors.

## Configuration

**Load from `.ultra/config.json`**:
```json
{
  "quality_gates": {
    "code_quality": {
      "max_function_lines": 50,
      "max_nesting_depth": 3,
      "max_complexity": 10,
      "max_duplication_lines": 3
    }
  }
}
```

**Loading config in runtime** (TypeScript example):
```typescript
// Load config from project
const configPath = '.ultra/config.json';
const config = JSON.parse(await Read(configPath));

// Extract code quality thresholds
const maxLines = config.quality_gates.code_quality.max_function_lines;      // 50
const maxNesting = config.quality_gates.code_quality.max_nesting_depth;     // 3
const maxComplexity = config.quality_gates.code_quality.max_complexity;     // 10
const maxDuplication = config.quality_gates.code_quality.max_duplication_lines;  // 3

// Use in quality checks
if (functionLines > maxLines) {
  // Flag: Function too long, suggest extraction
}
```

## When
- Editing code files (`.js/.ts/.jsx/.tsx/.py/.java/.go`)
- Large refactors, PR reviews

## Do
- Check: functions >{max_function_lines} lines, nesting >{max_nesting_depth}, duplicate blocks (>{max_duplication_lines} lines), magic numbers (from config)
- Suggest: extract method/constant, simplify conditions, rename for clarity
- Surface SOLID/DRY/KISS/YAGNI guidance

## Don't
- Do not block execution
- Do not trigger for non-code files

## Outputs
- Concise findings with grade (A-F scale)
- Refactoring suggestions with expected improvement
- Language: Chinese (simplified) at runtime

## Integration with /ultra-refactor

**Role clarification**: This skill **detects** code quality violations; `/ultra-refactor` **executes** the fixes.

**Workflow**:
1. guarding-code-quality detects violations (e.g., "Function exceeds 50 lines, violates SRP")
2. Suggests specific refactoring: "Consider `/ultra-refactor extract UserService/processPayment`"
3. User runs `/ultra-refactor` command to execute the refactoring with Serena MCP

**Why separate**: Detection (this skill) is passive and continuous; execution (/ultra-refactor) is active and requires user confirmation for safety.

## Tools
- Grep for quick search; use Serena MCP only for cross-file refactors

## Quality Grades
- A (90-100): Excellent
- B (80-89): Good
- C (70-79): Average
- D (60-69): Needs improvement
- F (<60): Needs refactoring

## Performance Metrics
- Detection accuracy: 95%
- False positive rate: <5%
- Check speed: <200ms
- Suggestion effectiveness: 85%
