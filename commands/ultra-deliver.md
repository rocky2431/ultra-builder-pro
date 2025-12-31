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

### Validation 1: /ultra-test Passed

Read `.ultra/test-report.json` and verify:
- File exists (if not: "❌ Run /ultra-test first")
- `passed` is `true` (if not: show `blocking_issues` and block)
- `git_commit` matches current HEAD (if not: "⚠️ Code changed since last test, re-run /ultra-test")

If validation fails, block delivery.

### Validation 2: No Uncommitted Changes

Run `git status` and verify working directory is clean.

If unclean:
- Report: "⚠️ Uncommitted changes exist"
- Ask user to commit or stash

### Validation 3: Specs Up-to-Date

Run `git diff .ultra/specs/` to check for uncommitted spec changes.

If changes found:
- Report: "⚠️ Uncommitted spec changes"
- Ask user to commit or discard

---

## Delivery Workflow

### Step 1: Performance Optimization

Delegate to ultra-performance-agent:

```
Task(subagent_type="ultra-performance-agent",
     prompt="Analyze and optimize performance. Focus on Core Web Vitals (LCP<2.5s, INP<200ms, CLS<0.1) and bottleneck identification.")
```

### Step 2: Verify Security

Security results already in `.ultra/test-report.json` (validated in Pre-Delivery).

If `git_commit` mismatch detected, Validation 1 already blocked.

### Step 3: Documentation Update

**CHANGELOG.md**:
1. Run `git log --oneline` since last release tag
2. Categorize by Conventional Commit prefix (feat→Added, fix→Fixed, etc.)
3. Update CHANGELOG.md with new version section

**Technical Debt** (optional):
1. Use Grep to find TODO/FIXME/HACK markers
2. Generate `.ultra/docs/technical-debt.md`

**README** (if API changed):
1. Update usage examples to reflect changes

### Step 4: Production Build

Detect and run production build command from project config.

Verify build succeeds before proceeding.

### Step 5: Prepare Release

1. Determine version bump (patch/minor/major) based on commits
2. Update version using project's version management method
3. Report release readiness

---

## Deliverables Checklist

- [ ] `/ultra-test` passed (Anti-Pattern, Coverage, E2E, Perf, Security)
- [ ] No uncommitted changes
- [ ] Specs up-to-date (Dual-Write verified)
- [ ] Documentation updated (CHANGELOG, README)
- [ ] Production build successful
- [ ] Version bumped

---

## Integration

- **Prerequisites**: `/ultra-test` must pass first
- **Agents**: ultra-performance-agent for optimization
- **Next**: Deploy or create release PR

**Workflow**:
```
/ultra-dev (tasks) → /ultra-test (audit) → /ultra-deliver (release)
```

## Output Format

Display delivery report in Chinese including:
- Merge status
- Performance scores
- Security audit results
- Documentation updates
- Release readiness
