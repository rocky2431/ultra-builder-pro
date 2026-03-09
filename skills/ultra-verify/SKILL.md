---
name: ultra-verify
description: "This skill should be used when the user asks to 'ultra-verify', 'cross-verify', 'triple review', 'all AIs check', 'multi-AI verify', 'three-way check', or wants independent analysis from all three AI models (Claude + Gemini + Codex)."
argument-hint: "decision|diagnose|audit|estimate <question>"
user-invocable: true
---

# Ultra Verify - Three-Way AI Verification

Orchestrate Claude + Gemini + Codex for independent three-way analysis. Each AI works independently, then Claude synthesizes with a confidence score based on consensus.

## Prerequisites

- Gemini CLI installed: `npm install -g @google/gemini-cli` + authenticated
- Codex CLI installed: `npm install -g @openai/codex` + `codex login`
- Verify both: `gemini --version && codex --version`

## Usage

```
/ultra-verify decision <question>    # Architecture/design decision — three independent analyses
/ultra-verify diagnose <symptoms>    # Bug diagnosis — three sets of hypotheses
/ultra-verify audit <scope>          # Code audit — findings ranked by consensus
/ultra-verify estimate <task>        # Effort estimation — confidence from agreement
```

## Workflow Tracking (MANDATORY)

**On command start**, create tasks for each major step using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 1 | Session Setup + Claude Analysis | Writing Claude analysis... |
| 2 | Launch External AIs | Launching Gemini + Codex... |
| 3 | Wait for Completion | Waiting for AI outputs... |
| 4 | Collect + Synthesize | Synthesizing results... |

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**On context recovery**: `TaskList` → resume from last incomplete step

## Orchestration — STRICT SEQUENTIAL EXECUTION

**RULE: Each step REQUIRES the output of the previous step. Never skip ahead. Never start synthesis without wait script JSON.**

### Step 1: Session Setup + Claude Analysis

```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)-verify-<mode>"
SESSION_PATH=".ultra/collab/${SESSION_ID}"
mkdir -p "${SESSION_PATH}"
```

Write Claude's own analysis to `${SESSION_PATH}/claude-analysis.md` FIRST (before reading external AI output).

### Step 2: Launch External AIs (both `run_in_background: true`, `timeout: 600000`)

Launch BOTH commands in a **single message** with two parallel Bash calls. Both MUST use `run_in_background: true`.

**Gemini** (all modes):
```bash
gemini -p "<PROMPT>" --yolo > "${SESSION_PATH}/gemini-output.md" 2>"${SESSION_PATH}/gemini-error.log"
```

**Codex** (all modes — always use `codex exec`):
```bash
codex exec "<PROMPT>" -s read-only -o "${SESSION_PATH}/codex-output.md" 2>"${SESSION_PATH}/codex-error.log"
```

**CRITICAL PROHIBITION** (after launching background tasks):
1. Run `verify_wait.py` IMMEDIATELY in the **next message** — do NOT process background task notifications first
2. NEVER read gemini-output.md or codex-output.md directly — wait for the wait script
3. Ignore ALL background task completion/idle notifications between launch and wait script return
4. The ONLY information path from external AIs is: `verify_wait.py` JSON → then Read output files

Violation of these rules causes premature synthesis without external AI input.

### Step 3: BACKGROUND WAIT

**IMMEDIATELY** after Step 2 (in the very next message), run this as a **background** Bash command:

```bash
python3 ~/.claude/skills/ultra-verify/scripts/verify_wait.py "${SESSION_PATH}" --timeout 1200
```

Use `run_in_background: true` (no Bash 600s limit for background tasks). The script polls every 3s for up to 20 minutes.

Two exit conditions:
1. **Output ready**: output file non-empty (size > 0) and size unchanged between consecutive polls → `status: "complete"`
2. **Timeout**: reached 1200s limit → `status: "timeout"`

Always exit 0. Result expressed via JSON `status` field.

When the background task completes, read the JSON output and proceed to Step 4.

### Step 4: Collect + Synthesize (REQUIRES Step 3 JSON)

**Do NOT enter this step without the JSON output from Step 3.**

1. **Parse the wait script JSON** — extract `gemini.status` and `codex.status`
2. **Read output files** only for AIs with `"complete"` status
3. **Compute confidence** — see `references/confidence-system.md`
4. **Write synthesis** — see `references/collab-protocol.md` for template

If both AIs failed → Claude-only analysis with explicit warning.
If one AI failed → two-way synthesis, note missing perspective.

### Session Structure

```
.ultra/collab/<SESSION_ID>/
  ├── metadata.json
  ├── claude-analysis.md
  ├── gemini-output.md
  ├── codex-output.md
  └── synthesis.md
```

## Modes

- **decision** — Architecture/design decisions with three independent recommendations
- **diagnose** — Bug diagnosis with three sets of top-3 hypotheses, ranked by consensus
- **audit** — Code audit with findings graded by consensus count (3=critical, 2=high, 1=investigate)
- **estimate** — Effort estimation with confidence based on estimate convergence

## Confidence System

| Level | Agreement | Meaning |
|-------|-----------|---------|
| **Consensus** | 3/3 agree | Highest confidence — strongly recommended |
| **Majority** | 2/3 agree | High confidence — investigate the dissenting view |
| **No Consensus** | All differ | Low confidence — decompose the problem or gather more data |

## Degraded Operation

- **One AI fails**: Continue with two-way comparison, note the missing perspective
- **Two AIs fail**: Claude-only analysis with explicit warning about reduced confidence
- Never block the workflow on external AI failures

## Reference Files

Read these when you need details beyond what's in this SKILL.md:

- **`references/orchestration-flow.md`** — READ when setting up session dirs, collecting results, or writing metadata.json. Contains session setup commands, parallel invocation patterns, result collection steps, and metadata schema.
- **`references/cross-verify-modes.md`** — READ when you need mode-specific prompt templates or scoring criteria. Contains detailed definitions for decision/diagnose/audit/estimate modes.
- **`references/confidence-system.md`** — READ when computing confidence scores. Contains consensus calculation rules and thresholds.
- **`references/collab-protocol.md`** — READ when writing synthesis reports. Contains core principles, synthesis report template, session management, and error handling.
