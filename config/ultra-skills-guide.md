# Skills System - Complete Guide

**Ultra Builder Pro 4.1** - Automated quality enforcement through model-invoked skills.

---

## Overview

Skills are **model-invoked**—Claude autonomously decides when to use them based on your request and each Skill's description. This is official Claude Code behavior, not a custom feature.

---

## How Skills Work (Official Claude Code)

### Activation Mechanism

1. **Automatic Discovery**: All Skills in `~/.claude/skills/` are automatically discovered and loaded into context
2. **Description Matching**: Claude analyzes your request and matches it against each Skill's `description` field
3. **Autonomous Invocation**: When a Skill's description matches your request, Claude invokes it automatically
4. **No Manual Control**: You cannot manually activate/deactivate Skills—activation is purely based on relevance

### Official Configuration Format

Each skill is defined in `~/.claude/skills/skill-name/SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name              # Required: lowercase, hyphens, max 64 chars
description: "..."            # Required: clear description for matching (max 1024 chars)
allowed-tools: Tool1, Tool2   # Optional: restrict tool access
---

# Skill content in markdown
```

**Official fields** (only these are supported):
- `name`: Skill identifier
- `description`: How Claude decides when to invoke
- `allowed-tools`: Tool permissions (optional)

---

## Available Skills (6 total)

### 1. guarding-quality

**Description**: "Enforces code quality (SOLID), test coverage, and UI design standards."

**Purpose**:
- Real-time SOLID/DRY/KISS/YAGNI violation detection
- Enforce 6-dimensional test coverage (≥80%)
- UI design anti-pattern prevention

**Auto-triggers when**:
- Editing code files (`.ts`, `.js`, `.tsx`, `.jsx`, `.py`, `.go`, `.java`, `.vue`)
- Editing UI files (`.css`, `.scss`, `.styled.ts`)
- Discussing quality, refactoring, testing, coverage
- Running /ultra-test or marking tasks complete

**Key checks**:
- Functions >50 lines → Split
- Nesting depth >3 → Refactor
- Duplicate code >3 lines → Extract
- Magic numbers → Named constants
- Test coverage ≥80%, critical paths 100%
- UI: Avoid default fonts, hard-coded colors

**Location**: `~/.claude/skills/guarding-quality/SKILL.md`

---

### 2. guarding-git-workflow

**Description**: "Enforces git safety and independent-branch workflow. Blocks dangerous operations."

**Purpose**:
- Prevent dangerous git operations (force push, hard reset)
- Enforce mandatory independent-branch workflow
- Require confirmation for destructive commands

**Auto-triggers when**:
- Git operations: commit, push, branch, merge, rebase, reset, delete
- Discussing git workflow, branch strategy, or merge timing
- Keywords: "force push", "rebase", "reset --hard", "unified branch"

**Risk levels**:
- 🔴 **Critical**: Force push to main, hard reset on shared branches → BLOCK
- 🟡 **Medium**: Rebase shared branches, delete remote branches → Confirm
- 🟢 **Low**: Normal commit/push → Allow with reminder

**Workflow enforced**:
```
main (always active, never frozen)
 ├── feat/task-1 (create → complete → merge → delete)
 ├── feat/task-2 (create → complete → merge → delete)
 └── feat/task-3 (create → complete → merge → delete)
```

**Location**: `~/.claude/skills/guarding-git-workflow/SKILL.md`

---

### 3. compressing-context

**Description**: "Compresses context to prevent overflow. Archives completed tasks, enables 20-30 tasks/session."

**Purpose**:
- Prevent context overflow during long sessions
- Archive completed tasks to `.ultra/context-archive/`
- Enable 20-30 tasks per session (vs 10-15 without)

**Auto-triggers when**:
- After 5+ tasks completed
- Token usage >120K (Yellow zone)
- Token usage >140K (Orange zone)
- Before /ultra-test or /ultra-deliver

**Thresholds** (from `.ultra/config.json`):
- <120K: Safe (Green)
- 120-140K: Suggest compression (Yellow)
- 140-170K: Enforce compression (Orange)
- >170K: BLOCK ultra-dev (Red)

**Compression ratio**: 40-60% (typical), 50-100K tokens freed per compression

**Location**: `~/.claude/skills/compressing-context/SKILL.md`

---

### 4. guiding-workflow

**Description**: "Guides next workflow steps based on project state. Suggests optimal commands with rationale."

**Purpose**:
- Suggest next logical command based on filesystem state
- Support Scenario B intelligent routing
- Enable session recovery via session-index.json

**Auto-triggers when**:
- After phase completion (init/research/plan/dev/test/deliver)
- User asks "what's next" or seems uncertain
- After /ultra-init or /ultra-research completes

**State detection** (filesystem-based):
- Spec files: `specs/product.md`, `specs/architecture.md`
- Research: `.ultra/docs/research/*.md`
- Tasks: `.ultra/tasks/tasks.json`
- Code changes: `git status`

**Scenario B routing**:
- New Project → Full 4-round research
- Incremental Feature → Skip to solution exploration
- Tech Decision → Focus on tech validation

**Location**: `~/.claude/skills/guiding-workflow/SKILL.md`

---

### 5. automating-e2e-tests

