<div align="center">

# Ultra Builder Pro

**English** · [简体中文](README.zh-CN.md)

**A production-grade engineering harness for Claude Code.**

**Six-command workflow · Sensor-driven hooks · Multi-agent review · Cross-session memory · Live project KB · Three-way AI verification.**

[![Version](https://img.shields.io/badge/version-7.1.0-blue?style=for-the-badge)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-179_passing-brightgreen?style=for-the-badge)](hooks/tests/)
[![Hooks](https://img.shields.io/badge/hooks-15-yellow?style=for-the-badge)](docs/architecture.md#hooks-system)
[![Agents](https://img.shields.io/badge/agents-9-red?style=for-the-badge)](docs/architecture.md#agent-system)
[![Skills](https://img.shields.io/badge/skills-22-orange?style=for-the-badge)](skills/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
```

**Works wherever Claude Code does.** macOS · Linux · Windows.

[Why I Built This](#why-i-built-this) · [What's Inside](#whats-inside) · [How It Works](#how-it-works) · [Why It Works](#why-it-works) · [Architecture](docs/architecture.md) · [Changelog](CHANGELOG.md)

</div>

---

## Why I Built This

I'm a Web3 + AI-native engineer. I don't write code — Claude Code does.

But getting code *written* and getting code *to production* are two different things. When you need:

- Real code review, not "looks fine to me"
- Real tests passing, not mocks pretending to be green
- Specs that survive 50 rounds of drift, not silent semantic decay
- Context that persists across sessions, not yesterday's decisions vanishing overnight
- Cross-AI sanity checks, not one model marking its own homework

— LLM-by-conversation isn't enough. It forgets. It silently scope-reduces. It mocks core paths and calls them tested. It says "VIP free shipping" while implementing a 50% discount.

Ultra Builder Pro is the **engineering harness** that sits on top of Claude Code and makes it production-grade. Not one tool — an integrated substrate of six layers:

1. **Spec-driven 6-command workflow** that takes you from idea to release
2. **Sensor-driven 15-hook chain** that informs without obstructing (v7.0 doctrine)
3. **7-agent parallel code review pipeline** with semantic-drift detection
4. **Cross-session SQLite + vector memory** with structured AI summaries
5. **Live bidirectional task ↔ code ↔ spec knowledge base** (v7.1)
6. **Three-way AI verification** (Claude + Gemini + Codex with consensus scoring)

It doesn't think for you. It **keeps Claude honest** while you do.

Other systems give you parts of this. BMAD has the workflow. claude-mem tried memory and exploded. GSD nailed the spec-driven discipline. Ultra Builder Pro is the integrated assembly — every piece reinforces the others.

— **rocky2431**

---

## Who This Is For

People shipping real products with Claude Code who want:

- **Production discipline by default** — TDD enforcement, parallel review, atomic commits per task
- **A system that remembers** — across files, tasks, sessions, AI providers
- **Drift caught early** — when "free shipping" silently becomes "5% off", not after deploy
- **No theater** — 9 commands instead of 30; no sprint planning, no story points, no Jira

If you want heavy enterprise process, use [BMAD](https://github.com/bmad-code-org/BMAD-METHOD). For pure planning, use [Speckit](https://github.com/specifyx/speckit). For lighter context engineering, use [GSD](https://github.com/gsd-build/get-shit-done). Ultra Builder Pro is the maximalist option — pick it when you want every layer integrated.

---

## What's Inside

Built on Claude Code. Adds six layers of production-engineering discipline.

### 1. Spec-Driven 6-Command Workflow

```
/ultra-init  →  /ultra-research  →  /ultra-plan  →  /ultra-dev  →  /ultra-test  →  /ultra-deliver
```

Each command does one thing well; the system handles complexity behind the scenes. Behind it: TDD red-green-refactor enforcement, automatic git flow with atomic per-task commits, walking-skeleton-first task ordering, integration checkpoints every 3-4 tasks.

`/ultra-research` is itself a 17-step-file architecture (BMAD-inspired) — each step has dense instructions, pre-written web search queries, structured output templates, and write-immediately discipline. Output: `discovery.md`, `product.md`, `architecture.md`, plus a token-efficient `research-distillate.md` for `/ultra-plan`.

→ See `commands/ultra-*.md` and [docs/architecture.md](docs/architecture.md).

### 2. Sensor-Driven Hook Harness (15 hooks)

**v7.0 doctrine: blocks reserved for *truly irreversible* actions only.** Hardcoded secrets, SQL injection, force-push to main, DB migration commits. Everything else — mocks, scope reduction, silent catches, TODO/FIXME, default-off feature flags — is *advisory*. The agent reads, decides, proceeds.

This inverts the pre-v7 over-correction loop, where blocked agents would silently edit tests and specs to escape blocks (worse outcome than no hooks). Sensor mode gives signal without distortion. Hooks now also inject **goal context** at decision time: when you start to edit a file, `mid_workflow_recall.py` injects the active task's acceptance criteria + relevant past failures from memory.db.

→ Hook table: [docs/architecture.md#hooks-system](docs/architecture.md#hooks-system).

### 3. Multi-Agent Code Review Pipeline (7 specialists, parallel)

Sequential reviews lose context as findings accumulate. `/ultra-review` fans out 7 specialists in parallel — each in a fresh 200k context — and a coordinator dedupes and prioritizes. **Main session stays at 30-40% context usage** even during deep review.

Specialists:
- `review-code` — security, SOLID, forbidden patterns, scope drift
- `review-tests` — mock violations, coverage gaps, boundary tests
- `review-errors` — silent failures, swallowed errors, empty catches
- `review-design` — type design, encapsulation, complexity
- `review-comments` — stale, misleading, low-value comments
- `review-ac-drift` (v7.1) — **semantic alignment**: reads spec text + diff together, catches "VIP free shipping → 5% off" structural lints can't see
- `review-coordinator` — aggregate, deduplicate, generate SUMMARY

Verdict logic: P0 > 0 → REQUEST_CHANGES; P1 > 3 → REQUEST_CHANGES; P1 > 0 → COMMENT; else APPROVE. Branch-scoped session index with iteration chains for re-checks.

→ See `skills/ultra-review/SKILL.md`.

### 4. Cross-Session Memory + AI Summary

SQLite FTS5 + Chroma vector store + structured Haiku summaries. **At session end** a non-blocking daemon parses the transcript, generates a structured JSON summary (`request`, `completed`, `learned`, `next_steps`), and upserts both the SQLite FTS5 row and the Chroma vector. **At session start** one line (~50 tokens) about the previous session is injected — no bulk dump.

Search on demand via `/recall`. Hybrid mode (default): FTS5 keyword + Chroma semantic via RRF (k=60). Pure semantic and pure keyword modes available. The skill runs in a forked context so search results never pollute your main conversation.

Designed as the safe alternative to **claude-mem** after that project's ~25k token bulk injection killed it.

→ See `skills/recall/SKILL.md`.

### 5. Live Project Knowledge Base (v7.1)

Bidirectional task ↔ code ↔ spec index in `.ultra/relations.json`. Auto-derived wiki views in `.ultra/wiki/{index,log}.md`. Session facts folded into task contexts as a `## Session Trail` section. Sessions without an active task still leave residue in `.ultra/sessions/orphan-trail.md`.

Three-layer architecture:

```
Layer 3 — Schema (immutable):     PHILOSOPHY.md, CLAUDE.md, harness rules
Layer 2 — Wiki (interpretation):  wiki/{index,log}.md, ## Session Trail, orphan-trail
Layer 1 — Facts (machine-kept):   relations.json, progress/*.json, git history
```

Wiki nodes never store facts; they only store interpretation. **No silent staleness** — when facts change, wiki regenerates. Edit a file owned by a task → stderr shows the task + first AC. Edit an unowned file → git context fallback (branch + last commit). Edit a non-Ultra project → silent.

→ See [CHANGELOG v7.1](CHANGELOG.md#v710-2026-05-01--dynamic-project-knowledge-base).

### 6. Three-Way AI Verification

`/ultra-verify` spawns Claude + Gemini + Codex *independently* as parallel background tasks. Claude writes its answer to a file *before* reading the others — preventing contamination. Then Claude reads all three outputs and synthesizes with confidence scoring:

| Outcome | Confidence |
|---------|------------|
| 3/3 agree | **Consensus** |
| 2/3 agree | **Majority** |
| All differ | **No Consensus** |

Four modes: `decision` (architecture choices), `diagnose` (bug hypotheses), `audit` (code review), `estimate` (effort). Degrades gracefully — one AI fails → two-way capped at Majority; two fail → Claude-only with explicit warning.

Built on a shared `ai-collab-base` skill with synced collaboration protocol files. Eliminates ~90% structural duplication between gemini-collab and codex-collab.

→ See `skills/ultra-verify/SKILL.md`.

---

## What's New — v7.1.0

**Dynamic Project Knowledge Base** — five additions on top of the v7.0 sensor-first foundation:

- File→task reverse trace with git-context fallback (`post_edit_guard.py`)
- 7th review specialist `review-ac-drift` for semantic alignment
- Auto-derived wiki views with Recent Activity table
- Session trail fold-back into task context
- Orphan session handling for cross-task / no-plan / hotfix work

→ Full version history: [CHANGELOG.md](CHANGELOG.md).

---

## Getting Started

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
cd ~/.claude && python3 -m pytest hooks/tests/ --ignore=hooks/tests/test_pre_stop_check.py
# Expected: 179 passed
```

In any project:

```bash
cd ~/your-project && claude
```

In Claude Code, run `/ultra-init` to initialize. Verify with `/ultra-status`.

### Recommended: Skip Permissions Mode

```bash
claude --dangerously-skip-permissions
```

The harness is designed for frictionless automation. Stopping to approve `git commit` 50 times defeats the purpose. Granular alternative: whitelist specific commands in `.claude/settings.json` `permissions.allow`.

---

## How It Works

The 6-command pipeline, end to end. Each command outputs files the next one consumes.

| Step | Command | What happens | Outputs |
|------|---------|--------------|---------|
| 1 | `/ultra-init` | Auto-detect project type; copy templates from `.ultra-template/`; set up `.ultra/` directory | `.ultra/{specs,tasks,docs}/`, `PHILOSOPHY.md`, `north-star.md` |
| 2 | `/ultra-research` | 17-step research pipeline; mandatory web search per step; structured output templates | `discovery.md`, `product.md`, `architecture.md`, `research-distillate.md` |
| 3 | `/ultra-plan` | Atomic task breakdown; mode (EXPAND/SELECTIVE/HOLD/REDUCE); walking skeleton first; integration checkpoints | `tasks.json`, `contexts/task-N.md` per task |
| 4 | `/ultra-dev` | TDD red-green-refactor; goal-always-present AC injection; per-task atomic commit; runs `/ultra-review all` at step 4.5 | implementation, tests, commits |
| 5 | `/ultra-review` | 7-agent parallel review; coordinator dedupes; SUMMARY.json + .md | `.ultra/reviews/<session>/SUMMARY.{json,md}` |
| 6 | `/ultra-deliver` | Pre-flight tests + review verdict APPROVE; CHANGELOG; version bump; tag; push | release artifacts, git tag |

Standalone gates (any time): `/ultra-status`, `/ultra-verify`, `/ultra-test`, `/ultra-think`. Memory: `/recall`, `/learn`.

---

## Why It Works

### Sensor-Not-Blocker Philosophy (v7.0)

Pre-v7 hooks blocked on every recoverable issue — agents responded by editing tests/specs to escape, *worse* than no hooks. v7 inverts: blocks for irreversibility only, advisories for everything else. The agent has the signal and the autonomy. PHILOSOPHY.md C3 (Sensors not Blockers) + C4 (Incremental Validation) codify this.

### Bidirectional Traceability

Most tools maintain `spec → task`. Ultra Builder maintains all three:
- `task → spec section` (`trace_to`)
- `spec section → tasks` (`referenced_by`)
- `code path → tasks` (`files` reverse map, v7.1)

Edit `src/checkout/shipping.ts` → system knows it's task-3 → traces to `specs/product.md#vip-shipping` → has 2 ACs. Visible in stderr the moment you edit.

### Parallel Multi-Agent Review (Zero Context Pollution)

Sequential reviews lose context. Ultra Review fans out 7 specialists in parallel, each in fresh 200k context, writes findings to JSON files; coordinator dedupes. Main conversation never sees raw findings — only the deduplicated SUMMARY. Context usage stays at 30-40% even after a 7-way review.

### Cross-Session Memory Without Bulk Injection

claude-mem injected ~25k tokens at SessionStart and exploded contexts. Our approach: 1 line at start (~50 tokens), search on-demand. Auto-captured at Stop via async daemon (no hot-path blocking). Hybrid retrieval: FTS5 + Chroma vectors via Reciprocal Rank Fusion.

### Three-Way AI as Independent Reviewers

A single LLM marks its own homework. Three LLMs from different families (Anthropic, Google, OpenAI) provide actual independence. Confidence emerges from consensus, not assertion.

---

## Commands & Skills

**9 commands** under `commands/`:

| Family | Commands |
|--------|----------|
| Workflow | `ultra-init` `ultra-research` `ultra-plan` `ultra-dev` `ultra-test` `ultra-deliver` |
| Quality | `ultra-status` `ultra-think` |
| Memory | `learn` |

**22 skills** under `skills/`:

| Category | Skills |
|----------|--------|
| Workflow | `ultra-research` (17 step-files), `ultra-review`, `ultra-verify`, `recall` |
| AI Collab | `ai-collab-base`, `gemini-collab`, `codex-collab` |
| Agent-only checklists | `code-review-expert`, `integration-rules`, `security-rules`, `testing-rules` |
| Utility | `agent-browser`, `find-skills`, `use-railway`, `market-research` |
| Design / Output | `web-design-guidelines`, `guizang-ppt-skill`, `html-ppt` |
| Vercel best practices | `vercel-react-best-practices`, `vercel-react-native-skills`, `vercel-composition-patterns` |
| Pattern extraction | `learned/` (populated by `/learn`) |

**9 agents** under `agents/`:

| Type | Agents |
|------|--------|
| Interactive | `code-reviewer`, `debugger` |
| Review pipeline (parallel) | `review-code`, `review-tests`, `review-errors`, `review-design`, `review-comments`, `review-ac-drift`, `review-coordinator` |

All agents have `memory: project` for per-project pattern accumulation.

→ Full reference: [docs/architecture.md](docs/architecture.md).

---

## Configuration

Project state in `.ultra/` (per-project, mostly gitignored). Global config in `~/.claude/settings.json`.

### Recommended `.gitignore`

```
.ultra/memory/
.ultra/reviews/
.ultra/compact-snapshot.md
.ultra/debug/
.ultra/workflow-state.json
.ultra/sessions/orphan-trail.md
```

Keep these in version control:
- `.ultra/specs/`
- `.ultra/tasks/tasks.json`, `.ultra/tasks/contexts/`
- `.ultra/relations.json`
- `.ultra/wiki/{index,log}.md` (auto-generated; useful for code review)

### Sensitive File Protection

Add to `~/.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)", "Read(./.env.*)",
      "Read(./secrets/**)", "Read(./**/*credential*)"
    ]
  }
}
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tests fail after install | Run `python3 hooks/system_doctor.py` for deep audit |
| Hooks not firing | Check `~/.claude/settings.json` has `hooks` section; restart Claude Code |
| Stale wiki | Edit any file in `.ultra/specs/` or `.ultra/tasks/` to retrigger; or run `python3 ~/.claude/hooks/wiki_generator.py /your/repo` |
| Memory.db locked | Close stale Claude Code sessions (only one writer at a time) |
| `relations.json` dangling trace_to | Run `/ultra-status`; broken traces are highlighted |
| `ultra-verify` Gemini/Codex unavailable | Install: `npm i -g @google/gemini-cli @openai/codex`; degrades to Claude-only with warning |

---

## License

MIT. See [LICENSE](LICENSE).

---

<div align="center">

**Claude Code is powerful. Ultra Builder Pro makes it production-grade.**

</div>
