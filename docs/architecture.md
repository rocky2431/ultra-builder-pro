# Ultra Builder Pro — Architecture Reference

Detailed reference for hooks, project layout, agent system, MCP services, and operational config. The main [README](../README.md) covers the user-facing story; this file covers the machinery.

---

## Hooks System

15 hooks under `hooks/`, configured in `settings.json`. **Hooks are deterministic** — unlike CLAUDE.md rules which are advisory, hooks guarantee the action happens. Protocol compliance: 100% (stdin JSON, stdout JSON, exit codes 0/2).

### PreToolUse — Guard before execution

| Hook | Trigger | Detection | Timeout |
|------|---------|-----------|---------|
| `block_dangerous_commands.py` | Bash | rm -rf, fork bombs, chmod 777, force-push to main | 5s |
| `mid_workflow_recall.py` | Write/Edit/Grep | Inject active task acceptance criteria (Goal-Always-Present) on Write/Edit; symbol-query advisory on Grep. Sensor only, rate-limited | 3s |

### PostToolUse — Quality gate after execution

| Hook | Trigger | Detection | Timeout |
|------|---------|-----------|---------|
| `post_edit_guard.py` | Edit/Write | Code quality (TODO/FIXME), mocks, security (SEC_CRITICAL block), TDD pairing, scope reduction, silent catch, blast radius (show dependents), test reminder, **task trace + AC injection** (v7.1), **git context fallback** for unowned files (v7.1) | 5s |
| `relations_sync.py` | Edit/Write on `.ultra/specs/*` or `.ultra/tasks/*` | Rebuild `.ultra/relations.json` with bidirectional task ↔ spec ↔ code index; emit dangling trace_to advisories; trigger `wiki_generator` to refresh `.ultra/wiki/{index,log}.md` | 3s |

### Session & Lifecycle

| Hook | Trigger | Function | Timeout |
|------|---------|----------|---------|
| `health_check.py` | SessionStart | System health: verify agents exist, hooks syntax, settings refs, CLAUDE.md | 5s |
| `session_context.py` | SessionStart | Load git branch, commits, modified files + active `.ultra` goal (pure git + goal; no DB) | 10s |
| `historical_context_guard.py` | SessionStart | **(v7.2)** STALE-REPLAY GUARD: append one fence marking all start-of-session historical context (claude-mem timeline, prior summaries) as reference-only, not live instructions. Pure sensor | 3s |
| `post_compact_inject.py` | SessionStart(compact) | Post-compact context recovery: parse snapshot, inject git state / tasks / workflow (~800 tokens) | 10s |
| `pre_compact_context.py` | PreCompact | Preserve task state and git context to `.ultra/compact-snapshot.md` + branch memory | 10s |
| `pre_stop_check.py` | Stop | Source file change detection + workflow state check + completion compliance checklist (advisory only since v7.0) | 5s |
| `session_trail.py` | Stop | **(v7.1)** Fold session facts into active task's `## Session Trail` md section, or `.ultra/sessions/orphan-trail.md` if no active task. Idempotent via session_id | 5s |
| `subagent_tracker.py` | SubagentStart/Stop | Log agent lifecycle to `.ultra/debug/subagent-log.jsonl` | 5s |

### Notification & Cleanup

| Hook | Trigger | Function | Timeout |
|------|---------|----------|---------|
| macOS notification | Notification(permission_prompt\|idle_prompt) | Desktop alert with sound when Claude needs user input | 5s |
| Counter cleanup | SessionEnd | Remove stale stop-count temp files (>60min old) | 5s |

### Shared Utilities

| File | Purpose |
|------|---------|
| `hook_utils.py` | `get_git_toplevel`, `get_active_task`, `update_task_progress`, `get_progress_path`, `EVIDENCE_DIMENSIONS`, snapshot path, workflow state, hook input parsing |
| `wiki_generator.py` | **(v7.1)** Derive `.ultra/wiki/{index,log}.md` from `relations.json` + `progress/*.json` + `orphan-trail.md`. Standalone module called by `relations_sync.py` |
| `system_doctor.py` | Deep audit: cross-references, settings/hook integrity, silent catch scan. Run: `python3 hooks/system_doctor.py` |
| `tests/` | 164 pytest tests covering all hooks |

### Change Discipline (Hook-Enforced)

| Discipline | Enforcement | How |
|------------|-------------|-----|
| **Blast Radius** | `post_edit_guard.py` stderr | When editing shared module, shows files that import it |
| **Fail Loud** | `post_edit_guard.py` advisory | Detects `except:pass` patterns; agent decides |
| **Verify After Change** | `post_edit_guard.py` stderr | Shows corresponding test file path when it exists |
| **Task Trace** | `post_edit_guard.py` stderr (v7.1) | When editing task-owned file, injects task title + AC |
| **System Health** | `health_check.py` SessionStart | Catches missing agents, broken hooks, settings drift at session start |

