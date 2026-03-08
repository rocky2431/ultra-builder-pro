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

## Orchestration

### Step 1: Session Setup + Claude Analysis

Set up `SESSION_PATH` and write Claude's own analysis FIRST (before reading external AI output).

### Step 2: Launch External AIs

Launch Gemini + Codex in parallel (`run_in_background: true`).

### Step 3: MANDATORY WAIT

Run `verify_wait.py` to block until both AIs complete:

```bash
python3 ~/.claude/skills/ultra-verify/scripts/verify_wait.py "${SESSION_PATH}"
```

Do NOT read output files or start synthesis until this script returns.

### Step 4: Collect + Synthesize

Read the wait script JSON output, read available output files, compute confidence, write synthesis.

### CRITICAL: Exact CLI Commands

**Gemini** (correct — `-p` flag for non-interactive):
```bash
gemini -p "<prompt>" --yolo > "${SESSION_PATH}/gemini-output.md" 2>"${SESSION_PATH}/gemini-error.log"
```

**Codex** (correct — must use `codex exec` subcommand, NOT `codex -p` or `codex -q`):
```bash
codex exec "<prompt>" -s read-only -o "${SESSION_PATH}/codex-output.md" 2>"${SESSION_PATH}/codex-error.log"
```

**Codex for audit mode** (use built-in `codex review`):
```bash
codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/codex-raw.txt"
```

**FORBIDDEN Codex patterns** (these DO NOT WORK):
- `codex -p "prompt"` — NO `-p` flag exists
- `codex -q "prompt"` — NO `-q` flag exists
- `codex --full-auto -s read-only` — `--full-auto` conflicts with `-s read-only`

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
