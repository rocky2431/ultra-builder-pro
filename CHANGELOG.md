# Changelog

All notable changes to Ultra Builder Pro.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) loosely — newest first, each entry is `Why → What → Files`.

---

## v7.1.0 (2026-05-01) — Dynamic Project Knowledge Base

Live project knowledge base that survives requirement drift. Extends the v7.0 sensor-first harness with bidirectional task ↔ code ↔ spec traceability and a compounding wiki layer.

**Why**: Engineering reality is that requirements drift. PRDs and code decouple; the gap is where technical debt and silent failures grow. Static docs cannot follow this drift. We need a layer that updates itself when code changes — and surfaces both *engineering breaks* (schema/types/calls) and *functional breaks* (semantics/intent).

**Five additions, all sensor-only, all reusing v7 substrate**:

- **GAP 1 — Reverse trace** (`hooks/post_edit_guard.py`): When editing a file, stderr injects which task owns it + first AC bullets. Files outside any task get a git-context fallback (branch + last commit). Non-Ultra projects stay silent.
- **GAP 2 — AC drift detection** (`agents/review-ac-drift.md`): 7th specialist in the ultra-review pipeline. Reads AC text and diff together; judges semantic alignment. Catches drift structural lints miss — "VIP free shipping" silently shipped as "VIP 50% off", process-chain breaks, Definition-of-Drift violations, cross-domain inconsistency, unstated removal.
- **GAP 3 — Wiki views** (`hooks/wiki_generator.py`): Derives `.ultra/wiki/{index,log}.md` from `relations.json` + `progress/*.json`. Index groups tasks by status + spec coverage. Log orders progress chronologically. Recent Activity table merges task and orphan activity (last 30 days).
- **GAP 4 — Session trail fold-back** (`hooks/session_trail.py`): Stop hook folds session facts into the active task's context md as a `## Session Trail` section. Idempotent via session_id de-dup. The Karpathy "compounding artifact", in pure structural form (no LLM call).
- **Phase 5 — Orphan session handling**: When no active task exists, sessions still leave residue. Trace fallback to git context, session facts to `.ultra/sessions/orphan-trail.md`, Recent Activity table in wiki. KB now reflects all work — exploratory edits, hotfixes, cross-task hops.

**Foundation files** (machine-maintained; humans + LLMs read):
- `.ultra/relations.json` — task ↔ spec section ↔ code bidirectional index (schema v2 with `files` reverse map)
- `.ultra/tasks/progress/task-*.json` — per-task 6-dim evidence_score + files_touched + advisories
- `.ultra/sessions/orphan-trail.md` — sessions without active task
- `.ultra/wiki/{index,log}.md` — derived human-readable views
- `task-*.md ## Session Trail` — folded-back session bullets

**Tests**: 179 hook tests pass. 67 new tests across the five additions.

**Touched**: `hooks/{post_edit_guard,relations_sync,session_trail,wiki_generator}.py`, `agents/review-ac-drift.md`, `skills/ultra-review/SKILL.md`, `skills/ultra-review/references/unified-schema.md`, `settings.json` (Stop hook), 5 new test files.

---

## v7.0.0 (2026-04-30) — Sensor-First Harness + Goal-Always-Present

Major shift in hook philosophy: **blocks reserved for irreversible actions only** (hardcoded secrets, SQL injection, force-push to main, DB migration commits). Recoverable patterns (mocks, scope reduction, silent catches, TODO/FIXME, default-off feature flags) become **advisories** — the agent reads, decides, proceeds.

**Why**: Pre-v7 block-mode triggered an over-correction loop. Agents would edit tests / specs / assertions to escape blocks, drifting from user intent. v7 inverts: hooks emit signal, humans and agents decide. PHILOSOPHY.md C3 (Sensors not Blockers) + C4 (Incremental Validation) codify this.

**New mechanics**:
- `progress.json` — per-task 6-dim `evidence_score` (tests_written, tests_passed, persistence_real, feature_flags_audit, vertical_slice, spec_trace), updated continuously by `post_edit_guard.py`
- `relations.json` v1 — derived task ↔ spec index, emits dangling `trace_to` advisories on stderr
- Goal-Always-Present — `mid_workflow_recall.py` injects active task's acceptance criteria on Edit/Write so the goal is in front of the agent at decision time
- `.ultra/templates/` — testcontainer-postgres, vertical-slice, persistence-real, feature-flag-audit canonical code templates
- Forbidden patterns ship with **Enabling Templates** (the right path is the cheap path) — no more pure prohibitions
- `pre_stop_check.py` simplified to advisory-only (the pre-v7 circuit breaker was an admission that block loops were harmful, not a fix)

