---
name: syncing-status
description: "TRIGGERS when: /ultra-dev marks task as 'completed', /ultra-test execution completes (pass or fail), /ultra-status runs, keywords 'task completed'/'tests pass'/'tests fail'/'coverage'/'feature status'. Syncs feature-status.json with task completion and test results. DO NOT trigger for: task creation, documentation-only changes, non-task discussions."
allowed-tools: Read, Write, Glob
---

# Feature Status Guardian

## Purpose
Ensure feature-status.json accurately reflects task completion and test results.

## When
**Auto-triggers when**:
- /ultra-dev marks any task as "completed"
- /ultra-test execution completes (pass or fail)
- /ultra-status runs (for consistency validation)
- Keywords: "task completed", "tests pass", "tests fail", "coverage", "feature status"

**Do NOT trigger for**:
- Task creation (only completion)
- Documentation-only changes
- Non-task related discussions

## Do

### 1. On Task Completion (/ultra-dev)
1. Read .ultra/tasks/tasks.json
2. Find newly completed task (status changed to "completed")
3. Read .ultra/docs/feature-status.json
4. Create entry if missing:
   ```json
   {
     "id": "feat-{taskId}",
     "name": "{taskTitle}",
     "status": "pending",
     "taskId": "{taskId}",
     "implementedAt": "{ISO timestamp}",
     "commit": "{git commit hash}",
     "branch": "{branch name}"
   }
   ```
5. Write back to feature-status.json
6. Output: Status recorded message (Chinese at runtime)

### 2. On Test Completion (/ultra-test)
1. Read test results (coverage percentage, pass/fail)
2. Read feature-status.json
3. Find entry by taskId
4. Update entry:
   - status: "pass" (all tests pass + coverage ≥80%) or "fail"
   - testedAt: "{ISO timestamp}"
   - coverage: {percentage}
   - coreWebVitals: {lcp, inp, cls} (frontend only)
5. Write back to feature-status.json
6. Output: Test status updated message (Chinese at runtime)

### 3. Consistency Check (/ultra-status)
1. Read tasks.json → get all completed tasks
2. Read feature-status.json → get all entries
3. Compare and identify gaps:
   - Tasks completed but no feature-status entry
   - Entries with stale/missing data (pending > 24 hours)
4. Report gaps: List missing entries and stale entries (Chinese at runtime)
5. Offer auto-fix option: create missing entries with status "unknown"

## Don't
- Do not create entries for non-completed tasks
- Do not overwrite existing pass/fail status without new test run
- Do not block task completion if status update fails (log warning instead)
- Do not trigger on task creation (only completion)

## Outputs

**Language**: Chinese (simplified) at runtime

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

**Format**:
- Clear status indicators (✅ ⚠️)
- Feature ID and task mapping
- Coverage and test results when available

**Failure Handling**:
If feature-status.json update fails:
1. Display warning (Chinese at runtime)
2. Log error to .ultra/docs/status-sync.log
3. Continue with task completion (do not block)
4. Auto-fix on next /ultra-status run
