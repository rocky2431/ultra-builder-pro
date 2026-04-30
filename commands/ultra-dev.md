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

### Step 0: Workflow Resume Check (Before Task Selection)

1. Check if `.ultra/workflow-state.json` exists
2. If yes AND branch matches current branch:
   - Display: "Resuming task {id} from Step {step}: {status}"
   - Skip to the step AFTER the last completed checkpoint
   - If review_session exists, skip re-running review
3. If no or branch mismatch: proceed to Step 0.5

### Step 0.5: Design Approval Gate (First Run Only)

**Trigger**: `.ultra/workflow-state.json` does NOT exist (first run, not resume)

1. Check `.ultra/tasks/tasks.json` exists
   - If missing → "No task plan found. Run /ultra-plan first to create task decomposition." → **EXIT**
   - If ANY task has status `completed` or `in_progress` → plan was already approved in a prior run → **skip gate, proceed to Step 1**
2. Read tasks.json, display overview:
   - Total tasks, priority distribution (P0/P1/P2), complexity range
   - Full task list (ID, title, priority, dependencies)
   - Whether Walking Skeleton is Task #1
3. Use **AskUserQuestion** to request confirmation:
   - "Confirm this task breakdown to start implementation?"
   - Option A: "Confirm, start implementation" → Continue to Step 1
   - Option B: "Revise plan first" → Suggest /ultra-plan → **EXIT**
4. On approval, write workflow-state.json:
   ```json
   {"command":"ultra-dev","task_id":0,"branch":"","step":"0.5","status":"design_approved","ts":"ISO8601"}
   ```

**Resume behavior**: When workflow-state.json exists, this gate is skipped (already approved).

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

**Subagent isolation** (complexity ≥ 7):
For tasks with complexity ≥ 7, consider spawning the TDD cycle (Steps 3.1-3.3) as an independent subagent. The subagent reads the task context file, executes TDD, commits, and returns a summary. The main session stays lean for review and commit steps. This is optional and depends on runtime support.

**Mid-TDD compact checkpoint** (complexity ≥ 6):
After GREEN phase completes (Step 3.2), write workflow-state.json checkpoint and consider running `/compact` if context feels heavy (>40 tool calls in session). Then resume from Step 3.3.

**RED Phase**: Write failing tests
- Use Acceptance section from context file as test spec
- Cover test dimensions:
  - Functional: Core feature works
  - Boundary: Edge cases handled
  - Exception: Errors handled gracefully
  - Security: No vulnerabilities
  - Integration: At least one test proving this code connects to upstream/downstream boundary (if applicable)
- Tests MUST fail initially
- Run tests to confirm failure

**GREEN Phase**: Write minimum code to pass
- Only enough code to pass tests
- Production-ready (no TODO, no placeholder)
- Run tests to confirm pass

**REFACTOR Phase**: Improve quality
- Apply SOLID, DRY, KISS, YAGNI
- Tests must still pass

**Workflow checkpoint**: Write `{"command":"ultra-dev","task_id":ID,"branch":"BRANCH","step":"3.3","status":"tdd_complete","ts":"ISO8601"}` to `.ultra/workflow-state.json`

### Step 4: Quality Gates (incremental)

**v7 change**: Gates are read from `.ultra/tasks/progress/task-{id}.json` (`evidence_score` updated continuously by `post_edit_guard.py`). This is **not** a final-gate audit — incremental scores are visible throughout Step 3's TDD cycle, so you should already know where the gaps are. This step **reads** the current state, doesn't recompute.

**Read progress**:
```bash
cat .ultra/tasks/progress/task-{id}.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['evidence_score'], indent=2))"
```

**Evidence dimensions** (each 0–100):

| Dimension | Read as |
|-----------|---------|
| `tests_written` | Are there tests for the changes? |
| `tests_passed` | Do they pass? |
| `persistence_real` | Real DB / object store, not in-memory facades |
| `feature_flags_audit` | No `default off` to dodge integration |
| `vertical_slice` | ≥1 entry-point→DB integration test exists |
| `spec_trace` | task `trace_to` field set to a spec section |

**Test double policy** (informational, enforced as advisory by hooks):
- ❌ Core logic (domain/service/state) → NO mocking — see `.ultra/templates/testcontainer-*`
- ✅ External systems → testcontainers/sandbox/stub allowed

**Decision**:
- If all dims ≥80 → record gates_passed and proceed.
- If any dim < 80 → list which, then **decide whether to fix now or proceed knowingly**. The hook does not block; you are accountable.

**Workflow checkpoint**: Write `{"command":"ultra-dev","task_id":ID,"branch":"BRANCH","step":"4","status":"gates_read","ts":"ISO8601"}` to `.ultra/workflow-state.json`

### Step 4.4: Context Checkpoint (Before Review)

Before launching ultra-review:
1. Write workflow state to `.ultra/workflow-state.json`:
   ```json
   {"command":"ultra-dev","task_id":ID,"branch":"BRANCH","step":"4.5","status":"pre_review","ts":"ISO8601"}
   ```
2. Run `/compact` to reclaim context for the review phase
3. After compact, read `.ultra/compact-snapshot.md` + `.ultra/workflow-state.json` to restore context
4. Proceed to Step 4.5

### Step 4.5: Ultra Review (Mandatory)

**When**: After Quality Gates pass, before commit.

