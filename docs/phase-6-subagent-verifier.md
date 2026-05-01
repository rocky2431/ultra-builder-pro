# Phase 6 Plan — Subagent Output Verifier

**Status**: **v1 SHIPPED 2026-05-02** — `hooks/subagent_verify.py` + 30 tests + registered on `SubagentStop` (8s timeout)
**Author**: rocky2431 + Claude
**Date**: 2026-05-01 (design) / 2026-05-02 (v1 ship)
**Resolves**: structural unreliability of subagent output (hallucination)

---

## Origin — what triggered this

A `claude-code-guide` subagent was asked "what is Transcript view in Claude Code". It returned a confidently-formatted answer:

- Field name: `viewMode` in `~/.claude/settings.json`
- Three values: `default` / `verbose` / `focus`
- Slash command: `/focus`
- Doc URL: `code.claude.com/docs/en/settings.md`

**All four were wrong.** The actual UI (visible in user screenshot) shows:
- A web-app dropdown with **4** options: Normal / Thinking / Verbose / Summary
- Keyboard shortcut `⌃+O`
- **Not** a settings.json field — UI state on the web side
- Real docs at `docs.claude.com/en/docs/claude-code` (different host)

`grep -i transcript ~/.claude/settings.json` returned exit 1 (no match). The subagent fabricated a plausible-looking answer with fake field names, fake values, fake URL. Token usage 36k, 3 tool calls — it *did* call tools, but evidently fell back to training memory and synthesised the rest.

This is **not a one-off**. It is the structural failure mode of LLM-driven agent delegation.

---

## Why it's structural (not a one-off bug)

1. **Tool output → LLM → prose** is a generation step. Even when the tool returned truth, the summary the agent writes is generated text and can hallucinate.
2. **6-step compound error chain**: main frames task → translates to prompt → subagent parses → calls tools → interprets results → writes summary → main parses summary. Each step has independent failure probability. ~10% per step compounds.
3. **Anti-skeptical training bias**: LLMs are rewarded for "useful output". "I couldn't find it" loses to "plausible-looking answer" in probability.
4. **No verification gate**: main's default contract is "subagent says X → X is true". No automatic check that cited URLs exist, field names are real, file paths resolve.
5. **Plausibility ≠ truth**: structured outputs (URL + field name + value enum) increase trust without increasing accuracy.

---

## Subagent vs Agent Teams — what this Phase is *not*

Considered: would Agent Teams (TeamCreate + SendMessage) solve this? Verdict: **partially, but it's the wrong axis**.

| | Subagent (`Agent` tool default) | Agent Teams |
|--|---------------------------------|-------------|
| Lifetime | One-shot, fire-and-forget | Persistent, message-driven |
| Communication | Unidirectional summary | Bidirectional via `SendMessage`; peer DM visible to lead |
| State | Black box | Shared `tasks/{team}/` TaskList; on-disk inboxes auditable |
| Verify advantages | None | Can re-query, cross-check member A vs B, read inbox ground truth |
| Cost | Cheap, fast | Spawn overhead + coordination latency + shutdown protocol |

**Teams give you tools to verify, not automatic verification.** Hallucination doesn't disappear because the agent is on a team — it's still an LLM. Teams are the right tool for *multi-step coordination*, not for *single-shot factual queries*.

→ Phase 6 is orthogonal: an automatic verifier that runs **regardless of subagent or team mode**.

---

## Proposal — Subagent Output Verifier

A sensor-mode hook that intercepts every `Agent` tool result, extracts cited claims, verifies each automatically against ground truth, and injects an advisory to the next main turn.

### Architecture

```
Main agent calls Agent tool
        │
        ▼
Subagent runs, returns summary
        │
        ▼
PostToolUse(Agent) hook fires
        │
        ▼
hooks/subagent_verify.py
  ├─ Parse summary
  ├─ Extract claims:
  │   • URLs                → HEAD request, expect 2xx
  │   • File paths          → fs.exists
  │   • Field names in JSON → grep target schema/file
  │   • Commit hashes       → git cat-file -e
  │   • Function/class names → grep repo
  └─ For each failed claim → emit [Verify] advisory to stderr
        │
        ▼
Next main turn sees advisories alongside summary
        │
        ▼
Main decides: trust / re-query / escalate to /ultra-verify
```

### Categories of claim to verify

