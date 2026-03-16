# Claude Audit — AI Collab Skills

## Scope
New/rewritten skill files: ai-collab-base, gemini-collab, codex-collab, ultra-verify

## Findings

### 1. [Warning] gemini-collab SKILL.md still shows `-p` as "required for scripting"
- Location: `gemini-collab/SKILL.md` line ~30
- Issue: The CLI reference correctly documents that positional prompt also works (`gemini "prompt"`), but the SKILL.md "How to Call Gemini" section only shows `-p` pattern
- Impact: Minor inconsistency, not a bug — `-p` does work
- Recommendation: Low priority, both forms are valid

### 2. [Warning] codex-collab SKILL.md still mentions `-o` flag
- Location: `codex-collab/SKILL.md` line ~37 ("Does NOT support `-o` flag")
- Issue: After the fix, the SKILL.md correctly says review has no `-o` flag, but the exec section below was updated to remove `-o` mention. However the text "Does NOT support `-o` flag" is now confusing since `-o` doesn't exist anywhere in Codex CLI
- Impact: Minor confusion — the flag simply doesn't exist, not just "not supported in review"
- Recommendation: Reword to "capture via `2>&1 | tee`" without mentioning `-o`

### 3. [Info] Session cleanup has no automation
- Location: collab-protocol.md — "Sessions older than 7 days are safe to delete"
- Issue: No cron job or automated cleanup mechanism exists
- Impact: Disk accumulation over time
- Recommendation: Low priority — manual cleanup is acceptable for now

### 4. [Info] No validation of CLI output before Read
- Location: orchestration-flow.md Step 4
- Issue: If Gemini/Codex write empty files or error messages, Claude reads and synthesizes garbage
- Impact: Handled by degraded operation protocol, but no explicit file-size check
- Recommendation: Consider checking file size before reading in future iteration

### 5. [Info] collab-protocol.md metadata schema has placeholder model field
- Location: collab-protocol.md metadata schema
- Issue: `"model": "<model>"` is a template — actual value depends on runtime
- Recommendation: Expected behavior for a template, no action needed

## Summary
- Critical: 0
- Warning: 2 (both minor wording issues)
- Info: 3
- Overall: Clean, well-structured skill architecture
