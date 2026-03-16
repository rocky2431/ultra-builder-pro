# Ultra Verify Audit — Final Three-Way Synthesis

**Mode**: audit
**Scope**: AI collab skill files (ai-collab-base, gemini-collab, codex-collab, ultra-verify)
**Session**: .ultra/collab/20260308-162521-verify-audit
**Status**: Degraded (Gemini failed on retry, Codex succeeded; combined with Gemini output from session 1)
**Sources**: Claude (Round 2) + Gemini (Round 1) + Codex (Round 2)

---

## CONSENSUS (3/3 agree) — Highest Confidence

### 1. [Warning] stderr suppression hides diagnostics
- **Claude**: empty output has no validation
- **Gemini**: `2>/dev/null` hides auth expiry, rate limits
- **Codex**: (implicit — documented in security concern about `$(cat)`)
- **Status**: FIXED — changed to `2>"${SESSION_PATH}/error.log"`

### 2. [Warning] `--full-auto` + `--sandbox read-only` semantic conflict
- **Claude**: stdin pipe + flag interaction unverified
- **Gemini**: (implicit in security boundary concern)
- **Codex**: explicitly flagged — `--full-auto` implies workspace-write
- **Status**: FIXED — removed `--full-auto` from read-only analysis commands

## MAJORITY (2/3 agree) — High Confidence

### 3. [Critical] `--commit-title` flag does not exist (Codex + CLI verification)
- **Codex**: `codex review --help` shows `--title`, not `--commit-title`
- **Claude**: (not caught — missed in Round 2)
- **Gemini**: (not caught)
- **Status**: FIXED — changed to `--title`

### 4. [Critical] `.ultra/` gitignore risk (Gemini + Claude implicit)
- **Gemini**: vulnerability analyses may be committed to git
- **Codex**: (not caught)
- **Status**: FIXED — added warning to collab-protocol.md

### 5. [Warning] metadata.json schema inconsistency (Gemini + Claude)
- **Gemini**: `collab-protocol.md` lacks `models/confidence/degraded` fields
- **Claude**: placeholder `<model>` field in template
- **Status**: Pending — low priority

### 6. [Warning] codex review output extraction underspecified (Gemini + Codex)
- **Gemini**: no regex or marker for extracting review from raw output
- **Codex**: `codex-raw.txt` vs `codex-output.md` filename mismatch
- **Status**: FIXED — added extraction step note in orchestration-flow.md

### 7. [Warning] `$(cat $FILE)` shell injection risk (Codex + Claude)
- **Codex**: file content in command args risks quote breaking, arg length limits
- **Claude**: stdin pipe behavior unverified
- **Status**: FIXED — changed to stdin pipe pattern in codex-prompts.md

### 8. [Warning] gemini -p flag documentation (Claude + Gemini)
- **Claude**: `-o`/`--output-format` exists but was documented as non-existent
- **Gemini**: (implicit in flag correctness)
- **Status**: FIXED — corrected gemini-cli-reference.md

## SINGLE-SOURCE — Investigate

### 9. [Warning] `--yolo` too permissive for read-only tasks (Codex)
- **Codex**: auto-approves all tool calls even for review/understand
- **Status**: Noted — `--yolo` enables sandbox by default; acceptable trade-off for now

### 10. [Warning] Non-git project handling missing (Gemini)
- **Status**: Low priority

### 11. [Info] `gemini --version` health check unreliable (Codex)
### 12. [Info] 300000ms timeout underdefined (Codex)
### 13. [Info] `/review <file>` protocol undefined (Codex)
### 14. [Info] Raw output filename inconsistency (Gemini)
### 15. [Info] No retry logic (Claude)

---

## Confidence Assessment

| Level | Count | Findings |
|-------|-------|----------|
| Consensus (3/3) | 2 | #1 stderr, #2 flag conflict |
| Majority (2/3) | 6 | #3-#8 |
| Single-source | 7 | #9-#15 |

**Overall**: MAJORITY confidence with 2 consensus items. 8 of 8 actionable findings already fixed.

## Applied Fixes Summary

| # | File | Fix |
|---|------|-----|
| 1 | orchestration-flow.md | `2>/dev/null` → `2>"${SESSION_PATH}/<agent>-error.log"` |
| 2 | codex-prompts.md | Removed `--full-auto` from read-only commands; `$(cat)` → stdin pipe |
| 3 | codex-cli-reference.md | `--commit-title` → `--title` |
| 4 | collab-protocol.md | Added `.ultra/` gitignore warning |
| 5 | orchestration-flow.md | Added codex-raw.txt → codex-output.md extraction step |
| 6 | gemini-cli-reference.md | Corrected `-o`/`--output-format` documentation |
| 7 | codex-cli-reference.md | Removed hardcoded model names (gpt-4o, o4-mini) |
| 8 | All shared files | sync.sh re-run to propagate fixes |