| Claim type | How to verify | Cost |
|-----------|---------------|------|
| URL | `curl -sI -m 3 <url>` → check 2xx | ~500ms per URL |
| File path | `os.path.exists(path)` | <1ms |
| Settings field | `python3 -c "import json; ..." | grep` | <10ms |
| Commit hash | `git cat-file -e <hash>` | <50ms |
| Function/class name | `grep -rn "<name>"` in repo | ~100ms |
| Schema enum value | check against known schemas (`unified-schema.md`, etc.) | <10ms |

### Output format (advisory, not blocker)

```
[Verify] subagent guide-agent cited 4 claims, 3 unverified:
  ✗ URL: code.claude.com/docs/en/settings.md → 404
  ✗ Field: viewMode → not found in any settings schema
  ✗ Command: /focus → not in commands/ directory
  ✓ Tool: WebFetch → exists in tool registry

→ Treat this summary as hypothesis, not fact. Cross-check before acting.
```

### Sensor not blocker (CLAUDE.md C3)

- Never refuse the main agent's next turn
- Never delete/edit the subagent's summary
- Just **inject signal** to next turn's stderr/additionalContext
- Main decides whether to act on it

---

## Integration with existing v7 substrate

| v7 piece | How Phase 6 plugs in |
|----------|---------------------|
| `post_edit_guard.py` | Pattern reference — same sensor philosophy, same advisory injection mechanism |
| `relations.json` | Phase 6 verifier *queries* this for "is this file/task real?" — no schema changes needed |
| `progress.json` advisories field | Each subagent fail-to-verify can append to active task's `advisories` |
| `/ultra-review` | Already does multi-agent + coordinator — Phase 6 doesn't replace it; Phase 6 is for *one-off subagent* delegation |
| `/ultra-verify` | Three-way AI is the *strong* mitigation; Phase 6 is the *cheap default* mitigation |

---

## Implementation sketch

### Files to create

```
hooks/subagent_verify.py           # PostToolUse(Agent) hook
hooks/tests/test_subagent_verify.py
```

### settings.json hook entry

```json
"PostToolUse": [
  ...,
  {
    "matcher": "Agent",
    "hooks": [{
      "type": "command",
      "command": "python3 ~/.claude/hooks/subagent_verify.py",
      "timeout": 8
    }]
  }
]
```

(8s timeout because URL HEAD checks are slow; cap at 5 URLs per summary to stay under.)

### Verifier core (pseudocode)

```python
def main():
    hook_input = json.loads(sys.stdin.read())
    if hook_input.get('tool_name') != 'Agent':
        return ok()

    tool_response = hook_input.get('tool_response', {})
    summary = extract_summary(tool_response)  # the subagent's final text

    claims = parse_claims(summary)  # regex extract URLs, paths, fields, hashes
    failures = []

    for claim in claims:
        if claim.kind == 'url' and not verify_url(claim.value):
            failures.append(claim)
        elif claim.kind == 'path' and not os.path.exists(claim.value):
            failures.append(claim)
        # ... etc

    if failures:
        emit_advisory(failures)  # stderr + additionalContext
        update_task_progress(advisories=...)  # plug into progress.json
```

### Test plan

1. **Unit**: each verifier (URL/path/field/hash) tested with real and fake input
2. **Integration**: synthesize a fake subagent summary with known fabrications, run hook, assert advisories
3. **E2E**: real `Agent` call with known-honest task → 0 advisories. Real `Agent` call with prompt designed to provoke fabrication → ≥1 advisory.

### Edge cases / open questions

- **False negatives**: subagent makes claims that *can't* be auto-verified (e.g. "I think this is a good idea") → no signal, that's OK
- **False positives**: agent cites URL that returns 503 transiently → verifier should retry once with backoff
- **Schema sources**: where does the verifier know which fields are valid in `settings.json`? Bootstrap with current schema; let it grow over time. Or: just check the user's own `~/.claude/settings.json` keys as the universe.
- **Cost ceiling**: max 5 URL verifies per summary, max 8s total hook runtime. Fail-open if exceeded.
- **What about Bash tool output?** Bash already returns truth; it's the *interpretation* that's unreliable. Verifier should focus on Agent (subagent) and ToolSearch summaries, not raw Bash.

---

## Out of scope (explicit non-goals)

- Phase 6 does **not** validate subjective judgments ("this is well-designed", "VIP feature is risky") — only factual cites
- Phase 6 does **not** block or rewrite subagent output — sensor only
- Phase 6 does **not** replace `/ultra-verify` for high-stakes decisions — that stays as the strong mitigation
- Phase 6 does **not** add a new agent — pure hook

---

## Decision points for next session

Before implementing, decide:

