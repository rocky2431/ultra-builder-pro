---
description: Agile development execution with native task management and simplified TDD workflow
argument-hint: [task-id]
allowed-tools: Read, Write, Edit, Bash, TodoWrite, Grep, Glob, Task
---

# /ultra-dev (Production Absolutism)

> "There is no test code. There is no demo. There is no MVP.
> Every line is production code. Every test is production verification."

Execute development tasks using TDD workflow with native task management.

**Quality Formula**:
```
Code Quality = Real Implementation × Real Tests × Real Dependencies
If ANY component is fake/mocked/simulated → Quality = 0
```

## Arguments

- `$1`: Task ID (if empty, auto-select next pending task)

---

## Pre-Execution Validation (MANDATORY)

**Before writing ANY code, you MUST perform these three validations. If any validation fails, STOP and report the failure to the user with the solution. Do NOT proceed with development.**

### Validation 1: Specification Exists

**What to check**: Read `.ultra/tasks/tasks.json` and verify the target task has a `trace_to` field pointing to a valid specification file.

**Why this matters**: Development without specification leads to mock code, hardcoded values, and degraded implementations — all violate Production Absolutism. The spec provides the contract that tests verify against with real dependencies.

**If validation fails**:
- Report: "❌ Task #{id} has no linked specification (trace_to field missing)"
- Solution: "Run /ultra-research to create specs, or add trace_to field to tasks.json"
- STOP here. Do not proceed.

**If validation passes**: Continue to Validation 2.

### Validation 2: Feature Branch Active

**What to check**: Run `git branch --show-current` and verify the result is NOT `main` or `master`.

**Why this matters**: Main branch must remain deployable at all times. Each task requires an independent branch so changes can be reverted individually without affecting other work.

**If validation fails**:
- Report: "❌ Currently on main/master branch, direct development prohibited"
- Solution: "Run: git checkout -b feat/task-{id}-{slug}"
- STOP here. Do not proceed.

**If validation passes**: Continue to Validation 3.

### Validation 3: Dependencies Check (Soft Validation)

**What to check**: Read `.ultra/tasks/tasks.json`, find the target task's `dependencies` array, and check each dependency task status.

**Parallel Development Mode**: Dependencies are soft constraints. Tasks can run in parallel even if dependencies are incomplete.

**If dependencies incomplete**:
- Report: "⚠️ Dependency task incomplete: Task #{dep_id} (status: {status})"
- Warning: "Parallel development mode: can proceed, but watch interface compatibility"
- **Continue with development** (do not block)

**If dependencies are `completed`**: No warning needed.

**If all validations pass**: Proceed to Development Workflow.

---

## Development Workflow

### Step 1: Task Selection and Context

1. Read `.ultra/tasks/tasks.json`
2. If task ID provided, select that task; otherwise select first task with `status: "pending"`
3. **Read context file** (split architecture):
   - If `context_file` exists: Read `.ultra/tasks/{context_file}` (e.g., `contexts/task-1.md`)
   - Fallback: Read from `trace_to` spec file (backward compatibility)

4. **Display task context** (from MD file):

