# Orchestration Flow

Step-by-step execution flow for three-way cross-verification.

## 1. Session Setup

```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)-verify-<mode>"
SESSION_PATH=".ultra/collab/${SESSION_ID}"
mkdir -p "${SESSION_PATH}"
```

## 2. Claude Answers First

Claude writes its own analysis to `${SESSION_PATH}/claude-analysis.md` **BEFORE** reading any external AI output. This prevents contamination.

```
Write ${SESSION_PATH}/claude-analysis.md
```

## 3. Parallel External AI Invocation

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

## 4. Collect Results

Wait for both background tasks to complete, then read all three files:

```
Read ${SESSION_PATH}/claude-analysis.md
Read ${SESSION_PATH}/gemini-output.md
Read ${SESSION_PATH}/codex-output.md   (or codex-raw.txt for audit mode — extract findings from raw output)
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
