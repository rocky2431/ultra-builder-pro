# Ultra Builder Pro 4.1

<div align="center">

**Version 4.1.1 (Production Ready)**

*Production-Grade AI-Powered Development System for Claude Code*

---

[![Version](https://img.shields.io/badge/version-4.1.1-blue)](docs/CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-production--ready-green)](tests/verify-documentation-consistency.sh)
[![Skills](https://img.shields.io/badge/skills-6-orange)](config/ultra-skills-guide.md)
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

## What's New in 4.1.1

### 1. Official Compliance Migration

- **`permissions.allow`**: Migrated from undocumented `alwaysAllowTools` to official format
- **Settings Schema**: 100% compliant with Claude Code official documentation

### 2. Skills Consolidation (11 → 6)

| Before (4.1.0) | After (4.1.1) |
|----------------|---------------|
| guarding-code-quality | **guarding-quality** (merged) |
| guarding-test-coverage | ↑ |
| guarding-ui-design | ↑ |
| guarding-git-safety | **guarding-git-workflow** (merged) |
| enforcing-workflow | ↑ |
| syncing-docs | syncing-docs |
| automating-e2e-tests | automating-e2e-tests |
| compressing-context | compressing-context |
| guiding-workflow | guiding-workflow |
| routing-serena-operations | (removed) |

**Token Savings**: ~1,050 tokens (-45%)

### 3. Skills Trigger Logging (NEW)

- **Log Location**: `~/.claude/logs/skill-triggers.jsonl`
- **Format**: JSONL (one JSON object per line)
- **Auto-rotation**: Archives when >1MB
- **Use Case**: Debug and optimize trigger rules

**Log Entry Example**:
```json
{
  "timestamp": "2025-11-28T04:21:00.000Z",
  "skill": "guarding-quality",
  "matchReason": "keyword+intent",
  "enforcement": "suggest",
  "priority": "high",
  "promptPreview": "Help me refactor this code..."
}
```

### 4. Research Config Consolidation

- **Before**: 7 files (~2,870 lines)
- **After**: 4 files (~2,090 lines)
- **Reduction**: 27% fewer lines, 43% fewer files

| Kept | Purpose |
|------|---------|
| `interaction-points-core.md` | Core questions (Hybrid Model) |
| `mode-1-discovery.md` | Full Mode 1 workflow |
| `metadata-schema.md` | Quality metrics schema |
| `research-quick-reference.md` | Quick reference (merged) |

---

## System Overview

Ultra Builder Pro 4.1 is a **complete AI-powered development workflow system** designed for Claude Code.

### Core Features

- **Structured 7-Phase Workflow**: Standardized development process
- **6 Automated Skills**: Real-time quality guards with auto-activation
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
Ultra Builder Pro 4.1.1
│
├── CLAUDE.md                          # Main config (~16KB)
│
├── settings.json                      # Claude Code settings (in .gitignore)
│   └── permissions.allow              # Official tool permissions
│
├── guidelines/                        # Development guidelines
│   ├── ultra-solid-principles.md      # SOLID/DRY/KISS/YAGNI
│   ├── ultra-quality-standards.md     # Quality baselines
│   └── ultra-git-workflow.md          # Git workflow
│
├── config/                            # Tool configuration
│   ├── ultra-skills-guide.md          # 6 Skills guide
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
├── skills/                            # 6 Automated Skills (gerund naming)
│   ├── guarding-quality/              # Code + Test + UI (merged)
│   ├── guarding-git-workflow/         # Git + Workflow (merged)
│   ├── syncing-docs/                  # Documentation sync
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
│   ├── ultra-think.md                 # /ultra-think
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

## 6 Automated Skills

### Skills Overview

| Skill | Trigger | Function |
|-------|---------|----------|
| **guarding-quality** | Edit code/tests/UI | SOLID + 6D testing + UI design |
| **guarding-git-workflow** | Git operations | Git safety + workflow enforcement |
| **syncing-docs** | Feature completion | Documentation sync reminders |
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
    ]
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
# Check Skills (should be 6)
ls ~/.claude/skills/ | grep -v "skill-rules\|DEPRECATION" | wc -l

# Check gerund naming
ls ~/.claude/skills/
# Expected: All end with -ing

# Start Claude Code
claude
/ultra-status
```

---

## Version History

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

- **[Skills Guide](config/ultra-skills-guide.md)** - All 6 Skills detailed
- **[MCP Guide](config/ultra-mcp-guide.md)** - MCP decision tree
- **[SOLID Principles](guidelines/ultra-solid-principles.md)** - Code quality
- **[Git Workflow](guidelines/ultra-git-workflow.md)** - Branching strategy

---

## Support

- **GitHub**: https://github.com/rocky2431/ultra-builder-pro
- **Official Docs**: https://docs.claude.com/claude-code

---

<div align="center">

**Ultra Builder Pro 4.1.1** - Production-Grade Claude Code Development System

*Every line of code, rigorously crafted*

[Quick Start](ULTRA_BUILDER_PRO_4.1_QUICK_START.md) | [Skills Guide](config/ultra-skills-guide.md) | [MCP Guide](config/ultra-mcp-guide.md)

</div>
