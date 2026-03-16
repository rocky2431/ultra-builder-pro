# Ultra Verify Audit — Synthesis

**Mode**: audit
**Scope**: AI collab skill files (ai-collab-base, gemini-collab, codex-collab, ultra-verify)
**Session**: .ultra/collab/20260308-162046-verify-audit
**Status**: Degraded (2/3 — Codex failed to produce output)

---

## Consensus Findings [MAJORITY 2/2]

### 1. [Warning] metadata.json schema inconsistency
- **Claude**: noted collab-protocol.md has placeholder `<model>` field
- **Gemini**: noted collab-protocol.md lacks `models`/`confidence`/`degraded` fields that orchestration-flow.md has; also `project_path` is only in one
- **Consensus**: The two metadata schemas (dual-AI vs triple-AI) are divergent
- **Action**: Define a superset schema in collab-protocol.md, let consumers extend

### 2. [Warning] stderr suppression hides diagnostics
- **Claude**: noted empty output has no validation
- **Gemini**: flagged `2>/dev/null` hides auth expiry, rate limits, network failures
- **Consensus**: Both identify that silent failure makes debugging hard
- **Action**: Redirect stderr to `${SESSION_PATH}/error.log` instead of `/dev/null`

### 3. [Warning] codex review output extraction is underspecified
- **Claude**: (implicit in "no validation of CLI output")
- **Gemini**: explicitly flagged — no regex or marker for extracting review from raw output
- **Consensus**: Need explicit extraction heuristic
- **Action**: Document marker pattern (e.g., first `#` heading after log noise)

## Gemini-Only Findings

### 4. [Critical] .ultra/ directory may leak sensitive audit data to git
- **Gemini**: If `.ultra/` is not in `.gitignore`, vulnerability analyses get committed
- **Action**: Add `.ultra/` to `.gitignore` check in collab-protocol.md or ultra-init

### 5. [Warning] Non-git project handling missing
- **Gemini**: `review` mode and `git diff` pipes assume git repo
- **Action**: Add note about `--skip-git-repo-check` for Codex; check `.git` existence before git commands

### 6. [Info] Raw output filename inconsistency
- **Gemini**: `raw.txt` vs `codex-raw.txt` across files
- **Action**: Standardize to `<agent>-raw.txt`

## Claude-Only Findings

### 7. [Warning] codex-collab SKILL.md mentions non-existent `-o` flag
- **Claude**: Text says "Does NOT support `-o` flag" but `-o` doesn't exist at all
- **Action**: Reword to avoid referencing a non-existent flag

### 8. [Info] No automated session cleanup
- **Claude**: Manual cleanup only
- **Action**: Low priority — acceptable for now

## Confidence Assessment

| Level | Count | Findings |
|-------|-------|----------|
| Majority (2/2) | 3 | #1 metadata schema, #2 stderr, #3 extraction |
| Single-source | 5 | #4-#8 |

**Overall**: MAJORITY confidence (degraded — Codex missing). 1 potentially Critical finding (#4 .gitignore) from Gemini only — worth investigating despite single-source.

## Recommended Priority

1. **#4** `.ultra/` gitignore check — security concern (Gemini Critical)
2. **#2** stderr → error.log — improves debuggability (Majority)
3. **#7** Remove `-o` reference — prevents confusion (Claude Warning)
4. **#1** Unify metadata schema — consistency (Majority)
5. **#3** Extraction marker — robustness (Majority)
6. **#5-#8** — Lower priority improvements
