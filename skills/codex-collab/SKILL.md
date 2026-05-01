---
name: codex-collab
description: "Dual-AI collaboration with Codex. Use for architecture opinions, comparative verification, project understanding. For code review, use the official /codex:review plugin directly — this skill no longer wraps it. Triggers: 'ask Codex', 'Codex opinion', 'let Codex check', 'compare with Codex'."
argument-hint: "understand|opinion|compare|free [target]"
user-invocable: true
---

# Codex Collab - Dual AI Collaboration (OpenAI)

Use OpenAI's Codex CLI as an independent sub-agent within Claude Code. Claude orchestrates, Codex provides independent analysis powered by OpenAI models, Claude synthesizes the final result. All output goes through files — zero context pollution.

For **code review** specifically, use the official `/codex:review` plugin (or `/codex:adversarial-review`) directly — that's the dedicated, well-maintained path for the review use case. This skill covers the *non-review* collaboration modes the official plugin doesn't address.

## Prerequisites

- Codex CLI installed: `npm install -g @openai/codex`
- Authenticated: `codex login`
- Verify: `codex --version`

## Usage

```
/codex-collab understand            # Codex analyzes project structure
/codex-collab opinion <topic>       # Get Codex's take on an architecture decision
/codex-collab compare <topic>       # Both AIs answer independently, then synthesize
/codex-collab free <prompt>         # Free-form prompt to Codex
```

When the user doesn't use a subcommand but mentions Codex in a collaborative way, infer the most appropriate mode from context. **Never infer review** — route review explicitly to `/codex:review` instead.

## `codex exec` — Non-Interactive Mode

For understand/opinion/compare/free modes. Use `-o` (`--output-last-message`) to save clean output.

```bash
# Write mode (default)
codex exec "Your prompt here" --full-auto -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"

# Read-only analysis (no --full-auto, use -s read-only instead)
codex exec "Analyze this project" -s read-only -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Error Handling

- If `codex` not found: `npm install -g @openai/codex`
- If auth fails: `codex login`
- If timeout (>5min): check partial output in file
- If empty output: proceed with Claude-only analysis
- Never block the workflow on Codex failure

## Reference Files

Read these when you need details beyond what's in this SKILL.md:

- **`references/codex-cli-reference.md`** — READ when you need advanced Codex CLI flags (model selection, sandbox modes, config overrides). Contains full flag reference for `codex exec`. (The `codex review` flag reference is now redundant with the official `/codex:review` plugin — use that instead for review.)
- **`references/codex-prompts.md`** — READ when constructing Codex prompts. Contains CLI-ready prompt templates for understand/opinion/compare/free modes.
- **`references/collaboration-modes.md`** — READ when you need the detailed step-by-step flow for a specific mode. Contains definitions for understand/opinion/compare/free modes. (Review mode in this file is deprecated — see `/codex:review` instead.)
- **`references/collab-protocol.md`** — READ when writing synthesis reports or managing sessions. Contains core principles, synthesis template, session management, and error handling.
