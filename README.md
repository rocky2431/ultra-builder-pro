# Ultra Builder Pro 4.1

<div align="center">

**Version 4.1.3 (Production Ready)**

*Production-Grade AI-Powered Development System for Claude Code*

---

[![Version](https://img.shields.io/badge/version-4.1.3-blue)](docs/CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-production--ready-green)](tests/verify-documentation-consistency.sh)
[![Skills](https://img.shields.io/badge/skills-8-orange)](config/ultra-skills-guide.md)
[![Official Compliance](https://img.shields.io/badge/official-compliant-brightgreen)](https://docs.claude.com/claude-code)

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

## What's New in 4.1.3

### 1. Anti-Fake-Test System (TAS)

- **Test Authenticity Score (TAS)**: Static analysis system to detect fake/useless tests
- **New Skill**: `guarding-test-quality` - Detects tautologies, empty tests, over-mocking
- **Quality Gate**: TAS ≥70% required for task completion (Grade A/B pass, C/D/F blocked)
- **10 Anti-Patterns**: Documented with BAD/GOOD code examples

### 2. Skills Expansion (6 → 8)

- **guarding-test-quality**: TAS calculation, fake test detection
- **syncing-status**: Feature status tracking (task completion + test results)

### 3. TDD Workflow Hardening

- **Removed**: All bypass options (skip-tests, no-branch, skip-refactor)
- **Added**: State machine validation (RED → GREEN → REFACTOR → COMMIT)
- **Added**: 6 mandatory quality gates (G1-G6)

### 4. Testing Philosophy Documentation

- **New File**: `guidelines/ultra-testing-philosophy.md`
- **Core Principle**: "Test Behavior, Not Implementation"
- **Mock Policy**: Clear boundary definitions (External=YES, Internal=NO)

---

## What's New in 4.1.2

### 1. Enhanced Security with permissions.deny

- **Sensitive File Protection**: Auto-block reading `.env`, `secrets/`, `credentials*` files
- **Pattern Matching**: Glob-style rules for comprehensive coverage
- **Zero Configuration**: Works out-of-the-box after installation

### 2. @import Modular References

- **CLAUDE.md Enhancement**: Added `@path/to/file` imports for modular loading
- **Referenced Modules**: Skills guide, MCP guide, Quality standards, Git workflow, SOLID principles
- **Benefit**: Clearer organization while maintaining full content

### 3. UI Design Guidelines Enhanced

- **Recommended Component Libraries**: shadcn/ui, Galaxy UI, React Bits (primary)
- **Design Thinking**: Purpose → Tone → Differentiation workflow
- **Anti-Patterns**: Enhanced enforcement (default fonts, hard-coded colors, cookie-cutter layouts)
- **Best Practices**: Typography, color systems, motion, spatial composition, backgrounds

### 4. Sandbox Mode (Optional)

- **Isolation Support**: File system and network isolation for bash execution
- **Configuration**: Set `sandbox.enabled: true` in settings.json
- **Use Case**: High-security environments requiring containerized execution

### 5. CLAUDE.local.md Template

- **Personal Preferences**: Template for project-local personal settings
- **Git-ignored**: Auto-added to .gitignore, not shared with team
- **Location**: `.ultra-template/CLAUDE.local.md`

---

## System Overview

Ultra Builder Pro 4.1 is a **complete AI-powered development workflow system** designed for Claude Code.

### Core Features

- **Structured 7-Phase Workflow**: Standardized development process
- **8 Automated Skills**: Real-time quality guards with auto-activation
- **Modular Documentation**: On-demand loading
- **Specialized Tools**: 4 Expert Agents + 2 MCP servers
- **Token Efficient**: Optimized for minimal context usage
- **Bilingual Support**: Chinese output, English system files
- **Trigger Logging**: Debug and optimize skill activation

### Quantified Improvements (4.1.0 → 4.1.1)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Skills Count** | 11 | 6 | **-45%** |
| **Skill Tokens** | ~2,350 | ~1,300 | **-45%** |
| **Research Config Files** | 7 | 4 | **-43%** |
| **Research Config Lines** | ~2,870 | ~2,090 | **-27%** |
| **Official Compliance** | Partial | 100% | **+100%** |

---

## System Architecture

```
Ultra Builder Pro 4.1.2
│
├── CLAUDE.md                          # Main config with @import references
│
├── settings.json                      # Claude Code settings (in .gitignore)
│   ├── permissions.allow              # Official tool permissions
│   ├── permissions.deny               # Sensitive file protection
│   └── sandbox                        # Optional isolation mode
│
├── guidelines/                        # Development guidelines
│   ├── ultra-solid-principles.md      # SOLID/DRY/KISS/YAGNI
│   ├── ultra-quality-standards.md     # Quality baselines
│   ├── ultra-git-workflow.md          # Git workflow
│   └── ultra-testing-philosophy.md    # Testing philosophy + anti-patterns (NEW)
│
├── config/                            # Tool configuration
│   ├── ultra-skills-guide.md          # 8 Skills guide
│   ├── ultra-mcp-guide.md             # MCP decision tree
│   └── research/                      # Research modes (4 files)
│       ├── interaction-points-core.md # Core questions
│       ├── mode-1-discovery.md        # Full workflow
│       ├── metadata-schema.md         # Quality metrics
│       └── research-quick-reference.md # Quick reference
│
├── workflows/                         # Workflow processes
│   ├── ultra-development-workflow.md  # 7-phase complete flow
│   └── ultra-context-management.md    # Token optimization
│
├── skills/                            # 8 Automated Skills (gerund naming)
│   ├── guarding-quality/              # Code + 6D coverage + UI
│   ├── guarding-test-quality/         # TAS + fake test detection (NEW)
│   ├── guarding-git-workflow/         # Git safety + workflow
│   ├── syncing-docs/                  # Documentation sync
│   ├── syncing-status/                # Feature status tracking (NEW)
│   ├── automating-e2e-tests/          # E2E automation
│   ├── compressing-context/           # Context compression
│   ├── guiding-workflow/              # Workflow guidance
│   └── skill-rules.json               # Auto-activation config
│
├── hooks/                             # Auto-activation hooks
│   ├── skill-activation-prompt.ts     # UserPromptSubmit hook
│   └── post-tool-use-tracker.sh       # PostToolUse hook
│
├── logs/                              # Skill trigger logs (NEW)
│   └── skill-triggers.jsonl           # JSONL format logs
│
├── agents/                            # 4 Expert agents
│   ├── ultra-research-agent.md        # Technical research
│   ├── ultra-architect-agent.md       # Architecture design
│   ├── ultra-performance-agent.md     # Performance optimization
│   └── ultra-qa-agent.md              # Test strategy
│
├── commands/                          # 9 Workflow commands
│   ├── ultra-init.md                  # /ultra-init
│   ├── ultra-research.md              # /ultra-research
│   ├── ultra-plan.md                  # /ultra-plan
│   ├── ultra-dev.md                   # /ultra-dev
│   ├── ultra-test.md                  # /ultra-test
│   ├── ultra-deliver.md               # /ultra-deliver
│   ├── ultra-status.md                # /ultra-status
│   ├── max-think.md                   # /max-think
│   └── ultra-session-reset.md         # /ultra-session-reset
│
└── .ultra-template/                   # Project template
    ├── config.json                    # Configuration SSOT
    ├── constitution.md                # Project principles
    ├── specs/                         # Specifications
    ├── docs/                          # Documentation
    └── context-archive/               # Session archives
```

---

## Core Workflow

### Standard 7-Phase Process

```
/ultra-init     → Initialize project structure
    ↓
/ultra-research → AI-assisted technical research (Scenario B routing)
    ↓
/ultra-plan     → Task planning with dependency analysis
    ↓
/ultra-dev      → TDD development (RED-GREEN-REFACTOR)
    ↓
/ultra-test     → 6-dimensional testing + Core Web Vitals
    ↓
/ultra-deliver  → Performance optimization + security audit
    ↓
/ultra-status   → Real-time progress + risk assessment
```

### Example Usage

```bash
# 1. Initialize project
/ultra-init my-app web react-ts git

# 2. Research (Scenario B - auto-detects project type)
/ultra-research
# → New Project: Full 4-round discovery (70 min)
# → Incremental Feature: Rounds 2-3 only (30 min)
# → Tech Decision: Round 3 only (15 min)

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

## 8 Automated Skills

### Skills Overview

| Skill | Trigger | Function |
|-------|---------|----------|
| **guarding-quality** | Edit code/tests/UI | SOLID + 6D coverage + UI design |
| **guarding-test-quality** | Edit test files | TAS calculation + fake test detection |
| **guarding-git-workflow** | Git operations | Git safety + workflow enforcement |
| **syncing-docs** | Feature completion | Documentation sync reminders |
| **syncing-status** | Task/test completion | Feature status tracking |
| **automating-e2e-tests** | Playwright mention | E2E test code generation |
| **compressing-context** | >120K tokens | Proactive context compression |
| **guiding-workflow** | Phase completion | Next-step suggestions |

### Auto-Activation Flow

```
User Prompt → UserPromptSubmit Hook → skill-rules.json → Match → Suggest skills
                                            ↓
                                    Log to skill-triggers.jsonl
```

**Complete guide**: See `config/ultra-skills-guide.md`

---

## 2 MCP Integrations

### Decision Tree

```
Need to operate code?
    ↓
Can built-in tools handle? (Read/Write/Edit/Grep)
    ├─ YES → Use built-in (fastest)
    └─ NO ↓

Need specialized capabilities?
    ├─ Official docs → Context7 MCP
    ├─ Code examples → Exa MCP (AI semantic search)
    └─ General use → Built-in tools
```

### Available MCP Servers

| Server | Purpose | Tools |
|--------|---------|-------|
| **context7** | Library documentation | `resolve-library-id`, `get-library-docs` |
| **exa** | AI semantic search | `web_search_exa`, `get_code_context_exa` |

**Complete guide**: See `config/ultra-mcp-guide.md`

---

## Configuration

### settings.json (Official Format)

```json
{
  "permissions": {
    "allow": [
      "Bash", "WebSearch", "WebFetch", "Grep", "Glob",
      "Read", "Write", "Edit", "NotebookEdit", "Task",
      "Skill", "SlashCommand", "TodoWrite", "AskUserQuestion",
      "BashOutput", "KillShell", "ExitPlanMode", "mcp__*"
    ],
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)",
      "Read(./**/credentials*)", "Read(./**/*secret*)"
    ]
  },
  "sandbox": {
    "enabled": false,
    "_comment": "Set to true for sandboxed bash execution"
  },
  "hooks": {
    "UserPromptSubmit": [...],
    "PostToolUse": [...]
  }
}
```

### Project Config (.ultra/config.json)

```json
{
  "context": {
    "total_limit": 200000,
    "thresholds": { "green": 0.60, "yellow": 0.70, "orange": 0.85 }
  },
  "quality_gates": {
    "test_coverage": { "overall": 0.80, "critical_paths": 1.00 }
  }
}
```

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
cp -r Ultra-Builder-Pro-4.1/* ~/.claude/
```

### Verification

```bash
# Check Skills (should be 8)
ls ~/.claude/skills/ | grep -v "skill-rules\|DEPRECATION\|\.DS_Store" | wc -l

# Check gerund naming
ls ~/.claude/skills/
# Expected: All end with -ing (guarding-*, syncing-*, automating-*, compressing-*, guiding-*)

# Start Claude Code
claude
/ultra-status
```

---

## Version History

### v4.1.3 (2025-12-17) - Anti-Fake-Test System

- **TAS System**: Test Authenticity Score for fake test detection
- **Skills Expansion**: 6 → 8 Skills (+guarding-test-quality, +syncing-status)
- **TDD Hardening**: Removed all bypass options, added state machine validation
- **Testing Philosophy**: New guidelines with 10 anti-patterns and examples
- **Quality Gates**: 6 mandatory gates (G1-G6) with TAS ≥70% requirement

### v4.1.2 (2025-12-07) - Security & Design Enhancement

- **Security**: `permissions.deny` for sensitive file protection
- **Modular**: `@import` syntax in CLAUDE.md for clearer organization
- **UI Design**: Enhanced guidelines with shadcn/Galaxy/React Bits recommendations
- **Sandbox**: Optional containerized bash execution support
- **Templates**: CLAUDE.local.md for personal project preferences

### v4.1.1 (2025-11-28) - Optimization Release

- **Official Compliance**: `alwaysAllowTools` → `permissions.allow`
- **Skills Consolidation**: 11 → 6 Skills (-45% tokens)
- **Trigger Logging**: New `skill-triggers.jsonl` for debugging
- **Research Config**: 7 → 4 files (-27% lines)
- **Code Cleanup**: ~9,700 lines removed

### v4.1.0 (2025-11-17) - Production Ready

- Skills system overhaul (gerund naming)
- Scenario B intelligent routing
- Configuration system (config.json SSOT)
- 100% documentation consistency

### v4.0.1 (2025-10-28) - Modular Edition

- Modular refactoring
- Token consumption reduced by 28.6%

**Complete Changelog**: See [docs/CHANGELOG.md](docs/CHANGELOG.md)

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Skills not triggering | skill-rules.json missing | Re-copy skills/ directory |
| Commands unavailable | Commands missing | Re-copy commands/ directory |
| MCP errors | Server not configured | Check `claude mcp list` |
| High token usage | Context not compressed | Run compressing-context skill |

### Debug Skill Triggers

```bash
# View recent skill triggers
tail -20 ~/.claude/logs/skill-triggers.jsonl | jq .

# Count triggers by skill
cat ~/.claude/logs/skill-triggers.jsonl | jq -r '.skill' | sort | uniq -c
```

---

## Documentation

### Essential Reading

1. **This README** - System overview (5 min)
2. **[Quick Start](ULTRA_BUILDER_PRO_4.1_QUICK_START.md)** - Getting started (10 min)
3. **[Development Workflow](workflows/ultra-development-workflow.md)** - 7-phase guide (30 min)

### Reference

- **[Skills Guide](config/ultra-skills-guide.md)** - All 8 Skills detailed
- **[MCP Guide](config/ultra-mcp-guide.md)** - MCP decision tree
- **[SOLID Principles](guidelines/ultra-solid-principles.md)** - Code quality
- **[Git Workflow](guidelines/ultra-git-workflow.md)** - Branching strategy
- **[Testing Philosophy](guidelines/ultra-testing-philosophy.md)** - Anti-patterns + TAS

---

## Support

- **GitHub**: https://github.com/rocky2431/ultra-builder-pro
- **Official Docs**: https://docs.claude.com/claude-code

---

<div align="center">

**Ultra Builder Pro 4.1.3** - Production-Grade Claude Code Development System

*Every line of code, rigorously crafted*

[Quick Start](ULTRA_BUILDER_PRO_4.1_QUICK_START.md) | [Skills Guide](config/ultra-skills-guide.md) | [MCP Guide](config/ultra-mcp-guide.md)

</div>
