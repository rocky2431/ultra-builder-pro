# Ultra Builder PHILOSOPHY (v7.0)

**Authority**: This document defines the harness design philosophy. Every hook, command, skill, and agent must be justifiable by these principles. Conflicts → cite the principle, not the rule.

---

## 4 Core Goals

The harness exists to serve these — every constraint derives its legitimacy from contributing to one or more.

1. **Intent Fidelity** — what the user said they wanted is what gets built. No silent reinterpretation, no scope creep, no convenient shortcuts that drift from the original ask.
2. **Long-term Evolvability** — iteration #5 is as easy as iteration #1. Cognitive debt cannot accumulate; spec/task/code/doc must stay coherent.
3. **Production-Ready** — real persistence, real tests, real integration. No in-memory facades, no `default off` to dodge integration, no `it.skip` to dodge failures.
4. **Cognitive Coherence** — agent and user share the same picture of "what is currently true." Spec changes propagate. Doc rot is detected. Orphan code surfaces.

---

## 5 Commandments

### C1 — Goal-Always-Present
The agent never stops seeing the north-star. Every hook trigger that costs context-budget injects: project-level one-liner + current task acceptance criteria. The cost of repetition is always less than the cost of drift.

> **Test**: pick a random in-progress task, ask the agent "what's the acceptance criteria?" — if it can't answer in one sentence, this commandment is broken.

### C2 — Enabling > Defensive
Every `forbidden_pattern` ships with a runnable alternative. Prohibitions without enabling paths force agents to find loopholes (rename `mock` to `stub`, etc.). The cheaper path must be the right path.

> **Test**: scan all forbidden patterns; each must reference a `.ultra/templates/` file that the agent can copy.

### C3 — Sensors not Blockers
Hooks emit signal; agents and users decide. Block only the **truly irreversible**:
- `git push` to protected branches
- Funds transfer / on-chain transactions
- DB migrations / DROP / TRUNCATE
- Hardcoded secret commit
- Arbitrary code execution via user input

Everything else is `stderr` advisory — the work stands, the signal is delivered, the agent proceeds.

> **Test**: count `decision: "block"` outputs across all hooks; should map 1:1 to the irreversible list.

### C4 — Incremental Validation
The agent always knows "how far from done." Each PostToolUse updates `progress.json` with evidence completeness across dimensions (tests / persistence / integration / docs / spec-trace). Final-gate audits are forbidden — if a gap matters at the end, it matters mid-flight.

> **Test**: at any point in a task, `cat .ultra/tasks/<id>/progress.json` should answer "what's left."

### C5 — Bounded Autonomy
Autonomy is defined by goals, not rules. Inside the boundary the agent picks freely; crossing the boundary surfaces to the user.
- Inside: choosing libraries, naming, file layout, internal abstractions
- Crossing: weakening test assertions, modifying spec to match implementation, default-off feature flags, in-memory replacing real DB, scope reduction

> **Test**: any boundary-crossing action must trigger an `AskUserQuestion` or write to `.ultra/drift-log.md`.

---

## When commandments conflict

Goals override commandments. Commandments override rules. Cite the higher level:
- `commandment C2 overrides rule "no mock" → use testcontainer template`
- `goal Intent-Fidelity overrides commandment C5 → ask user before scope-reducing`

---

## Modifying this file

Changes to PHILOSOPHY require:
1. Concrete failure case the change addresses (linked observation in `.ultra/drift-log.md` or session_journal)
2. Impact assessment on existing hooks/commands
3. Migration of any dependent constraint

PHILOSOPHY is the only file whose changes propagate to forbidden_patterns / verification / agent prompts. Don't touch it casually.

---

## Origin

v7.0 derived from a system audit (2026-04-30) that identified three systemic gaps:
- Goal-Always-Present **completely missing** from mid-execution
- Incremental Validation **only in ultra-research** (write-immediately)
- CAAF Dynamic Override **completely missing** — circuit breakers escalated instead of relaxing minimally

References: Anthropic *Effective harnesses for long-running agents*, OpenAI *Harness engineering*, Martin Fowler *Harness engineering for coding agent users*, CAAF (arXiv 2604.17025).

---

## Contract Table (for harness maintainers)

> Each row is a hardcoded contract between two parts of the system. Changing one side **without** updating the other is the v7 audit's #1 cause of broken Goal-Always-Present injection. Update this table BEFORE editing either side; CI/system_doctor should diff it.

### Hook → File contracts (string keys, paths, schemas)

