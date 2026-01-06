---
description: Agile development execution with TDD workflow
argument-hint: [task-id]
allowed-tools: Read, Write, Edit, Bash, TodoWrite, Grep, Glob, Task, AskUserQuestion
---

# /ultra-dev

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
5. **Update status to `in_progress`**:
   - tasks.json: `status: "in_progress"`
   - context file: Change header `> **Status**: in_progress`
6. Create todos from Acceptance section

### Step 2: Environment Setup

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

### Step 4.5: PR Review Toolkit (Mandatory)

**When**: After Quality Gates pass, before commit.

**Process**:

#### Phase 1: Comprehensive Review (parallel)

Run these agents in parallel using Task tool:

| Agent | Focus |
|-------|-------|
| `pr-review-toolkit:code-reviewer` | Bugs, logic errors, security, code quality |
| `pr-review-toolkit:silent-failure-hunter` | Silent failures, inadequate error handling |
| `pr-review-toolkit:pr-test-analyzer` | Test coverage gaps, missing edge cases |
| `pr-review-toolkit:type-design-analyzer` | Type design, encapsulation, invariants |
| `pr-review-toolkit:comment-analyzer` | Comment accuracy, technical debt |

#### Phase 2: Fix Issues

- **If issues found** → Fix all issues, re-run tests
- **If tests fail after fix** → Return to GREEN phase
- **Repeat Phase 1** until all agents pass

#### Phase 3: Code Optimization

After all reviews pass:

1. Run `pr-review-toolkit:code-simplifier` agent
2. Apply simplification suggestions
3. Verify tests still pass
4. **If "PASS"** → Continue to Step 5

**Blocking Behavior**: Cannot commit until all PR Review agents pass.

### Step 5: Commit and Update

> **Prerequisite**: Step 4 Quality Gates + Step 4.5 PR Review all passed

1. **Update status to `completed`** (before commit):
   - tasks.json: `status: "completed"`
   - context file header: `> **Status**: completed`
   - context file Completion section (date + summary, hash later):
     ```markdown
     ## Completion
     - **Completed**: {today's date}
     - **Commit**: _pending_
     - **Summary**: {what was delivered}
     ```

2. **Commit & Merge** (single confirmation):
   - Run `git status` to show staged/unstaged changes
   - Use `AskUserQuestion` with options:
     - Option A: "Commit + Merge to main" (recommended) → full flow
     - Option B: "Commit only, create PR later" → commit but skip merge
     - Option C: "Review diff first" → show `git diff --stat` then ask again

   **If user approves commit**:
   ```bash
   git add -A
   git commit -m "feat(scope): description"
   ```

3. **Record commit hash**:
   - `git rev-parse HEAD` → update context file
   - `git commit --amend --no-edit`

4. **Sync with main**:
   ```bash
   git fetch origin && git rebase origin/main
   ```
   - If conflicts → resolve → `git rebase --continue`

5. **Verify after rebase**:
   - Run tests again
   - If fail → fix → amend → repeat step 4-5

6. **Merge to main** (if user chose Option A):
   ```bash
   git checkout main && git pull origin main
   git merge --no-ff feat/task-{id}-{slug}
   git push origin main && git branch -d feat/task-{id}-{slug}
   ```

### Step 6: Report

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
