# Orchestration Flow

Step-by-step execution flow for three-way cross-verification.

## 0. Workflow Tasks

See the task table in SKILL.md `## Workflow Tracking (MANDATORY)`. Steps below map to those 4 tasks. Substeps (4a/4b/4c) are part of Task 4, not separate TaskCreate items.

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

Launch BOTH commands in a **single message** with two parallel Bash calls. Both MUST use `run_in_background: true` and `timeout: 600000`.

**Gemini** (all modes):
```bash
gemini -p "<PROMPT>" --yolo > "${SESSION_PATH}/gemini-output.md" 2>"${SESSION_PATH}/gemini-error.log"
```

**Codex** (all modes — always use `codex exec`):
```bash
codex exec "<PROMPT>" -s read-only -o "${SESSION_PATH}/codex-output.md" 2>"${SESSION_PATH}/codex-error.log"
```

**CRITICAL PROHIBITION** (after launching background tasks):
1. Run `verify_wait.py` IMMEDIATELY in the **next message**
2. NEVER read output files directly — wait for the wait script
3. Ignore ALL background task completion/idle notifications between launch and wait script return
4. The ONLY information path: `verify_wait.py` JSON → then Read output files

## 3. BACKGROUND WAIT — Strict Dependency Gate

**IMMEDIATELY** after launching Step 2 background tasks, run this as a **background** Bash command:

```bash
python3 ~/.claude/skills/ultra-verify/scripts/verify_wait.py "${SESSION_PATH}" --timeout 1200
```

Use `run_in_background: true`. Background tasks bypass the Bash tool's 600s foreground limit, allowing a full 20-minute wait.

**Two exit conditions:**
1. **Output ready**: output file non-empty (size > 0) and size unchanged between consecutive polls (3s) → exit 0, `status: "complete"`
2. **Timeout**: reached 1200s limit → exit 0, `status: "timeout"`

Always exit 0. Result expressed via JSON `status` field. Error logs only checked at timeout.

**HARD RULES — violation = broken workflow:**
- Wait for the background task completion notification before proceeding
- Do NOT read gemini-output.md or codex-output.md before this completes
- Do NOT write synthesis.md before this completes
- Do NOT skip this step even if you believe the AIs already finished
- The JSON output from this command is the REQUIRED input for Step 4

JSON output on stdout:

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

**After wait returns**, parse the JSON and proceed based on status:
- Both `complete` → full three-way synthesis
- One `failed`/`empty` → two-way synthesis (degraded)
- Both `failed` → Claude-only analysis

## 4. Collect + Synthesize (REQUIRES Step 3 JSON — never start without it)

This step covers collecting results, computing confidence, and writing synthesis (substeps 4a-4c).

### 4a. Collect Results

Read all available output files:

```
Read ${SESSION_PATH}/claude-analysis.md
Read ${SESSION_PATH}/gemini-output.md    (if gemini status = complete)
Read ${SESSION_PATH}/codex-output.md     (if codex status = complete)
```

### 4b. Compute Confidence

Compare the three analyses:
1. Identify points of agreement (consensus items)
2. Identify majority positions (2/3 agreement)
3. Identify unique positions (1/3 only)
4. Apply the confidence system from `confidence-system.md`

### 4c. Write Synthesis

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

## 5. Degraded Handling

If one AI fails:
- Continue with two-way comparison
- Set `"degraded": true` in metadata
- Note the missing perspective in synthesis
- Confidence is capped at "Majority" level

If two AIs fail:
- Claude-only analysis
- Set `"degraded": true` + `"agents_responded": ["claude"]`
- Explicitly warn: "Single-source analysis — no consensus scoring available"

## Timeout Design

- External AI Bash calls: `run_in_background: true` (no foreground timeout limit)
- verify_wait.py: `run_in_background: true`, `--timeout 1200` (20 min)
- Codex typically takes 1-5 minutes, rarely exceeds 10
- Error logs are ONLY checked at timeout — CLIs write startup info to stderr even on success