| Consumer | Reads | Source of truth | Failure mode if drift |
|----------|-------|-----------------|----------------------|
| `mid_workflow_recall._get_active_task_acceptance` | heading `## Acceptance Criteria` | `.ultra-template/tasks/contexts/TEMPLATE.md` | hook silently injects nothing (Goal-Always-Present dies) |
| `session_context.get_north_star_context` | headings `## One-line`, `## Hard Constraints`; section delimiter `\n---\n` | `.ultra-template/north-star.md` | SessionStart shows no goal |
| `session_context.get_north_star_context` | reads `.ultra/tasks/contexts/task-{id}.md` for active in_progress task | `tasks.json.tasks[].id` + `contexts/task-{id}.md` filename pattern | acceptance criteria not surfaced |
| `user_prompt_capture._try_write_north_star` | exact placeholder string `_(not yet defined — run \`/ultra-init\` or first user request will populate)_` | `.ultra-template/north-star.md` | placeholder never replaced; first-prompt capture lost |
| `post_edit_guard` mock advisory | path string `.ultra/templates/testcontainer-*` | `.ultra-template/templates/testcontainer-postgres.{ts,py}` | advisory points at non-existent file → agent ignores |
| `post_edit_guard` → `update_task_progress` | path `.ultra/tasks/progress/task-{id}.json` | created on-demand by `hook_utils._init_progress` | progress never persists |
| `relations_sync.normalize_ref` | trace_to form `specs/file.md#anchor` (strips leading `.ultra/`) | `tasks.json._schema.task_example.trace_to` | every trace_to flagged dangling |
| `relations_sync.index_spec_anchors` | GFM heading slugify (lowercase, non-word stripped, whitespace→hyphen, code-fence aware) | `.ultra-template/specs/*.md` headings | anchors never resolve → all dangling |
| `review-tests` agent JSON output | required field `enabling_alternative` pointing at `.ultra/templates/*` | `.ultra-template/templates/` | tests reviewer reverts to pure-defensive (loophole-friendly) |
| `hook_utils.EVIDENCE_DIMENSIONS` | 6 keys: `tests_written, tests_passed, persistence_real, feature_flags_audit, vertical_slice, spec_trace` | `progress.json.evidence_score`; quoted in `CLAUDE.md <verification>` and `commands/ultra-dev.md` Step 4 | renaming a dim breaks read of progress.json across hook + commands |
| `pre_compact_context` / `post_compact_inject` | `.ultra/compact-snapshot.md` | written by `pre_compact_context` itself | compact recovery loses goal context |
| `system_doctor` agent regex | agent names: `code-reviewer`, `debugger`, `review-\w+`, `smart-contract-\w+` | `~/.claude/agents/*.md` filenames | doctor reports false-positive missing agents |
| `block_dangerous_commands` rm regex | anchored: `\brm\s+(-[rf]+\s+)*~/?\s*$` (NOT `~` followed by anything) | shell command intent — block ONLY `rm ~`/`rm -rf ~/`, NOT `rm ~/.claude/x.bak` | over-block legitimate cleanups (was a v7-era false-positive) |

### settings.json → Hook contracts

| Hook event + matcher | Hook script | Notes |
|---------------------|-------------|-------|
| `PreToolUse:Bash` | `block_dangerous_commands.py` | irreversible-ops gate |
| `PreToolUse:Bash` | `rtk-rewrite.sh` | enabling: token rewrite |
| `PreToolUse:Write\|Edit\|Grep` | `mid_workflow_recall.py` | matcher MUST include `Grep` for symbol-query advisory (v7 addition) |
| `PostToolUse:Edit\|Write` | `post_edit_guard.py` | only SEC_CRITICAL blocks |
| `PostToolUse:Edit\|Write\|Bash` | `observation_capture.py` | passive sensor |
| `PostToolUse:Edit\|Write` | `relations_sync.py` | v7 — only acts when `.ultra/specs/*` or `.ultra/tasks/*` changes |

### .ultra-template → ultra-init contracts

The `/ultra-init` Step 4 MUST copy ALL of these. Adding a new template file requires updating ultra-init.md Step 4 list:
- `PHILOSOPHY.md` (this file)
- `north-star.md`
- `specs/{discovery,product,architecture}.md`
- `tasks/tasks.json`
- `tasks/contexts/TEMPLATE.md`
- `templates/` (full tree)
- `delivery-report.json`, `test-report.json`
- `docs/research/README.md`

### Maintenance protocol

Before editing any row's source-of-truth:
1. Find every consumer in this table
2. Update consumer + source together in one PR
3. Re-run end-to-end injection test (`/ultra-test --harness-self-check` if available, else manual)
4. Update this table if the contract surface changed

If a row gains/loses an entry, the v7 audit's lesson says: **the next contract drift will silently break Goal-Always-Present**. Don't let that happen.
