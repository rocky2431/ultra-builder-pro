---
description: Agile development execution with native task management and simplified TDD workflow
argument-hint: [task-id]
allowed-tools: Read, Write, Edit, Bash, TodoWrite, Grep, Glob, Task
---

# /ultra-dev

Execute development tasks using TDD workflow with native task management.

## Arguments

- `$1`: Task ID (if empty, auto-select next pending task)

---

## Pre-Execution Validation (MANDATORY)

**Before writing ANY code, you MUST perform these three validations. If any validation fails, STOP and report the failure to the user with the solution. Do NOT proceed with development.**

### Validation 1: Specification Exists

**What to check**: Read `.ultra/tasks/tasks.json` and verify the target task has a `trace_to` field pointing to a valid specification file.

**Why this matters**: Development without specification leads to mock code, hardcoded values, and degraded implementations. The spec provides the contract that tests verify against.

**If validation fails**:
- Report: "❌ 任务 #{id} 没有关联规范 (trace_to 字段缺失)"
- Solution: "请先运行 /ultra-research 建立规范，或在 tasks.json 中添加 trace_to 字段"
- STOP here. Do not proceed.

**If validation passes**: Continue to Validation 2.

### Validation 2: Feature Branch Active

**What to check**: Run `git branch --show-current` and verify the result is NOT `main` or `master`.

**Why this matters**: Main branch must remain deployable at all times. Each task requires an independent branch so changes can be reverted individually without affecting other work.

**If validation fails**:
- Report: "❌ 当前在 main/master 分支，禁止直接开发"
- Solution: "请运行: git checkout -b feat/task-{id}-{slug}"
- STOP here. Do not proceed.

**If validation passes**: Continue to Validation 3.

### Validation 3: Dependencies Check (Soft Validation)

**What to check**: Read `.ultra/tasks/tasks.json`, find the target task's `dependencies` array, and check each dependency task status.

**Parallel Development Mode**: Dependencies are soft constraints. Tasks can run in parallel even if dependencies are incomplete.

**If dependencies incomplete**:
- Report: "⚠️ 依赖任务未完成: Task #{dep_id} (状态: {status})"
- Warning: "并行开发模式：可继续开发，但需注意接口兼容性"
- **Continue with development** (do not block)

**If dependencies are `completed`**: No warning needed.

**If all validations pass**: Proceed to Development Workflow.

---

## Development Workflow

### Step 1: Task Selection and Context

1. Read `.ultra/tasks/tasks.json`
2. If task ID provided, select that task; otherwise select first task with `status: "pending"`
3. Display task context to user: ID, title, complexity, dependencies, description
4. Update task status to `"in_progress"` in tasks.json
5. Use TodoWrite to track progress

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

### Step 3: Create Changes Directory

Create task workspace (if not exists):
```
.ultra/changes/task-{id}/
├── proposal.md     # Feature overview, rationale, and completion status
└── tasks.md        # Task details from tasks.json
```

**On completion**: Add `## Status: Completed` section to proposal.md with completion date and summary.

**On spec changes**: Document changes in proposal.md, do not create new files.

### Step 4: TDD Development Cycle

**You MUST follow RED → GREEN → REFACTOR strictly. Do NOT write implementation before tests.**

**RED Phase**: Write failing tests first
- Cover 6 dimensions: Functional, Boundary, Exception, Performance, Security, Compatibility
- Tests MUST fail initially (verifies tests are meaningful)
- Run tests to confirm failure

**GREEN Phase**: Write minimum code to pass tests
- Only enough code to make tests pass
- No premature optimization or extra features
- Run tests to confirm all pass

**REFACTOR Phase**: Improve code quality
- Apply SOLID principles
- Remove duplication (DRY)
- Simplify complexity (KISS)
- Remove unused code (YAGNI)
- Tests must still pass after refactoring

### Step 4.5: Codex Feedback Loop (Dual-Engine)

**After GREEN phase, before final REFACTOR, trigger Codex review.**

**Codex Code Review**:
```bash
# Option 1: Direct Codex CLI
codex -q "Review {modified_files} for bugs, security issues, and performance problems. Provide specific line numbers and fixes."

# Option 2: codeagent-wrapper
codeagent-wrapper --backend codex - <<EOF
Review the following files for quality issues:
{modified_files}

Focus on:
1. Logic errors and edge cases
2. Security vulnerabilities (injection, XSS, etc.)
3. Performance bottlenecks
4. Error handling completeness
EOF
```

**Codex Test Generation**:
```bash
codex -q "Generate additional test cases for {modified_files} covering boundary conditions and security scenarios."
```

**Process Flow**:
```
Claude Code (GREEN) → Codex Review → Feedback?
                                        ├─ No issues → Continue to REFACTOR
                                        └─ Has issues → Claude Code Fix → Re-review
```

**Stuck Detection** (原地打转检测):
- If Claude Code fails to fix same issue 3 times consecutively
- **Role Swap**: Codex attempts fix → Claude Code reviews
- Final approval always from Claude Code

```
Normal:  Claude → Codex review → Claude fix → pass
Stuck:   Claude → fail(x3) → Codex fix → Claude review → pass
```

**Quality Threshold**:
- Codex review score must be ≥ 80/100
- Critical issues (security, correctness) must be 0

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

**TAS Score Requirement**: guarding-test-quality skill calculates Test Authenticity Score.
- TAS ≥70% required (Grade A/B)
- TAS <70% blocks completion (Grade C/D/F)

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
10. Mark completion in `.ultra/changes/task-{id}/proposal.md` (add Status section)
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
  - Guards: guarding-quality, guarding-git-workflow, guarding-test-quality
  - Sync: **syncing-docs** (CLAUDE.md), **syncing-status** (feature-status.json)
  - Codex: codex-reviewer
- **Dual-Engine**: Claude Code (primary) + Codex (reviewer)
- **Agents available**: ultra-architect-agent (for complexity >= 7)
- **Output files**:
  - `.ultra/tasks/tasks.json` (status update)
  - `.ultra/changes/task-{id}/proposal.md` (completion record)
  - `.ultra/docs/feature-status.json` (implementation tracking)
  - `CLAUDE.md` (current focus update)
- **Next command**: `/ultra-test` or `/ultra-dev [next-task-id]`

## Usage

```bash
/ultra-dev              # Auto-select next pending task
/ultra-dev 5            # Work on task #5
```
