# Orchestration Flow

Step-by-step execution flow for three-way cross-verification.

## 0. Create Tasks (MANDATORY — before anything else)

Create one task per step using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 1 | Session Setup + Claude Analysis | Writing Claude analysis... |
| 2 | Launch External AIs | Launching Gemini + Codex... |
| 3 | Wait for Completion | Waiting for AI outputs... |
| 4 | Collect + Synthesize | Synthesizing results... |

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**Recovery after compact**: Run `TaskList`, find incomplete ultra-verify tasks, resume from last incomplete step.

## 1. Session Setup + Claude Analysis

```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)-verify-<mode>"
SESSION_PATH=".ultra/collab/${SESSION_ID}"
mkdir -p "${SESSION_PATH}"
```

Claude writes its own analysis to `${SESSION_PATH}/claude-analysis.md` **BEFORE** reading any external AI output. This prevents contamination.

```
Write ${SESSION_PATH}/claude-analysis.md
```

## 2. Parallel External AI Invocation

Launch Gemini and Codex simultaneously using `run_in_background: true`:

**Gemini:**
```bash
gemini -p "<prompt>" --yolo > "${SESSION_PATH}/gemini-output.md" 2>"${SESSION_PATH}/gemini-error.log"
```

**Codex:**
```bash
codex exec "<prompt>" -s read-only -o "${SESSION_PATH}/codex-output.md" 2>"${SESSION_PATH}/codex-error.log"
```

For `audit` mode using `codex review`:
```bash
codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/codex-raw.txt"
```

Set Bash timeout to 300000ms for both.

## 3. Wait for Completion (MANDATORY)

**CRITICAL**: After launching background tasks, you MUST run the wait script. Do NOT read output files or start synthesis until the wait script returns.

```bash
python3 ~/.claude/skills/ultra-verify/scripts/verify_wait.py "${SESSION_PATH}"
```

The script polls every 3 seconds for up to 5 minutes, checking for output files from both AIs. It returns structured JSON on stdout:

```json
{
  "status": "complete",
  "gemini": {"name": "gemini", "status": "complete", "file": "..."},
  "codex": {"name": "codex", "status": "complete", "file": "..."},
  "elapsed_seconds": 45
}
```

Possible per-AI status values:
- `"complete"` — output file exists and is non-empty
- `"failed"` — error log exists but no output (CLI error)
- `"empty"` — output file exists but is empty
- `"pending"` — no output yet (only on timeout)

**After wait returns**, read the JSON output and proceed:
- Both `complete` → full three-way synthesis
- One `failed`/`empty` → two-way synthesis (degraded)
- Both `failed` → Claude-only analysis

## 4. Collect Results

Read all available output files:

```
Read ${SESSION_PATH}/claude-analysis.md
Read ${SESSION_PATH}/gemini-output.md    (if gemini status = complete)
Read ${SESSION_PATH}/codex-output.md     (if codex status = complete, or codex-raw.txt for audit mode)
```

For `codex review` raw output: read `codex-raw.txt`, extract the review findings (skip MCP/shell logs), save cleaned content as `codex-output.md`.

## 5. Compute Confidence

Compare the three analyses:
1. Identify points of agreement (consensus items)
2. Identify majority positions (2/3 agreement)
3. Identify unique positions (1/3 only)
4. Apply the confidence system from `confidence-system.md`

## 6. Write Synthesis

Write `${SESSION_PATH}/synthesis.md` with:
- Mode and scope
- Per-AI summary (3 sections)
- Consensus items with confidence level
- Majority items with dissent analysis
- Unique items worth investigating
- Action items prioritized by confidence
- Overall confidence assessment

Write `${SESSION_PATH}/metadata.json`:
```json
{
  "id": "<SESSION_ID>",
  "agent": "ultra-verify",
  "mode": "<mode>",
  "models": {
    "claude": "claude-opus-4-6",
    "gemini": "<model>",
    "codex": "<model>"
  },
  "scope": "<what was analyzed>",
  "timestamp": "<ISO 8601>",
  "confidence": "<consensus|majority|no_consensus>",
  "degraded": false
}
```

## 7. Degraded Handling

If one AI fails:
- Continue with two-way comparison
- Set `"degraded": true` in metadata
- Note the missing perspective in synthesis
- Confidence is capped at "Majority" level

If two AIs fail:
- Claude-only analysis
- Set `"degraded": true` + `"agents_responded": ["claude"]`
- Explicitly warn: "Single-source analysis — no consensus scoring available"

## Bash Timeout

All external AI calls: `timeout: 300000` (5 minutes). Check partial output on timeout.
