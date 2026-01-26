---
name: codex
description: Use when the user asks to run Codex CLI (codex exec, codex resume) or references OpenAI Codex for code analysis, refactoring, or automated editing
allowed-tools: Bash, Read, Glob, Grep
version: "5.0.0"
---

# Codex Skill Guide

## Running a Task

### Defaults
- **Model**: `gpt-5.2-codex`
- **Reasoning effort**: `medium`
- **Sandbox**: `workspace-write`

### Invocation Modes

**Mode 1: Template invocation** (from commands like `/ultra-dev`, `/ultra-test`)
- Use template config directly, NO user interaction
- Templates define model/effort/sandbox/prompt

**Mode 2: Regular invocation** (user requests codex directly)
1. Display current defaults
2. Use `AskUserQuestion`:
   - Option A: "Use default config" (Recommended) - gpt-5.2-codex, medium, workspace-write
   - Option B: "Custom config" - then ask model/effort/sandbox separately
3. Execute with chosen config

### Configuration Options

**Models**:
- `gpt-5.2-codex` (default, optimized for code)
- `gpt-5.2` (general purpose)

**Reasoning effort**:
- `low` - fast, simple tasks
- `medium` (default) - balanced
- `high` - complex analysis
- `xhigh` - maximum reasoning

**Sandbox**:
- `workspace-write` (default) - can run git/ls for context
- `read-only` - analysis only, no file access
- `danger-full-access` - requires explicit user permission

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
- `--full-auto` requires explicit confirmation in Mode 2 custom config flow.
- `--sandbox danger-full-access` requires explicit user permission (separate confirmation).
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
Review this technical research output against these rules:

[Evidence-First]
- Every claim must have verifiable source (official docs, benchmarks)
- Unverified claims must be marked as "Speculation"
- Priority: 1) Official docs 2) Community practices 3) Inference

[Honesty & Challenge]
- Detect risk underestimation or wishful thinking
- Point out logical gaps explicitly
- No overly optimistic assumptions without evidence

[Architecture Decisions]
- Critical state requirements addressed?
- Migration/rollback plan for breaking changes?
- Persistence/recovery/observability considered?

[Completeness]
- Missing risks or edge cases not considered
- Contradictions between sections

Provide specific issues with file:line references.
Label each finding: Fact | Inference | Speculation
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
Review this code diff against these rules:

[Code Quality]
- No TODO/FIXME/placeholder in code
- Modular structure, avoid deep nesting (max 3 levels)
- No hardcoded secrets or credentials

[Security]
- No injection vulnerabilities (SQL, XSS, CSRF, command injection)
- No auth bypass or secrets exposure
- Input validation at system boundaries

[Architecture]
- Critical state (funds/permissions/external API) must be persistable/recoverable
- No in-memory-only storage for critical data
- Breaking API changes require migration plan

[Logic]
- No race conditions or incorrect state handling
- No N+1 queries or memory leaks
- Spec compliance - implementation matches acceptance criteria
- Edge cases handled (boundary values, null, empty, error paths)

[Testing in Code]
- No mocks on core logic (domain/service/state paths must use real deps)
- Test files included should follow Core Logic NO MOCKING rule

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
Review this test suite against these rules:

[Core Logic Testing - NO MOCKING ALLOWED]
Core Logic = Domain/service/state machine/funds-permission paths
- These paths MUST use real implementations, not mocks
- Repository interfaces: prefer testcontainers with production DB
- Fallback: SQLite/in-memory only when testcontainers unavailable

[External Systems - Test Doubles ALLOWED]
- External APIs, third-party services → testcontainers/sandbox/stub OK
- Must document rationale for each test double

[Coverage]
- Missing edge cases (null, empty, boundary values, error paths)
- Untested critical paths (auth flows, payment, data mutations, deletions)

[Anti-Patterns]
- Flaky tests (time-dependent, order-dependent)
- Tautology assertions (expect(true).toBe(true))
- Empty test bodies
- False confidence - tests that pass but don't verify behavior

[Security Testing]
- Auth/permission tests exist for protected endpoints
- Input validation tests for injection vectors
- Sensitive data handling tests (no plaintext secrets in logs/responses)

Provide specific issues with file:line references.
If no critical issues found, respond with "PASS: No blocking issues".
```
