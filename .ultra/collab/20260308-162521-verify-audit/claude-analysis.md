# Claude Audit — AI Collab Skills (Round 2)

## Scope
Skill files: ai-collab-base, gemini-collab, codex-collab, ultra-verify — after CLI flag corrections

## Findings

### 1. [Warning] codex review stdin pipe behavior unverified
- Location: codex-prompts.md, orchestration-flow.md
- Issue: `cat file | codex exec -` works (verified), but we pipe content into `codex exec "prompt"` in several places without using `-` for stdin. The prompt is passed as positional arg, so piped content may be ignored.
- Recommendation: When piping content, use `codex exec - <<< "prompt with $(cat file)" ` or include file content in the prompt string

### 2. [Warning] gemini -p with pipe may conflict
- Location: gemini-prompts.md
- Issue: `cat file | gemini -p "prompt"` — when `-p` is used with piped stdin, behavior depends on whether Gemini reads stdin or uses -p. Both channels competing.
- Recommendation: Verify pipe + -p interaction; may need to embed content in prompt string instead

### 3. [Info] codex exec review subcommand exists
- Location: codex-cli-reference.md
- Issue: `codex exec --help` shows `codex exec review` as a subcommand, distinct from top-level `codex review`. Not documented in our skill.
- Recommendation: Low priority — top-level `codex review` is the documented path

### 4. [Info] No retry logic for transient failures
- Location: All skills
- Issue: Network timeouts, rate limits have no retry. Single attempt only.
- Recommendation: Acceptable for v1 — retries add complexity

## Summary
- Critical: 0
- Warning: 2 (stdin pipe behavior)
- Info: 2
