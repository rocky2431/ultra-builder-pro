---
description: Agile development execution with TDD workflow
argument-hint: [task-id]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task, AskUserQuestion, Skill
model: opus
---

# /ultra-dev

## Workflow Tracking (MANDATORY)

**On command start**, create tasks for each major step using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 1 | Task Selection | Selecting task... |
| 1.5 | Update Status to In-Progress | Updating task status... |
| 2 | Environment Setup | Setting up environment... |
| 3 | TDD Cycle | Running TDD cycle... |
| 3.1 | TDD: RED Phase | Writing failing tests... |
| 3.2 | TDD: GREEN Phase | Writing minimal code... |
| 3.3 | TDD: REFACTOR Phase | Refactoring code... |
| 4 | Quality Gates | Running quality gates... |
| 4.5 | Ultra Review | Running ultra-review... |
| 5 | Update Status to Completed | Updating task status... |
| 5.5 | Pre-Commit Checklist | Verifying checklist... |
| 6 | Commit and Merge | Committing and merging... |
| 7 | Report | Generating report... |

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**On context recovery**: `TaskList` → resume from last incomplete step

---

Execute development tasks using TDD workflow.

## Arguments

- `$1`: Task ID (if empty, auto-select next pending task)

---

## Workflow

### Step 1: Task Selection

1. Read `.ultra/tasks/tasks.json`
2. Select task:
   - If task ID provided → select that task
   - Otherwise → select first task with `status: "pending"`
3. Read context file: `.ultra/tasks/contexts/task-{id}.md`
4. Display task context
5. Create todos from Acceptance section

### Step 1.5: Update Status to In-Progress (MANDATORY)

**CRITICAL**: BOTH files MUST be updated. Do not proceed until verified.

**1. Update `.ultra/tasks/tasks.json`**:
```json
{ "id": {id}, "status": "in_progress", ... }
```

**2. Update `.ultra/tasks/contexts/task-{id}.md`**:

Find and change the status header line:
```markdown
> **Status**: in_progress
```

**3. Verify BOTH updates**:
- Read tasks.json → confirm `"status": "in_progress"`
- Read context file → confirm header shows `in_progress`
- **If either missing → fix before proceeding**

### Step 2: Environment Setup

**Check for unmerged completed tasks** (recovery from context loss):

1. List all local feat branches: `git branch --list 'feat/task-*'`
2. For each branch, extract task ID from branch name
3. Check task status in `.ultra/tasks/tasks.json`
4. **If found completed task with unmerged branch**:
   → Use AskUserQuestion:
     - "Merge task-{id} to main first" (Recommended)
     - "Delete branch (already merged or abandoned)"
     - "Skip, continue with new task"

   **If user chooses "Merge first"**:
   ```bash
   git checkout feat/task-{id}-{slug}
   git fetch origin && git rebase origin/main
   # Run tests to verify
   git checkout main && git pull origin main
   git merge --no-ff feat/task-{id}-{slug}
   git push origin main
   git branch -d feat/task-{id}-{slug}
   ```
   Then continue to new task.

**Check git branch**:

1. Get current branch: `git branch --show-current`
2. Define expected branch pattern: `feat/task-{id}-*`

**Decision tree**:

- **If on `main` or `master`**:
  ```bash
  git pull origin main
  git checkout -b feat/task-{id}-{slug}
  ```

