---
description: Agile development execution with native task management and simplified TDD workflow
argument-hint: [task-id]
allowed-tools: Read, Write, Edit, Bash, TodoWrite, Grep, Glob, Task
---

# /ultra-dev

## Purpose

Execute development tasks using TDD workflow with native task management.

## Arguments

- `$1`: Task ID (if empty, auto-select next pending task)

## Bypass Flags (REMOVED)

**The following flags have been REMOVED to enforce quality**:
- ~~`no-branch`~~ - Independent branches are mandatory
- ~~`skip-tests`~~ - TDD workflow is mandatory

See `guidelines/ultra-testing-philosophy.md` for testing philosophy.

## Pre-Execution Checks

Display warnings (don't block execution):
- Check for in-progress tasks → Warn if found
- Check git status → Suggest commit/stash if uncommitted changes
- Validate task dependencies → Warn if dependencies incomplete

## Workflow

### 1. Task Selection

- Use `$1` task ID, or auto-select next pending task
- Display task context: ID, title, complexity, dependencies, description
- Mark task `"in_progress"` in `.ultra/tasks/tasks.json`

### 2. Development Branch

Create independent branch per task:
```bash
git checkout -b feat/task-{id}-{slug}
```

**Note**: Workflow enforcement is handled by `guarding-git-workflow` skill. See `@guidelines/ultra-git-workflow.md` for complete branch workflow rules.

### 2.7. Create Changes Directory (OpenSpec Pattern)

Create isolated workspace for feature proposals following OpenSpec two-folder pattern:

**Directory structure**:
```bash
mkdir -p .ultra/changes/task-{id}/specs
```

**Files to create**:
```
.ultra/changes/task-{id}/
├── proposal.md          # Feature overview and rationale
├── tasks.md             # Implementation checklist (copy from tasks.json)
└── specs/               # Spec deltas (optional, only if specs change)
    ├── product.md       # New/modified user stories
    └── architecture.md  # Architecture changes
```

**proposal.md template**:
```markdown
# Feature: [Task Title]

**Task ID**: {id}
**Status**: In Progress
**Branch**: feat/task-{id}-{slug}

## Overview
[What is being built]

## Rationale
[Why this change is needed - link to requirement]

## Impact Assessment
- **User Stories Affected**: [List from specs/product.md]
- **Architecture Changes**: [Yes/No - describe if yes]
- **Breaking Changes**: [Yes/No - list if yes]

## Requirements Trace
- Traces to: specs/product.md#{user-story-id}
```

**tasks.md content**: Copy task details from .ultra/tasks/tasks.json for tracking

**specs/ usage** (optional):
- Create specs/product.md if adding/modifying user stories
- Create specs/architecture.md if changing technology decisions
- These are **deltas** (what's new/changed), not full copies
- Will be merged back to main specs/ after task completion

**Output** (Chinese): Report changes directory creation, proposal template ready

### 3. TDD Development Cycle

**RED → GREEN → REFACTOR**:
- **RED**: Write failing tests (6 dimensions: Functional, Boundary, Exception, Performance, Security, Compatibility)
- **GREEN**: Implement minimum code to pass
- **REFACTOR**: Improve quality (SOLID/DRY/KISS/YAGNI)

**Tool Selection**:
- Small projects (<50 files): Grep/Glob + Edit
- Large projects (>100 files): Use built-in tools (explicit instruction required)

**Reference**: `@config/ultra-mcp-guide.md` for tool selection decision tree

### 4. Commit & Update

- Commit with conventional format (Git Workflow Guardian assists)
- Update task status in `tasks.json`
- Add implementation notes

### 5. Quality Gates (6 Mandatory)

**⚠️ ALL gates must pass before marking task complete. No exceptions.**

| Gate | Requirement | Verification |
|------|-------------|--------------|
| **G1** | Tests pass | `npm test` exit code 0 |
| **G2** | Coverage ≥80% | `npm test -- --coverage` |
| **G3** | TDD phases verified | RED→GREEN→REFACTOR completed |
| **G4** | No tautologies | No `expect(true).toBe(true)` patterns |
| **G5** | No skipped tests | Max 1 `.skip()` allowed |
| **G6** | 6D coverage | All dimensions tested |

**Test Authenticity Score (TAS)**:
- `guarding-test-quality` skill auto-calculates TAS
- **TAS ≥70% required** (Grade A/B pass, Grade C/D/F blocked)
- Components: Mock Ratio (25%), Assertion Quality (35%), Real Execution (25%), Pattern Compliance (15%)

**Blocking Conditions**:
- ❌ TAS < 70% → Task cannot complete
- ❌ Critical anti-patterns (tautology, empty tests) → Task cannot complete
- ❌ Zero assertions in test file → Task cannot complete

**Reference**: `guidelines/ultra-testing-philosophy.md` for anti-pattern examples

### 6. Merge to Main & Clean Up

**Prerequisites**: All Quality Gates must pass

### 6.1. Merge Spec Deltas (if exists)

**Check for spec deltas**:
```bash
if [ -d ".ultra/changes/task-{id}/specs" ]; then
  echo "Spec deltas detected, merging back to main specs/"
fi
```

**Merge process** (if spec deltas exist):

1. **Review changes**:
   - Read `.ultra/changes/task-{id}/specs/product.md` (if exists)
   - Read `.ultra/changes/task-{id}/specs/architecture.md` (if exists)
   - Verify alignment with implemented code

2. **Merge to main specs**:
   - Append new user stories to `specs/product.md`
   - Update technology stack in `specs/architecture.md`
   - Update traceability: Ensure task.trace_to matches merged specs

3. **Archive changes**:
   ```bash
   mkdir -p .ultra/changes/archive
   mv .ultra/changes/task-{id} .ultra/changes/archive/task-{id}-$(date +%Y-%m-%d)
   ```

**Output** (Chinese - Detailed status):
```
📋 Spec Delta Merge Status
========================
✅ Reviewed spec changes in .ultra/changes/task-{id}/specs/

Updated sections:
- specs/product.md #{section-id} (new user story added)
- specs/architecture.md #{section-id} (technology decision updated)

Traceability verified:
- task.trace_to matches merged specs: ✅

Changes archived:
- .ultra/changes/task-{id} → .ultra/changes/archive/task-{id}-{date}
```

### 6.2. Merge Branch to Main

**Execution**:
```bash
# 1. Switch to main branch
git checkout main

# 2. Pull latest changes (avoid conflicts)
git pull origin main

# 3. Merge feature branch (--no-ff preserves history)
git merge --no-ff feat/task-{id}-{slug}

# 4. Push to remote (if configured)
git push origin main

# 5. Delete local feature branch
git branch -d feat/task-{id}-{slug}

# 6. Delete remote branch (if exists)
git push origin --delete feat/task-{id}-{slug}
```

**Mark task as "completed"** in `.ultra/tasks/tasks.json`

### 6.3. Update Feature Status (MANDATORY)

**⚠️ CRITICAL: This step is NON-OPTIONAL. Do NOT skip under any circumstances.**

**Before displaying "Task Completed" message**, you MUST execute these steps:

**Step 1: Read current feature status**
```bash
cat .ultra/docs/feature-status.json
```

**Step 2: Check if entry exists for current task**
- If entry with matching `taskId` exists → Skip creation (already recorded)
- If NO entry exists → Proceed to Step 3

**Step 3: Create new entry** (execute, not just describe)
```bash
# Get task info from context
TASK_ID="${current_task_id}"
TASK_TITLE="${current_task_title}"
COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "no-commit")
BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Create the feature entry JSON
NEW_ENTRY='{
  "id": "feat-'$TASK_ID'",
  "name": "'$TASK_TITLE'",
  "status": "pending",
  "taskId": "'$TASK_ID'",
  "implementedAt": "'$TIMESTAMP'",
  "commit": "'$COMMIT'",
  "branch": "'$BRANCH'"
}'

# Update feature-status.json (add new entry to features array)
```

**Step 4: Verify update succeeded**
```bash
cat .ultra/docs/feature-status.json | grep "feat-${TASK_ID}"
# Must show the newly created entry
```

**Output Format** (Chinese at runtime):
```
Task #{id} completed message including:
   - Commit hash
   - Branch merge status: feat/task-{id} → main
   - Feature status recorded: pending (awaiting /ultra-test)
   - Project progress: {completed}/{total} tasks
```

**Failure Handling**:
If feature-status.json update fails:
1. Display warning (Chinese at runtime)
2. Log error to .ultra/docs/status-sync.log (if available)
3. Continue with task completion (do NOT block)
4. syncing-status Skill will auto-fix on next trigger

**Output** (Example structure - output in Chinese at runtime per Language Protocol):
```
🎉 Task #{id} Completed!
========================

✅ Development Completed
   - All code committed: feat/task-{id}-{slug}
   - TDD cycle: RED → GREEN → REFACTOR ✅
   - Code quality checks: SOLID principles passed ✅

✅ Branch Merge Completed
   - Switched to main branch
   - Pulled latest code: main up-to-date
   - Merged: feat/task-{id}-{slug} → main (--no-ff)
   - Pushed to remote: origin/main
   - Deleted local branch: feat/task-{id}-{slug} ✅
   - Deleted remote branch: origin/feat/task-{id}-{slug} ✅

✅ Spec Updates (if any)
   - specs/product.md: [updated section]
   - specs/architecture.md: [updated section]
   - Changes archived to: .ultra/changes/archive/task-{id}-{date}

✅ Task Status Updated
   - .ultra/tasks/tasks.json: task #{id} → "completed"
   - Completion time: {timestamp}

========================
📊 Project Progress
   - Completed: X/Y tasks ({percentage}%)
   - In progress: 0 tasks
   - Pending: Y-X tasks

🚀 Next Steps
   - Run /ultra-test to verify all tests pass
   - Or run /ultra-dev to continue next task
   - Or run /ultra-status to view overall progress
```

## Integration

- **Skills**: guarding-quality, guarding-git-workflow (auto-activate)
- **Agents**: ultra-architect-agent (for complex design)
- **Next**: `/ultra-test` or `/ultra-dev [next-task-id]`

## Usage Examples

```bash
/ultra-dev              # Auto-select next task
/ultra-dev 5            # Work on task 5
```

## Output Format

**Standard output structure**: See `@config/ultra-command-output-template.md` for the complete 6-section format.

**Command icon**: 💻

**Example output**: See template Section 7.4 for ultra-dev specific example (includes detailed merge back report).

## References

- @workflows/ultra-development-workflow.md - Complete TDD workflow
- @guidelines/ultra-solid-principles.md - Code quality standards
- @config/ultra-mcp-guide.md - Tool selection guide