**Description**: "Generate and run E2E tests with Playwright CLI. Measures Core Web Vitals via Lighthouse."

**Purpose**:
- Generate Playwright test code (TypeScript)
- Run tests via `npx playwright test`
- Measure Core Web Vitals with Lighthouse CLI

**Auto-triggers when**:
- Keywords: "E2E test", "browser automation", "Playwright"
- Keywords: "Core Web Vitals", "LCP", "INP", "CLS"
- Running /ultra-test for frontend projects

**Core principle**: Use Playwright CLI via Bash (not MCP)
- Token savings: ~98.7% vs Playwright MCP
- Functionality: 100% equivalent

**Core Web Vitals targets**:
- LCP < 2.5s
- INP < 200ms
- CLS < 0.1

**Location**: `~/.claude/skills/automating-e2e-tests/SKILL.md`

---

### 6. syncing-docs

**Description**: "Syncs documentation with code changes. Updates specs/, proposes ADRs, detects spec-code drift."

**Purpose**:
- Ensure documentation stays synchronized with code
- Detect spec-code drift
- Auto-create ADRs for major decisions

**Auto-triggers when**:
- After /ultra-research completion
- Feature completion
- Architecture changes
- /ultra-deliver execution

**Actions**:
- Suggest updates to specs/product.md or specs/architecture.md
- Create ADRs in `.ultra/docs/decisions/`
- Detect [NEEDS CLARIFICATION] markers
- Flag outdated documentation

**Location**: `~/.claude/skills/syncing-docs/SKILL.md`

---

## Skills Best Practices

### Writing Effective Skill Descriptions

Based on official Claude Code best practices:

1. **Be specific**: Include concrete trigger conditions
   - Good: "TRIGGERS when editing .tsx/.jsx files or discussing UI components"
   - Bad: "Helps with UI work"

2. **Use action keywords**: TRIGGERS, MONITORS, ENFORCES, BLOCKS, SUGGESTS
   - Makes matching more reliable

3. **Include examples**: Mention specific scenarios
   - "USE WHEN: User completes research/plan/dev/test"

4. **Third person**: Write in third person for clarity
   - Good: "Detects code quality violations"
   - Bad: "I detect code quality violations"

5. **Length limit**: Max 1024 characters for description
   - Keep it concise but specific

### SKILL.md Content Guidelines

Based on official best practices:

1. **Keep under 500 lines**: Split larger content into reference files
2. **Use English for system instructions**: Optimal AI performance
3. **Chinese for user-facing output**: As per Language Protocol
4. **Progressive disclosure**: Reference detailed docs externally
5. **Concrete examples**: Show input/output patterns

---

## Skills Modes

Ultra Builder Pro supports two documentation styles for Skills:

### 1) Slim Mode (recommended)
- Keep `SKILL.md` minimal: Purpose, When, Do, Don't, Outputs
- Include negative triggers (what NOT to trigger on) to reduce false positives
- Move detailed rules/examples to `REFERENCE.md` and load on-demand
- Benefits: Lower steady-state token footprint; fewer misfires

### 2) Verbose Mode
- Self-contained `SKILL.md` with detailed rules and examples
- Higher token cost; useful for teams without separate guidelines

Default: `skills.mode = "slim"`. Keep all `SKILL.md` files English-only; at runtime, user-visible messages should be in Chinese (simplified).

---

## Skills vs Agents

### When to Use Skills

- **Automated quality checks**: SOLID violations, code smells
- **Safety enforcement**: Git workflow guards
- **Standards enforcement**: UI design rules, test coverage
- **Continuous monitoring**: Context overflow, performance

### When to Use Agents

- **Complex research tasks**: Technology comparisons
- **Architecture design**: System design decisions
- **Deep analysis**: Performance bottleneck investigation
- **Strategic planning**: Test strategy design

**Key difference**: Skills are **reactive guards**, Agents are **proactive experts**.

---

## Troubleshooting Skills

### Skill Not Triggering

**Possible causes**:
1. Description too vague → Make more specific
2. Missing trigger keywords → Add TRIGGERS, USE WHEN
3. SKILL.md too long (>500 lines) → Split into smaller files
4. Wrong language mixing → Use English for instructions

**Fix**: Update skill description with clearer trigger conditions

### Skill Triggering Too Often

**Possible causes**:
1. Description too broad → Narrow down scope
2. Too many trigger keywords → Be more selective

**Fix**: Refine description to be more specific

### Multiple Skills Conflicting

**Solution**: Skills can run concurrently—conflicts are rare. If they occur, adjust allowed-tools to create boundaries.

---

## Skills Configuration Reference

### Official Documentation

- Skills overview: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/skills-overview
- Best practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

### Current Skill Structure

```
~/.claude/skills/
├── guarding-quality/
│   ├── SKILL.md              # Main skill file
│   └── REFERENCE.md          # Detailed guidelines
├── guarding-git-workflow/
│   ├── SKILL.md
│   └── REFERENCE.md
├── compressing-context/
│   └── SKILL.md
├── guiding-workflow/
│   └── SKILL.md
├── automating-e2e-tests/
│   └── SKILL.md
└── syncing-docs/
    └── SKILL.md
```

---

**Remember**: Skills are your automated quality guardians. They work silently in the background, ensuring standards are met without manual intervention.