- **If on `feat/task-{current-id}-*`** (current task's branch):
  → Continue (resume from checkpoint)

- **If on any other branch**:
  → Use AskUserQuestion:
    - "Switch to main and create new branch" (Recommended)
    - "Continue on current branch"

**Check dependencies** (soft validation):
- If dependency tasks incomplete → Warn but continue
- Parallel development allowed

### Step 3: TDD Cycle

**RED → GREEN → REFACTOR**

**RED Phase**: Write failing tests
- Use Acceptance section from context file as test spec
- Cover test dimensions:
  - Functional: Core feature works
  - Boundary: Edge cases handled
  - Exception: Errors handled gracefully
  - Security: No vulnerabilities
- Tests MUST fail initially
- Run tests to confirm failure

**GREEN Phase**: Write minimum code to pass
- Only enough code to pass tests
- Production-ready (no TODO, no placeholder)
- Run tests to confirm pass

**REFACTOR Phase**: Improve quality
- Apply SOLID, DRY, KISS, YAGNI
- Tests must still pass

### Step 4: Quality Gates

**Before marking complete**:

| Gate | Requirement |
|------|-------------|
| Tests pass | All tests green |
| Coverage | ≥80% (project standard) |
| No mocks on core logic | Domain/service/state paths use real deps |
| No degradation | No fallback or demo code |

**Test double policy**:
- ❌ Core logic (domain/service/state) → NO mocking
- ✅ External systems → testcontainers/sandbox/stub allowed

### Step 4.5: Ultra Review (Mandatory)

**When**: After Quality Gates pass, before commit.

**Process**:

#### Phase 1: Run /ultra-review

Execute the ultra-review skill in `all` mode (force all 6 agents, no auto-skip):

```
/ultra-review all
```

This automatically:
1. Launches 6 specialized review agents in parallel (review-code, review-tests, review-errors, review-types, review-comments, review-simplify)
2. Aggregates and deduplicates findings via review-coordinator
3. Generates SUMMARY.json with verdict (APPROVE / COMMENT / REQUEST_CHANGES)
4. Reports top findings to conversation

#### Phase 2: Act on Verdict

| Verdict | Action |
|---------|--------|
| **APPROVE** | Proceed to Step 5 |
| **COMMENT** | Review P1 findings, fix if warranted, then proceed |
| **REQUEST_CHANGES** | Fix ALL P0 issues (mandatory) and P1 issues, re-run tests |

- **If tests fail after fix** → Return to GREEN phase
- **After fixing** → Run `/ultra-review recheck` to verify P0/P1 resolved
- **Repeat** until verdict is APPROVE or COMMENT with acceptable P1 count

#### Phase 3: Verification (BLOCKING)

**Before proceeding to Step 5**:

- [ ] SUMMARY.json verdict is NOT `REQUEST_CHANGES`
- [ ] All P0 issues resolved
- [ ] Tests still passing

**Note**: `pre_stop_check.py` hook will also block session stop if unresolved P0s exist.

### Step 5: Update Status to Completed (MANDATORY)

> **Prerequisite**: Step 4 Quality Gates + Step 4.5 Ultra Review all passed

**CRITICAL**: BOTH files MUST be updated BEFORE commit. Do not proceed until verified.

**1. Update `.ultra/tasks/tasks.json`**:
```json
{ "id": {id}, "status": "completed", ... }
```

**2. Update `.ultra/tasks/contexts/task-{id}.md`**:

Update the status header line:
```markdown
> **Status**: completed
```

Add or update the Completion section at the end of the file:
```markdown
## Completion
- **Completed**: {today's date, e.g., 2026-01-28}
- **Commit**: _pending_ (will update after commit)
- **Summary**: {brief description of what was delivered}
```

**3. Verify BOTH updates**:
- Read tasks.json → confirm `"status": "completed"`
- Read context file → confirm header shows `completed`
- Read context file → confirm Completion section exists
- **If any missing → fix before proceeding**

### Step 5.5: Pre-Commit Checklist (BLOCKING)

**Before `git commit`, verify ALL items**:

- [ ] tasks.json: status = "completed"
- [ ] context file: header = "completed"
- [ ] context file: Completion section exists
- [ ] All tests passing
- [ ] Ultra Review verdict is NOT `REQUEST_CHANGES`

**If any unchecked → fix first, do NOT commit**

### Step 6: Commit and Merge

**1. Confirm with user**:
- Run `git status` to show staged/unstaged changes
- Use `AskUserQuestion` with options:
  - Option A: "Commit + Merge to main" (recommended) → full flow
  - Option B: "Commit only, create PR later" → commit but skip merge
  - Option C: "Review diff first" → show `git diff --stat` then ask again

**2. Create commit** (if user approves):
```bash
git add -A
git commit -m "feat(scope): description"
```

**3. Record commit hash in context file**:
- Run `git rev-parse HEAD` to get hash
- Update context file Completion section:
  ```markdown
  - **Commit**: {actual hash}
  ```
- Amend commit to include this update:
  ```bash
  git add .ultra/tasks/contexts/task-{id}.md
  git commit --amend --no-edit
  ```

**4. Sync with main**:
```bash
git fetch origin && git rebase origin/main
```
- If conflicts → resolve → `git rebase --continue`

**5. Verify after rebase**:
- Run tests again
- If fail → fix → amend → repeat step 4-5

**6. Merge to main** (if user chose Option A):
```bash
git checkout main && git pull origin main
git merge --no-ff feat/task-{id}-{slug}
git push origin main && git branch -d feat/task-{id}-{slug}
```

### Step 7: Report

Output:
- Commit hash
- Project progress (completed/total)
- Next task suggestion

---

## Dual-Write Mode

**Trigger**: When implementation reveals spec gaps or requirement changes.

**Examples**:
- API signature differs from spec
- New edge case discovered
- Constraint changed

**Process**:

1. **Update specs immediately** (`.ultra/specs/product.md` or `architecture.md`)
   - Keep specifications current for parallel tasks

2. **Record change in context file** Change Log:
   ```markdown
   | {date} | {change description} | specs/{file}#{section} | {reason} |
   ```

**Key principle**: `specs/` is source of truth, `contexts/` tracks implementation history.

---

## Integration

- **Input**:
  - `.ultra/tasks/tasks.json` (task registry)
  - `.ultra/tasks/contexts/task-{id}.md` (implementation context)
- **Output**:
  - `.ultra/tasks/tasks.json` (status update)
  - `.ultra/tasks/contexts/task-{id}.md` (updated context with change log)
- **Next**: `/ultra-test` or `/ultra-dev [next-task-id]`

## Usage

```bash
/ultra-dev          # Auto-select next pending task
/ultra-dev 3        # Work on task #3
```
