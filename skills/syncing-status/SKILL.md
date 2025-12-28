---
name: syncing-status
description: "Maintains feature-status.json with task completion and test results. Activates when tasks complete, tests run, or /ultra-status executes."
allowed-tools: Read, Write, Glob
---

# Status Guardian

Keeps feature status accurate and current.

## Activation Context

This skill activates when:
- `/ultra-dev` marks a task as completed
- `/ultra-test` finishes (pass or fail)
- `/ultra-status` runs
- Discussions about task or feature status

## Status Tracking

### On Task Completion

Record completion in `.ultra/docs/feature-status.json`:

```json
{
  "id": "feat-{taskId}",
  "name": "{task title}",
  "status": "pending",
  "taskId": "{taskId}",
  "implementedAt": "{ISO timestamp}",
  "commit": "{git commit hash}",
  "branch": "{branch name}"
}
```

### On Test Completion

Update entry with test results:

```json
{
  "status": "pass",
  "testedAt": "{ISO timestamp}",
  "coverage": 85,
  "coreWebVitals": {
    "lcp": 2100,
    "inp": 150,
    "cls": 0.05
  }
}
```

Status values:
- `pass` - Tests pass and coverage ≥80%
- `fail` - Tests fail or coverage below threshold
- `pending` - Implemented but not yet tested

### Consistency Check

When `/ultra-status` runs:
1. Compare tasks.json completed tasks with feature-status entries
2. Identify gaps (completed tasks without status entries)
3. Flag stale entries (pending > 24 hours)
4. Offer to create missing entries

## Error Handling

If status update fails:
1. Log warning to `.ultra/docs/status-sync.log`
2. Continue with task completion (status is informational)
3. Auto-repair on next `/ultra-status` run

## Output Format

Provide updates in Chinese at runtime:

```
状态同步
========================

✅ Task #{id} 状态已记录
   - 实现时间：{timestamp}
   - 提交：{commit hash}
   - 分支：{branch}

========================
```

**Tone:** Concise, informational
