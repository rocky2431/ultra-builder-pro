---
name: compressing-context
description: "Compresses context to prevent overflow. TRIGGERS: After completing multiple tasks, high token usage, or before critical operations. ACTIONS: Summarize completed tasks, archive details. BLOCKS: Further development without compression at critical thresholds."
allowed-tools: Read, Write, TodoWrite
---

# Context Compressor

## Purpose
Prevent context overflow by proactively compressing accumulated information during long development sessions.

## Configuration

**Load from `.ultra/config.json`**:
```json
{
  "context": {
    "total_limit": 200000,
    "thresholds": {
      "green": 0.60,   // 120K = 200K * 0.60
      "yellow": 0.70,  // 140K = 200K * 0.70
      "orange": 0.85,  // 170K = 200K * 0.85
      "red": 0.95      // 190K = 200K * 0.95
    },
    "compression": {
      "trigger_task_count": 5,
      "target_ratio": 0.10,
      "archive_path": ".ultra/context-archive/"
    }
  }
}
```

**Calculate thresholds at runtime**:
- Green limit: `config.context.total_limit * config.context.thresholds.green`
- Yellow limit: `config.context.total_limit * config.context.thresholds.yellow`
- Orange limit: `config.context.total_limit * config.context.thresholds.orange`
- Red limit: `config.context.total_limit * config.context.thresholds.red`

**Loading config in runtime** (TypeScript example):
```typescript
// Load config from project
const configPath = '.ultra/config.json';
const config = JSON.parse(await Read(configPath));

// Extract thresholds
const totalLimit = config.context.total_limit;  // 200000
const thresholds = config.context.thresholds;

// Calculate actual limits
const greenLimit = totalLimit * thresholds.green;    // 120000
const yellowLimit = totalLimit * thresholds.yellow;  // 140000
const orangeLimit = totalLimit * thresholds.orange;  // 170000

// Use in compression logic
if (currentTokens > orangeLimit) {
  // Enforce compression
} else if (currentTokens > yellowLimit) {
  // Suggest compression
}
```

## When (Trigger Conditions)

### Primary Triggers
1. **After ultra-dev completes {trigger_task_count}+ tasks** (most common, from config)
2. **Token usage > {green threshold}** (from config: total_limit * thresholds.green)
3. **Token usage > {yellow threshold}** (from config: total_limit * thresholds.yellow)
4. **Before ultra-test or ultra-deliver** (preserve context for final phases)

### Detection Signals
- Check `.ultra/tasks/tasks.json` for completed task count
- Monitor context-overflow-handler warnings
- User mentions "running out of context" or similar

## Do

### Compression Strategy (3-Step Process)

**Step 1: Identify Compressible Content**
```typescript
Candidates for compression:
• Completed task details (in tasks.json)
• Historical code snippets (already committed)
• Repeated Skills output (quality reports)
• Verbose tool outputs (git status, npm install logs)
• Large research reports (already saved to .ultra/docs/research/)

Keep uncompressed:
• Current task context
• Recent code changes (uncommitted)
• Active debugging information
• Critical decisions (not yet documented)
```

**Step 2: Generate Compression Summary**
```markdown
# Session Summary - 2025-11-14 10:30

## Completed Tasks (5 tasks, 75K tokens → 3K tokens)

### Task #1: Implement user authentication
- Status: Completed
- Branch: feat/task-1-auth (merged to main)
- Key changes:
  - src/auth/AuthService.ts (JWT implementation)
  - tests/auth.test.ts (6-dimensional coverage)
- Tests: All passing (coverage 92%)
- Commit: abc123 "feat: add JWT authentication"

### Task #2: Create user dashboard
- Status: Completed
- Branch: feat/task-2-dashboard (merged)
- Key changes:
  - src/components/Dashboard.tsx
  - src/hooks/useDashboardData.ts
- Tests: All passing (coverage 87%)
- Core Web Vitals: LCP 2.1s
- Commit: def456 "feat: implement dashboard with real-time data"

[... Task #3-5 similar format ...]

## Technical Decisions
- Chose JWT over sessions (performance reasons)
- Material Design 3 for Dashboard UI
- Real-time data via WebSocket (not polling)

## Known Issues
- None (all tasks completed cleanly)

## Next Steps
- Continue with Task #6: Payment integration
- Remaining tasks: 15 (estimated 8 hours)

## Context Stats
- Before compression: [actual tokens]
- After compression: [compressed tokens]
- Compression ratio: [percentage]
```