**Touched**: All 15 hooks audited. `agents/review-coordinator.md` updated for sensor mode. `commands/ultra-dev.md` Phase 4 Quality Gates rewritten as `evidence_score` reads (not recompute).

---

## v6.8.0 (2026-03-31) — Research Step-File Architecture

**Core change**: Replaced monolithic `ultra-research.md` (491 lines) with **step-file architecture** inspired by [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) (42.9k stars).

**What changed**:
- `skills/ultra-research/SKILL.md` — orchestrator with step routing and project type detection
- `skills/ultra-research/steps/step-{00-99}.md` — 17 self-contained step files (3122 lines total, ~200 lines/step)
- Each step has: MANDATORY RULES, SEARCH STRATEGY (pre-written queries), OUTPUT TEMPLATE (field-level structure), SUCCESS METRICS, FAILURE MODES
- `step-99-synthesis.md` — generates `research-distillate.md` (token-efficient summary for /ultra-plan)
- `commands/ultra-research.md` — slimmed to 60-line router pointing to SKILL.md

**Why**: Previous single-file approach had ~16 lines of instruction per step. LLM attention was diluted across 5 Rounds. Now each step gets focused, dense instructions → **~11x instruction density increase**.

**Key improvements**: Mandatory web search with pre-written queries per step | Structured output templates with field-level specs | Write-immediately discipline (no context loss) | [C] Continue user gates | Research distillate for /ultra-plan consumption | Field-level spec validation in /ultra-plan

---

## v6.5.0 (2026-03-20) — Product Velocity Fusion