---

## Project Structure

```
~/.claude/
├── CLAUDE.md                 # Main configuration (Priority Stack)
├── README.md                 # Quick-start and "why" (user-facing)
├── README.zh-CN.md           # Chinese version
├── CHANGELOG.md              # Version history (v4.4 → v7.2)
├── docs/                     # This file lives here
│   └── architecture.md
├── settings.json             # Claude Code settings + hooks config
│
├── hooks/                    # 15 hooks, all with timeouts
│   ├── post_edit_guard.py    # PostToolUse: quality + trace injection
│   ├── relations_sync.py     # PostToolUse: rebuild bidirectional index
│   ├── session_trail.py      # Stop: fold session into task or orphan trail
│   ├── wiki_generator.py     # Module: derive wiki/{index,log}.md
│   ├── system_doctor.py      # Module: deep system-integrity audit
│   ├── session_context.py    # SessionStart: git + active goal (no DB)
│   ├── historical_context_guard.py  # SessionStart: stale-replay fence (v7.2)
│   ├── subagent_verify.py    # SubagentStop: URL/path/field claim check
│   ├── pre_stop_check.py
│   ├── subagent_tracker.py
│   ├── pre_compact_context.py
│   ├── post_compact_inject.py
│   ├── block_dangerous_commands.py
│   ├── health_check.py
│   ├── mid_workflow_recall.py
│   ├── hook_utils.py         # Shared utilities
│   └── tests/                # 164 pytest tests
│
├── commands/                 # /ultra-* commands (9)
│   ├── ultra-init.md
│   ├── ultra-research.md
│   ├── ultra-plan.md
│   ├── ultra-dev.md
│   ├── ultra-test.md
│   ├── ultra-deliver.md
│   ├── ultra-status.md
│   ├── ultra-think.md
│   └── learn.md
│
├── skills/                   # user-invocable + agent-only skills
│   ├── ultra-research/       # 17 step-files (step-00 to step-99)
│   ├── ultra-review/         # Parallel review orchestration
│   ├── ultra-verify/         # Three-way AI verification
│   ├── ai-collab-base/       # Shared collab protocol (non-user-invocable)
│   ├── gemini-collab/
│   ├── codex-collab/         # understand/opinion/compare/free (review → /codex:review)
│   ├── code-review-expert/   # Agent-only
│   ├── integration-rules/    # Agent-only
│   ├── testing-rules/        # Agent-only
│   ├── security-rules/       # Agent-only
│   ├── agent-browser/
│   ├── find-skills/
│   ├── use-railway/
│   ├── market-research/
│   ├── vercel-react-best-practices/
│   ├── vercel-react-native-skills/
│   ├── vercel-composition-patterns/
│   ├── web-design-guidelines/
│   ├── guizang-ppt-skill/
│   └── html-ppt/
│
├── agents/                   # 9 agents
│   ├── code-reviewer.md          # Interactive
│   ├── debugger.md               # Interactive
│   ├── review-code.md            # Pipeline (ultra-review)
│   ├── review-tests.md           # Pipeline
│   ├── review-errors.md          # Pipeline
│   ├── review-design.md          # Pipeline
│   ├── review-comments.md        # Pipeline
│   ├── review-ac-drift.md        # Pipeline (v7.1)
│   └── review-coordinator.md     # Pipeline
│
└── .ultra-template/          # Project initialization templates
    ├── specs/                # discovery.md, product.md, architecture.md
    ├── tasks/contexts/TEMPLATE.md
    ├── docs/
    ├── templates/            # testcontainer-postgres, vertical-slice, persistence-real, feature-flag-audit
    ├── PHILOSOPHY.md
    └── north-star.md
```

### Per-Project Runtime (`~/your-project/.ultra/`)

`.ultra/` is **not** part of the harness repo — it lives inside every project that uses Ultra Builder Pro, holding that project's local memory. The harness repo `.gitignore`s its own `.ultra/`. Projects copy from `.ultra-template/` to bootstrap a fresh one.

