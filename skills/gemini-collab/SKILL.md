---
name: gemini-collab
description: "This skill should be used when the user asks to 'ask Gemini', 'Gemini review', 'let Gemini check', 'Gemini analysis', 'dual AI', or mentions 'gemini' in any collaborative context for code review, project analysis, architecture opinions, or comparative verification."
argument-hint: "review|understand|opinion|compare|free [target]"
user-invocable: true
---

# Gemini Collab - Dual AI Collaboration

Use Gemini CLI as an independent sub-agent within Claude Code. Claude orchestrates, Gemini provides independent analysis, Claude synthesizes the final result. All output goes through files — zero context pollution.

## Prerequisites

- Gemini CLI installed: `npm install -g @google/gemini-cli`
- Authenticated: `gemini` should work in terminal
- Verify: `gemini --version`

## Usage

```
/gemini-collab review                # Gemini reviews current changes
/gemini-collab review <file>         # Gemini reviews specific file(s)
/gemini-collab understand            # Gemini analyzes project structure
/gemini-collab opinion <topic>       # Get Gemini's take on an architecture decision
/gemini-collab compare <topic>       # Both AIs answer independently, then synthesize
/gemini-collab free <prompt>         # Free-form prompt to Gemini
```

When the user doesn't use a subcommand but mentions Gemini in a collaborative way, infer the most appropriate mode from context.

## How to Call Gemini

```bash
SESSION_PATH=".ultra/collab/$(date +%Y%m%d-%H%M%S)-gemini-<mode>"
mkdir -p "${SESSION_PATH}"

# Standard call — output goes to stdout by default (no -o flag needed)
gemini -p "Your prompt here" --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"

# With file context piped in
cat file.py | gemini -p "Review this code" --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"

# Always read output with Read tool, never rely on Bash stdout
```

**Important:**
- Always redirect to file with `> output.md`
- Always use `--yolo` for auto-approve in headless mode
- Use `2>"${SESSION_PATH}/error.log"` to suppress stderr noise
- Use the Read tool to read output files
- Set Bash timeout to 300000ms for large analyses

## Error Handling

- If `gemini` not found: `npm install -g @google/gemini-cli`
- If timeout (>5min): check partial output in file
- If empty output: proceed with Claude-only analysis
- Never block the workflow on Gemini failure

## Reference Files

Read these when you need details beyond what's in this SKILL.md:

- **`references/gemini-cli-reference.md`** — READ when you need advanced Gemini CLI flags (model selection, sandbox, output format). Contains full flag reference, approval modes, and pipe patterns.
- **`references/gemini-prompts.md`** — READ when constructing Gemini prompts. Contains CLI-ready prompt templates for each collaboration mode with recommended model per mode.
- **`references/collaboration-modes.md`** — READ when you need the detailed step-by-step flow for a specific mode. Contains definitions for review/understand/opinion/compare/free modes.
- **`references/collab-protocol.md`** — READ when writing synthesis reports or managing sessions. Contains core principles, synthesis template, session management, and error handling.
