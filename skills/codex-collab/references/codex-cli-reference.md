# Codex CLI Reference

Correct CLI usage for OpenAI's Codex CLI (`@openai/codex`).

## Installation

```bash
npm install -g @openai/codex
codex login
```

## Mode 1: `codex review` — Built-in Code Review

Purpose-built for reviewing code changes. Outputs review findings to stdout/stderr.

```bash
# Capture ALL output (stdout + stderr)
codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/raw.txt"
```

### Scope Flags

| Flag | Scope |
|------|-------|
| `--uncommitted` | Unstaged + staged changes |
| `--base <branch>` | Changes vs branch (e.g., `--base main`) |
| `--commit <sha>` | Specific commit |
| `--title "title"` | Optional commit title to display in review summary |

### Custom Review Instructions

`codex review` accepts a custom prompt as a positional argument:

```bash
# Custom review focus
codex review "Focus on security vulnerabilities and SQL injection risks" 2>&1 | tee "${SESSION_PATH}/raw.txt"

# With scope flag
codex review --base main 2>&1 | tee "${SESSION_PATH}/raw.txt"
```

### Extracting Review from Raw Output

The raw output contains MCP startup logs, shell exec logs, and the final review. The actual review findings are at the end. Read the file and extract from the review summary onward. Save as `output.md`.

## Mode 2: `codex exec` — General Non-Interactive

For any prompt beyond built-in review.

```bash
codex exec "Your prompt here" --full-auto -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

**Key flags:**
| Flag | Purpose |
|------|---------|
| `--full-auto` | Auto-approve with workspace-write sandbox |
| `-s <mode>` / `--sandbox <mode>` | `read-only`, `workspace-write`, `danger-full-access` |
| `-o <file>` / `--output-last-message <file>` | Save final message to file (clean, no process logs) |
| `--json` | Output events as JSONL to stdout |
| `-m <model>` | Model selection (pass any supported OpenAI model name) |
| `-c key=value` | Override config for this session |
| `--skip-git-repo-check` | Allow running in non-git directories |
| `--ephemeral` | Run without persisting session files |

## Model Selection

Use `-m <model>` with the actual OpenAI model name:

```bash
codex exec "prompt" --full-auto -m <model> -o output.md
```

Or via config override:
```bash
codex -c model=<model> "prompt"
```

Check available models in your OpenAI account. Can also be set in `~/.codex/config.toml`.

## Sandbox Modes

| Mode | Behavior |
|------|----------|
| `read-only` | Blocks all writes and network access (default) |
| `workspace-write` | Allows writing within workspace, blocks network |
| `danger-full-access` | Disables sandboxing entirely |

Set via `--sandbox <mode>` or `-s <mode>`.

## Important Notes

- `codex review` outputs to stdout/stderr — capture with `2>&1 | tee`
- `codex exec` uses `-o` (`--output-last-message`) to save clean output to file
- Always use Read tool to read output files
- Set Bash timeout to 300000ms (5 min) for large analyses
- Use `--sandbox read-only` for analysis-only tasks
