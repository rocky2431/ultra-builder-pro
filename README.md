# Ultra Builder Pro 4.4

<div align="center">

**Production-Grade AI-Powered Development System for Claude Code**

---

[![Version](https://img.shields.io/badge/version-4.5.0-blue)](README.md#version-history)
[![Status](https://img.shields.io/badge/status-production--ready-green)](README.md)
[![Commands](https://img.shields.io/badge/commands-8-purple)](commands/)
[![Skills](https://img.shields.io/badge/skills-4-orange)](skills/)
[![Agents](https://img.shields.io/badge/agents-6-red)](agents/)

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

## Commands (8)

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `/ultra-init` | Initialize project | Auto-detect type/stack, copy templates, git setup |
| `/ultra-research` | Interactive discovery | 4 rounds (User→Feature→Architecture→Quality), 90%+ confidence |
| `/ultra-plan` | Task planning | Dependency analysis, complexity assessment, context files |
| `/ultra-dev` | TDD development | RED→GREEN→REFACTOR, Codex review, auto git flow |
| `/ultra-test` | Quality audit | Anti-Pattern detection, Coverage gaps, E2E, Performance, Security |
| `/ultra-deliver` | Release preparation | CHANGELOG, build, version bump, tag, push |
| `/ultra-status` | Progress monitoring | Real-time stats, risk analysis, recommendations |
| `/ultra-think` | Deep analysis | Structured reasoning, multi-dimension comparison |

### Command Details

#### /ultra-init
- Auto-detects project type (web/api/cli/fullstack)
- Auto-detects tech stack from dependencies
- Creates `.ultra/` structure with specs and tasks
- Interactive confirmation for existing projects

#### /ultra-research
- **Round 1**: User & Scenario (Personas, User Scenarios)
- **Round 2**: Feature Definition (User Stories, Features, Metrics)
- **Round 3**: Architecture Design (arc42 §1-6)
- **Round 4**: Quality & Deployment (arc42 §7-12)
- Each round: 6-step cycle with satisfaction rating (≥4 stars to continue)

#### /ultra-dev
- TDD workflow: RED (failing tests) → GREEN (pass) → REFACTOR
- Git branch management with decision tree
- Mandatory Codex review before commit
- Dual-write mode: update specs when implementation reveals gaps

#### /ultra-test
- **Anti-Pattern Detection**: Tautology, empty tests, core logic mocks
- **Coverage Gap Analysis**: Find untested exported functions
- **E2E Testing**: Chrome MCP for web UI
- **Performance**: Core Web Vitals (LCP <2.5s, INP <200ms, CLS <0.1)
- **Security**: Dependency vulnerability scan
- Auto-fix loop (max 5 attempts)

---

## Skills (4)

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| `codex` | OpenAI Codex CLI | Code analysis, refactoring, **can modify code** |
| `gemini` | Google Gemini CLI | Research, validation, docs; `-y` for code changes |
| `senior-prompt-engineer` | Prompt engineering | LLM optimization, prompt patterns, RAG, agent design |
| `skill-creator` | Create new skills | Workflow guidance, packaging |

### Codex Skill

**Templates**:
- `research-review`: Validate research output (read-only)
- `code-review`: Review code diff (read-only, high effort)
- `test-review`: Audit test suite (workspace-write)

**Config**: Model `gpt-5.2-codex`, Effort `medium`, Sandbox `workspace-write`

### Gemini Skill

**Templates**:
- `tech-research`: Deep research with evidence
- `architecture-review`: Validate architecture decisions
- `documentation-gen`: Generate/review documentation
- `spec-validation`: Validate implementation vs spec
- `code-review`: Review code (read-only by default)

**Config**: Model `gemini-3-flash-preview`, Mode `suggest` (read-only default)

**Note**: Use `-y` flag for auto-approve when code changes needed

### Senior Prompt Engineer Skill

World-class prompt engineering for production AI systems:
- **Prompt Patterns**: Advanced prompting techniques, few-shot, CoT
- **LLM Evaluation**: Frameworks for assessing model performance
- **Agentic Design**: Multi-agent orchestration patterns
- **RAG Optimization**: Retrieval-augmented generation best practices

**Resources**: `references/prompt_engineering_patterns.md`, `references/llm_evaluation_frameworks.md`, `references/agentic_system_design.md`

---

## Agents (6)

Specialized agents for domain-specific tasks (all inherit full toolset):

| Agent | Purpose |
|-------|---------|
| `backend-architect` | Backend system architecture, API design |
| `frontend-developer` | React/Next.js, UI components, performance |
| `smart-contract-auditor` | Security audits, vulnerability detection |
| `smart-contract-specialist` | Solidity development, gas optimization |
| `ui-ux-designer` | User research, wireframes, design systems |
| `web3-integration-specialist` | Wallet integration, dApp development |

### Usage

Agents are invoked automatically by the Task tool based on task requirements:
- Backend/API design → `backend-architect`
- React/UI development → `frontend-developer`
- Smart contract security → `smart-contract-auditor`
- Smart contract development → `smart-contract-specialist`
- UI/UX design → `ui-ux-designer`
- Web3/dApp development → `web3-integration-specialist`

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
| Codex Review | No critical issues |

### Code Limits

| Metric | Limit |
|--------|-------|
| Function lines | ≤ 50 |
| Nesting depth | ≤ 3 |
| Cyclomatic complexity | ≤ 10 |

### Testing Policy

| Type | Mock Allowed? |
|------|---------------|
| Core Logic (domain/service/state) | **NO** |
| Repository interfaces | **NO** (use testcontainers) |
| External APIs | Yes (testcontainers/sandbox/stub) |
| Third-party services | Yes (with rationale) |

---

## Project Structure

```
~/.claude/
├── CLAUDE.md                 # Main configuration (Priority Stack)
├── README.md                 # This file
├── settings.json             # Claude Code settings
│
├── commands/                 # /ultra-* commands (8)
│   ├── ultra-init.md
│   ├── ultra-research.md
│   ├── ultra-plan.md
│   ├── ultra-dev.md
│   ├── ultra-test.md
│   ├── ultra-deliver.md
│   ├── ultra-status.md
│   └── ultra-think.md
│
├── skills/                   # Domain skills (4)
│   ├── codex/                # OpenAI Codex CLI
│   ├── gemini/               # Google Gemini CLI
│   ├── senior-prompt-engineer/ # LLM & prompt engineering
│   └── skill-creator/        # Create new skills
│
├── agents/                   # Specialized agents (6)
│   ├── backend-architect.md
│   ├── frontend-developer.md
│   ├── smart-contract-auditor.md
│   ├── smart-contract-specialist.md
│   ├── ui-ux-designer.md
│   └── web3-integration-specialist.md
│
└── .ultra-template/          # Project initialization templates
    ├── specs/
    │   ├── product.md        # Product specification template
    │   └── architecture.md   # arc42 architecture template
    ├── tasks/
    │   ├── tasks.json        # Task registry
    │   └── contexts/         # Task context files
    └── docs/
        └── research/         # Research reports
```

---

## Version History

### v4.5.0 (2026-01-07) - Agent Architecture Edition

**Skills Refactoring**:
- Removed `backend`, `frontend`, `smart-contract` domain skills
- Added `senior-prompt-engineer` skill for LLM/prompt engineering

**New Agent System (6 agents)**:
- `backend-architect`: Backend system architecture, API design
- `frontend-developer`: React/Next.js, UI components, performance
- `smart-contract-auditor`: Security audits, vulnerability detection
- `smart-contract-specialist`: Solidity development, gas optimization
- `ui-ux-designer`: User research, wireframes, design systems
- `web3-integration-specialist`: Wallet integration, dApp development

**Plugin Changes**:
- Added: `secrets-scanner`, `typescript-lsp`, `pyright-lsp`, `gopls-lsp`
- Removed: `commit-commands`, `code-review`, `hookify`

### v4.4.0 (2026-01-01) - Streamlined Edition

**Core Changes**:
- Unified Priority Stack in CLAUDE.md
- Removed agents directory (empty)
- Removed hooks system
- Removed install.sh, execution_config.json
- Removed plans/, plugins/, chrome/, telemetry/

**Codex Integration**:
- Added `codex` skill with 3 review templates
- Mandatory Codex review in `/ultra-dev`, `/ultra-test`, `/ultra-research`

**Gemini Integration**:
- Added `gemini` skill with 5 templates
- Default read-only mode, `-y` for code changes

**Command Refinements**:
- `/ultra-test`: Anti-Pattern Detection (replaced TAS scoring)
- `/ultra-dev`: Git branch decision tree
- `/ultra-research`: 4-round interactive discovery with satisfaction rating

### v4.3.x (2025-12)

- Production Absolutism enforcement
- ZERO MOCK policy for core logic

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
