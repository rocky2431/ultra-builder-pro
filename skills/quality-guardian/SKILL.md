---
name: quality-guardian
description: "Code quality, test coverage, and UI design enforcement. TRIGGERS when editing code/UI files (*.ts, *.js, *.tsx, *.jsx, *.py, *.vue, *.css, *.scss), discussing quality/refactoring/testing/coverage, or running tests. Loads detailed guidelines on-demand."
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

**Output** (Chinese):
```
⚠️ 代码质量问题：
1. getUserById() 超过 50 行（78 行）→ 拆分
2. 重复代码 3 处 → 提取 handleApiError()
参考：REFERENCE.md (Part 1: SOLID Principles)
```

### 2. Test Coverage Validation

**Load**: `REFERENCE.md` (Part 2: Testing Quality Baseline) when testing

**Enforce 6 Dimensions**:
1. Functional, 2. Boundary, 3. Exception, 4. Performance, 5. Security, 6. Compatibility

**Requirements**: Overall ≥80%, Critical paths 100%, Branch ≥75%

**Output** (Chinese):
```
⚠️ 测试覆盖率不足（73%，目标 ≥80%）：
缺失: Performance 测试、Security SQL 注入验证
参考：REFERENCE.md (Part 2: Testing Quality Baseline)
```

### 3. UI Design Constraints

**Load**: `REFERENCE.md` (Part 2: Frontend Quality Baseline) when editing UI

**Enforced**:
- ❌ Default fonts (Inter, Roboto, Open Sans)
- ❌ Hard-coded colors → Use design tokens

**Suggested**:
- ✅ Typography: 3x+ size jumps
- ✅ Component libraries: MUI, Ant Design, Chakra

**Output** (Chinese):
```
⚠️ UI 设计约束：
1. 硬编码颜色 '#3b82f6' → theme.colors.primary
2. 默认字体 'Inter' → 使用自定义字体
参考：REFERENCE.md (Part 2: Frontend Quality Baseline)
```

## Don't

- ❌ Trigger for git operations
- ❌ Trigger for documentation-only changes

## Outputs

Format (Chinese): ⚠️ + brief summary + actionable recommendations + guideline reference

---

**Token Efficiency**: ~200 tokens (vs 450 for 3 separate Skills). Loads guidelines on-demand.
