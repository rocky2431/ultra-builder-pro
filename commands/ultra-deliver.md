---
description: Delivery optimization (performance + security + documentation)
argument-hint: [version-type]
allowed-tools: TodoWrite, Task, Read, Write, Edit, Bash, Grep, Glob
---

# /ultra-deliver

Prepare for delivery with performance optimization, security audit, and documentation updates.

---

## Pre-Delivery Validations

**Before proceeding, you MUST verify these conditions. If any fails, report and block.**

### Validation 1: All Tests Pass

Run `npm test` and verify exit code is 0 with coverage ≥80%.

If failed:
- Report: "❌ 测试未通过：{pass_count}/{total_count}"
- Block delivery

### Validation 2: No Uncommitted Changes

Run `git status` and verify working directory is clean.

If unclean:
- Report: "⚠️ 存在未提交的更改"
- Ask user to commit or stash

### Validation 3: Pending Changes Merged

Check if `.ultra/changes/` has unmerged proposals for completed tasks.

If found:
- List pending proposals
- Execute OpenSpec Merge (Step 1) first

---

## Delivery Workflow

### Step 1: OpenSpec Merge

**Purpose**: Merge completed feature proposals to main specs.

**Process**:
1. List directories in `.ultra/changes/task-*`
2. For each, read the task ID and check if task status is "completed" in tasks.json
3. If completed:
   - Read proposal.md for spec changes documented during development
   - Apply relevant changes to main specs (.ultra/specs/product.md, .ultra/specs/architecture.md)
   - Verify proposal.md has `## Status: Completed` section
4. Mark as processed (no separate archive - completion tracked in proposal.md)

**Output** (Chinese):
```
📋 OpenSpec 合并报告
====================
已处理：{count} 个变更提案
已合并到主规范：{merged_list}
```

### Step 2: Performance Optimization

Delegate to ultra-performance-agent:

```
Task(subagent_type="ultra-performance-agent",
     prompt="Analyze and optimize performance. Focus on Core Web Vitals (LCP<2.5s, INP<200ms, CLS<0.1) and bottleneck identification.")
```

### Step 3: Security Audit

Run `npm audit` and review results. For high/critical issues, apply fixes or document exceptions.

### Step 4: Documentation Update

**Step 4.1: Draft Documentation**

**CHANGELOG.md**:
1. Run `git log --oneline` since last release tag
2. Categorize by Conventional Commit prefix (feat→Added, fix→Fixed, etc.)
3. Update CHANGELOG.md with new version section

**Technical Debt**:
1. Use Grep to find TODO/FIXME/HACK markers in code
2. Generate `.ultra/docs/technical-debt.md` with categorized items

**API Documentation / README updates**:
1. Draft based on code changes
2. Include basic usage examples

**Step 4.2: Review Documentation**

Check for:
1. Technical accuracy (code examples work)
2. Completeness (all APIs documented)
3. Clarity (no ambiguity)
4. Practical examples

**Step 4.3: Enhance Documentation**

Add:
1. More code examples (covering edge cases)
2. FAQ section (common questions)
3. Best practices
4. Troubleshooting guide
5. Migration notes (if applicable)

**Step 4.4: Final Review**

- Ensure consistent style and tone
- Verify accuracy
- Final approval before commit

### Step 5: Final Quality Check

1. Run full test suite: `npm test`
2. Build production: `npm run build`
3. Verify build succeeds

### Step 6: Prepare Release

1. Determine version bump (patch/minor/major)
2. Update version: `npm version {type}`
3. Report release readiness

### Step 7: Update Project Context

**Update CLAUDE.md** (via syncing-docs):
- Add release version to project overview
- Clear "Current Focus" (all tasks completed)
- Update any changed development rules

**Update feature-status.json** (via syncing-status):
- Mark all features as released
- Add release version to metadata

---

## Deliverables Checklist

- [ ] All tests pass (coverage ≥80%)
- [ ] Performance optimized (Core Web Vitals pass)
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] Specs merged from changes/
- [ ] Production build successful
- [ ] CLAUDE.md updated with release info
- [ ] feature-status.json marked as released

---

## Integration

- **Agents**: ultra-performance-agent for optimization
- **Skills**: syncing-docs, syncing-status
- **Next**: Deploy or create release PR

## Output Format

Display delivery report in Chinese including:
- Merge status
- Performance scores
- Security audit results
- Documentation updates
- Release readiness
