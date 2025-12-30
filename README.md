# Ultra Builder Pro 4.3

<div align="center">

**Version 4.3.4 (Production Absolutism)**

*Production-Grade AI-Powered Development System for Claude Code + Codex*

---

[![Version](https://img.shields.io/badge/version-4.3.4-blue)](README.md#version-history)
[![Status](https://img.shields.io/badge/status-production--ready-green)](tests/verify-documentation-consistency.sh)
[![Skills](https://img.shields.io/badge/skills-14-orange)](skills/)
[![Dual-Engine](https://img.shields.io/badge/dual--engine-Claude%20%2B%20Codex-purple)](skills/codex-reviewer/SKILL.md)
[![Official Compliance](https://img.shields.io/badge/official-100%25%20native-brightgreen)](https://docs.claude.com/claude-code)

</div>

---

## Quick Start

### One-Command Install

```bash
# Clone the repository
git clone https://github.com/rocky2431/ultra-builder-pro.git
cd ultra-builder-pro

# Copy to Claude Code config directory
cp -r ./* ~/.claude/

# Start Claude Code
claude
```

**Installation Time**: < 1 minute

---

## What's New in 4.3.4

### 🔥 Production Absolutism (生产绝对主义)

> "There is no test code. There is no demo. There is no MVP.
> Every line is production code. Every test is production verification."

**Core Formula:**
```
Code Quality = Real Implementation × Real Tests × Real Dependencies
If ANY component is fake/mocked/simulated → Quality = 0
```

**Absolute Prohibitions:**

| Category | Prohibited Patterns | Consequence |
|----------|---------------------|-------------|
| **Mock/Simulation** | `jest.mock()`, `vi.mock()`, `jest.fn()`, `AsyncMock` | Immediate rejection |
| **Degradation** | Fallback logic, simplified implementations | Immediate rejection |
| **Static Data** | Hardcoded test data, inline fixtures | Immediate rejection |
| **Placeholders** | `TODO`, `FIXME`, `// placeholder`, `// demo` | Immediate rejection |
| **Test Cheating** | Tautologies, empty bodies, `.skip()` | Immediate rejection |
| **MVP Mindset** | "Good enough for now", partial implementations | Immediate rejection |

### 🛡️ ZERO MOCK Policy

Complete prohibition of mocking in all tests:

```typescript
// ❌ PROHIBITED - All mocking is banned
jest.mock('../services/UserService');
vi.mock('../utils/validator');
jest.fn().mockResolvedValue({});

// ✅ REQUIRED - Real implementations only
const db = createTestDatabase();        // Real in-memory DB
const gateway = createTestPaymentGateway(); // Real test gateway
const service = new PaymentService(db, gateway);
```

**TAS Formula Updated:**
- `real_data_score` (30%): 100 if no mocks, **0 if any mock detected**
- `assertion_quality_score` (35%): Behavioral assertions
- `real_execution_score` (20%): Real code path coverage
- `pattern_quality_score` (15%): No anti-patterns

### 🔧 Hook System Improvements

| Fix | Description |
|-----|-------------|
| **TypeScript Type Fix** | Added `requiresCodex` and `hookType` to `SkillRule` interface |
| **Permission Fix** | Fixed `chmod +r` for hook scripts (source requires read permission) |
| **Stop Hook Simplified** | Removed `codex-test-gen` from Stop hook (now command-only) |
| **Codex Detection** | Three-layer enforcement: Hook → SKILL.md → skill-rules.json |

**Codex Skill Trigger Mechanism:**

| Hook | Codex Skill | Trigger |
|------|-------------|---------|
| PostToolUse | codex-reviewer | Edit/Write code files |
| UserPromptSubmit | codex-doc-reviewer, codex-research-gen | Keywords |
| Command | codex-test-gen | `/ultra-test` only |

**Output Format:**
```
🔥 CODEX REQUIRED: codex-reviewer
⚠️ You MUST execute `codex exec` command. Manual analysis is NOT acceptable.
```

---

## What's New in 4.3.3

### 🌐 Bilingual Trigger Support (中英文触发)

All 14 skills now support **Chinese keyword triggers**:

| Skill | English | 中文 |
|-------|---------|------|
| **frontend** | frontend, React, component | 前端, 组件, 界面, 页面 |
| **backend** | backend, API, database | 后端, 接口, 数据库, 服务端 |
| **smart-contract** | contract, solidity, web3 | 合约, 智能合约, 区块链, DeFi |
| **guarding-quality** | refactor, code review | 重构, 代码审查, 质量 |
| **guarding-test-quality** | test, coverage, TAS | 测试, 覆盖率, 单元测试 |
| **guarding-git-workflow** | commit, push, merge | 提交, 推送, 合并, 分支 |
| **ultra-think** | trade-off, should we | 深度分析, 技术选型, 权衡 |

**Example Triggers:**

```bash
# These now trigger the same skills:
"帮我写个前端组件"     → frontend skill ✅
"Help me write a component" → frontend skill ✅

"后端接口设计"         → backend skill ✅
"Design backend API"   → backend skill ✅

"智能合约安全审计"     → smart-contract skill ✅
"Smart contract audit" → smart-contract skill ✅
```

### 📋 Detailed Skill Configs

Each skill now includes specialized configuration with Chinese translations:

| Skill | Config | Key Settings |
|-------|--------|--------------|
| **guarding-quality** | `qualityConfig` | SOLID原则, 函数≤50行, 嵌套≤3层, 圈复杂度≤10 |
| **guarding-test-quality** | `testConfig` | TAS≥70%, 覆盖率≥80%, Mock数量=0 (ZERO MOCK) |
| **guarding-git-workflow** | `gitConfig` | 危险命令拦截, Conventional Commits |
| **frontend** | `frontendConfig` | Core Web Vitals, WCAG 2.1 AA, 反模式列表 |
| **backend** | `backendConfig` | OWASP安全检查, 输入验证, N+1预防 |
| **smart-contract** | `contractConfig` | 7项安全检查, Fuzz测试, 不变量测试 |
| **ultra-think** | `analysisConfig` | 6D分析框架, 3-5个方案, 魔鬼代言人 |

### 🧠 Ultra-Think Skill (6D Analysis)

New dedicated skill for deep analysis:

```bash
/ultra-think "微服务还是单体架构?"
```

**6 Dimensions Analyzed:**
1. Technical (技术) - Architecture, scalability, security
2. Business (业务) - Cost, ROI, time-to-market
3. Team (团队) - Learning curve, velocity impact
4. Ecosystem (生态) - Community, library support
5. Strategic (战略) - Long-term sustainability
6. Meta (元层面) - Assumptions, paradigm shifts

---

## What's New in 4.3.2

### 🚀 Dual-Engine Collaborative Development

Ultra Builder Pro now supports **Claude Code + Codex** dual-engine collaboration:

```
Claude Code (Primary)          Codex (Reviewer)
      │                              │
      ├── Development ──────────────→│ Code Review
      │                              │ (bugs, security, performance)
      │←─────────────── Feedback ────┤
      │                              │
      ├── Tests ────────────────────→│ Test Generation
      │                              │ (edge cases, security tests)
      │←─────────────── New Tests ───┤
      │                              │
      ├── Documentation ────────────→│ Doc Enhancement
      │                              │ (examples, FAQ, best practices)
      │←─────────── Enhanced Docs ───┤
      │                              │
      └── Final Approval ────────────┘
```

**Key Features:**

| Feature | Description |
|---------|-------------|
| **Codex Code Review** | After every Edit/Write, Codex reviews for bugs, security, performance |
| **Stuck Detection** | If Claude Code fails same issue 3 times → Codex takes over fixing |
| **Role Swap** | Codex fixes → Claude Code reviews (bidirectional collaboration) |
| **Test Generation** | Codex generates comprehensive tests with 6D coverage |
| **Doc Collaboration** | Claude drafts → Codex reviews/enhances → Claude finalizes |

### New Codex Skills (10 → 14)

| Skill | Trigger | Function |
|-------|---------|----------|
| **codex-reviewer** | Edit/Write on code files | 100-point code review with 4 dimensions |
| **codex-test-gen** | Coverage gaps detected | 6-dimensional test generation with TAS |
| **codex-doc-reviewer** | Documentation updates | Review + enhancement with examples |
| **codex-research-gen** | /ultra-research, technology decisions | Evidence-based research with 90%+ confidence |

### New Hook: Codex Review Trigger

```
Edit/Write on .ts/.tsx/.js/.py/.go/...
       ↓
PostToolUse Hook triggers
       ↓
codex-review-trigger.sh activates
       ↓
Outputs: "🔍 CODEX REVIEW TRIGGERED"
       ↓
Auto-executes: scripts/review.sh (if CODEX_AUTO_REVIEW=true)
       ↓
Or suggests: `codex exec --json "Review {file}"`
```

### Codex CLI Integration (Official Syntax)

```bash
# Non-interactive execution (scripts use this)
codex exec --json "Review this code for bugs..."
codex exec "Generate tests for this file..."

# Enable auto-review after every Edit/Write
export CODEX_AUTO_REVIEW=true
```

Each Codex skill now includes executable scripts:

| Skill | Script | Usage |
|-------|--------|-------|
| codex-reviewer | `scripts/review.sh` | `./scripts/review.sh path/to/file.ts` |
| codex-test-gen | `scripts/generate.sh` | `./scripts/generate.sh src/service.ts` |
| codex-doc-reviewer | `scripts/review-docs.sh` | `./scripts/review-docs.sh docs/api.md --enhance` |
| codex-research-gen | `scripts/research.sh` | `./scripts/research.sh "React vs Vue"` |

### Stuck Detection & Role Swap

```
Normal Flow:
  Claude Code → implement → Codex review → pass ✅

Stuck Flow (same error 3x):
  Claude Code → fail → fail → fail
       ↓
  ⚠️ STUCK DETECTION ACTIVATED
       ↓
  Codex → fix attempt → Claude Code review → pass ✅
```

### Quality Score System

Codex reviews use 100-point scoring:

| Dimension | Weight | Checks |
|-----------|--------|--------|
| Correctness | 40% | Logic errors, null checks, race conditions |
| Security | 30% | Injection, XSS, CSRF, secrets exposure |
| Performance | 20% | N+1, memory leaks, complexity |
| Maintainability | 10% | Naming, complexity, coupling |

**Threshold**: Score ≥ 80/100 required to proceed

---

## System Overview

Ultra Builder Pro 4.3 is a **dual-engine AI-powered development workflow system** combining Claude Code and Codex.

### Core Features

- **Dual-Engine Collaboration**: Claude Code (dev) + Codex (review/test/docs)
- **Structured 7-Phase Workflow**: Standardized development process
- **14 Automated Skills**: Quality guards + domain expertise + **Codex integration**
- **2 Expert Agents**: Specialized sub-agents for architecture and performance
- **Stuck Detection**: Automatic role swap when blocked
- **2 MCP Integrations**: Context7 (docs) + Exa (code search)
- **Bilingual Support**: Chinese output, English system files

### Quantified Improvements (4.2.1 → 4.3.0)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Skills Count** | 10 | 14 | **+40%** (Codex skills) |
| **Code Review** | Manual | Automated (Codex) | **100% coverage** |
| **Test Generation** | Claude only | Claude + Codex | **6D coverage** |
| **Doc Quality** | Single pass | Dual-engine review | **Enhanced** |
| **Stuck Recovery** | Manual | Auto role swap | **Automated** |

---

## System Architecture

```
Ultra Builder Pro 4.3.2 (Dual-Engine)
│
├── CLAUDE.md                          # Single source of truth (config + principles)
│
├── settings.json                      # Claude Code settings
│   ├── permissions.allow              # Official tool permissions
│   ├── permissions.deny               # Sensitive file protection
│   └── hooks                          # UserPromptSubmit + PostToolUse hooks
│       ├── UserPromptSubmit           # skill-activation-prompt.sh
│       └── PostToolUse                # post-tool-use-tracker.sh + codex-review-trigger.sh
│
├── hooks/                             # Hook implementations
│   ├── skill-activation-prompt.ts     # Command-skill binding logic
│   ├── skill-activation-prompt.sh     # Hook shell wrapper
│   ├── post-tool-use-tracker.sh       # File modification tracker
│   └── codex-review-trigger.sh        # 🆕 Codex review auto-trigger
│
├── skills/                            # 14 Automated Skills (native + Codex)
│   ├── skill-rules.json               # Command-skill bindings + dualEngineConfig
│   │
│   │   # Guard Skills (Quality Enforcement)
│   ├── guarding-quality/              # SOLID principles + code quality
│   ├── guarding-test-quality/         # TAS + fake test detection
│   ├── guarding-git-workflow/         # Git safety + parallel workflow
│   │
│   │   # Sync Skills (Automation)
│   ├── syncing-docs/                  # Documentation sync
│   ├── syncing-status/                # Feature status tracking
│   ├── guiding-workflow/              # Workflow guidance
│   │
│   │   # Domain Skills (Expertise)
│   ├── frontend/                      # React/Vue/Next.js patterns
│   ├── backend/                       # Node.js/Python/Go patterns
│   ├── smart-contract/                # Solidity + Foundry patterns
│   ├── skill-creator/                 # Guide for creating skills
│   │
│   │   # 🆕 Codex Skills (Dual-Engine) - with scripts/
│   ├── codex-reviewer/                # Code review (100-point scoring)
│   │   └── scripts/review.sh          # CLI execution script
│   ├── codex-test-gen/                # Test generation (6D coverage)
│   │   └── scripts/generate.sh        # CLI execution script
│   ├── codex-doc-reviewer/            # Doc review + enhancement
│   │   └── scripts/review-docs.sh     # CLI execution script
│   └── codex-research-gen/            # Research with 90%+ confidence
│       └── scripts/research.sh        # CLI execution script
│
├── agents/                            # 2 Expert agents (Anthropic-compliant)
│   ├── ultra-architect-agent.md       # Architecture design (opus)
│   └── ultra-performance-agent.md     # Performance optimization (sonnet)
│   # Note: Research/QA → Codex Skills (codex-research-gen, codex-test-gen)
│
├── commands/                          # 8 Workflow commands (Dual-Engine enhanced)
│   ├── ultra-init.md                  # /ultra-init
│   ├── ultra-research.md              # /ultra-research
│   ├── ultra-plan.md                  # /ultra-plan
│   ├── ultra-dev.md                   # /ultra-dev + Codex feedback loop
│   ├── ultra-test.md                  # /ultra-test + Codex test generation
│   ├── ultra-deliver.md               # /ultra-deliver + Codex doc collaboration
│   ├── ultra-status.md                # /ultra-status
│   └── ultra-think.md                 # /ultra-think
│
├── config/                            # Tool configuration
│   ├── ultra-mcp-guide.md             # MCP decision tree
│   └── research/                      # Research templates
│
└── .ultra-template/                   # Project template
    ├── constitution.md                # Project principles
    ├── specs/                         # Specifications
    └── docs/                          # Documentation
```

---

## Core Workflow

### Standard 7-Phase Process

```
/ultra-init     → Initialize project structure
    ↓
/ultra-research → AI-assisted technical research
    ↓
/ultra-plan     → Task planning with dependency analysis
    ↓
/ultra-dev      → TDD development (RED-GREEN-REFACTOR)
    ↓
/ultra-test     → 6-dimensional testing
    ↓
/ultra-deliver  → Performance optimization + security audit
    ↓
/ultra-status   → Real-time progress + risk assessment
```

### Example Usage

```bash
# 1. Initialize project
/ultra-init my-app web react-ts git

# 2. Research
/ultra-research

# 3. Task planning
/ultra-plan

# 4. TDD development
/ultra-dev 1

# 5. Testing
/ultra-test

# 6. Delivery
/ultra-deliver

# 7. Status check
/ultra-status
```

---

## 14 Automated Skills

### Guard Skills (Quality Enforcement)

| Skill | Trigger | Function |
|-------|---------|----------|
| **guarding-quality** | Edit code files | SOLID principles + complexity limits |
| **guarding-test-quality** | Edit test files | TAS calculation + fake test detection |
| **guarding-git-workflow** | Git operations | Parallel workflow + conflict resolution |

### Sync Skills (Automation)

| Skill | Trigger | Function |
|-------|---------|----------|
| **syncing-docs** | Feature completion | Documentation sync reminders |
| **syncing-status** | Task/test completion | Feature status tracking |
| **guiding-workflow** | Phase completion | Next-step suggestions |

### Domain Skills (Specialized Expertise)

| Skill | Trigger | Function |
|-------|---------|----------|
| **frontend** | React/Vue/Next.js code | Component patterns, Core Web Vitals, accessibility |
| **backend** | API/DB/server code | Express/FastAPI/Gin patterns, OWASP security |
| **smart-contract** | Solidity code | Security audit, gas optimization, Foundry tests |
| **skill-creator** | Creating new skills | Skill structure guide, packaging scripts |

### 🆕 Codex Skills (Dual-Engine Collaboration)

| Skill | Trigger | Function |
|-------|---------|----------|
| **codex-reviewer** | Edit/Write on code files | 100-point code review (correctness, security, performance, maintainability) |
| **codex-test-gen** | Coverage < 80% or gaps detected | 6-dimensional test generation with TAS validation |
| **codex-doc-reviewer** | Documentation updates | Review + enhancement (examples, FAQ, best practices) |
| **codex-research-gen** | /ultra-research, tech decisions | Evidence-based research with 90%+ confidence requirement |

### Command-Skill Binding (Hook-Based Auto-Activation)

```
User runs /ultra-dev
       ↓
UserPromptSubmit Hook triggers
       ↓
skill-activation-prompt.ts detects command
       ↓
Loads bound skills from skill-rules.json
       ↓
Outputs: "🚀 SKILLS AUTO-ACTIVATED for /ultra-dev"
       ↓
Claude + Codex follow skill specifications
```

**Command-Skill Bindings (Dual-Engine):**

| Command | Auto-Activated Skills |
|---------|----------------------|
| `/ultra-dev` | guarding-quality, guarding-git-workflow, guarding-test-quality, **codex-reviewer** |
| `/ultra-test` | guarding-test-quality, guarding-quality, **codex-test-gen** |
| `/ultra-deliver` | syncing-docs, syncing-status, guarding-quality, **codex-doc-reviewer** |
| `/ultra-status` | syncing-status, guiding-workflow |
| `/ultra-research` | syncing-docs, guiding-workflow, **codex-research-gen** |
| `/ultra-plan` | guarding-quality |
| `/ultra-think` | guiding-workflow |

Skills also activate via keyword/file triggers for non-command contexts.

**Bilingual Keyword Support:**

Skills can now be triggered in both English and Chinese:

```
User: "帮我重构这段代码"
       ↓
Hook detects "重构" keyword
       ↓
guarding-quality skill activated ✅

User: "前端性能优化"
       ↓
Hook detects "前端" keyword
       ↓
frontend skill activated ✅
```

### PostToolUse Hook: Codex Review Trigger

After Edit/Write on code files (`.ts`, `.tsx`, `.js`, `.py`, `.go`, etc.):

```
codex-review-trigger.sh
       ↓
Detects code file modification
       ↓
CODEX_AUTO_REVIEW=true?
       ├─ Yes → Auto-execute scripts/review.sh (background)
       └─ No  → Output reminder with command
       ↓
Tracks error history for stuck detection
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `CODEX_AUTO_REVIEW` | `false` | Enable automatic review after Edit/Write |
| `CODEX_MIN_SCORE` | `80` | Minimum score to pass review |
| `CODEX_TIMEOUT` | `120` | Timeout in seconds |

---

## 2 Expert Agents

| Agent | Model | Purpose | Trigger |
|-------|-------|---------|---------|
| **ultra-architect-agent** | opus | System design with SOLID compliance scoring | complexity ≥ 7 |
| **ultra-performance-agent** | sonnet | Core Web Vitals optimization | /ultra-deliver |

> **Note**: Research and QA functions now handled by Codex Skills:
> - `codex-research-gen` replaces ultra-research-agent (90%+ confidence)
> - `codex-test-gen` replaces ultra-qa-agent (6D coverage + TAS validation)

---

## 2 MCP Integrations

### Decision Tree

```
Need specialized capabilities?
    ├─ Official docs → Context7 MCP
    ├─ Code examples → Exa MCP (AI semantic search)
    └─ General use → Built-in tools (Read/Write/Edit/Grep)
```

### Available MCP Servers

| Server | Purpose | Tools |
|--------|---------|-------|
| **context7** | Library documentation | `resolve-library-id`, `get-library-docs` |
| **exa** | AI semantic search | `web_search_exa`, `get_code_context_exa` |

---

## Quality Gates

All gates defined in CLAUDE.md (single source):

| Gate | Requirement |
|------|-------------|
| TDD | RED → GREEN → REFACTOR mandatory |
| Coverage | ≥80% overall, 100% critical paths |
| TAS | ≥70% Test Authenticity Score |
| SOLID | Full compliance enforced |
| Git | Parallel branches → rebase → merge → delete |

---

## Installation

### Method 1: Git Clone (Recommended)

```bash
git clone https://github.com/rocky2431/ultra-builder-pro.git
cd ultra-builder-pro
cp -r ./* ~/.claude/
```

### Method 2: Download ZIP

```bash
# Download and extract, then:
cp -r Ultra-Builder-Pro-4.2/* ~/.claude/
```

### Verification

```bash
# Check Skills (should be 10)
ls ~/.claude/skills/ | wc -l

# Check Commands (should be 8)
ls ~/.claude/commands/ | wc -l

# Start Claude Code
claude
/ultra-status
```

---

## Version History

### v4.3.4 (2025-12-30) - Production Absolutism 🔥

- **Production Absolutism**: Core principle - no mock/demo/MVP, every line is production code
- **ZERO MOCK Policy**: Complete prohibition of all mocking (jest.mock, vi.mock, jest.fn)
- **TAS Formula Update**: `real_data_score` replaces `mock_ratio_score`, any mock = 0 score
- **Hook TypeScript Fix**: Added `requiresCodex` and `hookType` to `SkillRule` interface
- **Hook Permission Fix**: Fixed script permissions for `source` command
- **Stop Hook Simplified**: Removed `codex-test-gen` from Stop hook (command-only trigger)
- **Three-Layer Enforcement**: Hook output → SKILL.md CRITICAL block → skill-rules.json
- **Components Updated**: CLAUDE.md, ultra-think, ultra-dev, guarding-quality, guarding-test-quality, codex-reviewer, codex-test-gen

### v4.3.3 (2025-12-30) - Bilingual Trigger Support 🌐

- **Chinese Keywords**: All 14 skills now support Chinese keyword triggers
- **Ultra-Think Skill**: New skill with 6D analysis framework configuration
- **Detailed Configs**: Added `qualityConfig`, `testConfig`, `gitConfig`, etc. to each skill
- **Chinese Translations**: All config descriptions have `_zh` translations
- **Domain Keywords**: frontend/backend/smart-contract trigger with single keywords (前端/后端/合约)
- **Intent Patterns**: Bilingual regex patterns for natural language matching

### v4.3.2 (2025-12-30) - Codex CLI Integration & Official Standards 🚀

- **Codex CLI Fix**: Corrected syntax from `codex -q` to official `codex exec`
- **scripts/ Directory**: Each Codex skill now has executable scripts per skill-creator standard
- **Auto-Review Toggle**: `CODEX_AUTO_REVIEW=true` enables automatic review after Edit/Write
- **SKILL.md Optimization**: Aligned with official skill-creator standards (third-person descriptions)
- **Guidelines Consolidation**: Merged guidelines/ into skills/ (single source of truth)
- **Hook Enhancement**: codex-review-trigger.sh supports auto-execution mode

### v4.3.0 (2025-12-30) - Dual-Engine Collaborative Development

- **Claude Code + Codex**: Dual-engine collaboration system
- **4 New Codex Skills**: codex-reviewer, codex-test-gen, codex-doc-reviewer, codex-research-gen
- **Codex Review Hook**: Auto-trigger after Edit/Write on code files
- **Stuck Detection**: Auto role swap when same error repeated 3 times
- **100-Point Scoring**: Codex code review with 4-dimensional analysis
- **6D Test Generation**: Codex generates comprehensive tests
- **Doc Collaboration**: Claude drafts → Codex reviews/enhances → Claude finalizes
- **Commands Enhanced**: ultra-dev, ultra-test, ultra-deliver with Codex integration

### v4.2.1 (2025-12-30) - Command-Skill Binding System

- **Hook-Based Activation**: UserPromptSubmit hook triggers skill auto-activation
- **Command Bindings**: `/ultra-dev` → `[guarding-quality, guarding-git-workflow, guarding-test-quality]`
- **skill-rules.json**: New config for command-skill mappings + keyword/file triggers
- **Workflow Integration**: Skills now truly integrated into command execution
- **New Command**: `/ultra-think` for 6-dimensional deep analysis

### v4.2.0 (2025-12-28) - Anthropic Compliance + Domain Skills

- **Prompt Engineering**: All prompts rewritten following Anthropic best practices
- **Intellectual Honesty**: New framework for principled pushback
- **Parallel Development**: Git workflow supporting concurrent task execution
- **Single Source**: Removed config.json, consolidated to CLAUDE.md
- **Domain Skills**: Added frontend, backend, smart-contract, skill-creator (6 → 10)
- **Separation of Concerns**: guarding-quality → principles only, implementation → domain skills
- **Agent Optimization**: -71% verbosity (QA agent 441 → 128 lines)
- **Positive Framing**: Eliminated negative instruction patterns

### v4.1.4 (2025-12-20) - Native Skills Optimization

- **Native Activation**: Removed `skill-rules.json` and `skill-activation` hook
- **Enhanced Descriptions**: All SKILL.md files have comprehensive trigger conditions
- **Agent Upgrade**: Explicit model selection + permissionMode
- **Performance**: ~200ms faster skill activation

### v4.1.3 (2025-12-17) - Anti-Fake-Test System

- **TAS System**: Test Authenticity Score for fake test detection
- **Skills Expansion**: 6 → 8 Skills
- **TDD Hardening**: Removed all bypass options

### v4.1.2 (2025-12-07) - Security & Design Enhancement

- **Security**: `permissions.deny` for sensitive file protection
- **Modular**: `@import` syntax in CLAUDE.md

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Skills not triggering | Description mismatch | Check SKILL.md description field |
| Commands unavailable | Commands missing | Re-copy commands/ directory |
| MCP errors | Server not configured | Check `claude mcp list` |

---

## Documentation

### Essential Reading

1. **This README** - System overview (5 min)
2. **[CLAUDE.md](CLAUDE.md)** - Core configuration and principles

### Reference

- **[MCP Guide](config/ultra-mcp-guide.md)** - MCP decision tree
- **[Code Quality](skills/guarding-quality/SKILL.md)** - SOLID/DRY/KISS/YAGNI + Production Absolutism
- **[Test Quality](skills/guarding-test-quality/SKILL.md)** - TAS + ZERO MOCK Policy
- **[Codex Reviewer](skills/codex-reviewer/SKILL.md)** - 100-point code review

---

## Support

- **GitHub**: https://github.com/rocky2431/ultra-builder-pro
- **Official Docs**: https://docs.claude.com/claude-code

---

<div align="center">

**Ultra Builder Pro 4.3.4** - Production Absolutism Edition

*Claude Code + Codex: No mock. No demo. No MVP. Production-grade only.*

[MCP Guide](config/ultra-mcp-guide.md) | [Codex Reviewer](skills/codex-reviewer/SKILL.md) | [Quality Guard](skills/guarding-quality/SKILL.md) | [Test Guard](skills/guarding-test-quality/SKILL.md)

</div>
