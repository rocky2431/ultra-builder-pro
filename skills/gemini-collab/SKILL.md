---
name: gemini-collab
description: "Invoke Gemini CLI as an independent sub-agent for code review, project analysis, architecture opinions, and comparative verification. Trigger when the user says 'ask Gemini', 'Gemini review', 'let Gemini check', 'Gemini analysis', 'dual AI', or mentions 'gemini' in any collaborative context."
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

See `references/gemini-cli-reference.md` for full CLI syntax. Key pattern:

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

## Collaboration Protocol

See `references/collab-protocol.md` for:
- Core principles (independent thinker, no priming, Claude synthesizes)
- File-based output protocol and session management
- Synthesis report template
- Error handling

## Collaboration Modes

See `references/collaboration-modes.md` for the 5 mode definitions (review, understand, opinion, compare, free).

## Gemini-Specific Prompts

See `references/gemini-prompts.md` for CLI-ready prompt templates with recommended model selection per mode.

## Error Handling

- If `gemini` not found: `npm install -g @google/gemini-cli`
- If timeout (>5min): check partial output in file
- If empty output: proceed with Claude-only analysis
- Never block the workflow on Gemini failure
