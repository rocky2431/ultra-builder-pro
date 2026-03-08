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

## 2. Parallel External AI Invocation (Agent-based)

Launch BOTH agents in a **single message** with two parallel `Agent` tool calls. Both MUST use `run_in_background: true`.

**Gemini** — `verify-gemini` agent:
- prompt: include analysis question/scope + output file paths
- Output: `${SESSION_PATH}/gemini-output.md`
- Error: `${SESSION_PATH}/gemini-error.log`

**Codex** — `verify-codex` agent:
- prompt: include analysis question/scope, mode, + output file paths
- Output: `${SESSION_PATH}/codex-output.md` (or `codex-raw.txt` for audit)
- Error: `${SESSION_PATH}/codex-error.log`

Agents handle CLI invocation internally via their collab skills (`gemini-collab`, `codex-collab`).
Output files are written atomically with the Write tool (complete or absent — no partial writes).

## 3. BLOCKING WAIT — Strict Dependency Gate

**IMMEDIATELY** after launching Step 2 background tasks, run this as a **foreground** (NOT background) Bash command:

```bash
python3 ~/.claude/skills/ultra-verify/scripts/verify_wait.py "${SESSION_PATH}" --timeout 300
```

**HARD RULES — violation = broken workflow:**
- This command BLOCKS until both AIs finish or timeout (up to 5 min)
- Do NOT read gemini-output.md or codex-output.md before this returns
- Do NOT write synthesis.md before this returns
- Do NOT skip this step even if you believe the AIs already finished
- The JSON output from this command is the REQUIRED input for Step 4

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
Read ${SESSION_PATH}/codex-output.md     (if codex status = complete, or codex-raw.txt for audit mode)
```

For `codex review` raw output: read `codex-raw.txt`, extract the review findings (skip MCP/shell logs), save cleaned content as `codex-output.md`.

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

## Agent Timeout

Agents handle their own CLI timeout internally (4 minutes per agent, configured in agent frontmatter `maxTurns: 10`).
The wait script has its own 5-minute timeout as a safety net.
