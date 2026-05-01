# Ultra Builder Pro — Architecture Reference

Detailed reference for hooks, project layout, agent system, MCP services, and operational config. The main [README](../README.md) covers the user-facing story; this file covers the machinery.

---

## Hooks System

15 hooks under `hooks/`, configured in `settings.json`. **Hooks are deterministic** — unlike CLAUDE.md rules which are advisory, hooks guarantee the action happens. Protocol compliance: 100% (stdin JSON, stdout JSON, exit codes 0/2).

### PreToolUse — Guard before execution

| Hook | Trigger | Detection | Timeout |
|------|---------|-----------|---------|
| `block_dangerous_commands.py` | Bash | rm -rf, fork bombs, chmod 777, force-push to main | 5s |
| `mid_workflow_recall.py` | Write/Edit/Grep | Inject past test failures + edit history + learned lessons + active task acceptance criteria from memory.db (rate-limited) | 3s |

### PostToolUse — Quality gate after execution

| Hook | Trigger | Detection | Timeout |
|------|---------|-----------|---------|
| `post_edit_guard.py` | Edit/Write | Code quality (TODO/FIXME), mocks, security (SEC_CRITICAL block), TDD pairing, scope reduction, silent catch, blast radius (show dependents), test reminder, **task trace + AC injection** (v7.1), **git context fallback** for unowned files (v7.1) | 5s |
| `relations_sync.py` | Edit/Write on `.ultra/specs/*` or `.ultra/tasks/*` | Rebuild `.ultra/relations.json` with bidirectional task ↔ spec ↔ code index; emit dangling trace_to advisories; trigger `wiki_generator` to refresh `.ultra/wiki/{index,log}.md` | 3s |
| `observation_capture.py` | Edit/Write/Bash | Capture file changes, test failures, significant commands (git/build/deploy) as session observations | 3s |

### User Input

| Hook | Trigger | Function | Timeout |
|------|---------|----------|---------|
| `user_prompt_capture.py` | UserPromptSubmit | Capture initial user request per session for structured summaries | 3s |

### Session & Lifecycle

| Hook | Trigger | Function | Timeout |
|------|---------|----------|---------|
| `health_check.py` | SessionStart | System health: verify agents exist, hooks syntax, DB health, settings refs, CLAUDE.md | 5s |
| `session_context.py` | SessionStart | Load git branch, commits, modified files + last session one-liner + branch memory from DB | 10s |
| `post_compact_inject.py` | SessionStart(compact) | Post-compact context recovery: parse snapshot, inject git state / tasks / workflow / memory (~800 tokens) | 10s |
| `pre_compact_context.py` | PreCompact | Preserve task state and git context to `.ultra/compact-snapshot.md` + branch memory | 10s |
| `pre_stop_check.py` | Stop | Source file change detection + workflow state check + completion compliance checklist (advisory only since v7.0) | 5s |
| `session_journal.py` | Stop | Auto-capture session + spawn AI summary daemon (Haiku, non-blocking) → SQLite + Chroma | 5s |
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
| `memory_db.py` | SQLite FTS5 + Chroma vector engine + CLI tool — foundation for all memory hooks |
| `wiki_generator.py` | **(v7.1)** Derive `.ultra/wiki/{index,log}.md` from `relations.json` + `progress/*.json` + `orphan-trail.md`. Standalone module called by `relations_sync.py` |
| `system_doctor.py` | Deep audit: cross-references, DB quality, Chroma consistency, silent catch scan. Run: `python3 hooks/system_doctor.py` |
| `tests/` | 179 pytest tests covering all hooks |

### Change Discipline (Hook-Enforced)

| Discipline | Enforcement | How |
|------------|-------------|-----|
| **Blast Radius** | `post_edit_guard.py` stderr | When editing shared module, shows files that import it |
| **Fail Loud** | `post_edit_guard.py` advisory | Detects `except:pass` patterns; agent decides |
| **Verify After Change** | `post_edit_guard.py` stderr | Shows corresponding test file path when it exists |
| **Task Trace** | `post_edit_guard.py` stderr (v7.1) | When editing task-owned file, injects task title + AC |
| **System Health** | `health_check.py` SessionStart | Catches missing agents, broken hooks, DB issues at session start |

---

## Project Structure

```
~/.claude/
├── CLAUDE.md                 # Main configuration (Priority Stack)
├── README.md                 # Quick-start and "why" (user-facing)
├── README.zh-CN.md           # Chinese version
├── CHANGELOG.md              # Version history (v4.4 → v7.1)
├── docs/                     # This file lives here
│   └── architecture.md
├── settings.json             # Claude Code settings + hooks config
│
├── hooks/                    # 15 hooks, all with timeouts
│   ├── post_edit_guard.py    # PostToolUse: quality + trace injection
│   ├── relations_sync.py     # PostToolUse: rebuild bidirectional index
│   ├── session_trail.py      # Stop: fold session into task or orphan trail
│   ├── wiki_generator.py     # Module: derive wiki/{index,log}.md
│   ├── observation_capture.py
│   ├── user_prompt_capture.py
│   ├── session_context.py
│   ├── session_journal.py
│   ├── pre_stop_check.py
│   ├── subagent_tracker.py
│   ├── pre_compact_context.py
│   ├── post_compact_inject.py
│   ├── block_dangerous_commands.py
│   ├── health_check.py
│   ├── mid_workflow_recall.py
│   ├── hook_utils.py         # Shared utilities
│   ├── memory_db.py          # SQLite FTS5 + Chroma engine
│   └── tests/                # 179 pytest tests
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
├── skills/                   # 22 skills (+ learned/)
│   ├── ultra-research/       # 17 step-files (step-00 to step-99)
│   ├── ultra-review/         # Parallel review orchestration
│   ├── ultra-verify/         # Three-way AI verification
│   ├── ai-collab-base/       # Shared collab protocol (non-user-invocable)
│   ├── gemini-collab/
│   ├── codex-collab/         # understand/opinion/compare/free (review → /codex:review)
│   ├── recall/               # Cross-session memory search
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
│   ├── html-ppt/
│   └── learned/              # Patterns from /learn
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
├── memory/                   # ✗ ignore: cross-session memory
│   ├── memory.db             #   SQLite FTS5
│   ├── chroma/               #   Chroma vector embeddings
│   └── sessions.jsonl        #   append-only backup
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

### Architecture

```
UserPromptSubmit ──> user_prompt_capture.py ──> initial_request (sessions table)
PostToolUse ──> observation_capture.py ──> observations table (max 20/session)

