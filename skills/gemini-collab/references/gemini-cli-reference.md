# Gemini CLI Reference

Correct CLI usage for Google's Gemini CLI (`@google/gemini-cli`).

## Installation

```bash
npm install -g @google/gemini-cli
```

## Basic Invocation

```bash
# Gemini outputs text to stdout by default
gemini -p "Your prompt here" --yolo > output.md 2>"${SESSION_PATH}/error.log"

# Or without -p flag (also works for non-interactive)
gemini "Your prompt here" --yolo > output.md 2>"${SESSION_PATH}/error.log"
```

**Key flags:**
| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Non-interactive prompt |
| `"prompt"` (positional) | Also works for non-interactive mode |
| `--yolo` | Auto-approve all tool calls (shorthand for `--approval-mode yolo`) |
| `--sandbox` / `-s` | Sandboxed execution (enabled by default in YOLO mode) |
| `-m <model>` | Model selection (pass any supported Gemini model name) |
| `-o` / `--output-format` | Output format: `text` (default), `json`, `stream-json` |
| `-i "prompt"` | Execute prompt then continue interactively |

## Model Selection

Use `-m <model>` with the actual Gemini model name:

```bash
gemini -p "prompt" --yolo -m gemini-2.5-flash > output.md 2>"${SESSION_PATH}/error.log"
```

Check available models in your Gemini account. Model names follow Google's naming (e.g., `gemini-2.5-flash`, `gemini-2.5-pro`). Can also be set via `GEMINI_MODEL` env var.

## Approval Modes

| Flag | Behavior |
|------|----------|
| `--approval-mode default` | Prompt for approval on each tool call |
| `--approval-mode auto_edit` | Auto-approve edit tools only |
| `--yolo` / `--approval-mode yolo` | Auto-approve all (enables sandbox by default) |
| `--approval-mode plan` | Read-only mode (experimental) |

## Common Patterns

### Redirect to file (standard)
```bash
gemini -p "Analyze this code" --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

### Pipe file content
```bash
cat src/main.py | gemini -p "Review this code for bugs and security issues" --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

### Pipe git diff
```bash
git diff HEAD~1 | gemini -p "Review this diff for bugs, security issues, and performance problems. Cite line numbers." --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

### Read-only analysis (sandbox)
```bash
gemini -p "Analyze this project's architecture" --yolo --sandbox > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

### Include additional directories
```bash
gemini --include-directories ../lib,../docs -p "Analyze the architecture" --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Important Notes

- `-o` / `--output-format` controls output format: `text` (default), `json`, `stream-json`
- Default is text to stdout — no need to specify `-o text` explicitly
- Always redirect stdout to a file for capture
- Redirect stderr to `error.log` for diagnostics: `2>"${SESSION_PATH}/error.log"`
- Use Read tool to read the output file — never rely on Bash stdout
- `--yolo` enables sandbox by default for safety
- Set Bash timeout to 300000ms (5 min) for large analyses