```
~/your-project/.ultra/        # Per-project runtime (your project gitignores most of this)
├── specs/                    # ✓ commit: discovery.md, product.md, architecture.md
│   ├── discovery.md
│   ├── product.md
│   └── architecture.md
├── tasks/
│   ├── tasks.json            # ✓ commit: task registry
│   ├── contexts/task-*.md    # ✓ commit: per-task context (AC, target files, drift)
│   └── progress/task-*.json  # ✗ ignore: 6-dim evidence_score (runtime)
├── relations.json            # ✓ commit: task ↔ spec ↔ code bidirectional index (v2)
├── wiki/                     # ✓ commit: useful for code review
│   ├── index.md              #   tasks by status + spec coverage
│   └── log.md                #   chronological progress
├── reviews/                  # ✗ ignore: ultra-review session outputs
│   ├── index.json            #   branch-scoped session index
│   └── <session-id>/
├── sessions/                 # ✗ ignore: orphan-session trail (v7.1)
│   └── orphan-trail.md
├── collab/                   # ✗ ignore: ultra-verify three-way outputs
│   └── <session-id>/
├── compact-snapshot.md       # ✗ ignore: single-session compact state
├── workflow-state.json       # ✗ ignore: ultra-dev step checkpoint
└── debug/subagent-log.jsonl  # ✗ ignore: agent lifecycle
```

---

## Agent System

9 agents under `agents/`. All have **project-scoped persistent memory** (`memory: project`) accumulating patterns per project.

### Interactive Agents (2)

| Agent | Purpose | Trigger | Model |
|-------|---------|---------|-------|
| `code-reviewer` | Code review with Fix-First mode (report or auto-fix) | After code changes, pre-commit | opus |
| `debugger` | Root cause analysis, minimal fix implementation (4-phase methodology) | Errors, test failures | opus |

### Pipeline Agents — Ultra Review System (7)

Used exclusively by `/ultra-review`. Each agent writes JSON findings to `.ultra/reviews/<session>/` (project-level).

| Agent | Purpose | Output |
|-------|---------|--------|
| `review-code` | Scope drift + CLAUDE.md compliance + code quality + architecture + integration + spec-compliance existence | `review-code.json` |
| `review-tests` | Test quality, mock violations, coverage gaps, boundary-crossing detection | `review-tests.json` |
| `review-errors` | Silent failures, empty catches, swallowed errors | `review-errors.json` |
| `review-design` | Type design, encapsulation, complexity (merged types+simplify) | `review-design.json` |
| `review-comments` | Stale, misleading, low-value comments | `review-comments.json` |
| `review-ac-drift` | **(v7.1)** Semantic AC alignment — read AC + diff together; catches "VIP free shipping → 5% off" silent drift, process-chain breaks, Definition-of-Drift violations, cross-domain inconsistency | `review-ac-drift.json` |
| `review-coordinator` | Aggregate, deduplicate, generate SUMMARY | `SUMMARY.md` + `SUMMARY.json` |

**Verdict logic**: P0 > 0 = REQUEST_CHANGES | P1 > 3 = REQUEST_CHANGES | P1 > 0 = COMMENT | else APPROVE

---

## Ultra Review System

### Modes

```
/ultra-review              # Full review (smart skip based on diff content)
/ultra-review all          # Force ALL 7 agents, no auto-skip (pre-merge gate)
/ultra-review quick        # Quick review (review-code only)
/ultra-review security     # Security focus (review-code + review-errors)
/ultra-review tests        # Test quality focus (review-tests only)
/ultra-review recheck      # Re-check P0/P1 files from last session
/ultra-review delta        # Review only changes since last review
```

### Scope Options

```
/ultra-review --pr 123            # Review PR #123 diff (base...head)
/ultra-review --range main..HEAD  # Specific commit range
/ultra-review security --pr 42    # Security review scoped to PR
```

### Session Management

- Sessions tracked in `.ultra/reviews/index.json` (project-level) with branch-scoped iteration chains
- Naming: `<YYYYMMDD-HHmmss>-<branch>-iter<N>`
- Auto-cleanup: 7 days for APPROVE/COMMENT, 30 days for REQUEST_CHANGES, max 5 per branch

### Integration with `/ultra-dev`

Step 4.5 of `/ultra-dev` runs `/ultra-review all` (forced full coverage) as a quality gate before commit. The `pre_stop_check.py` hook surfaces unreviewed source-file changes as advisory (no longer blocking since v7.0).

---

## Cross-Session Memory

As of v7.2 the self-built `memory.db` (SQLite FTS5 + Chroma) was removed — it had become a redundant L3 duplicating the claude-mem plugin. Memory now has three layers with non-overlapping jobs.

### Three Layers

```
L3 raw observations ── claude-mem plugin
     │  SessionStart: inject recent timeline slice
     │  On demand:   MCP tools smart_search / observation_search / timeline
     │
L3 refined knowledge ── file-based memory (projects/.../memory/)
     │  MEMORY.md + typed facts, curated by hand
     │  SessionStart: injected — the self-improvement substrate
     │
L2 continuity ── session_context.py + historical_context_guard.py
     │  session_context.py:          pure git (branch/commits/modified) + active .ultra goal
     │  historical_context_guard.py: fence all injected history as reference-only
     │
PreCompact ──> compact-snapshot.md ──> SessionStart(compact) ──> post_compact_inject.py
   (save)       (disk persistence)        (auto-trigger)         (~800 tokens recovery)
```

