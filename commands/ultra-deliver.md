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
- Report: "❌ Tests failed: {pass_count}/{total_count}"
- Block delivery

### Validation 2: No Uncommitted Changes

Run `git status` and verify working directory is clean.

If unclean:
- Report: "⚠️ Uncommitted changes exist"
- Ask user to commit or stash

### Validation 3: Specs Up-to-Date

Verify specs/ reflects current state (Dual-Write Mode ensures this during development).

Check `.ultra/tasks/contexts/task-*.md` Change Log sections for any untracked spec updates.

If inconsistency found:
- Report: "⚠️ Context files reference spec changes not reflected in specs/"
- List affected sections
- Ask user to verify

---

## Delivery Workflow

### Step 1: Performance Optimization

Delegate to ultra-performance-agent:

```
Task(subagent_type="ultra-performance-agent",
     prompt="Analyze and optimize performance. Focus on Core Web Vitals (LCP<2.5s, INP<200ms, CLS<0.1) and bottleneck identification.")
```

### Step 2: Security Audit

Run `npm audit` and review results. For high/critical issues, apply fixes or document exceptions.

### Step 3: Documentation Update

**Step 3.1: Draft Documentation**

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

**Step 3.2: Review Documentation**

Check for:
1. Technical accuracy (code examples work)
2. Completeness (all APIs documented)
3. Clarity (no ambiguity)
4. Practical examples

**Step 3.3: Enhance Documentation**

Add:
1. More code examples (covering edge cases)
2. FAQ section (common questions)
3. Best practices
4. Troubleshooting guide
5. Migration notes (if applicable)

**Step 3.4: Final Review**

- Ensure consistent style and tone
- Verify accuracy
- Final approval before commit

### Step 4: Final Quality Check

1. Run full test suite: `npm test`
2. Build production: `npm run build`
3. Verify build succeeds

### Step 5: Prepare Release

1. Determine version bump (patch/minor/major)
2. Update version: `npm version {type}`
3. Report release readiness

### Step 6: Update Project Context

**Update CLAUDE.md**:
- Add release version to project overview
- Clear "Current Focus" (all tasks completed)
- Update any changed development rules

---

## Deliverables Checklist

- [ ] All tests pass (coverage ≥80%)
- [ ] Performance optimized (Core Web Vitals pass)
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] Specs up-to-date (Dual-Write verified)
- [ ] Production build successful
- [ ] CLAUDE.md updated with release info

---

## Integration

- **Agents**: ultra-performance-agent for optimization
- **Next**: Deploy or create release PR

## Output Format

Display delivery report in Chinese including:
- Merge status
- Performance scores
- Security audit results
- Documentation updates
- Release readiness
