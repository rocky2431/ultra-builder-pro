---
description: Release preparation (documentation + build + version + publish)
argument-hint: [version-type]
allowed-tools: TodoWrite, Task, Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
model: opus
---

# /ultra-deliver

Prepare release after `/ultra-test` passes: update documentation, build, bump version, tag, and push.

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
1. Use `AskUserQuestion` to confirm:
   - Option A: "Auto-commit all changes" → commit with `chore: pre-delivery cleanup`
   - Option B: "Review changes first" → show `git diff --stat` and ask again
   - Option C: "Block delivery" → stop and let user handle manually
2. If user approves commit but it fails (conflicts, etc.) → block and report

---

## Delivery Workflow

### Step 1: Documentation Update

**CHANGELOG.md**:
1. Run `git log --oneline` since last release tag
2. Categorize by Conventional Commit prefix (feat→Added, fix→Fixed, etc.)
3. Update CHANGELOG.md with new version section

**Technical Debt** (optional):
1. Use Grep to find TODO/FIXME/HACK markers
2. Generate `.ultra/docs/technical-debt.md`

**README** (if API changed):
1. Update usage examples to reflect changes

### Step 2: Production Build

Detect build command by priority:
1. `package.json` → `scripts.build` → run `npm run build` or `pnpm build`
2. `Makefile` → run `make build` or `make release`
3. `Cargo.toml` → run `cargo build --release`
4. `go.mod` → run `go build ./...`
5. None found → use `AskUserQuestion` to ask user for build command

**Build validation**:
- Exit code 0 → proceed
- Exit code non-zero → block with error output, ask user how to proceed

### Step 3: Version & Release

1. Determine version bump (patch/minor/major) based on commits
2. Update version using project's version management method
3. Commit: `chore(release): vX.X.X`
4. Create git tag: `vX.X.X`
5. Push to remote:
   ```bash
   git push origin main   # release commit
   git push origin vX.X.X # version tag
   ```

### Step 4: Persist Results

Update `.ultra/delivery-report.json` with actual values:

```json
{
  "timestamp": "2025-01-01T04:00:00Z",
  "version": "1.2.0",
  "git_tag": "v1.2.0",
  "git_commit": "abc123",
  "changelog_updated": true,
  "build_success": true,
  "pushed": true
}
```

---

## Deliverables Checklist

- [ ] `/ultra-test` passed (verified via test-report.json)
- [ ] Uncommitted changes auto-committed
- [ ] Documentation updated (CHANGELOG)
- [ ] Production build successful
- [ ] Version bumped, tagged, pushed
- [ ] delivery-report.json written

---

## Integration

- **Prerequisites**: `/ultra-test` must pass first
- **Input**: `.ultra/test-report.json`
- **Output**: `.ultra/delivery-report.json`
- **Next**: Deploy or announce release

**Workflow**:
```
/ultra-dev (tasks) → /ultra-test (audit) → /ultra-deliver (release)
```

## Output Format

> Claude responds in Chinese per CLAUDE.md.

**Command icon**: 📦
