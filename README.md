# Ultra Builder Pro 5.2.0

<div align="center">

**Production-Grade AI-Powered Development System for Claude Code**

---

[![Version](https://img.shields.io/badge/version-5.2.0-blue)](README.md#version-history)
[![Status](https://img.shields.io/badge/status-production--ready-green)](README.md)
[![Commands](https://img.shields.io/badge/commands-9-purple)](commands/)
[![Skills](https://img.shields.io/badge/skills-5-orange)](skills/)
[![Agents](https://img.shields.io/badge/agents-7-red)](agents/)
[![Hooks](https://img.shields.io/badge/hooks-6-yellow)](hooks/)

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
Code Quality = Real Implementation × Real Tests × Real Dependencies
If ANY component is fake/mocked/simulated → Quality = 0
```

---

## Workflow

```
/ultra-init → /ultra-research → /ultra-plan → /ultra-dev → /ultra-test → /ultra-deliver
     ↓              ↓                ↓              ↓             ↓             ↓
  Project       4-Round          Task         TDD Cycle      Quality       Release
  Setup        Discovery       Breakdown      RED→GREEN      Audit        & Deploy
```

---

## Commands (9)

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `/ultra-init` | Initialize project | Auto-detect type/stack, copy templates, git setup |
| `/ultra-research` | Interactive discovery | 4 rounds (User→Feature→Architecture→Quality), 90%+ confidence |
| `/ultra-plan` | Task planning | Dependency analysis, complexity assessment, context files |
| `/ultra-dev` | TDD development | RED→GREEN→REFACTOR, PR Review Toolkit, auto git flow |
| `/ultra-test` | Quality audit | Anti-Pattern, Coverage gaps, E2E, Performance, Security |
| `/ultra-deliver` | Release preparation | CHANGELOG, build, version bump, tag, push |
| `/ultra-status` | Progress monitoring | Real-time stats, risk analysis, recommendations |
| `/ultra-think` | Deep analysis | Structured reasoning, multi-dimension comparison |
| `/learn` | Pattern extraction | Extract reusable patterns from session, save to skills/learned/ |

---

## Skills (5)

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| `codex` | OpenAI Codex CLI | Code analysis, refactoring, **can modify code** |
| `gemini` | Google Gemini CLI | Research, validation, docs; `-y` for code changes |
| `promptup` | Prompt engineering | Evidence-based principles, boundary detection, diagnostic iteration |
| `skill-creator` | Create new skills | Workflow guidance, packaging |
| `learned/` | Extracted patterns | Patterns from `/learn` command with confidence levels |

### Learned Patterns

Patterns extracted via `/learn` are stored in `skills/learned/` with confidence levels:

| Confidence | File Suffix | Description |
|------------|-------------|-------------|
| Speculation | `_unverified` | Freshly extracted, needs verification |
| Inference | No suffix | Human review passed |
| Fact | No suffix + marked | Multiple successful uses verified |

---

## Agents (7 Custom + Plugins)

> **Default Model**: ALL agents use Opus. No exceptions.

### Custom Agents (`~/.claude/agents/`)

| Agent | Purpose | Hook Trigger |
|-------|---------|--------------|
| `build-error-resolver` | Build error quick fix | Build command fails |
| `e2e-runner` | E2E testing with Playwright | /e2e/, "e2e test" |
| `frontend-developer` | React/Web3, UI components | .tsx/.jsx/.vue/.svelte |
| `refactor-cleaner` | Dead code cleanup | "refactor", "dead code" |
| `doc-updater` | Documentation maintenance | .md files, /docs/ |
| `smart-contract-specialist` | Solidity, gas optimization | .sol, "solidity" |
| `smart-contract-auditor` | Contract security audit | .sol, "audit contract" |

### Plugin Agents (pr-review-toolkit)

| Agent | Purpose | Hook Trigger |
|-------|---------|--------------|
| `pr-review-toolkit:code-reviewer` | CLAUDE.md compliance check | "review pr", API paths |
| `pr-review-toolkit:silent-failure-hunter` | Error handling review | "error handling" |
| `pr-review-toolkit:pr-test-analyzer` | Test coverage analysis | "test coverage" |
| `pr-review-toolkit:code-simplifier` | Code simplification | "simplify", "too complex" |
| `pr-review-toolkit:type-design-analyzer` | Type design analysis | "type design" |

---

## TDD Workflow

Mandatory for all new code:

```
1. RED    → Write failing test first (define expected behavior)
2. GREEN  → Write minimal code to pass test
3. REFACTOR → Improve code (keep tests passing)
4. COVERAGE → Verify 80%+ coverage
5. COMMIT → Atomic commit (test + implementation together)
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

## Hooks System (6 Hooks)

Automated enforcement of CLAUDE.md rules via Python hooks in `hooks/`:

### Blocking Hooks (BLOCK on violation)

| Hook | Trigger | Detection |
|------|---------|-----------|
| `mock_detector.py` | Edit/Write | jest.fn(), jest.mock(), InMemoryRepository |
| `code_quality.py` | Edit/Write | TODO/FIXME, NotImplementedError |
| `security_scan.py` | Edit/Write | Hardcoded secrets, SQL injection, empty catch |

### Reminder Hooks (Suggest agents)

| Hook | Trigger | Function |
|------|---------|----------|
| `agent_reminder.py` | Edit/Write/Bash | Suggest agents based on file type/path |
| `user_prompt_agent.py` | UserPromptSubmit | Suggest agents based on user intent |
| `pre_stop_check.py` | Stop | Remind to review uncommitted changes |

### Auto-Trigger Matrix

| Signal | Agent/Skill Triggered | Priority |
|--------|----------------------|----------|
| .sol files | smart-contract-specialist + auditor | MANDATORY |
| /auth/, /payment/ paths | security-reviewer | MANDATORY |
| Build command fails | build-error-resolver | Recommended |
| .tsx/.jsx files | frontend-developer + react-best-practices (skill) | Recommended |
| "review code/PR" | pr-review-toolkit:code-reviewer | Recommended |
| "ready to merge/commit" | pr-review-toolkit:code-reviewer | Recommended |

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
| Code Review | MANDATORY pr-review-toolkit:code-reviewer |

### Code Limits

| Metric | Limit |
|--------|-------|
| Function lines | ≤ 50 |
| File lines | 200-400 typical, 800 max |
| Nesting depth | ≤ 4 |
| Cyclomatic complexity | ≤ 10 |

---

## Project Structure

```
~/.claude/
├── CLAUDE.md                 # Main configuration (Priority Stack)
├── README.md                 # This file
├── settings.json             # Claude Code settings + hooks config
│
├── hooks/                    # Automated enforcement (6 hooks)
│   ├── mock_detector.py      # BLOCK: jest.fn(), InMemoryRepo
│   ├── code_quality.py       # BLOCK: TODO/FIXME, NotImplemented
│   ├── security_scan.py      # BLOCK: secrets, SQL injection
│   ├── agent_reminder.py     # REMIND: file-based agent suggestions
│   ├── user_prompt_agent.py  # REMIND: intent-based agent suggestions
│   └── pre_stop_check.py     # REMIND: review before session end
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
├── skills/                   # Domain skills (5)
│   ├── codex/                # OpenAI Codex CLI
│   ├── gemini/               # Google Gemini CLI
│   ├── promptup/             # Prompt engineering
│   ├── skill-creator/        # Create new skills
│   └── learned/              # Extracted patterns
│
├── agents/                   # Custom agents (7)
│   ├── build-error-resolver.md
│   ├── doc-updater.md
│   ├── e2e-runner.md
│   ├── frontend-developer.md
│   ├── refactor-cleaner.md
│   ├── smart-contract-specialist.md
│   └── smart-contract-auditor.md
│
└── .ultra-template/          # Project initialization templates
    ├── specs/
    ├── tasks/
    └── docs/
```

---

## Version History

### v5.2.0 (2026-01-29) - Hooks Enforcement Edition

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
- Smart contract files → BOTH specialist + auditor (MANDATORY)
- Auth/payment paths → security-reviewer (MANDATORY)
- Integration with pr-review-toolkit plugin agents

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
- Confidence levels: Speculation → Inference → Fact

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
