---
name: ultra-review
description: "Parallel code review orchestration with 6 specialized agents + coordinator. Zero context pollution - all output via JSON files."
user-invocable: true
---

# /ultra-review - Ultra Review System

Orchestrates parallel code review using specialized agents. All findings written to JSON files to prevent context window pollution.

## Usage

```
/ultra-review              # Full review (smart skip based on diff content)
/ultra-review all          # Force ALL 6 agents, no auto-skip (pre-merge gate)
/ultra-review quick        # Quick review (review-code only)
/ultra-review security     # Security focus (review-code + review-errors)
/ultra-review tests        # Test quality focus (review-tests only)
/ultra-review recheck      # Re-check only P0/P1 files from last session
/ultra-review delta        # Review only changes since last review session
/ultra-review <agents...>  # Custom: e.g., /ultra-review tests errors types
```

### Scope Options (combinable with any mode)

```
/ultra-review --pr 123            # Review PR #123 diff (base...head)
/ultra-review --range main..HEAD  # Review specific commit range
/ultra-review --range abc123      # Review single commit
/ultra-review security --pr 42    # Security review scoped to PR #42
```

## Orchestration Flow

### Phase 1: Setup & Scope Detection

```python
# 1. Determine session context
BRANCH = git branch --show-current            # e.g., "feat/task-3-auth"
ITER = count existing sessions matching this branch + 1  # iteration number

# 2. Create session directory with full context
SESSION_ID = "<YYYYMMDD-HHmmss>-<branch>-iter<N>"
# e.g., "20260214-103000-feat-task-3-auth-iter2"
SESSION_PATH = ".ultra/reviews/{SESSION_ID}/"
mkdir -p SESSION_PATH

# 3. Update session index (placeholder — verdict filled in Phase 5)
# Append entry to .ultra/reviews/index.json with verdict="pending"
# See Session Index below for full schema

# 4. Cleanup (see Lifecycle Management below)

# 5. Detect diff scope (priority order)
```

**Scope resolution priority:**

| Flag | Diff Command | DIFF_RANGE |
|------|-------------|------------|
| `--pr NUMBER` | `gh pr diff NUMBER --name-only` | PR base...head |
| `--range RANGE` | `git diff RANGE --name-only` | Specified range |
| _(default)_ | `git diff --name-only HEAD` + `git diff --cached --name-only` | HEAD (unstaged + staged) |

**PR scope details** (`--pr NUMBER`):
```bash
# Get PR metadata for session naming
gh pr view NUMBER --json headRefName,baseRefName,title
# Get changed files
gh pr diff NUMBER --name-only
# Set DIFF_RANGE to base...head for agents
DIFF_RANGE="$(gh pr view NUMBER --json baseRefName -q .baseRefName)..HEAD"
```

**Range scope details** (`--range RANGE`):
```bash
git diff RANGE --name-only
DIFF_RANGE="RANGE"
```

### Phase 2: Agent Selection

Based on the mode argument and file classification:

**Mode: `full` (default)**
Select all applicable agents based on diff content:

| Agent | Skip Condition | Warning |
|-------|---------------|---------|
| review-code | Never skip | - |
| review-tests | No test files in diff AND no source files without tests | WARN: "Code changed without test updates" |
| review-errors | No error handling code detected | - |
| review-types | No type definitions in diff | - |
| review-comments | No comment changes in diff | - |
| review-simplify | No function-level changes | - |

**Auto-skip detection commands:**
```bash
# Has type definitions?
grep -l "interface \|type \|class \|enum " <diff_files>

# Has comment changes?
git diff HEAD -- <diff_files> | grep "^[+-].*//\|^[+-].*\*\|^[+-].*#"

# Has test files?
echo "<diff_files>" | grep -E "\.(test|spec)\.(ts|tsx|js|jsx)$|test_.*\.py$|.*_test\.go$"

# Has error handling?
grep -l "try\|catch\|\.catch\|throw\|Error(" <diff_files>
```

**Mode: `all`** → Force ALL 6 agents, no auto-skip. Use for pre-merge gates (`/ultra-dev`).
**Mode: `quick`** → review-code only
**Mode: `security`** → review-code + review-errors
**Mode: `tests`** → review-tests only
**Mode: `recheck`** → See Recheck Logic below
**Mode: `delta`** → See Delta Logic below
**Mode: custom** → Parse agent names from arguments

### Phase 3: Background Execution (Zero Context Pollution)

Launch ALL selected agents in **background mode** (`run_in_background: true`) using multiple Task tool calls in a single message. This prevents agent output from polluting the main conversation context.

Each agent receives this prompt template:

```
You are running as part of /ultra-review pipeline.

SESSION_PATH: {SESSION_PATH}
OUTPUT_FILE: {agent-name}.json
DIFF_FILES: {comma-separated file list}
DIFF_RANGE: {resolved DIFF_RANGE from Phase 1}

Review the changed files and write your findings as JSON to:
{SESSION_PATH}/{agent-name}.json

Follow the ultra-review-findings-v1 schema exactly. Read the schema from:
~/.claude/skills/ultra-review/references/unified-schema.md

Only report findings with confidence >= 75.

After writing the JSON file, output one line: "Wrote N findings (P0:X P1:X P2:X P3:X) to <filepath>"
```

