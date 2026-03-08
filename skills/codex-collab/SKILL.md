---
name: codex-collab
description: "Invoke OpenAI Codex CLI as an independent sub-agent for code review, project analysis, architecture opinions, and comparative verification. Trigger when the user says 'ask Codex', 'Codex review', 'let Codex check', 'OpenAI opinion', or mentions 'codex' in any collaborative context."
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

Codex CLI has two distinct modes. See `references/codex-cli-reference.md` for full details.

### 1. `codex review` — Built-in Code Review (preferred for review tasks)

Purpose-built for code review. Understands git diffs natively. Capture output via `2>&1 | tee`.

```bash
codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/raw.txt"
```

### 2. `codex exec` — General Non-Interactive Mode

For any prompt beyond built-in review. Use `-o` (`--output-last-message`) to save clean output.

```bash
codex exec "Your prompt here" --full-auto -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Collaboration Protocol

See `references/collab-protocol.md` for:
- Core principles (independent thinker, no priming, Claude synthesizes)
- File-based output protocol and session management
- Synthesis report template
- Error handling

## Collaboration Modes

See `references/collaboration-modes.md` for the 5 mode definitions (review, understand, opinion, compare, free).

## Codex-Specific Prompts

See `references/codex-prompts.md` for CLI-ready prompt templates with mode-to-command mapping.

## Codex-Specific Output Handling

For `codex review`, the raw output contains MCP startup logs, shell exec logs, and the final review. Read the file and extract from the review summary onward. Save extracted findings as `output.md` alongside `raw.txt`.

## Error Handling

- If `codex` not found: `npm install -g @openai/codex`
- If auth fails: `codex login`
- If timeout (>5min): check partial output in file
- If empty output: proceed with Claude-only analysis
- Never block the workflow on Codex failure
