# Ultra Builder Pro 6.6.0

<div align="center">

**Production-Grade AI-Powered Development System for Claude Code**

---

[![Version](https://img.shields.io/badge/version-6.6.0-blue)](README.md#version-history)
[![Status](https://img.shields.io/badge/status-production--ready-green)](README.md)
[![Commands](https://img.shields.io/badge/commands-9-purple)](commands/)
[![Skills](https://img.shields.io/badge/skills-17-orange)](skills/)
[![Agents](https://img.shields.io/badge/agents-11-red)](agents/)
[![Hooks](https://img.shields.io/badge/hooks-15-yellow)](hooks/)
[![Tests](https://img.shields.io/badge/tests-84-brightgreen)](hooks/tests/)

</div>

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/rocky2431/ultra-builder-pro.git
cd ultra-builder-pro

# Copy to Claude Code config directory
cp -r ./* ~/.claude/

# Start Claude Code
claude
```

---

## Core Philosophy

### Priority Stack (CLAUDE.md)

| Priority | Rule |
|----------|------|
| 1 | **Role + Safety**: Deployable code, KISS/YAGNI, think in English, respond in Chinese |
| 2 | **Context Blocks**: Honor XML blocks exactly as written |
| 3 | **Evidence-First**: External facts require verification (Context7/Exa MCP) |
| 4 | **Honesty & Challenge**: Challenge user assumptions, name logical gaps |
| 5 | **Architecture**: Critical state must be persistable/recoverable/observable |
| 6 | **Code Quality**: No TODO/FIXME/placeholder, modular, avoid deep nesting |
| 7 | **Testing**: No mocking core logic, external deps allow test doubles |
| 8 | **Action Bias**: Default to progress, high-risk must brake and ask |

### Production Absolutism

> "There is no test code. There is no demo. There is no MVP.
> Every line is production code. Every test is production verification."

```
Code Quality = Real Implementation x Real Tests x Real Dependencies
If ANY component is fake/mocked/simulated -> Quality = 0
```

---

## Workflow

```
/ultra-init -> /ultra-research -> /ultra-plan -> /ultra-dev -> /ultra-test -> /ultra-deliver
     |              |                |              |             |             |
  Project       5-Round          Task         TDD Cycle      Quality       Release
  Setup      Discovery R0-4    Breakdown      RED>GREEN      Audit        & Deploy
               (optional)                        |
              Round 0: Product Discovery   /ultra-review
              Round 1: User & Scenario    (Quality Gate)
              Round 2: Feature Definition
              Round 3: Architecture
              Round 4: Quality & Deploy
```

---

## Commands (9)

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `/ultra-init` | Initialize project | Auto-detect type/stack, copy templates, git setup |
| `/ultra-research` | Interactive discovery | Forcing Questions + 5 rounds (Discovery>User>Feature>Architecture>Quality), 90%+ confidence |
| `/ultra-plan` | Task planning | Scope Mode (EXPAND/SELECTIVE/HOLD/REDUCE), dependency analysis, complexity assessment |
| `/ultra-dev` | TDD development | RED>GREEN>REFACTOR, Ultra Review gate, auto git flow |
| `/ultra-test` | Quality audit | Anti-Pattern, Coverage gaps, E2E, Performance, Security |
| `/ultra-deliver` | Release preparation | CHANGELOG, build, version bump, tag, push |
| `/ultra-status` | Progress monitoring | Real-time stats, risk analysis, recommendations |
| `/ultra-think` | Deep analysis | Structured reasoning, multi-dimension comparison |
| `/learn` | Pattern extraction | Extract reusable patterns from session, save to skills/learned/ |

---

## Skills (17 + Learned Patterns)

| Skill | Purpose | User-Invocable |
|-------|---------|----------------|
| `ultra-review` | Parallel code review with 6 agents + coordinator | Yes |
| `ultra-verify` | Three-way AI verification (Claude + Gemini + Codex) | Yes |
| `gemini-collab` | Gemini CLI as independent sub-agent for review, analysis, opinions | Yes |
| `codex-collab` | OpenAI Codex CLI as independent sub-agent for review, analysis | Yes |
| `recall` | Cross-session memory search, save summaries, tags | Yes |
| `agent-browser` | Browser automation CLI for AI agents | Yes |
| `find-skills` | Discover and install agent skills | Yes |
| `use-railway` | Railway infrastructure operations (deploy, provision, manage) | Yes |
| `vercel-react-best-practices` | React/Next.js performance optimization guidelines | Yes |
| `vercel-react-native-skills` | React Native/Expo best practices for mobile apps | Yes |
| `vercel-composition-patterns` | React composition patterns that scale | Yes |
| `web-design-guidelines` | Web Interface Guidelines compliance review | Yes |
| `ai-collab-base` | Shared collaboration protocol, modes, prompt templates | No (consumed by collab skills) |
| `code-review-expert` | Structured review checklists (SOLID, security, perf, integration) | No (agent-only) |
| `testing-rules` | TDD discipline, mock detection rules | No (agent-only) |
| `security-rules` | Input validation, injection prevention rules | No (agent-only) |
| `integration-rules` | Vertical slice, walking skeleton, contract-first, orphan detection | No (agent-only) |
| `learned/` | Extracted patterns from `/learn` | Yes |

---

## Agents (11)

All agents have **project-scoped persistent memory** (`memory: project`) that accumulates patterns per project, preventing cross-project pollution.

### Interactive Agents (5)

| Agent | Purpose | Trigger | Model | Memory |
|-------|---------|---------|-------|--------|
| `smart-contract-specialist` | Solidity, gas optimization, secure patterns | .sol files | opus | project |
| `smart-contract-auditor` | Contract security audit, vulnerability detection | .sol files | opus | project |
| `code-reviewer` | Code review with Fix-First mode (report or auto-fix) | After code changes, pre-commit | opus | project |
| `tdd-runner` | Test execution, failure analysis, coverage | "run tests", test suite | opus | project |
| `debugger` | Root cause analysis, minimal fix implementation | Errors, test failures | opus | project |

### Review Pipeline Agents (7) - Ultra Review System

Used exclusively by `/ultra-review`. Each agent writes JSON findings to `.ultra/reviews/<session>/` (project-level).

| Agent | Purpose | Output |
|-------|---------|--------|
| `review-code` | Scope drift detection + CLAUDE.md compliance, code quality, architecture, integration | `review-code.json` |
| `review-tests` | Test quality, mock violations, coverage gaps | `review-tests.json` |
| `review-errors` | Silent failures, empty catches, swallowed errors | `review-errors.json` |
| `review-design` | Type design, encapsulation, complexity analysis | `review-design.json` |
| `review-comments` | Stale, misleading, or low-value comments | `review-comments.json` |
| `review-coordinator` | Aggregate, deduplicate, generate SUMMARY | `SUMMARY.md` + `SUMMARY.json` |

**Verdict Logic**: P0 > 0 = REQUEST_CHANGES | P1 > 3 = REQUEST_CHANGES | P1 > 0 = COMMENT | else APPROVE

---

## Ultra Review System

### Overview

`/ultra-review` orchestrates parallel code review using 6 specialized agents + 1 coordinator. All findings are written to JSON files to prevent context window pollution.

### Usage Modes

```
/ultra-review              # Full review (smart skip based on diff content)
/ultra-review all          # Force ALL 6 agents, no auto-skip (pre-merge gate)
/ultra-review quick        # Quick review (review-code only)
/ultra-review security     # Security focus (review-code + review-errors)
/ultra-review tests        # Test quality focus (review-tests only)
/ultra-review recheck      # Re-check P0/P1 files from last session
/ultra-review delta        # Review only changes since last review
```

### Scope Options

```
/ultra-review --pr 123            # Review PR #123 diff
/ultra-review --range main..HEAD  # Review specific commit range
/ultra-review security --pr 42    # Security review scoped to PR #42
```

### Session Management

- Sessions tracked in `.ultra/reviews/index.json` (project-level) with branch-scoped iteration chains
- Naming: `<YYYYMMDD-HHmmss>-<branch>-iter<N>>`
- Auto-cleanup: 7 days for APPROVE/COMMENT, 30 days for REQUEST_CHANGES, max 5 per branch

### Integration with ultra-dev

Step 4.5 of `/ultra-dev` runs `/ultra-review all` (forced full coverage) as a mandatory quality gate before commit. The `pre_stop_check.py` hook blocks session stop if source files are changed but not reviewed (circuit breaker allows stop after 2 blocks).

---

## Ultra Verify — Three-Way AI Cross-Verification

### Overview

`/ultra-verify` orchestrates Claude + Gemini + Codex for independent three-way analysis. Each AI works independently, then Claude synthesizes with a confidence score based on consensus.

### Prerequisites

- Gemini CLI: `npm install -g @google/gemini-cli` + authenticated
- Codex CLI: `npm install -g @openai/codex` + `codex login`

### Usage

```
/ultra-verify decision <question>    # Architecture/design decision
/ultra-verify diagnose <symptoms>    # Bug diagnosis — three sets of hypotheses
/ultra-verify audit <scope>          # Code audit — findings ranked by consensus
/ultra-verify estimate <task>        # Effort estimation
```

### How It Works

1. **Claude answers first** (writes to file before reading external AI output — prevents contamination)
2. **Gemini + Codex run in parallel** (background tasks, 5 min timeout)
3. **Claude reads all three outputs** via Read tool
4. **Confidence scoring**: Consensus (3/3) > Majority (2/3) > No Consensus
5. **Synthesis** written to `.ultra/collab/<session-id>/synthesis.md`

### Degraded Operation

- **One AI fails**: Two-way comparison, confidence capped at Majority
- **Two AIs fail**: Claude-only with explicit warning
- Never blocks the workflow on external AI failures

### Architecture: Shared Base + Thin Skills

```
ai-collab-base/         # Canonical shared files (non-user-invocable)
  ├── references/        # collab-protocol.md, collaboration-modes.md, prompt-templates.md
  └── sync.sh            # Copies canonical files to consumer skills

gemini-collab/           # Thin skill: Gemini-specific CLI reference + shared files
codex-collab/            # Thin skill: Codex-specific CLI reference + shared files
ultra-verify/            # Orchestration: parallel execution + confidence scoring
```

---

## Cross-Session Memory

### Overview

AI-powered cross-session memory with hybrid search. Auto-captures session events, generates structured AI summaries via Haiku, and supports semantic + keyword retrieval. Designed as a safe alternative to claude-mem — no bulk context injection.

### Architecture

```
UserPromptSubmit ──> user_prompt_capture.py ──> initial_request (sessions table)
PostToolUse ──> observation_capture.py ──> observations table (max 20/session)

Stop hook (auto)                    /recall skill (forked context)
     |                                     |
     v                                     v
session_journal.py ──> SQLite FTS5 <── memory_db.py CLI
     |                  (memory.db)        |
     |                  Schema v2:         v
     |                  - sessions (+ content_session_id, initial_request)
     |                  - session_summaries (structured JSON)
     |                  - observations (file changes, test failures)
     |                  - summaries_fts (FTS5 over summaries)
     |
     |-- daemon (10s) ──> Haiku ──> structured JSON summary ──> SQLite + Chroma
     |                    {request, completed, learned, next_steps}
     v
sessions.jsonl (backup)      .ultra/memory/chroma/ (vector embeddings)

PreCompact ──> compact-snapshot.md ──> SessionStart(compact) ──> post_compact_inject.py
   (save)       (disk persistence)        (auto-trigger)         (~800 tokens recovery)
```

### How It Works

1. **Initial request capture** (UserPromptSubmit hook): Captures first user prompt per session
2. **Observation capture** (PostToolUse hook): Records file changes (Edit/Write) and test failures (Bash) — max 20 per session, deduped by content hash
3. **Auto-capture** (Stop hook): Every response records branch, cwd, modified files
4. **AI Summary** (async daemon): Double-fork daemon waits 10s after session stop, extracts transcript (head+tail sampling: 4K+11K chars), generates structured JSON summary via Haiku (three-tier fallback: claude CLI → Anthropic SDK → git commits)
5. **Vector Embedding**: After AI summary, auto-upserts to Chroma (local ONNX, no API key)
6. **Merge window**: Multiple stops within 30 minutes merge into one session record
7. **Real session identity**: `content_session_id` from hook protocol for accurate session tracking
8. **SessionStart injection**: Injects ONE line (~50 tokens) about the last session + up to 3 branch-relevant structured summaries — no context explosion
9. **Post-compact recovery**: `SessionStart(compact)` triggers `post_compact_inject.py` — injects ~800 tokens of git state, active tasks, workflow progress, and session memory for continuity after auto-compact
10. **Hybrid search**: `/recall` runs in forked context, combines FTS5 keyword + Chroma semantic via RRF

### Usage

```
/recall                          # Recent 5 sessions
/recall auth bug                 # Hybrid search (FTS5 + semantic RRF)
/recall --semantic "login flow"  # Pure semantic vector search
/recall --keyword session_journal # Pure FTS5 keyword search
/recall --recent 10              # Recent 10 sessions
/recall --date 2026-02-16        # Sessions on specific date
/recall --save "Fixed auth bug"  # Save summary for latest session
/recall --tags "auth,bugfix"     # Add tags to latest session
/recall --stats                  # Database statistics
/recall --cleanup 90             # Delete sessions older than 90 days
```

### Storage

- **Database**: `.ultra/memory/memory.db` (project-level, SQLite FTS5)
- **Vectors**: `.ultra/memory/chroma/` (project-level, Chroma + ONNX embeddings)
- **Backup**: `.ultra/memory/sessions.jsonl` (append-only JSONL)
- **Retention**: 90 days default
- **Dependencies**: chromadb (ONNX embeddings), anthropic SDK (optional, for AI summary fallback)

---

## TDD Workflow

Mandatory for all new code:

```
1. RED    -> Write failing test first (define expected behavior)
2. GREEN  -> Write minimal code to pass test
3. REFACTOR -> Improve code (keep tests passing)
4. COVERAGE -> Verify 80%+ coverage
5. COMMIT -> Atomic commit (test + implementation together)
```

### What NOT to Mock (Core Logic)

- Domain/service/state machine logic
- Funds/permission related paths
- Repository interface contracts

### What CAN be Mocked (External)

- Third-party APIs (OpenAI, Supabase, etc.)
- External services
- Must explain rationale for each mock

---

## Hooks System (15 Hooks)

Automated enforcement via Python hooks in `hooks/`. **Hooks are deterministic — unlike CLAUDE.md rules which are advisory, hooks guarantee the action happens.**

**Protocol compliance**: 100% — all hooks follow official Claude Code hook protocol (stdin JSON, stdout JSON, exit codes 0/2).

### PreToolUse Hooks (Guard before execution)

| Hook | Trigger | Detection | Timeout |
|------|---------|-----------|---------|
| `block_dangerous_commands.py` | Bash | rm -rf, fork bombs, chmod 777, force push main | 5s |
| `mid_workflow_recall.py` | Write/Edit | Inject past test failures + edit history + learned lessons from memory.db for the file being edited (rate-limited) | 3s |

### PostToolUse Hooks (Quality gate after execution)

| Hook | Trigger | Detection | Timeout |
|------|---------|-----------|---------|
| `post_edit_guard.py` | Edit/Write | Code quality (TODO/FIXME), mocks, security, TDD pairing, **blast radius** (show dependents), **silent catch detection** (block except:pass), **test reminder** | 5s |
| `observation_capture.py` | Edit/Write/Bash | Capture file changes, test failures, and significant commands (git/build/deploy) as session observations | 3s |

### User Input Hooks

| Hook | Trigger | Function | Timeout |
|------|---------|----------|---------|
| `user_prompt_capture.py` | UserPromptSubmit | Capture initial user request per session for structured summaries | 3s |

### Session & Lifecycle Hooks

| Hook | Trigger | Function | Timeout |
|------|---------|----------|---------|
| `health_check.py` | SessionStart | **System Health**: verify agents exist, hooks syntax, DB health, settings refs, CLAUDE.md | 5s |
| `session_context.py` | SessionStart | Load git branch, commits, modified files + last session one-liner + branch memory from DB | 10s |
| `session_journal.py` | Stop | Auto-capture session + spawn AI summary daemon (Haiku, non-blocking) → SQLite + Chroma | 5s |
| `pre_stop_check.py` | Stop | Source file change detection + workflow state check + **completion compliance checklist** (Taskmaster-inspired excuse detection) | 5s |
| `subagent_tracker.py` | SubagentStart/Stop | Log agent lifecycle to `.ultra/debug/subagent-log.jsonl` (project-level) | 5s |
| `pre_compact_context.py` | PreCompact | Preserve task state and git context to `.ultra/compact-snapshot.md` + branch memory | 10s |
| `post_compact_inject.py` | SessionStart(compact) | Post-compact context recovery: parse snapshot, inject git state/tasks/workflow/memory | 10s |

### Notification & Cleanup Hooks

| Hook | Trigger | Function | Timeout |
|------|---------|----------|---------|
| macOS notification | Notification(permission_prompt\|idle_prompt) | Desktop alert with sound when Claude needs user input | 5s |
| Counter cleanup | SessionEnd | Remove stale stop-count temp files (>60min old) | 5s |

### Shared Utilities & Tools

| File | Purpose |
|------|---------|
| `hook_utils.py` | Shared functions: `get_snapshot_path()`, `get_workflow_state()`, `parse_hook_input()` |
| `memory_db.py` | SQLite FTS5 + Chroma vector engine + CLI tool — foundation for all memory hooks |
| `system_doctor.py` | Deep audit: cross-references, DB quality, Chroma consistency, silent catch scan. Run: `python3 hooks/system_doctor.py` |
| `tests/` | **84 pytest tests** covering block_dangerous, observation_capture, memory_db, pre_stop_check, mid_workflow_recall |

### Change Discipline (Hook-Enforced)

| Discipline | Enforcement | How |
|------------|-------------|-----|
| **Blast Radius** | `post_edit_guard.py` stderr | When editing shared module, shows all files that import it |
| **Fail Loud** | `post_edit_guard.py` block | Detects `except:pass` patterns, blocks commit |
| **Verify After Change** | `post_edit_guard.py` stderr | Shows corresponding test file path when it exists |
| **System Health** | `health_check.py` SessionStart | Catches missing agents, broken hooks, DB issues at session start |

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
| Function lines | <= 50 |
| File lines | 200-400 typical, 800 max |
| Nesting depth | <= 4 |
| Cyclomatic complexity | <= 10 |

---

## Project Structure

```
~/.claude/
|-- CLAUDE.md                 # Main configuration (Priority Stack)
|-- README.md                 # This file
|-- settings.json             # Claude Code settings + hooks config
|
|-- hooks/                    # Automated enforcement (13 hooks, all with timeout)
|   |-- block_dangerous_commands.py  # PreToolUse: dangerous bash commands (5s)
|   |-- post_edit_guard.py           # PostToolUse: quality + mock + security unified (5s)
|   |-- observation_capture.py       # PostToolUse: session observations (Edit/Write/Bash) (5s)
|   |-- user_prompt_capture.py       # UserPromptSubmit: initial request capture (5s)
|   |-- session_context.py           # SessionStart: load dev context + last session (10s)
|   |-- session_journal.py           # Stop: auto-capture + AI summary daemon → SQLite + Chroma (5s)
|   |-- pre_stop_check.py            # Stop: source change detection → suggest code-reviewer (5s)
|   |-- subagent_tracker.py          # SubagentStart/Stop: lifecycle logging (5s)
|   |-- pre_compact_context.py       # PreCompact: preserve context + freshness marker (10s)
|   |-- post_compact_inject.py       # SessionStart(compact): post-compact context recovery (10s)
|   |-- hook_utils.py                # Shared: snapshot path, workflow state, input parsing
|   |-- memory_db.py                 # Shared: SQLite FTS5 + Chroma vector engine + CLI tool
|
|-- commands/                 # /ultra-* commands (9)
|   |-- ultra-init.md
|   |-- ultra-research.md
|   |-- ultra-plan.md
|   |-- ultra-dev.md
|   |-- ultra-test.md
|   |-- ultra-deliver.md
|   |-- ultra-status.md
|   |-- ultra-think.md
|   |-- learn.md
|
|-- skills/                   # Domain skills (18 + learned)
|   |-- ultra-review/         # Parallel review orchestration
|   |   |-- scripts/          # review_wait.py, review_verdict_update.py
|   |-- ultra-verify/         # Three-way AI verification (Claude+Gemini+Codex)
|   |   |-- references/       # cross-verify-modes, confidence-system, orchestration-flow
|   |   |-- evals/            # skill-creator eval tests
|   |-- ai-collab-base/       # Shared collab protocol (non-user-invocable)
|   |   |-- references/       # collab-protocol, collaboration-modes, prompt-templates
|   |   |-- sync.sh           # Sync canonical files to consumer skills
|   |-- gemini-collab/        # Gemini CLI as independent sub-agent
|   |   |-- references/       # gemini-cli-reference, gemini-prompts, shared files
|   |   |-- evals/            # skill-creator eval tests
|   |-- codex-collab/         # OpenAI Codex CLI as independent sub-agent
|   |   |-- references/       # codex-cli-reference, codex-prompts, shared files
|   |   |-- evals/            # skill-creator eval tests
|   |-- recall/               # Cross-session memory search
|   |-- code-review-expert/   # Structured review checklists (agent-only)
|   |-- integration-rules/    # System integration rules (agent-only)
|   |-- testing-rules/        # TDD rules (agent-only)
|   |-- security-rules/       # Security rules (agent-only)
|   |-- agent-browser/        # Browser automation CLI
|   |-- find-skills/          # Skill discovery and installation
|   |-- use-railway/          # Railway infrastructure operations
|   |-- vercel-react-best-practices/   # React/Next.js optimization
|   |-- vercel-react-native-skills/    # React Native/Expo best practices
|   |-- vercel-composition-patterns/   # React composition patterns
|   |-- web-design-guidelines/         # Web Interface Guidelines
|   |-- learned/              # Extracted patterns
|
|-- agents/                   # Custom agents (12)
|   |-- smart-contract-specialist.md  # Interactive
|   |-- smart-contract-auditor.md     # Interactive
|   |-- code-reviewer.md             # Interactive
|   |-- tdd-runner.md                # Interactive
|   |-- debugger.md                  # Interactive
|   |-- review-code.md               # Pipeline (ultra-review)
|   |-- review-tests.md              # Pipeline (ultra-review)
|   |-- review-errors.md             # Pipeline (ultra-review)
|   |-- review-design.md             # Pipeline (ultra-review, merged types+simplify)
|   |-- review-comments.md           # Pipeline (ultra-review)
|   |-- review-coordinator.md        # Pipeline (ultra-review)
|
|-- .ultra/                   # Project-level output (in each project, gitignored)
|   |-- memory/                      # Cross-session memory (auto-managed)
|   |   |-- memory.db                # SQLite FTS5 session database
|   |   |-- chroma/                  # Chroma vector embeddings (ONNX)
|   |   |-- sessions.jsonl           # Append-only backup
|   |-- reviews/                     # Ultra Review output (auto-managed)
|   |   |-- index.json               # Session index (branch-scoped)
|   |   |-- <session-id>/           # Per-session findings
|   |       |-- review-*.json
|   |       |-- SUMMARY.json
|   |       |-- SUMMARY.md
|   |-- collab/                      # AI collaboration sessions (auto-managed)
|   |   |-- <session-id>/           # Per-session output
|   |       |-- claude-analysis.md
|   |       |-- gemini-output.md
|   |       |-- codex-output.md
|   |       |-- synthesis.md
|   |       |-- metadata.json
|   |       |-- error.log
|   |-- compact-snapshot.md          # Context recovery after compaction
|   |-- debug/                       # Agent lifecycle logs
|       |-- subagent-log.jsonl
|
|-- .ultra-template/          # Project initialization templates
    |-- specs/                # discovery.md, product.md, architecture.md
    |-- tasks/
    |-- docs/
```

---

## Operational Config

> These are operational settings, not principles. CLAUDE.md contains the principles.

### Git Workflow

- Follow project branch naming conventions
- Conventional Commits format
- Include Co-author for AI commits:
  ```
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

### Project Structure

```
New Ultra projects use:
.ultra/
|-- tasks/              # Task tracking
|-- specs/              # Specifications (discovery.md, product.md, architecture.md)
|-- docs/               # Project documentation
|-- memory/             # Cross-session memory DB + Chroma + JSONL (auto-generated)
|-- reviews/            # Ultra Review output (auto-generated)
|-- compact-snapshot.md # Context recovery (auto-generated)
|-- debug/              # Agent lifecycle logs (auto-generated)
```

### Learned Patterns

Patterns extracted via `/learn` are stored in `skills/learned/`:

| Confidence | File Suffix | Description |
|------------|-------------|-------------|
| Speculation | `_unverified` | Freshly extracted, needs verification |
| Inference | No suffix | Human review passed |
| Fact | No suffix + marked | Multiple successful uses |

Priority: Fact > Inference > Speculation

### Workflow Tools

Multi-step tasks use the Task system:
- `TaskCreate`: Create new task
- `TaskList`: View all tasks
- `TaskGet`: Get task details
- `TaskUpdate`: Update task status

---

## Version History

### v6.5.0 (2026-03-20) - Product Velocity Fusion

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

**Enhanced Files** (8): `CLAUDE.md`, `agents/review-code.md`, `agents/code-reviewer.md`, `commands/ultra-research.md`, `commands/ultra-plan.md`, `hooks/pre_stop_check.py`, `skills/ultra-review/references/unified-schema.md`, `README.md`

### v6.3.0 (2026-03-09) - Memory System v2

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

**Enhanced Files** (8):
- `hooks/session_journal.py`, `hooks/memory_db.py`, `hooks/session_context.py`, `hooks/pre_compact_context.py`
- `hooks/user_prompt_capture.py` (New), `hooks/observation_capture.py` (New)
- `CLAUDE.md`, `README.md`

### v6.2.0 (2026-03-08) - Multi-AI Collaboration Refactor

**Shared base architecture + three-way AI verification**, verified by 3 rounds of ultra-verify audit (Claude + Gemini + Codex):

- New `ai-collab-base` skill: shared collaboration protocol, modes, prompt templates (non-user-invocable)
  - `sync.sh` keeps canonical files in sync across 3 consumer skills
  - Eliminates ~90% structural duplication between gemini-collab and codex-collab
- New `ultra-verify` skill: three-way AI cross-verification (Claude + Gemini + Codex)
  - 4 modes: `decision`, `diagnose`, `audit`, `estimate`
  - Confidence scoring: Consensus (3/3), Majority (2/3), No Consensus
  - Degraded operation: one AI fails → two-way, two fail → Claude-only with warning
- Rewritten `gemini-collab`: thin skill pointing to shared base + Gemini-specific CLI reference
- Rewritten `codex-collab`: thin skill pointing to shared base + Codex-specific CLI reference
- CLI bug fixes verified against actual `--help` output:
  - `--commit-title` → `--title` (codex review)
  - `--full-auto` + `--sandbox read-only` conflict resolved
  - `$(cat $FILE)` shell injection → stdin pipe pattern
  - `2>/dev/null` → `error.log` (all files, not just orchestration)
  - `-o`/`--output-format` correctly documented for Gemini CLI
  - Hardcoded model names removed (use `-m <model>`)
- skill-creator compatible `evals/evals.json` for all 3 user-invocable skills
- Files: `skills/ai-collab-base/`, `skills/ultra-verify/`, `skills/gemini-collab/`, `skills/codex-collab/`

### v6.1.0 (2026-03-08) - Product Discovery Round 0

**Product Discovery & Strategy phase** — fills the gap between vague ideas and technical specification. Inspired by [phuryn/pm-skills](https://github.com/phuryn/pm-skills) frameworks:

- New Round 0 in `/ultra-research` with 5 sub-steps:
  - **Opportunity Discovery**: OST framework (Teresa Torres), Opportunity Score prioritization (Dan Olsen)
  - **Market Assessment**: TAM/SAM/SOM dual estimation (top-down + bottom-up), WebSearch for real data
  - **Competitive Landscape**: Comparison matrix + Porter's Five Forces brief
  - **Product Strategy**: Condensed Strategy Canvas (Vision/Segments/Value Prop/Trade-offs/Defensibility)
  - **Assumptions & Validation Plan**: Risk categorization (Value/Usability/Feasibility/Viability/GTM) + experiment design (Pretotyping, Alberto Savoia)
- New `discovery.md` spec template in `.ultra-template/specs/`
- Updated `/ultra-init` and `/ultra-plan` to reference `discovery.md`
- Round 0 is **optional** — auto-skipped for Feature Only mode or when market research already exists
- New project type options: "Full Project" (R0-4), "Product Only" (R0-2)

### v6.0.0 (2026-03-07) - Consolidation Release

**System consolidation, cleanup, and Multi-AI collaboration**:

- New `gemini-collab` skill: Gemini CLI as sub-agent for review, project analysis, second opinions
- New `codex-collab` skill: OpenAI Codex CLI as sub-agent with built-in `codex review` integration
- Removed codex skill and all references (CLAUDE.md, README.md, skills/codex/)
- Stop hook hardening: removed main branch bypass, fixed git status path truncation
- Comprehensive hook audit: 20 fixes, model unification, 2 new hooks (Notification, SessionEnd)
- Ultra-think rewrite: adversarial reasoning framework
- All 12 agents unified to opus model
- Session summary model upgraded to opus
- Post-compact context injection via SessionStart(compact) hook
- Permission cleanup: removed obsolete tools, added missing tools

### v5.9.2 (2026-03-05) - Hook Audit & Model Unification

**Comprehensive hook audit against official docs + community best practices + model unification**:

**Model Unification**:
- All 12 agents unified to `opus` model (fixed `code-reviewer`/`debugger` inherit, `tdd-runner` haiku)
- AI summary daemon upgraded from Sonnet to Opus (session_journal.py)

**Hook Audit (20 fixes across 3 tiers)**:
- **Protocol compliance**: 100% — all hooks follow official Claude Code hook protocol
- **Security**: fail-closed patterns, DAEMON_ENV_WHITELIST, env sanitization
- **Performance**: all GIT_TIMEOUT values < hook timeout (session_context.py 10→3s safety fix)
- **Shared utilities**: `hook_utils.py` eliminates ~130 lines of duplication across hooks

**New Hooks (2)**:
- `Notification`: macOS desktop alert with sound when Claude needs user input (permission_prompt/idle_prompt)
- `SessionEnd`: Automatic cleanup of stale stop-count temp files (>60min old)

**Protocol Fixes**:
- `pre_stop_check.py`: Added `stop_hook_active` fast path (Layer 0a) per official docs — prevents infinite Stop hook loops
- `session_journal.py`: Fixed stale docstring (Sonnet → Opus), added `stop_hook_active` re-trigger guard

**Enhanced Files** (10):
- All 10 hook `.py` files audited and updated
- `settings.json`: +Notification hook, +SessionEnd hook
- `README.md`: Updated hook count, model references, hooks system section

### v5.9.1 (2026-03-04) - Hook Hardening + Post-Compact Recovery

**Stop Hook Hardening + Post-Compact Context Recovery + Permission Cleanup**:

**Post-Compact Context Recovery (New)**:
- `post_compact_inject.py`: New `SessionStart(compact)` hook — injects ~800 tokens of recovery context after auto-compact
- Parses `compact-snapshot.md` to extract git state, active tasks, workflow progress, session memory
- Freshness check: marker file (written by PreCompact) → mtime fallback → stale hint
- `pre_compact_context.py`: Added marker file write (`/tmp/.claude_compact_ts`) for post-compact freshness detection

**Stop Hook Hardening**:
- `pre_stop_check.py`: Three-layer → four-layer check, added `last_assistant_message` parsing for incomplete work detection (TODO/FIXME/WIP patterns)
- Added `stop_hook_active` loop guard (prevents Stop hook re-trigger from its own block message)
- Added security-sensitive file detection (auth/payment/token/credential/session path matching)
- Restored code-reviewer suggestion in block messages (lost in prior refactor)
- `session_journal.py`: Added `stop_hook_active` check, skips AI summary daemon spawn on re-trigger

**Permission Cleanup**:
- Removed `AskUserQuestion` from allow list (fixed UI not displaying — allow caused auto-skip)
- Added 8 missing tools: Agent, TaskOutput, TaskStop, TeamCreate, TeamDelete, SendMessage, EnterWorktree
- Removed 4 obsolete entries: Task, SlashCommand, BashOutput, KillShell

**Enhanced Files** (5):
- `hooks/post_compact_inject.py` (New), `hooks/pre_compact_context.py`, `hooks/pre_stop_check.py`, `hooks/session_journal.py`, `settings.json`

### v5.9.0 (2026-03-02) - Process Discipline Fusion

**Superpowers Process Discipline Fusion** — absorbed key process principles from the Superpowers project, closing 3 process gaps:

**Design Approval Gate (P0)**:
- `ultra-dev.md`: Added Step 0.5 — displays task breakdown overview on first run, requires user confirmation before implementation
- Prevents "Wrong Approach" (#1 remaining friction): user must review plan before writing code
- Auto-skipped on resume (already approved)

**Spec Compliance Check (P1)**:
- `ultra-dev.md`: Added Quality Gate #7 — verifies each acceptance criterion is implemented and tested
- `review-code.md`: Added Step 7 — infers task ID from branch name, reads task context, validates spec compliance
- Added `spec-compliance` category (P0: missing, P1: partially implemented, P2: edge cases uncovered)

**3-Fix Circuit Breaker (P1)**:
- `ultra-review SKILL.md`: Added per-file fix counter in Fix Flow
- Same file fails 3 consecutive fixes → circuit break, request user decision (skip/manual/abort)
- 3+ files circuit-broken globally → suggest architecture discussion, tag `ARCHITECTURAL_CONCERN`

**Systematic Debugging Methodology (P2)**:
- `debugger.md`: 5-step simple flow → 4-phase structured methodology
- Phase 1 (Root Cause Investigation) enforced, IRON LAW: no fix proposals before investigation complete
- 3-Fix Rule: 3 consecutive fix failures → stop, report architectural issue
- Red Flags table: detect common shortcut thinking and force return to Phase 1

**Enhanced Files** (4 core + 2 meta):
- `commands/ultra-dev.md`, `agents/review-code.md`, `skills/ultra-review/SKILL.md`, `agents/debugger.md`
- `CLAUDE.md`, `README.md`, `settings.json`

### v5.8.1 (2026-02-28) - System-Level Optimization

**Context Protection + Pipeline Reliability + Workflow Resilience** — targeting 65% → 80%+ completion rate based on 285-session usage analysis:

**Context Window Protection**:
- `ultra-dev.md`: Review iteration cap (MAX_REVIEW_ITERATIONS = 2), unresolved findings → UNRESOLVED.md
- `ultra-review SKILL.md`: CRITICAL PROHIBITION — never call TaskOutput for review agents; findings cap 15/agent
- `post_edit_guard.py`: Hook output compression (~70%), WARN/HIGH patterns deferred to review-code agent
- Agent maxTurns reduction: review-errors/types/simplify 20→15, review-comments 20→12

**Pipeline Reliability**:
- `ultra-dev.md`: Pre-review `/compact` checkpoint (Step 4.4); workflow state checkpoint at steps 3.3/4/4.5/6
- `review_wait.py`: Structured JSON output with partial success (≥1 agent = success)
- `ultra-review SKILL.md`: Incremental per-file fix-test flow; Step 0 context reset before fix phase

**Workflow Resilience**:
- `ultra-dev.md`: Step 0 resume check reads `.ultra/workflow-state.json`, skips completed steps
- `pre_compact_context.py`: Active Workflow section + RESUME line in compact hint

**CLAUDE.md Optimization**: ~365 → ~280 lines (~25% reduction, zero information loss)

**Enhanced Files** (9):
- `commands/ultra-dev.md`, `skills/ultra-review/SKILL.md`, `hooks/post_edit_guard.py`
- `skills/ultra-review/scripts/review_wait.py`, `hooks/pre_compact_context.py`
- `agents/review-errors.md`, `agents/review-design.md`, `agents/review-comments.md`

### v5.8.0 (2026-02-20) - AI Summarization + Vector Search

**AI-Powered Memory Upgrade** — transcript-based summaries, semantic vector search, hybrid retrieval, and forked recall context:

**Enhanced Files**:
- `hooks/session_journal.py`: +AI summarization via double-fork daemon (non-blocking, 10s delay)
  - Transcript parsing: extracts user/assistant text from JSONL, dedupes streaming chunks
  - Three-tier fallback: `claude -p --model opus` → Anthropic SDK → git commit messages
  - Daemon clears `CLAUDE*` env vars to avoid inheriting parent session config
  - Auto-upserts Chroma embedding after AI summary generation
  - CLI: `--ai-summarize <session_id> <transcript_path>` for manual re-summarize
- `hooks/memory_db.py`: +Chroma vector search engine (PersistentClient + local ONNX ONNXMiniLM_L6_V2)
  - `upsert_embedding()`: doc = summary + branch + top 5 files (~256 tokens)
  - `semantic_search()`: pure vector search via Chroma
  - `hybrid_search()`: RRF (k=60) fusion of FTS5 keyword + Chroma semantic
  - `reindex_chroma()`: backfill existing sessions into Chroma
  - CLI commands: `semantic`, `hybrid`, `reindex-chroma`
- `skills/recall/SKILL.md`: +`context: fork` (search results don't pollute main conversation)
  - Default search: hybrid (FTS5 + semantic RRF)
  - New modes: `--semantic` (pure vector), `--keyword` (pure FTS5)
  - Progressive retrieval strategy: search → expand query → synthesize

**Dependencies**: chromadb 1.5.0 (local ONNX embeddings, no API key required)

**Design Principle**: Same as v5.7.0 — auto-capture, on-demand retrieval, no bulk injection. AI summarization runs async after session stop, never blocking the hot path.

### v5.7.0 (2026-02-16) - Cross-Session Memory

**Cross-Session Memory System** — lightweight auto-capture + on-demand retrieval, designed as safe alternative to claude-mem:

**New Files**:
- `hooks/memory_db.py`: SQLite FTS5 storage engine + CLI tool (dual-use library)
- `hooks/session_journal.py`: Stop hook auto-captures branch/files/commits per session
- `skills/recall/SKILL.md`: `/recall` skill for on-demand memory search, summaries, tags

**Enhanced Files**:
- `hooks/session_context.py`: +last session one-liner injection at SessionStart (~50 tokens)
- `CLAUDE.md`: +`<session_memory>` block with proactive recall trigger rules
- `settings.json`: +session_journal.py in Stop hooks

**Design Principles**:
- Auto-capture at Stop, on-demand retrieval via `/recall` — no bulk SessionStart injection
- Zero external dependencies (Python stdlib + SQLite FTS5)
- 30-minute merge window: multiple stops within same session merge into one record
- Auto-summary from git commit messages (no AI needed), manual override via `/recall --save`
- 90-day retention policy with `/recall --cleanup`

**Learned from claude-mem failure**: claude-mem injected ~25k tokens at SessionStart causing context explosion. Our approach: inject 1 line (~50 tokens), search on-demand.

**Ultra Review Improvements**:
- Background execution: all review agents run with `run_in_background: true` (~535 tokens vs ~7000+)
- File-based waiting: `review_wait.py` polls for completion instead of TaskOutput reads
- Verdict update: `review_verdict_update.py` auto-updates SUMMARY.json + index.json after P0 fixes
- Pre-stop fix: skip code-change fallback on main/master (merged code already reviewed), remove instructional language from block messages to prevent AI re-trigger
- Scripts moved from `hooks/` to `skills/ultra-review/scripts/` (proper ownership)

### v5.6.1 (2026-02-14) - Project Isolation

**Project-Level Artifact Isolation** — all per-project output moved from global `~/.claude/` to project-level `.ultra/`:

| Artifact | Old (global) | New (project-level) |
|----------|-------------|---------------------|
| Review output | `~/.claude/reviews/` | `.ultra/reviews/` |
| Review index | `~/.claude/reviews/index.json` | `.ultra/reviews/index.json` |
| Compact snapshot | `~/.claude/compact-snapshot.md` | `.ultra/compact-snapshot.md` |
| Subagent logs | `~/.claude/debug/subagent-log.jsonl` | `.ultra/debug/subagent-log.jsonl` |
| Agent memory | `~/.claude/agent-memory/` (global) | `projects/<hash>/agent-memory/` (project) |

**Why**: Global storage caused cross-project pollution — pre_stop_check false positives from other projects' reviews, compact-snapshot restoring wrong project context, agent memory carrying irrelevant architecture knowledge.

**Changes**:
- 3 hooks updated with `git rev-parse --show-toplevel` detection + safe fallback for non-git environments
- All 12 agents switched from `memory: user` to `memory: project`
- `.gitignore` updated to exclude `.ultra/reviews/`, `.ultra/compact-snapshot.md`, `.ultra/debug/`

**Audit Fixes**:
- `pre_compact_context.py`: Added `mkdir -p` before writing snapshot (prevents silent failure when `.ultra/` doesn't exist)
- `settings.json`: Co-Authored-By removed hardcoded model version (aligned with CLAUDE.md)
- `settings.json`: Version comments updated to 5.6.1, removed redundant `mcp__pencil` permission

### v5.6.0 (2026-02-14) - System Integration Dimension

**System Integration Dimension** — macro-level integration guarantees complementing existing micro-level component quality:

**New CLAUDE.md Rules**:
- `<integration>` block: Vertical Slice, Walking Skeleton, Contract-First, Integration Proof, Orphan Detection
- `<testing>`: Cross-boundary contract/E2E test layer
- `<forbidden_patterns>`: Horizontal-only tasks, unwired components, missing contract tests
- `<red_flags>`: "I'll wire it up later", "It works in isolation", etc.
- `<verification>`: "Feature complete" requires E2E test, "Component works" requires entry point trace

**New Skill: `integration-rules`** (agent-only):
- Vertical slice principle with good/bad examples
- Walking skeleton requirements
- Contract-first development workflow
- Integration test requirements per boundary type
- Orphan detection checklist
- Injected into `review-code` and `code-reviewer` agents

**New Reference: `integration-checklist.md`**:
- Entry point tracing, contract validation, vertical slice assessment
- Integration test coverage matrix, data flow continuity checks
- Added to `code-review-expert` as Step 5.5

**Enhanced Agents**:
- `review-code`: +integration-rules skill, +step 6 integration review, +4 severity rows (orphan P1, missing integration test P1, horizontal-only P2, missing contract P2)
- `code-reviewer`: +integration-rules skill, +integration checks in Additional Checks
- `review-tests`: +boundary-crossing detection, +2 severity rows

**Enhanced Workflows**:
- `ultra-plan`: Walking skeleton as Task #1 (P0), contract definition tasks, integration checkpoints every 3-4 tasks, vertical slice validation
- `ultra-dev`: Integration test dimension in RED phase, integration quality gates, pre-commit orphan/integration checklist

**Schema**: `integration` category added to unified-schema-v1 Category Enum

**Zero additional cost**: Integration checks folded into existing review-code agent via skill injection — no new review agent needed.

### v5.5.1 (2026-02-14) - Codex v6.0 + Review Enhancements

- Codex v6.0 integration
- `/ultra-review all` mode (force all 6 agents, no auto-skip)
- `pre_stop_check.py` marker-based escape hatch (block once, allow on second attempt)

### v5.5.0 (2026-02-14) - Ultra Review System

**Ultra Review System** — native parallel code review pipeline:

**New Review Pipeline (7 agents)**:
- `review-code`: CLAUDE.md compliance, code quality, architecture
- `review-tests`: Test quality, mock violations, coverage gaps
- `review-errors`: Silent failures, empty catches, swallowed errors
- `review-design`: Type design, encapsulation, complexity analysis (merged types+simplify)
- `review-comments`: Stale, misleading, or low-value comments
- `review-coordinator`: Aggregate findings, deduplicate, generate SUMMARY

**New Skill: `/ultra-review`**:
- Modes: full, all, quick, security, tests, recheck, delta, custom
- Scope options: `--pr NUMBER`, `--range RANGE`
- Session tracking with branch-scoped index.json and iteration chains
- Lifecycle management: auto-cleanup by age (7d/30d) and per-branch cap (5)
- Verdict logic: P0 > 0 or P1 > 3 = REQUEST_CHANGES, P1 > 0 = COMMENT, else APPROVE
- Fix flow: auto-fix P0/P1, re-test, recheck cycle

**New Skill: `code-review-expert`** (agent-only):
- Structured review checklists: SOLID, security, performance, boundary conditions
- Injected into code-reviewer agent via frontmatter

**Enhanced: `pre_stop_check.py`**:
- Three-layer check: review artifacts (index.json branch-scoped) + incomplete session grace period + code change marker fallback
- Recency guard: only considers sessions < 2 hours old
- Incomplete session < 15min: warn only (agents may still be running)
- Incomplete session >= 15min: marker-based block (block once, allow on second attempt)
- P0/P1 block: marker-based escape hatch (block once, allow on second attempt)
- REQUEST_CHANGES without P0: also blocks with marker escape

**Enhanced: `/ultra-dev` Step 4.5**:
- `/ultra-review all` invocation (forced full coverage)
- 3-phase flow: Run review > Act on verdict > Verification gate

**CLAUDE.md Updates**:
- `agent_system`: Listed all 12 agents (5 interactive + 7 pipeline)
- Added ultra-review and code-review-expert to skills
- Added review pipeline to auto-trigger table

### v5.4.1 (2026-02-08) - Hooks Hardening

**Hooks Refactoring**:
- Merged 3 PostToolUse hooks (`code_quality.py`, `mock_detector.py`, `security_scan.py`) into unified `post_edit_guard.py`
- Removed `branch_protection.py`, simplified `pre_stop_check.py`
- 9 hooks -> 6 hooks (less overhead per tool call)

**Reliability Fix**:
- Added `timeout` to all hooks (5s default, 10s for SessionStart/PreCompact)
- Prevents UI freeze when hook scripts stall
- Fixed non-dict JSON input handling in `subagent_tracker.py`

### v5.4.0 (2026-02-07) - Agent & Memory Edition

**New Agents (3)**:
- `code-reviewer`: Code review specialist with security-rules skill injection
- `tdd-runner`: Test execution specialist (Haiku model, project memory) with testing-rules injection
- `debugger`: Root cause analysis specialist with Edit capability

**Agent Memory**: All agents now have persistent memory (`memory: project` since v5.6.1)
- Accumulates patterns, common issues, and architectural decisions per project
- Each agent loads its MEMORY.md at startup

**New Skills (2, agent-only)**:
- `testing-rules`: TDD discipline, forbidden mock patterns, coverage requirements
- `security-rules`: Input validation, injection prevention, security review checklist

**New Hooks (3)**:
- `subagent_tracker.py`: SubagentStart/Stop lifecycle logging to JSONL
- `pre_compact_context.py`: PreCompact context preservation (tasks + git state)

**Agent Teams**: Enabled experimental `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`

**CLAUDE.md Updates**:
- `agent_system`: Added task-type auto-triggers, updated agent/skill/hook counts
- `work_style`: Added Parallel Delegation, Pre-delegation, Context Isolation protocols

### v5.3.0 (2026-02-01) - Lean Architecture Edition

**Philosophy**: Apply Anthropic's "Start simple, add complexity only when simpler solutions fall short."

**Removed (redundant - Claude handles natively)**:
- Agents: build-error-resolver, doc-updater, e2e-runner, frontend-developer, refactor-cleaner
- Skills: gemini, promptup, skill-creator
- Hooks: user_prompt_agent.py (routing), agent_reminder.py (routing)

**Improved**:
- All hooks: standardized error handling (catch -> stderr log -> safe pass-through)
- pre_stop_check: added git timeout, marker cleanup, error logging
- Reduced per-request token overhead (no more routing hook noise)

**Architecture**: CLAUDE.md + Commands + Quality Hooks (three-layer, no bloat)

### v5.2.2 (2026-01-29) - Codex Purification Edition

**CLAUDE.md Refactoring**:
- Removed operational config (moved to README)
- Removed specific library names
- Removed specific agent/skill names
- Result: 322 -> 272 lines (-15%)
- CLAUDE.md is now pure principles only

### v5.2.1 (2026-01-29) - Hooks Optimization Edition

**New Hooks (3 new)**:
- `block_dangerous_commands.py`: PreToolUse - Block rm -rf, fork bombs, chmod 777, force push main
- `session_context.py`: SessionStart - Load git context at session start

**Enhanced Detection (aligned with CLAUDE.md 100%)**:
- `mock_detector.py`: Add it.skip/test.skip detection, allow UI handler mocks
- `code_quality.py`: Add hardcoded URL/port, static state, local file detection
- `security_scan.py`: Add catch(e){return null}, catch(e){console.log(e)}, generic Error detection

**Improved Prompts**:
- Layer-specific solutions (Functional Core vs Imperative Shell)
- CLAUDE.md line references for each rule
- Smart false positive reduction (skip config files, comments)

**Hook Output Fixes**:
- Fix field names: `tool` -> `tool_name`, `tool_result` -> `tool_response`
- Fix Stop hook format (no additionalContext support)
- Add `decision: block` for CRITICAL issues

### v5.2.0 (2026-01-28) - Hooks Enforcement Edition

**New Hooks System (6 Python hooks)**:
- `mock_detector.py`: BLOCK jest.fn(), InMemoryRepository patterns
- `code_quality.py`: BLOCK TODO/FIXME/NotImplementedError
- `security_scan.py`: BLOCK hardcoded secrets, SQL injection, empty catch
- `agent_reminder.py`: Suggest agents based on file type/path
- `user_prompt_agent.py`: Suggest agents based on user intent
- `pre_stop_check.py`: Remind to review before session end

**Enforcement Features**:
- Auto-BLOCK on CLAUDE.md rule violations
- Auto-trigger agents based on context
- Smart contract files -> BOTH specialist + auditor (MANDATORY)
- Auth/payment paths -> code-reviewer (MANDATORY)

**Architecture Changes**:
- Hooks enforce rules (not just suggest)
- settings.json hook configuration
- CLAUDE.md agent_system block updated

### v5.0.0 (2026-01-26) - Agent System Edition

**New Agent System (10 custom agents)**:
- `architect`: System architecture expert
- `planner`: Implementation planning expert
- `tdd-guide`: TDD workflow expert
- `build-error-resolver`: Build error fix specialist
- `e2e-runner`: E2E testing expert
- `frontend-developer`: React/Web3 UI development
- `refactor-cleaner`: Dead code cleanup
- `doc-updater`: Documentation maintenance
- `smart-contract-specialist`: Solidity development
- `smart-contract-auditor`: Contract security audit

**New Features**:
- `/learn` command for pattern extraction
- `skills/learned/` directory for extracted patterns
- Confidence levels: Speculation -> Inference -> Fact

### v4.5.1 (2026-01-07) - PromptUp Edition

**PromptUp Skill** (renamed from `senior-prompt-engineer`):
- Replaced hardcoded templates with 6 evidence-based principles
- Added boundary detection (when NOT to use prompt engineering)
- Mapped to Claude Code capabilities (Context7/Exa MCP, CLAUDE.md, skills)

### v4.5.0 (2026-01-07) - Agent Architecture Edition

**Skills Refactoring**:
- Removed `backend`, `frontend`, `smart-contract` domain skills
- Added `promptup` skill for prompt engineering

**New Agent System (4 agents)**:
- `backend-architect`, `frontend-developer`
- `smart-contract-specialist`, `smart-contract-auditor`

### v4.4.0 (2026-01-01) - Streamlined Edition

**Core Changes**:
- Unified Priority Stack in CLAUDE.md
- Codex and Gemini skill integration
- Anti-Pattern Detection in `/ultra-test`

---

## MCP Services

Ultra Builder Pro integrates with these MCP services:

| Service | Purpose |
|---------|---------|
| Context7 | Official documentation lookup |
| Exa | Code examples and community practices |
| Chrome | E2E testing and web automation |

---

## License

MIT

---

*Ultra Builder Pro: No mock. No demo. No MVP. Production-grade only.*
