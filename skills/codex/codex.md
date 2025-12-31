---
name: codex
description: Use when the user asks to run Codex CLI (codex exec, codex resume) or references OpenAI Codex for code analysis, refactoring, or automated editing
---

# Codex Skill Guide

## Running a Task

### Defaults (use unless user specifies otherwise)
- **Model**: `gpt-5.2-codex`
- **Reasoning effort**: `medium`
- **Sandbox**: `workspace-write`

### When to ask user
Only use `AskUserQuestion` if:
- User explicitly asks to choose model/effort
- Task is high-risk (e.g., `--full-auto` with edits)
- Previous codex call failed

Otherwise, **proceed with defaults automatically**.

### Sandbox mode selection:
   - `workspace-write` (default) - allows codex to run git/ls commands for context
   - `read-only` - only if user explicitly requests no file access
   - `danger-full-access` - only with explicit user permission

### Command template
```bash
codex exec \
  -m gpt-5.2-codex \
  -c model_reasoning_effort="medium" \
  --sandbox workspace-write \
  --skip-git-repo-check \
  "prompt here"
```

### Execution rules
- **Do NOT use `2>/dev/null`** - stderr contains important error info
- Run the command and show complete output to user
- After completion: "You can resume with 'codex resume'"

## Resume Syntax

```bash
# Resume with new prompt (correct syntax)
codex exec resume --last "new prompt here"

# Resume reading prompt from stdin
echo "new prompt" | codex exec resume --last -

# Resume with config overrides (flags BEFORE resume)
codex exec -m gpt-5.2-codex resume --last "prompt"
```

## Quick Reference

| Use case | Command |
|----------|---------|
| Analysis | `codex exec -m gpt-5.2-codex --sandbox workspace-write --skip-git-repo-check "prompt"` |
| With edits | `codex exec -m gpt-5.2-codex --sandbox workspace-write --full-auto --skip-git-repo-check "prompt"` |
| Resume | `codex exec resume --last "continue with..."` |
| Code review | `codex exec review` (built-in subcommand) |

## Following Up

- After every `codex` command, use `AskUserQuestion` to confirm next steps or whether to resume.
- When resuming, the session inherits original model/sandbox settings unless overridden.

## Error Handling

- If `codex exec` exits non-zero, show the error and ask user for direction.
- Before using `--full-auto` or `--sandbox danger-full-access`, ask user permission via `AskUserQuestion`.
- If output shows warnings, summarize and ask how to proceed.

---

## Review Templates

Use these predefined templates when commands reference `codex skill with template: <name>`.

### research-review

| Config | Value |
|--------|-------|
| Model | gpt-5.2-codex |
| Effort | medium |
| Sandbox | read-only |

**Prompt**:
```
Review this technical research output for:
1) Logical gaps or contradictions between sections
2) Missing risks or edge cases not considered
3) Unverified claims without cited sources
4) Overly optimistic assumptions or underestimated complexity

Provide specific issues with file:line references.
If no critical issues found, respond with "PASS: No blocking issues".
```

---

### code-review

| Config | Value |
|--------|-------|
| Model | gpt-5.2-codex |
| Effort | **high** |
| Sandbox | read-only |

**Prompt**:
```
Review this code diff for:
1) Security vulnerabilities (injection, XSS, CSRF, auth bypass, secrets exposure)
2) Logic errors, race conditions, or incorrect state handling
3) Performance issues (N+1 queries, memory leaks, blocking operations)
4) Spec compliance - does implementation match acceptance criteria?

Provide specific issues with file:line references and severity (Critical/High/Medium/Low).
If no critical/high issues found, respond with "PASS: No blocking issues".
```

---

### test-review

| Config | Value |
|--------|-------|
| Model | gpt-5.2-codex |
| Effort | medium |
| Sandbox | workspace-write |

**Prompt**:
```
Review this test suite for:
1) Missing edge cases (null, empty, boundary values, error paths)
2) Test anti-patterns (flaky tests, order-dependent, excessive mocking)
3) Untested critical paths (auth flows, payment, data mutations, deletions)
4) False confidence - tests that pass but don't actually verify behavior

Provide specific issues with file:line references.
If no critical issues found, respond with "PASS: No blocking issues".
```
