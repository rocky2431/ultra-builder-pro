---
description: Release preparation (documentation + build + version + publish)
argument-hint: [version-type]
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
model: opus
---

# /ultra-deliver

## Workflow Tracking (MANDATORY)

**On command start**, create tasks for each major step using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 0.1 | Validate /ultra-test Passed | Validating test results... |
| 0.2 | Check Uncommitted Changes | Checking git status... |
| 1 | Documentation Update | Updating documentation... |
| 1.1 | Update CHANGELOG.md | Updating changelog... |
| 1.2 | Generate Technical Debt Report | Generating debt report... |
| 1.3 | Update README.md | Updating readme... |
| 2 | Production Build | Building for production... |
| 3 | Version & Release | Bumping version and tagging... |
| 4 | Persist Results | Persisting delivery report... |

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**On context recovery**: `TaskList` → resume from last incomplete step

---

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

### Step 1: Documentation Update (MANDATORY)

**CRITICAL**: All applicable documentation MUST be updated. Verify each item.

**1.1 CHANGELOG.md** (REQUIRED):
1. Run `git log --oneline` since last release tag
2. Categorize by Conventional Commit prefix (feat→Added, fix→Fixed, etc.)
3. Update CHANGELOG.md with new version section
4. **Verify**: Read CHANGELOG.md → confirm new version section exists

**1.2 Technical Debt Report** (REQUIRED):
1. Use Grep to find TODO/FIXME/HACK markers in source code
2. Generate or update `.ultra/docs/technical-debt.md`
3. **Verify**: Read technical-debt.md → confirm it reflects current state

**1.3 README.md** (if API changed):
1. Check if any public API signatures changed in this release
2. If changed → Update usage examples to reflect changes
3. **Verify**: Read README.md → confirm examples match current API

**1.4 Documentation Checklist**:
- [ ] CHANGELOG.md updated with new version
- [ ] technical-debt.md generated/updated
- [ ] README.md updated (if API changed)

**If any required item unchecked → fix before proceeding**

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

### Step 3: Version & Release (MANDATORY)

**CRITICAL**: All 5 sub-steps MUST complete successfully. Verify after each step.

**3.1 Determine version bump**:
- Analyze commits since last tag
- patch: bug fixes only
- minor: new features (backward compatible)
- major: breaking changes
- **Output**: Display determined version (e.g., "1.2.0 → 1.3.0")

**3.2 Update version in project files**:
- package.json, Cargo.toml, pyproject.toml, etc.
- **Verify**: Read version file → confirm version updated

**3.3 Create release commit**:
```bash
git add -A
git commit -m "chore(release): vX.X.X"
```
- **Verify**: `git log -1 --oneline` → confirm commit message

**3.4 Create git tag**:
```bash
git tag vX.X.X
```
- **Verify**: `git tag -l "vX.X.X"` → confirm tag exists

**3.5 Push to remote**:
```bash
git push origin main      # release commit
git push origin vX.X.X    # version tag
```
- **Verify**: `git ls-remote --tags origin | grep vX.X.X` → confirm tag pushed

**3.6 Release Checklist**:
- [ ] Version determined and displayed
- [ ] Version file updated
- [ ] Release commit created
- [ ] Git tag created
- [ ] Commit and tag pushed to remote

**If any step fails → stop and report error, do NOT continue**

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