**Important**: Use `subagent_type` matching the agent name (e.g., `review-code`, `review-tests`, etc.).

**Important**: Set `run_in_background: true` on every Task call. Do NOT read TaskOutput — this avoids injecting agent results into main context.

Maximum 15 findings per agent. If you find more, report only the top 15 by severity (P0 first),
then confidence. Note total count in your output line: "Wrote 15/23 findings..."

**CRITICAL PROHIBITION**: After launching background agents, you MUST:
1. Call `review_wait.py` IMMEDIATELY — do NOT process idle notifications
2. NEVER call TaskOutput for any review agent — their output goes to JSON files only
3. Ignore all agent idle/completion messages between launch and wait script return
4. The ONLY information path from agents is: wait script → Read SUMMARY.json

Violation of these rules causes context overflow. The review agents write to files; you read from files.

### Phase 4: Wait & Coordinate (File-Based)

**Step 4a: Wait for agents** — Use Bash to block until all agents finish writing:

```bash
python3 ~/.claude/skills/ultra-review/scripts/review_wait.py {SESSION_PATH} agents {AGENT_COUNT}
```

This polls for `review-*.json` files every 2 seconds. Timeout: 5 minutes.
Output is structured JSON on stdout:
- `status: "complete"` → all agents done, proceed normally
- `status: "partial"` → timeout, log missing agents, pass only `agents_done` to coordinator, note partial review in SUMMARY
- Exit code 1 (0 agents) → skip review, warn user, allow ultra-dev to continue

**Step 4b: Launch coordinator in background:**

Launch review-coordinator with `run_in_background: true`:

```
You are the review coordinator.

SESSION_PATH: {SESSION_PATH}
AGENTS_RUN: {list of agents from wait output}

Read all review-*.json files in the session directory, deduplicate findings,
compute verdict, and generate SUMMARY.md + SUMMARY.json.
```

**Step 4c: Wait for coordinator:**

```bash
python3 ~/.claude/skills/ultra-review/scripts/review_wait.py {SESSION_PATH} summary
```

Output is a single verdict line (~15 tokens).

### Phase 5: Report to User

After `review_wait.py summary` returns:

1. **Read SUMMARY.json** (one Read call, ~500 tokens) to get verdict and counts
2. **Update index.json** — fill in the placeholder entry with actual verdict, p0, p1, total from SUMMARY.json
3. Present a concise summary:

```markdown
## Review Complete

**Verdict**: {APPROVE | COMMENT | REQUEST_CHANGES}
**Findings**: X total (P0: A, P1: B, P2: C, P3: D)
**Agents**: N ran, M succeeded

### Top Findings
1. [P0] {title} - {file}:{line}
2. [P1] {title} - {file}:{line}
3. ...
(show up to 5 most critical findings)

Full report: {SESSION_PATH}/SUMMARY.md
```

Then ask the user:
1. **Fix all** - Fix all P0 and P1 issues
2. **Fix P0 only** - Fix only critical issues
3. **View full report** - Read SUMMARY.md
4. **Skip** - No fixes needed

## Recheck Logic

When mode is `recheck`:
1. Find the most recent session **for the current branch** in `index.json`
2. Read its `SUMMARY.json`
3. Extract files with P0 or P1 findings
4. Run review-code only on those specific files
5. Compare with previous findings to show delta (resolved / new / unchanged)

## Delta Logic

When mode is `delta`:
1. Find the most recent session **for the current branch** in `index.json`
2. Read its `SUMMARY.json` to get the scope of last review
3. Identify files changed since the last review:
   ```bash
   # If last session was commit-based, diff from that commit
   git diff --name-only <last-reviewed-commit>..HEAD
   # If last session was working-tree-based, diff current unstaged + staged
   git diff --name-only HEAD
   ```
4. **Exclude** files that have NOT changed since last review (already reviewed)
5. Run full agent set only on the newly changed files
6. In coordinator, merge with previous session findings (carry forward unresolved P0/P1)

**Use case**: Iterative development — fix issues, add code, only review what's new.

## Session Index

A lightweight index file tracks all sessions for cross-referencing:

**File**: `.ultra/reviews/index.json`

```json
{
  "sessions": [
    {
      "id": "20260214-103000-feat-task-3-auth-iter1",
      "branch": "feat/task-3-auth",
      "iteration": 1,
      "mode": "full",
      "timestamp": "2026-02-14T10:30:00Z",
      "verdict": "REQUEST_CHANGES",
      "p0": 2,
      "p1": 3,
      "total": 12,
      "parent": null
    },
    {
      "id": "20260214-113000-feat-task-3-auth-iter2",
      "branch": "feat/task-3-auth",
      "iteration": 2,
      "mode": "recheck",
      "timestamp": "2026-02-14T11:30:00Z",
      "verdict": "COMMENT",
      "p0": 0,
      "p1": 1,
      "total": 4,
      "parent": "20260214-103000-feat-task-3-auth-iter1"
    }
  ]
}
```