**Fast product iteration + engineering discipline**, inspired by [garrytan/gstack](https://github.com/garrytan/gstack) context engineering patterns:

**Product Thinking Layer**:
- `/ultra-research` Round 0.0: **Problem Validation with 6 Forcing Questions** — Demand Reality, Status Quo, Desperate Specificity, Narrowest Wedge, Observation & Surprise, Future-Fit. Smart routing by product stage (pre-product/has users/paying/engineering)
- `/ultra-plan` Step 0: **Scope Mode Selection** — EXPAND (think bigger), SELECTIVE (cherry-pick expansions), HOLD (make bulletproof), REDUCE (cut to minimum). Commitment rule: no silent drift

**Review Acceleration**:
- `review-code` agent Step 0: **Scope Drift Detection** — compares stated intent (tasks/branch/commits) vs actual diff, detects scope creep (P1) and missing requirements (P0)
- `code-reviewer` agent: **Fix-First dual mode** — `report` (findings only) and `fix` (AUTO-FIX mechanical issues, ASK judgment calls). Now has Write/Edit tools
- Unified schema: new `scope-drift` and `spec-compliance` categories

**CLAUDE.md Enhancements**:
- `<ask_user_format>`: standardized AskUserQuestion format (re-ground context, simplify, recommend, options, dual-scale effort)
- **Completeness Principle**: KISS decides WHAT to build; Completeness decides HOW THOROUGH. No half-finished features
- `<red_flags>` + `<verification>`: new Completeness row and "Scope correct" verification
- `<work_style>`: proactive stage detection (suggest skills based on user's current phase)

**Stop Hook Simplification**:
- `pre_stop_check.py`: 474 → 154 lines. Three-layer → two-layer check
- Removed: review artifact scanning, security file detection, incomplete work patterns, /ultra-review routing
- Kept: circuit breaker + source file change detection → unified code-reviewer suggestion
- Design: complex audits are user's responsibility via `/ultra-review`

---

## v6.3.0 (2026-03-09) — Memory System v2

**Structured summaries, real session identity, security hardening**, verified by 3 rounds of ultra-verify (Claude + Gemini + Codex):

**Schema v2 Migration**:
- New `session_summaries` table: structured JSON fields (`request`, `completed`, `learned`, `next_steps`)
- New `observations` table: file changes (Edit/Write) + test failures (Bash), max 20/session, deduped by content hash
- New `summaries_fts` FTS5 index over structured summaries for fast text search
- `sessions` table: added `content_session_id`, `initial_request` columns

**Real Session Identity**:
- `content_session_id` from hook protocol replaces merge-window-based ID (fixed stop_count=4306 bug)
- `stop_hook_active=true` re-triggers skip DB write entirely

**AI Summary Upgrade**:
- Model: Haiku (cost-effective, structured output) with `max_tokens=1000`
- Output: structured JSON `{request, completed, learned, next_steps}` — pipe-separated bullets per field
- Stored in `session_summaries` table (structured) + `sessions.summary` (legacy compat)

**New Hooks (2)**:
- `user_prompt_capture.py` (UserPromptSubmit): captures initial user request per session
- `observation_capture.py` (PostToolUse): captures file changes and test failures as session observations

**Proactive Recall Upgrade**:
- SessionStart: last session one-liner + up to 3 branch-relevant structured summaries
- PreCompact: `LEFT JOIN session_summaries` for structured summary preference

**Security Hardening**:
- Path validation, SQL allowlist, daemon error logging, dead code removal

---

## v6.2.0 (2026-03-08) — Multi-AI Collaboration Refactor

**Shared base architecture + three-way AI verification**, verified by 3 rounds of ultra-verify audit (Claude + Gemini + Codex):

- New `ai-collab-base` skill: shared collaboration protocol, modes, prompt templates (non-user-invocable)
- `sync.sh` keeps canonical files in sync across 3 consumer skills; eliminates ~90% structural duplication between gemini-collab and codex-collab
- New `ultra-verify` skill: three-way AI cross-verification (Claude + Gemini + Codex)
  - 4 modes: `decision`, `diagnose`, `audit`, `estimate`
  - Confidence scoring: Consensus (3/3), Majority (2/3), No Consensus
  - Degraded operation: one AI fails → two-way, two fail → Claude-only with warning
- Rewritten `gemini-collab` and `codex-collab`: thin skills pointing to shared base
- CLI bug fixes verified against actual `--help` output

---

## v6.1.0 (2026-03-08) — Product Discovery Round 0

**Product Discovery & Strategy phase** — fills the gap between vague ideas and technical specification. Inspired by [phuryn/pm-skills](https://github.com/phuryn/pm-skills) frameworks:

- New Round 0 in `/ultra-research` with 5 sub-steps:
  - **Opportunity Discovery**: OST framework (Teresa Torres), Opportunity Score prioritization (Dan Olsen)
  - **Market Assessment**: TAM/SAM/SOM dual estimation (top-down + bottom-up), WebSearch for real data
  - **Competitive Landscape**: Comparison matrix + Porter's Five Forces brief
  - **Product Strategy**: Condensed Strategy Canvas (Vision/Segments/Value Prop/Trade-offs/Defensibility)
  - **Assumptions & Validation Plan**: Risk categorization + experiment design (Pretotyping)
- New `discovery.md` spec template in `.ultra-template/specs/`
- Round 0 is **optional** — auto-skipped for Feature Only mode or when market research already exists

---

## v6.0.0 (2026-03-07) — Consolidation Release

**System consolidation, cleanup, and Multi-AI collaboration**:

- New `gemini-collab` skill: Gemini CLI as sub-agent for review, project analysis, second opinions
- New `codex-collab` skill: OpenAI Codex CLI as sub-agent with built-in `codex review` integration
- Removed codex skill and all references
- Stop hook hardening: removed main branch bypass, fixed git status path truncation
- Comprehensive hook audit: 20 fixes, model unification, 2 new hooks (Notification, SessionEnd)
- Ultra-think rewrite: adversarial reasoning framework
- All 12 agents unified to opus model
- Session summary model upgraded to opus
- Post-compact context injection via SessionStart(compact) hook

---

## v5.9.2 (2026-03-05) — Hook Audit & Model Unification

**Comprehensive hook audit against official docs + community best practices + model unification**:

- All 12 agents unified to `opus` model (fixed `code-reviewer`/`debugger` inherit, `tdd-runner` haiku)
- AI summary daemon upgraded from Sonnet to Opus
- 20 hook fixes across 3 tiers (protocol compliance, security, performance)
- New Notification + SessionEnd hooks
- `pre_stop_check.py`: Added `stop_hook_active` fast path per official docs (prevents infinite Stop hook loops)

---

## v5.9.1 (2026-03-04) — Hook Hardening + Post-Compact Recovery

- New `post_compact_inject.py`: SessionStart(compact) hook injects ~800 tokens of recovery context after auto-compact
- Stop hook hardened: 3-layer → 4-layer check; security-sensitive file detection; `stop_hook_active` loop guard
- Permission cleanup: removed obsolete entries, added 8 missing tools

---

## v5.9.0 (2026-03-02) — Process Discipline Fusion

**Superpowers Process Discipline Fusion** — absorbed key process principles, closing 3 process gaps:

- `ultra-dev.md` Step 0.5: Design Approval Gate (P0) — task breakdown overview before code
- `ultra-dev.md` Quality Gate #7: Spec Compliance Check (P1)
- `review-code.md` Step 7: Spec compliance verification per acceptance criterion
- `ultra-review SKILL.md`: 3-Fix Circuit Breaker (per-file fix counter; suggest architecture discussion after 3+ files)
- `debugger.md`: 5-step → 4-phase systematic methodology with Root Cause Investigation IRON LAW

---

## v5.8.1 (2026-02-28) — System-Level Optimization

**Context Protection + Pipeline Reliability + Workflow Resilience** — targeting 65% → 80%+ completion rate based on 285-session usage analysis:

- Review iteration cap (MAX=2), unresolved findings → UNRESOLVED.md
- Hook output compression (~70%); WARN/HIGH patterns deferred to review-code agent
- `/ultra-dev` workflow checkpoint at steps 3.3/4/4.5/6
- `review_wait.py`: structured JSON output with partial success
- Step 0 resume check reads `.ultra/workflow-state.json`

---

## v5.8.0 (2026-02-20) — AI Summarization + Vector Search

**AI-Powered Memory Upgrade** — transcript-based summaries, semantic vector search, hybrid retrieval, forked recall context:

- `session_journal.py`: AI summarization via double-fork daemon (non-blocking, 10s delay)
  - Three-tier fallback: `claude -p` → Anthropic SDK → git commits
  - Auto-upserts Chroma embedding after summary generation
- `memory_db.py`: Chroma vector search engine (PersistentClient + local ONNX)
  - `hybrid_search()`: RRF (k=60) fusion of FTS5 + Chroma
  - CLI: `semantic`, `hybrid`, `reindex-chroma`
- `recall` skill: `context: fork` (no main-context pollution); default hybrid mode

---

## v5.7.0 (2026-02-16) — Cross-Session Memory

**Cross-Session Memory System** — lightweight auto-capture + on-demand retrieval, designed as a safe alternative to claude-mem:

- `hooks/memory_db.py` — SQLite FTS5 storage engine + CLI tool
- `hooks/session_journal.py` — Stop hook auto-captures branch/files/commits per session
- `skills/recall/SKILL.md` — `/recall` skill for on-demand search

**Learned from claude-mem failure**: claude-mem injected ~25k tokens at SessionStart causing context explosion. Our approach: inject 1 line (~50 tokens), search on-demand.

---

## v5.6.1 (2026-02-14) — Project Isolation

**Project-Level Artifact Isolation** — all per-project output moved from global `~/.claude/` to project-level `.ultra/`. Eliminates cross-project pollution (review false positives, wrong-project compact-snapshot, irrelevant agent memory).

- 3 hooks updated with `git rev-parse --show-toplevel` detection
- All 12 agents switched from `memory: user` to `memory: project`
- `.gitignore` updated to exclude `.ultra/reviews/`, `.ultra/compact-snapshot.md`, `.ultra/debug/`

---

## v5.6.0 (2026-02-14) — System Integration Dimension

**Macro-level integration guarantees** complementing existing micro-level component quality:

- New CLAUDE.md `<integration>` block: Vertical Slice, Walking Skeleton, Contract-First, Integration Proof, Orphan Detection
- New skill `integration-rules` (agent-only) with good/bad examples
- `review-code` agent: +integration step, +4 severity rows (orphan P1, missing integration test P1, horizontal-only P2, missing contract P2)
- `ultra-plan`: Walking skeleton as Task #1 (P0); contract definition tasks; integration checkpoints every 3-4 tasks
- `ultra-dev`: Integration test dimension in RED phase

**Schema**: `integration` category added to unified-schema-v1.

---

## v5.5.1 (2026-02-14) — Codex v6.0 + Review Enhancements

- Codex v6.0 integration
- `/ultra-review all` mode (force all agents, no auto-skip)
- `pre_stop_check.py` marker-based escape hatch (block once, allow on second attempt)

---

## v5.5.0 (2026-02-14) — Ultra Review System

**Native parallel code review pipeline** — 6 specialized agents + coordinator:

- `review-code` (CLAUDE.md compliance, code quality, architecture)
- `review-tests` (test quality, mock violations, coverage gaps)
- `review-errors` (silent failures, empty catches, swallowed errors)
- `review-design` (type design, encapsulation, complexity — merged types+simplify)
- `review-comments` (stale, misleading, low-value comments)
- `review-coordinator` (aggregate, deduplicate, generate SUMMARY)

**`/ultra-review` skill**: Modes (full, all, quick, security, tests, recheck, delta, custom), scope options (`--pr`, `--range`), branch-scoped session index, lifecycle management (7d/30d cleanup, max 5 per branch), verdict logic (P0>0 or P1>3 = REQUEST_CHANGES, P1>0 = COMMENT, else APPROVE).

---

## v5.4.1 (2026-02-08) — Hooks Hardening

- Merged 3 PostToolUse hooks (`code_quality.py`, `mock_detector.py`, `security_scan.py`) into unified `post_edit_guard.py`
- Removed `branch_protection.py`; simplified `pre_stop_check.py`
- 9 hooks → 6 hooks
- Added `timeout` to all hooks (5s default, 10s for SessionStart/PreCompact)

---

## v5.4.0 (2026-02-07) — Agent & Memory Edition

- 3 new agents: `code-reviewer`, `tdd-runner`, `debugger`
- All agents now have persistent memory (project-level since v5.6.1)
- 2 new agent-only skills: `testing-rules`, `security-rules`
- 3 new hooks: `subagent_tracker.py`, `pre_compact_context.py`
- Agent Teams enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)

---

## v5.3.0 (2026-02-01) — Lean Architecture Edition

**Apply Anthropic's "Start simple, add complexity only when simpler solutions fall short."**

- Removed redundant agents (build-error-resolver, doc-updater, e2e-runner, frontend-developer, refactor-cleaner)
- Removed redundant skills (gemini, promptup, skill-creator)
- Removed routing hooks (`user_prompt_agent.py`, `agent_reminder.py`)
- All hooks: standardized error handling (catch → stderr log → safe pass-through)

**Architecture**: CLAUDE.md + Commands + Quality Hooks (three-layer, no bloat).

---

## v5.2.x (2026-01-29) — Hooks Optimization & Codex Purification

- New hooks: `block_dangerous_commands.py`, `session_context.py`
- Enhanced detection: it.skip/test.skip, hardcoded URL/port, static state, local file
- Layer-specific solutions (Functional Core vs Imperative Shell)
- Hook output protocol fixes (`tool` → `tool_name`, decision: block for CRITICAL)
- CLAUDE.md refactoring: removed operational config (322 → 272 lines)

---

## v5.0.0 (2026-01-26) — Agent System Edition

**10 custom agents** introduced:
- `architect`, `planner`, `tdd-guide`, `build-error-resolver`, `e2e-runner`, `frontend-developer`, `refactor-cleaner`, `doc-updater`, `smart-contract-specialist`, `smart-contract-auditor`

- New `/learn` command for pattern extraction
- `skills/learned/` directory
- Confidence levels: Speculation → Inference → Fact

---

## v4.x (2026-01-01 — 2026-01-07) — Foundation

- v4.5.1 PromptUp Edition: 6 evidence-based principles, boundary detection
- v4.5.0 Agent Architecture: backend-architect, smart-contract specialist + auditor
- v4.4.0 Streamlined: Unified Priority Stack in CLAUDE.md, Codex/Gemini integration, Anti-Pattern Detection in `/ultra-test`

---

[Full git history available via `git log --oneline`.]
