---
name: codex
description: Run OpenAI Codex CLI for code analysis, generation, refactoring, and review. Supports exec, resume, review subcommands with inline config overrides.
allowed-tools: Bash, Read, Glob, Grep, AskUserQuestion
version: "6.0.0"
argument-hint: "[flags] <prompt> | resume [prompt] | review [--base branch]"
---

# Codex Skill v6.0

## Argument Parsing

Parse user input into: `action`, `flags`, `prompt`.

| Pattern | Action | Example |
|---------|--------|---------|
| `/codex <prompt>` | exec | `/codex "refactor auth module"` |
| `/codex resume [prompt]` | resume | `/codex resume "continue"` |
| `/codex review [flags]` | review | `/codex review --base main` |

**Inline flag shortcuts** (parsed from args before prompt):

| Shortcut | Expands to | Purpose |
|----------|-----------|---------|
| `--quick` | `-c model_reasoning_effort="low"` | Fast, simple tasks |
| `--deep` | `-c model_reasoning_effort="xhigh"` | Maximum reasoning |
| `--auto` | `--full-auto` | Auto-approve + workspace-write |
| `--readonly` | `-s read-only` | Analysis only, no writes |
| `--unsafe` | _(blocked, ask user)_ | Requires explicit confirmation |
| `-m <model>` | `-m <model>` | Override model directly |

If no flags provided, use config.toml defaults (no hardcoded values).

---

## Exec Flow

**Default**: zero-question execution. Just run it.

```bash
codex exec --skip-git-repo-check {flags} "{prompt}"
```

**Only ask user if**:
- `--unsafe` / `danger-full-access` requested → confirm before proceeding
- Prompt is empty → ask what they want to do

**Rules**:
- Do NOT hardcode `-m` or `-c model_reasoning_effort` — let config.toml handle defaults
- Do NOT use `2>/dev/null` — stderr has important info
- `--skip-git-repo-check` always included (Claude Code workspace may not be a git repo)
- Show complete output to user
- Set timeout to 300000ms (5 min) for exec commands

---

## Resume Flow

```bash
# Resume most recent session
codex resume --last

# Resume with follow-up prompt
codex resume --last "{prompt}"

# Resume specific session by ID
codex resume {session-id} "{prompt}"
```

**Rules**:
- Resume inherits original model/sandbox settings unless user overrides with flags
- If no session exists, inform user and suggest `codex exec` instead

---

## Review Flow

Codex has a built-in review subcommand. Use it directly.

```bash
# Review uncommitted changes
codex review --uncommitted

# Review against base branch
codex review --base main

# Review specific commit
codex review --commit {sha}

# Review with custom instructions
codex review "focus on security and error handling"
```

**When user says "review"**:
- If on feature branch → default: `codex review --base main`
- If has uncommitted changes → default: `codex review --uncommitted`
- If neither → ask what to review

---

## Quick Reference

| Intent | Command |
|--------|---------|
| Run task | `codex exec --skip-git-repo-check "prompt"` |
| Fast task | `codex exec --skip-git-repo-check -c model_reasoning_effort="low" "prompt"` |
| Deep analysis | `codex exec --skip-git-repo-check -c model_reasoning_effort="xhigh" "prompt"` |
| Auto-execute | `codex exec --skip-git-repo-check --full-auto "prompt"` |
| Read-only | `codex exec --skip-git-repo-check -s read-only "prompt"` |
| Model override | `codex exec --skip-git-repo-check -m o3 "prompt"` |
| Resume last | `codex resume --last` |
| Resume + prompt | `codex resume --last "continue with..."` |
| Review branch | `codex review --base main` |
| Review uncommitted | `codex review --uncommitted` |
| Review commit | `codex review --commit abc123` |

---

## Error Handling

- Non-zero exit → show error, ask user for direction
- Timeout → inform user, suggest resume
- Rate limit → wait and retry once, then inform user
- If output contains warnings → summarize key warnings

## Post-Execution

After codex completes:
- Show a brief summary of what was done
- Mention: "可以用 `/codex resume` 继续上次会话"