**Fields**:

| Field | Description |
|-------|-------------|
| `id` | Session directory name |
| `branch` | Git branch at review time |
| `iteration` | Nth review for this branch (auto-incremented) |
| `mode` | Review mode used (full/quick/security/recheck/delta) |
| `timestamp` | ISO 8601 |
| `verdict` | APPROVE / COMMENT / REQUEST_CHANGES |
| `p0`, `p1`, `total` | Finding counts from SUMMARY.json |
| `parent` | Previous session ID for this branch (forms iteration chain) |

**Branch-scoped queries**:
- `recheck` / `delta`: filter `index.json` by `branch == current branch`, take latest
- Avoids cross-task pollution when multiple branches are active

## Lifecycle Management

**Cleanup strategy** (runs at Phase 1 of every `/ultra-review`):

| Rule | Action |
|------|--------|
| Session > 7 days AND verdict = APPROVE | Delete directory + remove from index |
| Session > 7 days AND verdict = COMMENT | Delete directory + remove from index |
| Session > 7 days AND verdict = REQUEST_CHANGES | **Keep** (unresolved P0s should not be silently deleted) |
| Session > 30 days (any verdict) | Delete directory + remove from index |
| Per-branch limit: > 5 sessions | Delete oldest APPROVE/COMMENT sessions for that branch |

**Implementation**:
```python
# In Phase 1, after creating session directory:
index = read index.json (or create if missing)

# 1. Remove stale sessions
now = current_time()
for session in index.sessions:
    age_days = (now - session.timestamp).days
    if age_days > 30:
        delete(session)
    elif age_days > 7 and session.verdict != 'REQUEST_CHANGES':
        delete(session)

# 2. Per-branch cap (keep latest 5)
branch_sessions = [s for s in index.sessions if s.branch == current_branch]
if len(branch_sessions) > 5:
    # Sort by timestamp, keep latest 5, delete rest (except REQUEST_CHANGES)
    to_remove = sorted(branch_sessions, key=timestamp)[:-5]
    for s in to_remove:
        if s.verdict != 'REQUEST_CHANGES':
            delete(s)

# 3. Write updated index
write index.json
```

## Fix Flow

When user selects "Fix all" or "Fix P0 only" after review:

**Step 0: Context Reset** (if verdict is REQUEST_CHANGES):
- Run `/compact` to clear TDD cycle history from context
- After compact, read `.ultra/workflow-state.json` to restore task context
- Read `SUMMARY.json` fresh to get actionable findings
- Then proceed with fixes below

1. **Read SUMMARY.json** — extract actionable P0/P1 items, sort by severity (P0 first)
2. **Group by file** — organize findings per file
3. **For each file with findings**:
   a. Read the file once
   b. Apply ALL P0/P1 fixes for that file (batch within same file)
   c. Run the RELEVANT test file only:
      - Detect: `foo.ts` → `foo.test.ts` / `foo.spec.ts`
      - Run: `npx jest <test-file> --bail` or `pytest <test-file> -x`
   d. If test passes → mark findings as addressed, move to next file
   e. If test fails from THIS fix → revert file, try alternative approach
   f. If test fails from pre-existing issue → note it, continue
4. **After all files fixed**: run FULL test suite once as validation
5. **Update verdict** — after all P0 fixes applied and tests pass:
   ```bash
   python3 ~/.claude/skills/ultra-review/scripts/review_verdict_update.py {SESSION_PATH}
   ```
   This recalculates the verdict from current P0/P1 counts and updates both SUMMARY.json and index.json.
   Without this step, pre_stop_check will block on stale REQUEST_CHANGES verdict.
6. **Optionally**: `/ultra-review recheck` (counts as iteration, respects max 2 cap)

**Important**: The main agent (not review agents) performs fixes. Review agents are read-only by design.

## Integration with ultra-dev

This skill integrates with the TDD workflow:
- After `tdd-runner` confirms tests pass
- Before `commit` or PR creation
- Quick mode for iterative development
- Full mode for pre-merge gate
- Recheck mode after fixing review findings
- Delta mode for incremental review during long development sessions

## Error Handling

- If no diff detected: inform user, suggest using `--range` or `--pr` to specify scope
- If `--pr` fails (no gh CLI or no PR): fall back to default diff and warn user
- If an agent fails to write JSON: note in coordinator input, skip that agent's findings
- If coordinator fails: fall back to reading individual JSON files and presenting raw findings
- If no agents selected (all skipped): inform user with skip reasons

## Directory Structure

```
.ultra/reviews/
  ├── index.json                                    # Session index (all sessions metadata)
  ├── 20260214-103000-feat-task-3-auth-iter1/       # First review
  │   ├── review-code.json
  │   ├── review-tests.json
  │   ├── review-errors.json
  │   ├── review-types.json
  │   ├── review-comments.json
  │   ├── review-simplify.json
  │   ├── SUMMARY.json
  │   └── SUMMARY.md
  └── 20260214-113000-feat-task-3-auth-iter2/       # Recheck after fixes
      ├── review-code.json
      ├── SUMMARY.json
      └── SUMMARY.md
```
