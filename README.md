# Ultra Builder Pro 4.4

<div align="center">

**Version 4.4.1 (Command Refinement)**

*Production-Grade AI-Powered Development System for Claude Code*

---

[![Version](https://img.shields.io/badge/version-4.4.1-blue)](README.md#version-history)
[![Status](https://img.shields.io/badge/status-production--ready-green)](README.md)
[![Skills](https://img.shields.io/badge/skills-6-orange)](skills/)
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

## What's New in 4.4.1

### Command Refinement

- Refactored `/ultra-test` TAS scoring → Anti-Pattern Detection (executable)
- Refactored `/ultra-dev` git branch logic with decision tree
- Added AskUserQuestion to all commands (except status)
- Added `.ultra-template/` for project initialization

### Codex Integration

- Added `codex` skill with review templates (research/code/test)
- Mandatory Codex review at key checkpoints:
  - `/ultra-research` → after all rounds complete
  - `/ultra-dev` → after Quality Gates pass
  - `/ultra-test` → after all gates pass
- Templates aligned with CLAUDE.md rules

### Gemini Integration

- Added `gemini` skill for research, validation, and documentation
- **Gemini does NOT modify code** - use codex for code changes
- Models: gemini-3-flash-preview (default), gemini-3-pro-preview, gemini-2.5-pro
- Templates: tech-research, architecture-review, documentation-gen, spec-validation, code-review (read-only)

### Production Absolutism (Preserved)

> "There is no test code. There is no demo. There is no MVP.
> Every line is production code. Every test is production verification."

**Core Formula:**
```
Code Quality = Real Implementation × Real Tests × Real Dependencies
If ANY component is fake/mocked/simulated → Quality = 0
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `/ultra-init` | Initialize project with native task management |
| `/ultra-research` | Think-Driven Interactive Discovery |
| `/ultra-plan` | Task planning with dependency analysis |
| `/ultra-dev` | TDD development (RED→GREEN→REFACTOR) |
| `/ultra-test` | Pre-delivery quality audit (Anti-Pattern + Coverage + E2E + Perf + Security) |
| `/ultra-deliver` | Release preparation (docs + build + version + publish) |
| `/ultra-status` | Real-time progress + risk analysis |
| `/ultra-think` | Deep analysis with structured reasoning |

**Workflow**: init → research → plan → dev → test → deliver

---

## Skills (6 Total)

| Skill | Function |
|-------|----------|
| codex | OpenAI Codex CLI (code analysis, refactoring, **can modify code**) |
| gemini | Google Gemini CLI (research, validation, docs, **read-only**) |
| frontend | React/Vue/Next.js patterns, Core Web Vitals |
| backend | API/database/security patterns |
| smart-contract | EVM/Solana security audit |
| skill-creator | Creating new skills |

---

## Quality Standards

### Pre-Delivery Quality Gates (`/ultra-test`)

| Gate | Requirement |
|------|-------------|
| Anti-Pattern | No tautology, empty tests, core logic mocks |
| Coverage Gaps | No HIGH priority untested functions |
| E2E | All critical flows pass (Chrome MCP) |
| Performance | Core Web Vitals pass (if frontend) |
| Security | No critical/high vulnerabilities |
| Codex Review | No critical issues from Codex audit |

### Code Limits

| Metric | Limit |
|--------|-------|
| Function lines | ≤ 50 |
| Nesting depth | ≤ 3 |
| Cyclomatic complexity | ≤ 10 |

### Frontend (Core Web Vitals)

| Metric | Target |
|--------|--------|
| LCP | < 2.5s |
| INP | < 200ms |
| CLS | < 0.1 |

---

## Project Structure

```
~/.claude/
├── CLAUDE.md                 # Main configuration
├── settings.json             # Claude Code settings
├── .ultra-template/          # Project initialization templates
├── skills/                   # Domain skills
│   ├── codex/
│   ├── gemini/
│   ├── frontend/
│   ├── backend/
│   ├── smart-contract/
│   └── skill-creator/
└── commands/                 # /ultra-* commands
    ├── ultra-init.md
    ├── ultra-research.md
    ├── ultra-plan.md
    ├── ultra-dev.md
    ├── ultra-test.md
    ├── ultra-deliver.md
    ├── ultra-status.md
    └── ultra-think.md
```

---

## Version History

### v4.4.1 (2026-01-01) - Command Refinement + Codex/Gemini Integration

- **Added**: `codex` skill with 3 review templates (research/code/test)
- **Added**: `gemini` skill with 5 templates (tech-research, architecture-review, documentation-gen, spec-validation, code-review)
- **Added**: Mandatory Codex review in `/ultra-research`, `/ultra-dev`, `/ultra-test`
- **Added**: Git operation safety (AskUserQuestion before commit/merge/push)
- **Refactored**: `/ultra-test` TAS scoring → Anti-Pattern Detection
- **Refactored**: `/ultra-dev` git branch logic with decision tree
- **Refactored**: `/ultra-deliver` build detection with priority list
- **Added**: `.ultra-template/` for project initialization
- **Removed**: `skill-rules.json`, `agents/`
- **Fixed**: Review templates aligned with CLAUDE.md rules
- **Separation**: Codex = code changes, Gemini = research/docs (read-only)

### v4.4.0 (2025-12-31) - Simplified Edition

- **Removed**: Hooks system (SessionStart, PreToolUse, PostToolUse, Stop)
- **Removed**: Codex integration (4 codex-* skills)
- **Result**: Cleaner architecture, 4 skills

### v4.3.4 (2025-12-31) - Production Absolutism

- Production Absolutism enforcement
- ZERO MOCK policy

---

## Philosophy

### Priority Stack

1. **Safety & Production**: No TODO/FIXME/demo/placeholder
2. **TDD Mandatory**: RED → GREEN → REFACTOR
3. **Intellectual Honesty**: Mark uncertainty (Fact/Inference/Speculation)
4. **Action Bias**: Execute rather than ask

### Communication

- Think in English, respond in Chinese
- Lead with findings, then summarize
- File paths with line numbers (`file.ts:42`)

---

## License

MIT

---

*Ultra Builder Pro: No mock. No demo. No MVP. Production-grade only.*
