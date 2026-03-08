---
name: ultra-verify
description: "Three-way AI cross-verification using Claude + Gemini + Codex. Trigger when the user says 'ultra-verify', 'cross-verify', 'triple review', 'all AIs', 'multi-AI', 'three-way check', or wants independent analysis from all three AI models."
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

## Orchestration

See `references/orchestration-flow.md` for the full parallel execution flow. Summary:

1. **Claude answers FIRST** (writes to file BEFORE reading external AI output)
2. **Gemini + Codex run in parallel** (`run_in_background: true`)
3. **Claude reads all three outputs** via Read tool
4. **Compute confidence** based on consensus (see `references/confidence-system.md`)
5. **Write synthesis** to `SESSION_PATH/synthesis.md`

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

See `references/cross-verify-modes.md` for detailed mode definitions:

- **decision** — Architecture/design decisions with three independent recommendations
- **diagnose** — Bug diagnosis with three sets of top-3 hypotheses, ranked by consensus
- **audit** — Code audit with findings graded by consensus count (3=critical, 2=high, 1=investigate)
- **estimate** — Effort estimation with confidence based on estimate convergence

## Confidence System

See `references/confidence-system.md`:

| Level | Agreement | Meaning |
|-------|-----------|---------|
| **Consensus** | 3/3 agree | Highest confidence — strongly recommended |
| **Majority** | 2/3 agree | High confidence — investigate the dissenting view |
| **No Consensus** | All differ | Low confidence — decompose the problem or gather more data |

## Degraded Operation

- **One AI fails**: Continue with two-way comparison, note the missing perspective
- **Two AIs fail**: Claude-only analysis with explicit warning about reduced confidence
- Never block the workflow on external AI failures

## Collaboration Protocol

See `references/collab-protocol.md` for shared principles, file output protocol, and session management.
