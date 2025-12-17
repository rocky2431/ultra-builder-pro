---
name: guarding-quality
description: "Enforces code quality (SOLID), test coverage, and UI design standards."
allowed-tools: Read, Grep
---

# Quality Guardian

## Purpose

Enforces quality across three dimensions:
1. **Code Quality** - SOLID/DRY/KISS/YAGNI principles
2. **Test Coverage** - 6-dimensional testing strategy
3. **UI Design** - Anti-pattern prevention and design guidance

## When

**Auto-triggers when**:
- Editing code files (*.ts, *.js, *.tsx, *.jsx, *.py, *.go, *.java, *.vue)
- Editing UI files (*.css, *.scss, *.styled.ts)
- Discussing quality, refactoring, testing, coverage
- Running /ultra-test or marking tasks complete

**Do NOT trigger for**:
- Git operations (handled by git-guardian)
- Documentation-only changes
- Trivial formatting

## Do

### 1. Code Quality Check

**Load**: `REFERENCE.md` (Part 1: SOLID Principles) when violations detected

**Check for**:
- ❌ Functions >50 lines → Split
- ❌ Nesting depth >3 → Refactor
- ❌ Duplicate code >3 lines → Extract
- ❌ Magic numbers → Named constants
- ❌ SOLID violations

**Output** (Chinese at runtime):
```
Code quality warning including:
- Specific violations (function name, line count, issue type)
- Actionable fix recommendations
- Reference to REFERENCE.md section
```

### 2. Test Coverage Validation

**Load**: `REFERENCE.md` (Part 2: Testing Quality Baseline) when testing

**Enforce 6 Dimensions**:
1. Functional, 2. Boundary, 3. Exception, 4. Performance, 5. Security, 6. Compatibility

**Requirements**: Overall ≥80%, Critical paths 100%, Branch ≥75%

**⚠️ Test Quality Delegation**:
- Coverage **quantity** (≥80%): Handled HERE
- Coverage **quality** (TAS ≥70%): Delegated to `guarding-test-quality` skill

**Output** (Chinese at runtime):
```
Test coverage warning including:
- Current coverage vs target (e.g., 73% vs ≥80%)
- Missing test dimensions
- Reference to REFERENCE.md section
```

### 3. UI Design Constraints

**Load**: `REFERENCE.md` (Part 2: Frontend Quality Baseline) when editing UI

**Component Libraries** (recommended):
- ✅ shadcn/ui, Galaxy UI, React Bits (primary)
- ❌ Generic Bootstrap, default MUI without customization

**Enforced**:
- ❌ Default fonts (Inter, Roboto, Open Sans, Arial)
- ❌ Hard-coded colors → Use design tokens
- ❌ Purple gradients on white backgrounds
- ❌ Cookie-cutter layouts

**Suggested**:
- ✅ Bold aesthetic direction (minimal/maximal/retro/brutalist...)
- ✅ Distinctive typography, 3x+ size jumps
- ✅ Orchestrated motion, scroll-triggered animations
- ✅ Atmospheric backgrounds (gradients, textures, overlays)

**Output** (Chinese at runtime):
```
UI design constraint warning including:
- Hard-coded values detected → design token alternatives
- Default fonts detected → personalized font recommendations
- Component library suggestions
- Reference to REFERENCE.md section
```

## Don't

- ❌ Trigger for git operations
- ❌ Trigger for documentation-only changes

## Outputs

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

Format: ⚠️ + brief summary + actionable recommendations + guideline reference

---

**Token Efficiency**: ~200 tokens (vs 450 for 3 separate Skills). Loads guidelines on-demand.