**Step 3: Archive and Apply**
```bash
# Save to archive (path from config.context.compression.archive_path)
Write("{archive_path}/session-{timestamp}.md", summary)

# Update conversation context with compressed summary
# Output in Chinese at runtime
# Include: completed tasks summary, archive location, remaining capacity
```

### Compression Techniques

**Technique 1: Task Summarization**
```
Before (15,000 tokens per task):
• Full TDD cycle (RED-GREEN-REFACTOR)
• Complete code snippets
• Test outputs
• Git commit details
• Skills activation logs

After ({15000 * target_ratio} = 500 tokens per task):
• Task ID + title + status
• Key files changed
• Test coverage %
• Commit hash
• Critical decisions only
```

**Technique 2: Code Snippet Archival**
```
Before:
"Here's the complete AuthService.ts code: [500 lines]"

After:
"AuthService.ts implemented (see feat/task-1-auth commit abc123)"
```

**Technique 3: Skills Output Deduplication**
```
Before:
• code-quality-guardian report Task #1
• code-quality-guardian report Task #2
• code-quality-guardian report Task #3
[Each 2,000 tokens]

After:
"All tasks passed code quality checks (Grade: A average)"
```

## Compression Thresholds

**Load thresholds from config at runtime**:

### Green Zone (< {total_limit * thresholds.green})
- Status: Safe
- Action: Monitor, no compression needed
- Continue normal operations

### Yellow Zone ({green} - {yellow})
- Status: Warning
- Action: Suggest proactive compression
- Message: Show compression benefits, wait for confirmation (Chinese output)
- Wait for user confirmation

### Orange Zone ({yellow} - {orange})
- Status: Danger
- Action: Strongly recommend compression
- Message: Show critical warning, compression urgency (Chinese output)
- Auto-compress if user continues with ultra-dev

### Red Zone (> {orange})
- Status: Critical
- Action: BLOCK further ultra-dev, ENFORCE compression
- Message: Show critical alert, must compress (Chinese output)
- Show compression preview

## Don't
- Do not compress current task context (only completed tasks)
- Do not compress if < {trigger_task_count} tasks completed (insufficient gain, from config)
- Do not compress if token usage < ({total_limit * thresholds.green * 0.83}) (unnecessary)
- Do not delete archived information (only move to {archive_path} from config)

## Outputs

### Output Examples

**Yellow Zone ({green}-{yellow})**:
- Show current token usage
- Suggest compression with benefits
- Wait for user confirmation

**Red Zone (>{orange})**:
- Show critical warning
- Display compression plan
- Enforce compression

**Compression Complete**:
- Show before/after stats
- Provide archive location (from config)
- Show remaining capacity

*Note: All outputs in Chinese at runtime. See REFERENCE.md for detailed examples.*

## Integration with Other Skills

### With context-overflow-handler
```
context-overflow-handler: "Token usage {yellow+2K} (Yellow zone)"
    ↓
compressing-context: "Trigger compression suggestion"
    ↓
User confirms → Execute compression
    ↓
context-overflow-handler: "Token usage {green-55K} (Green zone)"
```

### With guiding-workflow
```
guiding-workflow: "Task #{trigger_task_count} completed, suggest next step"
    ↓
compressing-context: "Check if compression needed ({trigger_task_count} tasks done)"
    ↓
If needed → Compress first → Then suggest /ultra-dev
If not needed → Directly suggest /ultra-dev
```

### With ultra-dev command
```
ultra-dev: Starting task #10
    ↓
compressing-context: "Check token usage before starting"
    ↓
If >{yellow} → BLOCK, enforce compression
If {green}-{yellow} → WARN, suggest compression
If <{green} → PASS, proceed normally
```

## Performance Metrics
- Compression ratio: 40-60% (typical)
- Processing time: <10 seconds
- Token savings per compression: 50-100K tokens (typical)
- Tasks per session before compression: 5-7 → 20-30 after