```
📋 Task #{id}: {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Content from contexts/task-{id}.md]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

5. Update task status to `"in_progress"` in tasks.json
6. Use TodoWrite to track progress (create todos from Acceptance section)

**Context file location**: `.ultra/tasks/contexts/task-{id}.md`

**For complex tasks** (complexity >= 7 AND type == "architecture"):
Delegate to ultra-architect-agent using the Task tool:
```
Task(subagent_type="ultra-architect-agent",
     prompt="Design implementation approach for task #{id}: {title}.
             Provide SOLID compliance analysis and trade-off recommendations.")
```

### Step 2: Create Feature Branch (from main)

**Always start from latest main** (enables parallel development):

```bash
git checkout main
git pull origin main
git checkout -b feat/task-{id}-{slug}
```

Where `{slug}` is a 2-3 word lowercase hyphenated description of the task.

**Why from main**: Ensures branch is based on latest stable code, enabling parallel work without blocking on other tasks.

### Step 3: Context Update Workflow

**When requirements change during development** (Dual-Write Mode):

1. **Update context file** (`.ultra/tasks/contexts/task-{id}.md`):
   - Modify the relevant section (Context/Implementation/Acceptance)
   - Add entry to Change Log table

2. **Update specs if needed** (`.ultra/specs/`):
   - If change affects other tasks, update the source spec
   - Keep specs and context files in sync

**Change Log format** (in context file):
```markdown
## Change Log
| Date | Change | Reason |
|------|--------|--------|
| 2024-01-01 | Initial creation | Generated by /ultra-plan |
| 2024-01-02 | Changed auth to OAuth | User requested SSO support |
```

**On completion**: Update status in context file header to `completed`.

### Step 4: TDD Development Cycle

**You MUST follow RED → GREEN → REFACTOR strictly. Do NOT write implementation before tests.**

**RED Phase**: Write failing tests first (Production Absolutism)
- **Use task.acceptance.tests** as test specification (already defined in task)
- Cover 6 dimensions: Functional, Boundary, Exception, Performance, Security, Compatibility
- Tests MUST use real dependencies for core logic (no mocking domain/service/state machine)
- External systems may use test doubles (testcontainers/sandbox/stub) with rationale
- Tests MUST fail initially (verifies tests are meaningful)
- Run tests to confirm failure

**GREEN Phase**: Write minimum code to pass tests (Production-Grade Only)
- Only enough code to make tests pass
- Code must be production-ready (no TODO, no placeholder, no mock)
- No premature optimization or extra features
- Run tests to confirm all pass

**REFACTOR Phase**: Improve code quality (No Degradation)
- Apply SOLID principles
- Remove duplication (DRY)
- Simplify complexity (KISS)
- Remove unused code (YAGNI)
- Ensure no mock/simulation introduced
- Tests must still pass after refactoring

### Step 5: Quality Gates

**Before marking task complete, verify ALL gates pass:**

| Gate | Requirement | How to Verify |
|------|-------------|---------------|
| G1 | Tests pass | `npm test` exits with 0 |
| G2 | Coverage ≥80% | `npm test -- --coverage` |
| G3 | TDD verified | RED→GREEN→REFACTOR completed |
| G4 | No tautologies | No `expect(true).toBe(true)` patterns |
| G5 | No skipped tests | Max 1 `.skip()` allowed |
| G6 | 6D coverage | All dimensions have tests |
| G7 | **No Core Logic Mock** | No mocking domain/service/state machine (see glossary) |
| G8 | **No Degradation** | No fallback, simplified, or demo code |

**Test Double Policy** (aligned with CLAUDE.md glossary):
- ❌ **Core Logic**: Domain/service/state machine/funds-permission paths - NO mocking
- ❌ **Repository interfaces**: Contract cannot be mocked
- ✅ **Repository storage**: 1) Preferred: testcontainers with production DB 2) Acceptable: SQLite/in-memory when unavailable
- ✅ **External systems**: testcontainers/sandbox/stub allowed with rationale

### Step 6: Sync, Merge, and Cleanup

**Parallel-safe merge process:**

1. Commit with conventional format: `feat(scope): description`
2. Sync with main (handle parallel changes):
   ```bash
   git fetch origin
   git rebase origin/main
   # If conflicts: resolve, git add, git rebase --continue
   ```
3. Run tests after rebase to verify integration
4. Switch to main: `git checkout main`
5. Pull latest: `git pull origin main`
6. Merge with history: `git merge --no-ff feat/task-{id}-{slug}`
7. Push: `git push origin main`
8. Delete branch: `git branch -d feat/task-{id}-{slug}`
9. Update task status to `"completed"` in tasks.json
10. Update context file header status to `completed` in `.ultra/tasks/contexts/task-{id}.md`
11. **Update project context** (via syncing skills):
    - `syncing-status`: Record to `.ultra/docs/feature-status.json` (commit, branch, timestamp)
    - `syncing-docs`: Update CLAUDE.md "Current Focus" with next pending task

**Conflict resolution**: If rebase has conflicts, resolve them before merging. Never merge unresolved conflicts.

### Step 7: Report Completion

Display completion message in Chinese including:
- Commit hash
- Branch merge status
- Project progress (completed/total tasks)
- Next steps suggestion

---

## Integration

- **Skills activated**:
  - Sync: **syncing-docs** (CLAUDE.md), **syncing-status** (feature-status.json)
- **Agents available**: ultra-architect-agent (for complexity >= 7)
- **Input files**:
  - `.ultra/tasks/tasks.json` (task registry)
  - `.ultra/tasks/contexts/task-{id}.md` (full task context)
- **Output files**:
  - `.ultra/tasks/tasks.json` (status update)
  - `.ultra/tasks/contexts/task-{id}.md` (change log, completion status)
  - `.ultra/docs/feature-status.json` (implementation tracking)
  - `CLAUDE.md` (current focus update)
- **Next command**: `/ultra-test` or `/ultra-dev [next-task-id]`

## Usage

```bash
/ultra-dev              # Auto-select next pending task
/ultra-dev 5            # Work on task #5
```
