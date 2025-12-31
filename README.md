# Ultra Builder Pro 4.4

<div align="center">

**Version 4.4.0 (Simplified Edition)**

*Production-Grade AI-Powered Development System for Claude Code*

---

[![Version](https://img.shields.io/badge/version-4.4.0-blue)](README.md#version-history)
[![Status](https://img.shields.io/badge/status-production--ready-green)](README.md)
[![Skills](https://img.shields.io/badge/skills-10-orange)](skills/)
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

## What's New in 4.4.0

### Simplified Architecture

- Removed hooks system (PostToolUse/PreToolUse stdout doesn't inject to AI context)
- Removed Codex integration (skill triggering via hooks was ineffective)
- Streamlined to 10 core skills
- Cleaner, more maintainable configuration

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
| `/ultra-init` | Initialize project with specs |
| `/ultra-research` | Technical investigation with 6D analysis |
| `/ultra-plan` | Task planning and breakdown |
| `/ultra-dev` | TDD development (RED→GREEN→REFACTOR) |
| `/ultra-test` | Quality validation with TAS scoring |
| `/ultra-deliver` | Deployment preparation |
| `/ultra-status` | Progress report |
| `/ultra-think` | Deep multi-dimensional analysis |

**Workflow**: init → research → plan → dev → test → deliver

---

## Skills (10 Total)

### Guard Skills

| Skill | Function |
|-------|----------|
| guarding-quality | SOLID principles, complexity limits |
| guarding-test-quality | TAS scoring, ZERO MOCK enforcement |
| guarding-git-workflow | Safe commits, branch strategy |

### Sync Skills

| Skill | Function |
|-------|----------|
| syncing-docs | ADR, research reports |
| syncing-status | Task progress, test results |
| guiding-workflow | Next step suggestions |

### Domain Skills

| Skill | Function |
|-------|----------|
| frontend | React/Vue/Next.js patterns |
| backend | API/database/security |
| smart-contract | EVM/Solana/security audit |
| skill-creator | Creating new skills |

---

## Quality Standards

### Test Authenticity Score (TAS)

- TAS ≥ 70% required
- ZERO MOCK policy (no jest.mock, vi.mock)
- 6D coverage: Functional, Boundary, Exception, Performance, Security, Compatibility

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
├── skills/                   # 10 Automated Skills
│   ├── skill-rules.json      # Skill trigger rules
│   ├── guarding-quality/
│   ├── guarding-test-quality/
│   ├── guarding-git-workflow/
│   ├── syncing-docs/
│   ├── syncing-status/
│   ├── guiding-workflow/
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

### v4.4.0 (2025-12-31) - Simplified Edition

- **Removed**: Hooks system (SessionStart, PreToolUse, PostToolUse, Stop)
- **Removed**: Codex integration (4 codex-* skills)
- **Reason**: PostToolUse/PreToolUse hook stdout doesn't inject to AI context
- **Result**: 14 → 10 skills, cleaner architecture

### v4.3.4 (2025-12-31) - Production Absolutism

- Production Absolutism enforcement
- ZERO MOCK policy

### v4.3.3 (2025-12-30) - Pre-Hooks Stable

- Stable version before hooks experiment

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
