---
name: syncing-status
description: "Maintains feature-status.json with task completion and test results. This skill activates when tasks complete, tests run, or /ultra-status executes."
---

# Status Synchronization

Keeps feature status accurate and current.

## Activation Context

This skill activates when:
- `/ultra-dev` marks a task as completed
- `/ultra-test` finishes (pass or fail)
- `/ultra-status` runs
- Discussions about task or feature status

## Resources

| Resource | Purpose |
|----------|---------|
| `scripts/status_sync.py` | Manage status entries |

## Status Management

### Record Task Completion

```bash
python scripts/status_sync.py record <task-id> --name "Task name" --commit abc123 --branch feat/task-1
```

### Record Test Result

```bash
python scripts/status_sync.py test <task-id> --status pass --coverage 85
```

### Check Consistency

```bash
python scripts/status_sync.py check
```

### Generate Report

```bash
python scripts/status_sync.py report
```

## Status File Structure

Location: `.ultra/docs/feature-status.json`

### On Task Completion

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

## Status Values

| Status | Meaning |
|--------|---------|
| `pass` | Tests pass, coverage ≥80% |
| `fail` | Tests fail or coverage below threshold |
| `pending` | Implemented but not yet tested |

## Consistency Checks

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
