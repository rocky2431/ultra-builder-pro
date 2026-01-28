---
description: Status query with native task system (real-time progress + risk analysis)
argument-hint: [task-id]
allowed-tools: Read, Bash(git status), Bash(git log *), Grep, Glob, Task
model: opus
---

# /ultra-status

## Purpose

Real-time project status monitoring with progress tracking, risk analysis, and actionable insights using native task system.

## Workflow

### Phase 0: Validation

**Check environment before displaying status:**
1. Does `.ultra/tasks/tasks.json` exist? → If not: Suggest `/ultra-init` (Chinese)
2. Are there tasks in the system? → If not: Suggest `/ultra-plan` (Chinese)
3. Is task data valid? → Verify structure and timestamps
4. Determine output format (quick vs full report)

### Phase 1: Load Project Data

Read all status files:
- `.ultra/tasks/tasks.json` - Task progress
- `.ultra/test-report.json` - Test status
- `.ultra/delivery-report.json` - Delivery status

Extract:
- Task statistics (total, by status, by priority)
- Current task (in_progress) and next pending task
- Test pass/fail status and run count
- Delivery readiness

### Phase 2: Generate Progress Report

Display comprehensive project status:
- 📊 **Overview**: Progress bar, completion %, task velocity
- 📝 **Tasks**: By status (pending/in_progress/completed/blocked)
- 🧪 **Test**: Pass/fail, run count, blocking issues
- 📦 **Delivery**: Version, pushed status
- ⚠️ **Risks**: Auto-detected issues
- 📈 **Next**: Optimal next task

### Phase 3: Analyze Risks

**Auto-detect issues**:
- **Blockers**: Tasks with unsatisfied dependencies
- **Stalled tasks**: In-progress >3 days
- **Overdue**: Past estimated completion
- **Complexity spikes**: Multiple complex tasks queued
- **Resource constraints**: Parallel task limits

### Phase 4: Provide Recommendations

Suggest next optimal task based on:
- Priority (P0 > P1 > P2 > P3)
- Dependencies (only ready tasks)
- Complexity (balance with velocity)
- Context (similar to recent tasks)

## Usage

```bash
/ultra-status          # Full project status report
/ultra-status [task-id] # Status of specific task
```

## Risk Indicators

| Icon | Meaning | Action |
|------|---------|--------|
| 🟢 | All good, on track | Continue current plan |
| 🟡 | Minor issues, monitor | Review stalled tasks |
| 🟠 | Significant risks | Address blockers immediately |
| 🔴 | Critical blockers | Stop and resolve before continuing |

## Smart Analysis Features

**Velocity Calculation**: completed tasks / elapsed days = ETA for remaining tasks

**Critical Path Identification**: Find bottleneck tasks (most dependencies, longest chains)

**Task Recommendations**: Next task based on priority + dependencies + complexity + context

## Integration

- **Input**:
  - `.ultra/tasks/tasks.json` - Task progress
  - `.ultra/test-report.json` - Test status
  - `.ultra/delivery-report.json` - Delivery status
- **Output**: Console report in Chinese
- **Timing**: Run anytime to check project status

## Benefits

- ✅ Real-time insights (no external APIs)
- ✅ Risk early warning (prevent delays)
- ✅ Smart recommendations (optimize task order)
- ✅ Velocity tracking (predictable delivery)
- ✅ Native integration (consistent with workflow)

## Output Format

> Claude responds in Chinese per CLAUDE.md.

**Command icon**: 📊
