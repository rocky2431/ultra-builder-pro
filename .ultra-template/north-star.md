# Project North Star

> **Authority**: This file is the single source of truth for "what the user actually wants."
> Every task created against this project must trace back here. When something seems unclear,
> read this file before guessing.

---

## One-line

<!-- ONE sentence the user used to describe what they want.
     Captured by /ultra-init or auto-detected by user_prompt_capture hook on first request. -->

_(not yet defined — run `/ultra-init` or first user request will populate)_

---

## Success Metric

<!-- How do we know the project succeeded?
     Concrete, verifiable. Not "users like it" — "auth latency < 200ms p99" or "10 paid customers". -->

_(not yet defined)_

---

## Hard Constraints

<!-- What MUST NOT happen, even if convenient.
     Examples:
     - Never store plaintext passwords
     - Cannot break backwards compatibility with API v1
     - Total bundle size must stay < 500KB
     - No external API call costs > $X/month -->

_(not yet defined)_

---

## Out of Scope

<!-- What we explicitly chose NOT to do, to prevent scope creep.
     Updated by /ultra-plan when user declines features. -->

_(not yet defined)_

---

## Stakeholders

<!-- Who is this for? What do they actually do?
     Reference: see .ultra/specs/product.md#personas for detail -->

_(not yet defined)_

---

## Last Updated

_2026-04-30 (template placeholder)_

---

## Notes for Agents

When you read this file (you should, every session):
1. Re-anchor on the One-line — that is the literal user request
2. Check Hard Constraints before any "improvement" — improvements that violate constraints are regressions
3. If your current work doesn't trace back here, **stop and ask** — you may be building the wrong thing

This file is injected into context by:
- `session_context.py` (SessionStart) — top-level only (One-line + Success Metric + Hard Constraints)
- `mid_workflow_recall.py` (PreToolUse) — when editing source files
