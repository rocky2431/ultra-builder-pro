---
name: code-review-expert
description: "Structured code review checklists: SOLID, security, performance, boundary conditions, removal planning. Injected into code-reviewer agent."
user-invocable: false
---

# Code Review Expert Checklists

Provides structured review workflow and reference checklists for the code-reviewer agent.

## Severity Levels

| Level | Name | Description | Action |
|-------|------|-------------|--------|
| **P0** | Critical | Security vulnerability, data loss risk, correctness bug | Must block merge |
| **P1** | High | Logic error, significant SOLID violation, performance regression | Should fix before merge |
| **P2** | Medium | Code smell, maintainability concern, minor SOLID violation | Fix in this PR or create follow-up |
| **P3** | Low | Style, naming, minor suggestion | Optional improvement |

## Review Workflow

### Step 1: Preflight Context

- Run `git status -sb`, `git diff --stat`, and `git diff` to scope changes
- Use `git diff --cached` to include staged changes
- If needed, use Grep to find related modules, usages, and contracts

**Edge cases:**
- **No changes**: Inform user, ask if they want to review staged changes or a specific commit range
- **Large diff (>500 lines)**: Summarize by file first, then review in batches by module/feature area
- **Mixed concerns**: Group findings by logical feature, not just file order

### Step 2: SOLID + Architecture Smells

Load `references/solid-checklist.md` for detailed prompts.

Look for SRP/OCP/LSP/ISP/DIP violations and common code smells. When proposing refactor, explain *why* it improves cohesion/coupling. Non-trivial refactors get incremental plans, not large rewrites.

### Step 3: Removal Candidates

Load `references/removal-plan.md` for template.

Identify unused, redundant, or feature-flagged-off code. Distinguish **safe delete now** vs **defer with plan**. Provide follow-up steps with concrete checkpoints.

### Step 4: Security and Reliability

Load `references/security-checklist.md` for coverage.

Check injection, auth gaps, secrets, race conditions, crypto, supply chain. Call out both **exploitability** and **impact**.

### Step 5: Code Quality

Load `references/code-quality-checklist.md` for coverage.

Check error handling, performance/caching, boundary conditions. Flag issues that may cause silent failures or production incidents.

### Step 6: Output Format

```markdown
## Code Review Summary

**Files reviewed**: X files, Y lines changed
**Overall assessment**: [APPROVE / REQUEST_CHANGES / COMMENT]

---

## Findings

### P0 - Critical
(none or list)

### P1 - High
- **[file:line]** Brief title
  - Description of issue
  - Suggested fix

### P2 - Medium
...

### P3 - Low
...

---

## Removal/Iteration Plan
(if applicable)

## Additional Suggestions
(optional improvements, not blocking)
```

### Step 7: Next Steps Confirmation

After presenting findings, ask how to proceed:

1. **Fix all** - Implement all suggested fixes
2. **Fix P0/P1 only** - Address critical and high priority issues
3. **Fix specific items** - User specifies which issues to fix
4. **No changes** - Review complete, no implementation needed

**Important**: Do NOT implement any changes until user explicitly confirms.

## Additional Resources

### Reference Files

For detailed patterns and checklists, consult:
- **`references/solid-checklist.md`** - SOLID violation detection and refactor heuristics
- **`references/security-checklist.md`** - Security, reliability, and race condition checks
- **`references/code-quality-checklist.md`** - Error handling, performance, boundary conditions
- **`references/removal-plan.md`** - Deletion candidates and iteration planning template