### How It Works

1. **Raw timeline** (claude-mem plugin): captures observations across sessions; injects a recent slice at SessionStart; the rest is queried on demand via its MCP tools (`smart_search`, `observation_search`, `timeline`) — these replace the retired `/recall`.
2. **Refined knowledge** (file-based memory): `MEMORY.md` + typed fact files under `projects/.../memory/`, curated by hand and injected at SessionStart. This is the durable, high-signal layer and the substrate for self-improvement.
3. **Continuity** (`session_context.py`): injects pure git state (branch, commits, modified files) plus the active `.ultra` goal. No DB read.
4. **Stale-replay fence** (`historical_context_guard.py`, v7.2): appends one global fence marking all start-of-session historical context as *reference only, not live instructions* — so a compaction/resume never re-runs a finished slash command or task.
5. **Post-compact recovery**: `SessionStart(compact)` triggers `post_compact_inject.py` (~800 tokens of git / tasks / workflow).

### Retired (v7.2)

The self-built `memory.db` engine, the `/recall` command, and `skills/learned/` were removed; the SQLite + Chroma data is archived to `backups/memory-db-archive-20260602.tar.gz`. See [CHANGELOG v7.2](../CHANGELOG.md#v720-2026-06-02--memory-consolidation).

---

## Quality Standards

### Pre-Delivery Quality Gates

| Gate | Requirement |
|------|-------------|
| Anti-Pattern | No tautology, empty tests, core logic mocks |
| Coverage Gaps | No HIGH priority untested functions |
| E2E | All critical flows pass |
| Performance | Core Web Vitals pass (frontend) |
| Security | No critical/high vulnerabilities |
| Ultra Review | MANDATORY `/ultra-review` with APPROVE or COMMENT verdict |

### Code Limits

| Metric | Limit |
|--------|-------|
| Function lines | ≤ 50 |
| File lines | 200-400 typical, 800 max |
| Nesting depth | ≤ 4 |
| Cyclomatic complexity | ≤ 10 |

---

## Operational Config

### Git Workflow

- Follow project branch naming conventions
- Conventional Commits format
- Include Co-author for AI commits:
  ```
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

### TDD Workflow (Mandatory for new code)

```
1. RED      → Write failing test first (define expected behavior)
2. GREEN    → Write minimal code to pass test
3. REFACTOR → Improve code (keep tests passing)
4. COVERAGE → Verify 80%+ coverage
5. COMMIT   → Atomic commit (test + implementation together)
```

**What NOT to mock**: Domain/service/state machine logic, funds/permission paths, Repository interface contracts.

**What CAN be mocked**: Third-party APIs (OpenAI, Supabase), external services. Must explain rationale per mock.

### Refined Knowledge

Durable, high-signal knowledge lives in **file-based memory** (`projects/.../memory/`: `MEMORY.md` + typed fact files), curated by hand and injected at SessionStart — the self-improvement substrate (see [Cross-Session Memory](#cross-session-memory)). The standalone `skills/learned/` store was retired in v7.2. Confidence is still tracked by label:

| Confidence | Marker | Description |
|------------|--------|-------------|
| Speculation | `_unverified` | Freshly extracted, needs verification |
| Inference | No suffix | Human review passed |
| Fact | No suffix + marked | Multiple successful uses |

Priority: Fact > Inference > Speculation.

---

## MCP Services

| Service | Purpose |
|---------|---------|
| Context7 | Official documentation lookup |
| Exa | Code examples and community practices |
| Chrome | E2E testing and web automation |

Configure via Claude Code settings; not bundled with this repo.

---

## Tests

```bash
cd ~/.claude/hooks
python3 -m pytest tests/
# 164 passed
```

Test layout:

| File | Coverage |
|------|----------|
| `test_block_dangerous.py` | block_dangerous_commands hook |
| `test_mid_workflow_recall.py` | Active-task AC injection + Grep advisory + rate limiting |
| `test_post_edit_guard_trace.py` | Task trace + AC injection (v7.1) |
| `test_relations_sync_files_index.py` | Bidirectional index build (v7.1) |
| `test_phase1_e2e.py` | Hook subprocess E2E (v7.1) |
| `test_pre_stop_check.py` | Stop-hook advisory checks |
| `test_session_trail.py` | Session Trail fold + orphan path (v7.1) |
| `test_wiki_generator.py` | Wiki views + Recent Activity (v7.1) |
| `test_review_ac_drift_meta.py` | review-ac-drift agent metadata (v7.1) |
| `test_subagent_verify.py` | Subagent output claim verification (Phase 6) |