**Process**:

#### Phase 1: Run /ultra-review

Execute the ultra-review skill in `all` mode (force all 5 agents, no auto-skip):

```
/ultra-review all
```

This automatically:
1. Launches 5 specialized review agents in parallel (review-code, review-tests, review-errors, review-comments, review-design)
2. Aggregates and deduplicates findings via review-coordinator
3. Generates SUMMARY.json with verdict (APPROVE / COMMENT / REQUEST_CHANGES)
4. Reports top findings to conversation

#### Phase 2: Act on Verdict

**v7 change**: no hard iteration cap. Each `recheck` writes its issue counts into `.ultra/tasks/progress/task-{id}.json` under `advisories`. Use the trend to decide — don't blindly loop.

| Verdict | Action |
|---------|--------|
| APPROVE | Proceed to Phase 3 |
| COMMENT | Read P1s; fix if warranted; proceed |
| REQUEST_CHANGES | Fix P0s, then `/ultra-review recheck` |

**Stall handling** (after each recheck): compare current P0+P1 count to previous. If counts are **not decreasing**, the loop is stalled:
1. Write `.ultra/tasks/progress/stuck-report-{task_id}.md` containing:
   - All remaining P0/P1 findings
   - Recheck history (counts at each iteration)
   - Hypothesis: which constraint is too aggressive vs. which fix is genuinely insufficient
2. **Use AskUserQuestion** to surface the choice to the user:
   - Option A: continue another fix attempt (with named hypothesis)
   - Option B: ship with known issues recorded in stuck-report
   - Option C: relax a specific constraint (CAAF Dynamic Override) — e.g. accept a documented mock with rationale
3. Do NOT auto-escalate or auto-cap. The user owns the trade-off.

**Workflow state**: After each review pass, write:
```json
{"command":"ultra-dev","task_id":ID,"branch":"BRANCH","step":"4.5","status":"review_done","review_session":"SESSION_ID","review_iteration":N,"ts":"ISO8601"}
```

#### Phase 3: Verification (sensor — not a hard gate)

**Read progress before proceeding**:

- SUMMARY.json verdict (latest)
- Outstanding P0 count
- Test status (latest run)
- `evidence_score` from progress.json

**Decision rule**:
- All ≥80 + verdict APPROVE → proceed to Step 5 silently.
- Otherwise → use AskUserQuestion to surface a *Re-grounded* summary (project, current task, gap), recommend the best path, options A/B/C. The user decides; this step does not block on its own.

> Why no auto-block: hard final gates triggered the over-correction loop documented in PHILOSOPHY.md (C3 Sensors not Blockers + C4 Incremental Validation).

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

### Step 5.5: Pre-Commit Checklist (advisory + user decision)

**v7 change**: This is a *summary view* of state, not an automated gate. The hook layer decides what to block (only irreversible operations); humans decide everything else.

**Compute state** (each line: `✓` / `✗` / `?` if undeterminable):

- tasks.json: status = "completed"
- context file: header = "completed"
- context file: Completion section exists
- All tests passing (latest run)
- Ultra Review verdict is NOT `REQUEST_CHANGES`
- New modules reachable from at least one entry point (no orphan code)
- Boundary-crossing code has integration test
- progress.json `evidence_score`: dimensions ≥80%

**Decision rule**:
- All `✓` → proceed silently to Step 6.
- Any `✗` → use **AskUserQuestion** with the format from CLAUDE.md `<ask_user_format>`:
  - **Re-ground** the task and which checks failed (1–2 lines)
  - **Recommend** the safest path
  - Options: A) commit anyway (record gaps in commit body), B) fix the missing item now, C) split the task (commit done parts, defer the rest)

> Why no auto-block: a hard pre-commit fail-gate triggers the same over-correction loop that pre_stop_check used to. The user owns the trade-off; the harness surfaces it cleanly.

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

**Workflow checkpoint**: Write `{"command":"ultra-dev","task_id":ID,"branch":"BRANCH","step":"6","status":"committed","commit":"SHA","ts":"ISO8601"}` to `.ultra/workflow-state.json`

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

1. **Classify the change** (MANDATORY before updating specs):

   | Classification | Description | Action |
   |---------------|-------------|--------|
   | **EXPANSION** | New requirement discovered during implementation | Update spec, record in Change Log |
   | **CORRECTION** | Spec error or ambiguity found | Update spec, record in Change Log |
   | **REDUCTION** | Removing or weakening a requirement | **STOP** → AskUserQuestion for approval |

   **REDUCTION gate**: If the change would remove scope, weaken acceptance criteria, or defer functionality, use AskUserQuestion:
   - Explain what is being reduced and why
   - Option A: "Approve reduction — update spec" (user accepts simpler scope)
   - Option B: "Keep original scope — find alternative implementation"
   - Option C: "Split into separate task — defer to next cycle"

2. **Update specs immediately** (`.ultra/specs/product.md` or `architecture.md`)
   - Keep specifications current for parallel tasks

3. **Record change in context file** Change Log:
   ```markdown
   | {date} | {classification} | {change description} | specs/{file}#{section} | {reason} |
   ```

**Key principle**: `specs/` is source of truth, `contexts/` tracks implementation history. Specs may grow (EXPANSION) or be corrected (CORRECTION), but never silently shrink (REDUCTION).

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