Stop hook (auto)                    /recall skill (forked context)
     │                                     │
     ▼                                     ▼
session_journal.py ──> SQLite FTS5 <── memory_db.py CLI
     │                  (memory.db)        │
     │                  Schema v2:         │
     │                  - sessions         │
     │                  - session_summaries (structured JSON)
     │                  - observations
     │                  - summaries_fts (FTS5)
     │                                     ▼
     │                  daemon (10s) ──> Haiku ──> structured JSON
     │                                  ──> SQLite + Chroma
     ▼
sessions.jsonl (backup)      .ultra/memory/chroma/ (vector embeddings)

PreCompact ──> compact-snapshot.md ──> SessionStart(compact) ──> post_compact_inject.py
   (save)       (disk persistence)        (auto-trigger)         (~800 tokens recovery)
```

### How It Works

1. **Initial request capture** (UserPromptSubmit hook): captures first user prompt per session
2. **Observation capture** (PostToolUse hook): records file changes (Edit/Write) and test failures (Bash) — max 20 per session, deduped by content hash
3. **Auto-capture** (Stop hook): every response records branch, cwd, modified files
4. **AI Summary** (async daemon): double-fork daemon waits 10s after session stop, extracts transcript (head+tail sampling: 4K+11K chars), generates structured JSON via Haiku (three-tier fallback: claude CLI → Anthropic SDK → git commits)
5. **Vector Embedding**: after AI summary, auto-upserts to Chroma (local ONNX, no API key)
6. **Merge window**: multiple stops within 30 minutes merge into one session record
7. **Real session identity**: `content_session_id` from hook protocol for accurate session tracking
8. **SessionStart injection**: ONE line (~50 tokens) about last session + up to 3 branch-relevant structured summaries
9. **Post-compact recovery**: `SessionStart(compact)` triggers `post_compact_inject.py` (~800 tokens of git/tasks/workflow/memory)
10. **Hybrid search**: `/recall` runs in forked context, combines FTS5 keyword + Chroma semantic via RRF (k=60)

### `/recall` Usage

```
/recall                          # Recent 5 sessions
/recall auth bug                 # Hybrid search (FTS5 + semantic RRF)
/recall --semantic "login flow"  # Pure semantic vector search
/recall --keyword session_journal # Pure FTS5 keyword search
/recall --recent 10              # Recent 10 sessions
/recall --date 2026-02-16        # Sessions on specific date
/recall --save "Fixed auth bug"  # Save summary for latest session
/recall --tags "auth,bugfix"     # Add tags
/recall --stats                  # Database statistics
/recall --cleanup 90             # Delete sessions older than 90 days
```

### Storage

- **Database**: `.ultra/memory/memory.db` (project-level, SQLite FTS5)
- **Vectors**: `.ultra/memory/chroma/` (Chroma + ONNX embeddings)
- **Backup**: `.ultra/memory/sessions.jsonl` (append-only)
- **Retention**: 90 days default
- **Dependencies**: chromadb (ONNX), anthropic SDK (optional, for AI summary fallback)

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

### Learned Patterns

Patterns extracted via `/learn` are stored in `skills/learned/`:

| Confidence | File Suffix | Description |
|------------|-------------|-------------|
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
python3 -m pytest tests/ --ignore=tests/test_pre_stop_check.py
# 179 passed (1 stale Phase 6 test ignored)
```

Test layout:

| File | Coverage |
|------|----------|
| `test_block_dangerous.py` | block_dangerous_commands hook |
| `test_memory_db.py` | SQLite FTS5 + Chroma engine |
| `test_mid_workflow_recall.py` | Recall queries + rate limiting |
| `test_observation_capture.py` | Observation deduping + caps |
| `test_post_edit_guard_trace.py` | Task trace + AC injection (v7.1) |
| `test_relations_sync_files_index.py` | Bidirectional index build (v7.1) |
| `test_phase1_e2e.py` | Hook subprocess E2E (v7.1) |
| `test_session_journal_prompt.py` | AI summary prompt construction |
| `test_session_trail.py` | Session Trail fold + orphan path (v7.1) |
| `test_wiki_generator.py` | Wiki views + Recent Activity (v7.1) |
| `test_review_ac_drift_meta.py` | review-ac-drift agent metadata (v7.1) |