1. **Scope** — start with just URL + path + field check? Or full set including git hashes and function names from day 1?
2. **Schema universe** — which settings/configs/spec files does the verifier consider "ground truth"? Hardcoded list? Auto-discover? Configurable?
3. **Strict mode toggle** — should there be a `STRICT_VERIFY=1` env var that promotes advisories to advisories *and* a separate "strict" log? Or always sensor-only forever?
4. **Reverse direction** — should the verifier also emit *positive* signals ("✓ all 4 claims verified") to build trust, or only flag failures? Probably failures-only to minimize noise.
5. **Phase 6 prerequisites** — does this need a Phase 5.5 first to harden the existing post_edit_guard pattern? Or jump straight to the new hook?
6. **Naming** — `subagent_verify.py` or `output_verify.py` (broader name, future-proof for Bash/ToolSearch verification)?

---

## Why this is the right next Phase

Phases 1-5 closed the **engineering** drift gaps (file→task trace, semantic alignment, wiki views, session fold-back, orphan handling). Phase 6 closes a **trust** gap: every subagent output the harness produces or consumes goes through a verification net.

Without Phase 6, the harness is internally consistent but externally fragile — it builds beautiful task contexts and review pipelines, then trusts a single hallucinating subagent to assert "VIP shipping is implemented correctly" with no cross-check.

The dynamic project KB (Phase 1-5) gave Claude a memory it trusts. Phase 6 gives Claude a *skepticism* it trusts.

---

## References

- `hooks/post_edit_guard.py` — sensor pattern to clone
- `hooks/relations_sync.py` — how advisories are emitted to stderr
- `skills/ultra-verify/SKILL.md` — strong mitigation (three-way AI)
- `agents/review-coordinator.md` — multi-agent dedup pattern (less applicable here, but related)
- `CHANGELOG.md` v7.0 — sensor-not-blocker doctrine origin
- This session's transcript-view incident — concrete failure case

---

## v1 implementation log (2026-05-02)

**Hook**: `SubagentStop` (not `PostToolUse(Agent)` — `agent_transcript_path` is documented and stable; `tool_response` schema is undocumented).
**Source**: `hooks/subagent_verify.py` (~250 lines). **Tests**: `hooks/tests/test_subagent_verify.py` (30 cases, all green, real I/O — no mocks).

### Decision points resolved with these defaults
1. **Scope**: URL + path + settings field (Q1 minimal start).
2. **Schema universe**: auto-discover `~/.claude/settings.json` keys (recursive flatten, dotted paths) (Q2 auto-discover).
3. **Strict mode toggle**: not added — sensor-only forever (Q3 KISS).
4. **Positive signals**: failures-only; verified/unknown stay silent (Q4 minimize noise).
5. **Phase 5.5 prerequisite**: skipped — `post_edit_guard` template was mature enough to clone directly (Q5 jump straight).
6. **Naming**: `subagent_verify.py` (Q6 focused; broaden later if Bash/ToolSearch verification added).

### E2E findings — false-positive insights worth remembering

The first E2E run on a real `Explore` subagent's transcript that had explored an external repo (SuperAGI) produced **49 claims, 42 unverified** — a 91% false-positive rate. Three root causes, all traced to naive design assumptions:

1. **field check too broad**: subagent introduced "settings.json" once at the top, then described another repo's tables (`users`, `agents`, `projects`) — every backtick was flagged. **Fix**: per-sentence proximity — `` `name` `` is checked only if **the same sentence** mentions `settings.json`.
2. **relative paths un-verifiable**: subagent's working directory ≠ ours. `./install.sh` exists in their repo, not in our cwd → false fail. **Fix**: `PATH_RE` matches only absolute (`/...`) and home (`~/...`) paths; relative paths are skipped.
3. **URL trailing backtick**: markdown ``` `https://x/api` ``` extracted as `https://x/api\`` → 404. **Fix**: `URL_RE` excludes trailing backtick + paren + bracket.

After the fixes: same transcript yields **8 claims, 1 unverified** — the lone unverified is a real signal (`https://app.superagi.com/api` returned non-2xx).

The lesson: **a verifier that flags 90% false positives is worse than no verifier — agents will train themselves to ignore advisories**. Proximity heuristics + scope conservatism are not optional for this class of hook; they are the design.

### Deferred to v2

- Git commit hash existence (`git cat-file -e <hash>`)
- Function/class name presence (`grep` against repo)
- Slash command existence (e.g. `/focus` from the original transcript-view incident — not currently caught)
- Optional B-route LLM-adversary subagent (`/ultra-verify` already covers high-stakes; v2 may add lighter inline adversary)
- Memory file integrity tracking (Issue #27430 mitigation: flag entries written by Claude vs verified by user)
