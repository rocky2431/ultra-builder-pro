# Ultra Builder Pro 5.4.0

<div align="center">

**Production-Grade AI-Powered Development System for Claude Code**

---

[![Version](https://img.shields.io/badge/version-5.4.0-blue)](README.md#version-history)
[![Status](https://img.shields.io/badge/status-production--ready-green)](README.md)
[![Commands](https://img.shields.io/badge/commands-10-purple)](commands/)
[![Skills](https://img.shields.io/badge/skills-3-orange)](skills/)
[![Agents](https://img.shields.io/badge/agents-5-red)](agents/)
[![Hooks](https://img.shields.io/badge/hooks-9-yellow)](hooks/)

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

## Commands (10)

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
| `/commit` | Standardized commits | Conventional commit format, co-author attribution |
| `/learn` | Pattern extraction | Extract reusable patterns from session, save to skills/learned/ |

---

## Skills (3 + Learned Patterns)

| Skill | Purpose | User-Invocable |
|-------|---------|----------------|
| `codex` | OpenAI Codex CLI integration | Yes |
| `testing-rules` | TDD discipline, mock detection rules | No (agent-only) |
| `security-rules` | Input validation, injection prevention rules | No (agent-only) |
| `learned/` | Extracted patterns from `/learn` | Yes |

---

## Agents (5 Custom + Plugins)

### Custom Agents (`~/.claude/agents/`)

All agents have **persistent memory** that accumulates patterns across sessions.

| Agent | Purpose | Trigger | Model | Memory |
|-------|---------|---------|-------|--------|
| `smart-contract-specialist` | Solidity, gas optimization, secure patterns | .sol files | opus | user |
| `smart-contract-auditor` | Contract security audit, vulnerability detection | .sol files | opus | user |
| `code-reviewer` | Code review for quality, security, maintainability | After code changes, pre-commit | inherit | user |
| `tdd-runner` | Test execution, failure analysis, coverage | "run tests", test suite | haiku | project |
| `debugger` | Root cause analysis, minimal fix implementation | Errors, test failures | inherit | user |

### Plugin Agents (pr-review-toolkit)

| Agent | Purpose |
|-------|---------|
| `pr-review-toolkit:code-reviewer` | CLAUDE.md compliance check |
| `pr-review-toolkit:silent-failure-hunter` | Error handling review |
| `pr-review-toolkit:pr-test-analyzer` | Test coverage analysis |
| `pr-review-toolkit:code-simplifier` | Code simplification |
| `pr-review-toolkit:type-design-analyzer` | Type design analysis |

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

## Hooks System (10 Hooks)

Automated enforcement of CLAUDE.md rules via Python hooks in `hooks/`:

### PreToolUse Hooks (Guard before execution)

| Hook | Trigger | Detection |
|------|---------|-----------|
| `block_dangerous_commands.py` | Bash | rm -rf, fork bombs, chmod 777, force push main |

### PostToolUse Hooks (Quality gate after execution)

| Hook | Trigger | Detection |
|------|---------|-----------|
| `code_quality.py` | Edit/Write | TODO/FIXME, NotImplemented, hardcoded URLs/ports, static state |
| `mock_detector.py` | Edit/Write | jest.fn(), vi.fn(), InMemoryRepository, it.skip |
| `security_scan.py` | Edit/Write | Hardcoded secrets, SQL injection, empty catch, bad error handling |

### Session & Lifecycle Hooks

| Hook | Trigger | Function |
|------|---------|----------|
| `session_context.py` | SessionStart | Load git branch, recent commits, modified files |
| `pre_stop_check.py` | Stop | BLOCK if security files unreviewed |
| `subagent_tracker.py` | SubagentStart/Stop | Log agent lifecycle to debug/subagent-log.jsonl |
| `pre_compact_context.py` | PreCompact | Preserve task state and git context before compaction |

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
├── hooks/                    # Automated enforcement (9 hooks)
│   ├── block_dangerous_commands.py  # PreToolUse: dangerous bash commands
│   ├── code_quality.py              # PostToolUse: TODO, hardcoded config
│   ├── mock_detector.py             # PostToolUse: mock patterns, it.skip
│   ├── security_scan.py             # PostToolUse: secrets, SQL, errors
│   ├── session_context.py           # SessionStart: load dev context
│   ├── pre_stop_check.py            # Stop: security file review
│   ├── subagent_tracker.py          # SubagentStart/Stop: lifecycle logging
│   └── pre_compact_context.py       # PreCompact: preserve context
│
├── commands/                 # /ultra-* commands (10)
│   ├── ultra-init.md
│   ├── ultra-research.md
│   ├── ultra-plan.md
│   ├── ultra-dev.md
│   ├── ultra-test.md
│   ├── ultra-deliver.md
│   ├── ultra-status.md
│   ├── ultra-think.md
│   ├── commit.md
│   └── learn.md
│
├── skills/                   # Domain skills (3 + learned)
│   ├── codex/                # OpenAI Codex CLI
│   ├── testing-rules/        # TDD rules (agent-only)
│   ├── security-rules/       # Security rules (agent-only)
│   └── learned/              # Extracted patterns
│
├── agents/                   # Custom agents (5)
│   ├── smart-contract-specialist.md
│   ├── smart-contract-auditor.md
│   ├── code-reviewer.md
│   ├── tdd-runner.md
│   └── debugger.md
│
└── .ultra-template/          # Project initialization templates
    ├── specs/
    ├── tasks/
    └── docs/
```

---

## Operational Config

> These are operational settings, not principles. CLAUDE.md contains the principles.

### Git Workflow

- Follow project branch naming conventions
- Conventional Commits format
- Include Co-author for AI commits:
  ```
  Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
  ```

### Project Structure

```
New Ultra projects use:
.ultra/
├── tasks/    # Task tracking
├── specs/    # Specifications
└── docs/     # Project documentation
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

### v5.4.0 (2026-02-07) - Agent & Memory Edition

**New Agents (3)**:
- `code-reviewer`: Code review specialist with security-rules skill injection
- `tdd-runner`: Test execution specialist (Haiku model, project memory) with testing-rules injection
- `debugger`: Root cause analysis specialist with Edit capability

**Agent Memory**: All 5 agents now have persistent memory (`memory: user` or `memory: project`)
- Accumulates patterns, common issues, and architectural decisions across sessions
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
- All hooks: standardized error handling (catch → stderr log → safe pass-through)
- pre_stop_check: added git timeout, marker cleanup, error logging
- Reduced per-request token overhead (no more routing hook noise)

**Architecture**: CLAUDE.md + Commands + Quality Hooks (three-layer, no bloat)

### v5.2.2 (2026-01-29) - Codex Purification Edition

**CLAUDE.md Refactoring**:
- Removed operational config (moved to README)
- Removed specific library names
- Removed specific agent/skill names
- Result: 322 → 272 lines (-15%)
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
- Fix field names: `tool` → `tool_name`, `tool_result` → `tool_response`
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
- Smart contract files → BOTH specialist + auditor (MANDATORY)
- Auth/payment paths → pr-review-toolkit:code-reviewer (MANDATORY)
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
