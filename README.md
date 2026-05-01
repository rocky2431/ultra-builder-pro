<div align="center">

# Ultra Builder Pro

**English** · [简体中文](README.zh-CN.md)

**A dynamic project knowledge base for Claude Code that survives requirement drift.**

**Solves the gap between *what the PRD says* and *what the code actually does* — even after 50 rounds of scope change.**

[![Version](https://img.shields.io/badge/version-7.1.0-blue?style=for-the-badge)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/tests-179_passing-brightgreen?style=for-the-badge)](hooks/tests/)
[![Hooks](https://img.shields.io/badge/hooks-15-yellow?style=for-the-badge)](docs/architecture.md#hooks-system)
[![Agents](https://img.shields.io/badge/agents-12-red?style=for-the-badge)](docs/architecture.md#agent-system)
[![Skills](https://img.shields.io/badge/skills-17-orange?style=for-the-badge)](skills/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
```

**Works wherever Claude Code does.** macOS · Linux · Windows.

[Why I Built This](#why-i-built-this) · [How It Works](#how-it-works) · [The Knowledge Base](#the-dynamic-project-knowledge-base) · [Architecture](docs/architecture.md) · [Changelog](CHANGELOG.md)

</div>

---

## Why I Built This

I'm a DeFi engineer. Most days I don't write code — Claude Code does.

The more I shipped, the more I noticed the same failure mode: **requirements drift, and nobody catches it**.

Real engineering reality: PRDs are never "final" — only "today's version". A sub-feature is added, a constraint shifts, an edge case surfaces during implementation. Static docs can't follow this. They go stale. Technical debt grows silently in the gap between *what the spec says* and *what the code does*.

Tools like BMAD, Speckit, Taskmaster do good work on the planning side. But three phases in, your PRD says **"VIP users get free shipping"** while your code quietly returns a **50% discount** — and no test catches it, because the test was written against the new code, not the original spec.

**Structural lints (types, schemas, call graphs) can't see this. Only an LLM that reads spec text + diff together can.**

Ultra Builder Pro is the engineering implementation of that idea. It's a **dynamic project knowledge base**: a layer that updates itself when code changes, surfaces both *engineering breaks* (schema/types/calls) and *functional breaks* (semantics/intent), and feeds the right context into every Claude Code edit.

No 50-person enterprise theater. No sprint ceremonies. Just a 6-command workflow + a sensor-driven harness that keeps Claude honest as the project drifts.

— **rocky2431**

---

## Who This Is For

People building real products with Claude Code who want the system to:

- **Remember** what each file means and which task it belongs to
- **Surface drift** the moment "free shipping" silently becomes "5% off" — not after the next deploy
- **Stay out of the way** with 6 commands, no sprint ceremonies, no story points
- **Be testable** — 179 hook tests pass, no mocks on core paths

If you want heavy enterprise process, use [BMAD](https://github.com/bmad-code-org/BMAD-METHOD). If you want a pure planner, use [Speckit](https://github.com/specifyx/speckit). If you want git-free workflows, this isn't it — Ultra Builder commits per task.

---

## What's New — v7.1.0 (Dynamic Project Knowledge Base)

Live KB that survives requirement drift. Five additions, all sensor-only, all reusing the v7.0 substrate:

- **Reverse trace** (`post_edit_guard.py`) — edit any file → stderr shows owning task + first AC bullets; unowned files get a git-context fallback (branch + last commit)
- **AC drift detection** (`review-ac-drift` agent) — 7th specialist in `/ultra-review`; reads AC text + diff together; catches "VIP free shipping → 50% off" structural lints miss
- **Wiki views** (`wiki_generator.py`) — auto-derived `.ultra/wiki/{index,log}.md` from project state, including Recent Activity table
- **Session trail** (`session_trail.py`) — Stop hook folds session facts into the active task's `## Session Trail` section
- **Orphan handling** — sessions without an active task still leave residue: `.ultra/sessions/orphan-trail.md` + Recent Activity merge

→ Full version history in [CHANGELOG.md](CHANGELOG.md). Architecture detail in [docs/architecture.md](docs/architecture.md).

---

## Getting Started

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git ~/.claude
cd ~/.claude && python3 -m pytest hooks/tests/ --ignore=hooks/tests/test_pre_stop_check.py
# Expected: 179 passed
```

Then in any project:

```bash
cd ~/your-project && claude
```

In Claude Code, run `/ultra-init` to initialize a new project (or `/ultra-status` to verify install).

### Recommended: Skip Permissions Mode

```bash
claude --dangerously-skip-permissions
```

The system is designed for frictionless automation. Stopping to approve `date` and `git commit` 50 times defeats the purpose. Granular alternative: whitelist specific commands in `.claude/settings.json` `permissions.allow`.

---

## How It Works

Six commands. Each does one thing well; the system handles complexity behind the scenes.

### 1. Initialize

```
/ultra-init
```

Auto-detects project type, copies templates from `.ultra-template/`, sets up `.ultra/` directory structure. **Creates:** `.ultra/{specs,tasks,docs}/`, `PHILOSOPHY.md`, `north-star.md`.

### 2. Research (Optional but Recommended)

```
/ultra-research
```

17 step-files (BMAD-style architecture, ~200 lines/step). Each step has mandatory web search with pre-written queries, structured output template with field-level specs, write-immediately discipline.

- Steps 00–05: Product Discovery (TAM/SAM/SOM, Strategy Canvas, Validation Plan)
- Steps 10–11: Personas & Scenarios
- Steps 20–22: Feature Definition with Given/When/Then AC
- Steps 30–32: Architecture (sourced rationale per tech choice)
- Steps 40–41: Quality & Deployment
- Step 99: Synthesis → `research-distillate.md`

**Creates:** `.ultra/specs/{discovery,product,architecture}.md`.

### 3. Plan

```
/ultra-plan
```

Reads specs, generates atomic task breakdown. Mode selection: EXPAND / SELECTIVE (default) / HOLD / REDUCE. Each task has Given/When/Then acceptance criteria, Definition of Drift, target files, `trace_to` spec section. Walking skeleton is always Task #1. Integration checkpoints every 3-4 tasks.

**Creates:** `.ultra/tasks/{tasks.json, contexts/task-N.md}`.

### 4. Develop

```
/ultra-dev
```

TDD workflow: RED → GREEN → REFACTOR. **Goal-Always-Present** substrate (`mid_workflow_recall.py`) injects active task's AC on every Edit/Write — Claude always knows what success looks like. `progress.json` tracks 6-dimension `evidence_score` continuously. Step 4.5 runs `/ultra-review all` before commit.

**Creates:** implementation + tests + atomic commits per task.

### 5. Review

```
/ultra-review              # Smart skip based on diff content
/ultra-review all          # Force all 7 agents (pre-merge gate)
```

7 specialist agents run in parallel, each in fresh context, write findings to `.ultra/reviews/<session>/`. Coordinator aggregates → SUMMARY. The 7th agent (`review-ac-drift`, v7.1) reads spec + diff together for semantic alignment.

### 6. Deliver

```
/ultra-deliver
```

CHANGELOG, version bump, build, tag, push. Pre-flight: full test suite + ultra-review verdict must be APPROVE.

---

## The Dynamic Project Knowledge Base

What sets this apart from BMAD/Speckit/Taskmaster: **the KB is alive**. It updates on every Edit/Write/Stop without you doing anything.

### Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3 — Schema (philosophy, immutable)                   │
│    .ultra/PHILOSOPHY.md, CLAUDE.md, harness rules           │
│                                                              │
│  Layer 2 — Wiki (interpretation; humans + LLMs read)        │
│    .ultra/wiki/index.md            tasks by status          │
│    .ultra/wiki/log.md              chronological progress   │
│    task-*.md ## Session Trail      folded session facts     │
│    .ultra/sessions/orphan-trail.md no-task sessions         │
│                                                              │
│  Layer 1 — Facts (machine-maintained)                       │
│    .ultra/relations.json           task ↔ spec ↔ code       │
│    .ultra/tasks/progress/          per-task evidence_score  │
│    git history                     truth of record          │
└─────────────────────────────────────────────────────────────┘
```

Wiki nodes never store facts; they only store interpretation. **No silent staleness** — when facts change, wiki regenerates.

### Live Behavior (try it)

| Trigger | What you see |
|---------|--------------|
| Edit a file owned by a task | `[Trace] task-3 (in_progress): VIP shipping; AC-1: VIP user shipping fee = 0` injected to stderr |
| Edit an unowned file in an Ultra project | `[Trace] (no task) shipping.ts on branch main; last: abc123 fix...` |
| Edit a file in a non-Ultra project | Silent (no noise) |
| Stop with active task + edits | Bullet folded into task's `## Session Trail` section |
| Stop without active task + edits | Bullet folded into `.ultra/sessions/orphan-trail.md` |
| Edit a spec or task definition | `relations.json` rebuilt + wiki refreshed |
| Run `/ultra-review all` | 7 agents run in parallel; review-ac-drift reads spec + diff for semantic alignment |

---

## Why It Works

### Sensor-Not-Blocker Philosophy (v7.0)

Pre-v7 hooks blocked on every recoverable issue (mocks, scope words, silent catches). Result: agents edited tests/specs to *escape* the blocks — worse outcomes than no hooks.

v7 inverts: blocks reserved for **truly irreversible** actions (hardcoded secrets, SQL injection, force-push to main, DB migration commits). Everything else is advisory. The agent reads, decides, proceeds.

### Bidirectional Traceability

Most tools maintain `spec → task`. Ultra Builder maintains all three:

- `task → spec section` (`trace_to`)
- `spec section → tasks` (`referenced_by`)
- `code path → tasks` (`files` reverse map, v7.1)

Edit `src/checkout/shipping.ts`, the system knows: this is task-3, traces to `specs/product.md#vip-shipping`, has 2 acceptance criteria. All visible in stderr the moment you edit.

### Parallel Multi-Agent Review

Sequential reviews lose context as findings accumulate. Ultra Review fans out 7 specialists in parallel — each in a fresh 200k context — writes findings to JSON files, then a coordinator dedupes and prioritizes. Main session stays at 30-40% context usage.

### Cross-Session Memory

`session_journal.py` writes structured summaries to SQLite FTS5 + Chroma vectors. Next session, `mid_workflow_recall.py` injects relevant past failures + active AC at the moment you edit a file. Hybrid search (FTS5 + RRF) via `/recall`. Inspired by claude-mem's failure mode (~25k token bulk injection); we inject ~50 tokens at session start, search on-demand.

---

## Commands & Skills

| Family | Examples | Detail |
|--------|----------|--------|
| **Workflow** | `/ultra-init` `/ultra-research` `/ultra-plan` `/ultra-dev` `/ultra-test` `/ultra-deliver` | Step-by-step pipeline |
| **Quality** | `/ultra-review` `/ultra-verify` (3-way AI) `/ultra-status` | Standalone gates |
| **Memory** | `/recall` `/learn` | Cross-session search + pattern extraction |
| **Thinking** | `/ultra-think` | Adversarial reasoning framework |

**17 skills** under `skills/` — research step-files, review pipeline, three-way verify (Claude + Gemini + Codex), recall, vercel best practices, web design guidelines, and agent-only checklists (security, testing, integration).

**12 agents** under `agents/` — 5 interactive (smart-contract specialist + auditor, code-reviewer, tdd-runner, debugger) + 7 review pipeline. All have `memory: project` for per-project pattern accumulation.

→ Full reference: [docs/architecture.md](docs/architecture.md).

---

## Configuration

Project settings live in `.ultra/` (per-project, mostly gitignored). Global settings in `~/.claude/settings.json`.

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
- `.ultra/wiki/{index,log}.md` (auto-generated, useful for code review)

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
| `relations.json` dangling trace_to | Run `/ultra-status`; the broken trace will be highlighted |

---

## License

MIT. See [LICENSE](LICENSE).

---

<div align="center">

**Claude Code is powerful. Ultra Builder Pro keeps it honest as your project drifts.**

</div>
