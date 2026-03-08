---
name: codex-collab
description: "This skill should be used when the user asks to 'ask Codex', 'Codex review', 'let Codex check', 'OpenAI opinion', or mentions 'codex' in any collaborative context for code review, project analysis, architecture opinions, or comparative verification."
argument-hint: "review|understand|opinion|compare|free [target]"
user-invocable: true
---

# Codex Collab - Dual AI Collaboration (OpenAI)

Use OpenAI's Codex CLI as an independent sub-agent within Claude Code. Claude orchestrates, Codex provides independent analysis powered by OpenAI models, Claude synthesizes the final result. All output goes through files — zero context pollution.

## Prerequisites

- Codex CLI installed: `npm install -g @openai/codex`
- Authenticated: `codex login`
- Verify: `codex --version`

## Usage

```
/codex-collab review                # Codex reviews current uncommitted changes
/codex-collab review <file>         # Codex reviews specific file(s)
/codex-collab review --base main    # Codex reviews changes against main branch
/codex-collab understand            # Codex analyzes project structure
/codex-collab opinion <topic>       # Get Codex's take on an architecture decision
/codex-collab compare <topic>       # Both AIs answer independently, then synthesize
/codex-collab free <prompt>         # Free-form prompt to Codex
```

When the user doesn't use a subcommand but mentions Codex in a collaborative way, infer the most appropriate mode from context.

## Two Invocation Modes

Codex CLI has two distinct modes.

### 1. `codex review` — Built-in Code Review (preferred for review tasks)

Purpose-built for code review. Understands git diffs natively. Capture output via `2>&1 | tee`.

```bash
codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/raw.txt"
```

### 2. `codex exec` — General Non-Interactive Mode

For any prompt beyond built-in review. Use `-o` (`--output-last-message`) to save clean output.

```bash
# Write mode (default)
codex exec "Your prompt here" --full-auto -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"

# Read-only analysis (no --full-auto, use -s read-only instead)
codex exec "Analyze this project" -s read-only -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

**FORBIDDEN Codex patterns** (these DO NOT WORK):
- `codex -p "prompt"` — NO `-p` flag exists, use `codex exec "prompt"`
- `codex -q "prompt"` — NO `-q` flag exists
- `codex --full-auto -s read-only` — `--full-auto` implies workspace-write, conflicts with `-s read-only`

## Output Handling

For `codex review`, the raw output contains MCP startup logs, shell exec logs, and the final review. Read the file and extract from the review summary onward. Save extracted findings as `output.md` alongside `raw.txt`.

## Error Handling

- If `codex` not found: `npm install -g @openai/codex`
- If auth fails: `codex login`
- If timeout (>5min): check partial output in file
- If empty output: proceed with Claude-only analysis
- Never block the workflow on Codex failure

## Reference Files

Read these when you need details beyond what's in this SKILL.md:

- **`references/codex-cli-reference.md`** — READ when you need advanced Codex CLI flags (model selection, sandbox modes, config overrides). Contains full flag reference for both `codex review` and `codex exec`.
- **`references/codex-prompts.md`** — READ when constructing Codex prompts. Contains CLI-ready prompt templates for each collaboration mode with correct command mapping (review vs exec).
- **`references/collaboration-modes.md`** — READ when you need the detailed step-by-step flow for a specific mode. Contains definitions for review/understand/opinion/compare/free modes.
- **`references/collab-protocol.md`** — READ when writing synthesis reports or managing sessions. Contains core principles, synthesis template, session management, and error handling.
