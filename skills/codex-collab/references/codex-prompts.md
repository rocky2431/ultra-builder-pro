# Codex Prompts

CLI-ready prompt invocations for each collaboration mode. Generic prompt text is in `prompt-templates.md` (ai-collab-base).

Model selection: pass any available OpenAI model via `-m <model>`. Omit for default model.

**Sandbox note**: `--full-auto` implies `-s workspace-write`. For read-only analysis, use `-s read-only` without `--full-auto`.

## Review — Delegated to Official Plugin

Review mode now delegates to the official Codex plugin. Do NOT invoke `codex review` directly.

| Request | Delegate to |
|---------|-------------|
| General review | `/codex:review` |
| Review against branch | `/codex:review --base main` |
| Security/adversarial review | `/codex:adversarial-review` |

After receiving the plugin's output, apply the dual-AI synthesis protocol (Consensus / Divergent Views).

### Performance Review (still uses `codex exec`)
```bash
cat "$FILE" | codex exec "Analyze this code for performance issues: algorithm complexity, unnecessary allocations, N+1 queries, missing caching, blocking ops, memory leaks. Quantify impact." -s read-only -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Understand

```bash
codex exec "Analyze this project: 1) Purpose 2) Architecture patterns 3) Directory structure 4) Data flow 5) Key dependencies 6) Testing approach. Be thorough." -s read-only -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Opinion

```bash
codex exec "Architecture decision — Context: [CONTEXT]. Constraints: [CONSTRAINTS]. Options: A) [A] B) [B]. For each: pros/cons, trade-offs, risks, your recommendation." -s read-only -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Compare

```bash
codex exec "[QUESTION]. Provide your independent analysis with reasoning." -s read-only -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Free

```bash
codex exec "[USER_PROMPT]" --full-auto -o "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```
