# Claude Audit — AI Collab Skills (Round 3, post-fix)

## Scope
All skill files after applying fixes from Round 1+2 audit: ai-collab-base, gemini-collab, codex-collab, ultra-verify

## Verification Checks

### Previously Fixed Items — Verified
1. `--commit-title` → `--title` in codex-cli-reference.md: FIXED
2. `2>/dev/null` → `error.log` in orchestration-flow.md: FIXED
3. `.ultra/` gitignore warning in collab-protocol.md: FIXED
4. `$(cat $FILE)` → stdin pipe in codex-prompts.md: FIXED
5. `--full-auto` removed from read-only commands in codex-prompts.md: FIXED
6. `-o`/`--output-format` documented correctly in gemini-cli-reference.md: FIXED
7. Hardcoded model names removed from codex-cli-reference.md: FIXED
8. codex-raw.txt extraction step added to orchestration-flow.md: FIXED

### New Observations

#### 1. [Info] gemini-collab SKILL.md still uses `2>/dev/null`
- Location: gemini-collab/SKILL.md L39, L42
- Issue: orchestration-flow.md was fixed to use error.log, but gemini-collab's own SKILL.md examples still show `2>/dev/null`
- Impact: Minor inconsistency — SKILL.md is instructional, orchestration-flow.md is the execution guide
- Recommendation: Update SKILL.md examples for consistency

#### 2. [Info] codex-collab SKILL.md `codex exec` example still uses `2>/dev/null`
- Location: codex-collab/SKILL.md L48
- Impact: Same as above — instructional vs execution

#### 3. [Info] gemini-cli-reference.md still uses `2>/dev/null` in all examples
- Location: gemini-cli-reference.md L15, L55, L60, L65, L70, L75
- Impact: Reference doc examples not aligned with orchestration best practice

#### 4. [Info] sync.sh only syncs collab-protocol.md and collaboration-modes.md
- Location: ai-collab-base/sync.sh
- Issue: prompt-templates.md is not synced (but it's only consumed by ai-collab-base, so this is by design)

## Summary
- Critical: 0
- Warning: 0
- Info: 4 (all cosmetic consistency issues)
- All 8 previously-identified actionable bugs are confirmed fixed
- Overall: Clean — ready for production use
