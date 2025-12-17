# Ultra Builder Pro 4.1

Always respond in Chinese-simplified

---

## Modular References

@config/ultra-skills-guide.md
@config/ultra-mcp-guide.md
@guidelines/ultra-quality-standards.md
@guidelines/ultra-git-workflow.md
@guidelines/ultra-solid-principles.md
@guidelines/ultra-testing-philosophy.md

---

## Quick Start

| Command | Purpose |
|---------|---------|
| `/ultra-init <name> <type> <stack>` | Initialize project |
| `/ultra-research [topic]` | Technical investigation |
| `/ultra-plan` | Task planning |
| `/ultra-dev [task-id]` | TDD development |
| `/ultra-test` | Comprehensive testing |
| `/ultra-deliver` | Deployment optimization |
| `/ultra-status` | Progress report |
| `/max-think <problem>` | Deep analytical thinking |
| `/ultra-session-reset` | Archive and reset session |

---

## Language Protocol

- **User output**: Chinese (simplified)
- **Technical terms**: English (SOLID, JWT, LCP, etc.)
- **Code/paths**: English

---

## Configuration System

**All thresholds centralized in `.ultra/config.json`** (auto-created by /ultra-init).

Categories: Context limits, Quality gates, Git workflow, Project paths.

Skills load thresholds at runtime. Templates in `.ultra-template/`.

---

## Development Workflow

```
/ultra-init → /ultra-research → /ultra-plan → /ultra-dev → /ultra-test → /ultra-deliver
```

| Phase | Output | Key Action |
|-------|--------|------------|
| `/ultra-research` | `.ultra/docs/research/` | Auto-updates specs/architecture.md |
| `/ultra-plan` | `.ultra/tasks/tasks.json` | Auto-generates trace_to links |
| `/ultra-dev` | Code + Tests | TDD cycle, detailed merge status |
| `/ultra-test` | Quality validation | Six-dimensional coverage (>=80%) |
| `/ultra-deliver` | Deployment ready | Performance + security audit |

**Principles**: TDD mandatory, Independent branches, Quality gates enforced.

---

## Interactive Workflow

**Philosophy**: Implement changes rather than suggesting. Infer intent and proceed.

**Use AskUserQuestion ONLY for**:
- Genuinely ambiguous requests
- Multiple valid approaches with significant trade-offs
- Strategic tech decisions (frameworks, architecture)
- High-impact implementation choices

**DO NOT ask for**: Project type detection, Safe file operations, Documentation updates, Context compression.

---

## Project Scenarios

| Scenario | Workflow | Duration |
|----------|----------|----------|
| **New Project** | init → research (4-round) → plan → dev | ~70 min research |
| **Incremental Feature** | research (Round 2-3) → plan → dev | ~30 min research |
| **Tech Decision** | research (Round 3) → apply | ~15 min research |

Scenario auto-detected in `/ultra-research` Phase 0.

---

## Core Principles

**SOLID** (enforced by guarding-quality):

| Principle | Rule |
|-----------|------|
| Single Responsibility | Functions <50 lines |
| Open-Closed | Extend through abstraction |
| Liskov Substitution | Subtypes substitutable |
| Interface Segregation | Minimal interfaces |
| Dependency Inversion | Depend on abstractions |

**DRY**: No duplication >3 lines | **KISS**: Complexity <10 | **YAGNI**: Current requirements only

---

## Quality Baselines

**All projects**:
- SOLID/DRY/KISS/YAGNI enforced
- Test coverage >=80% (critical paths 100%)
- Functions <50 lines, nesting <3 levels

**Frontend only**:
- Core Web Vitals: LCP<2.5s, INP<200ms, CLS<0.1
- Design tokens required, avoid default fonts

**Six-Dimensional Testing**: Functional, Boundary, Exception, Performance, Security, Compatibility

---

## Git Workflow

**Branch naming**: `feat/task-{id}-{desc}`, `fix/bug-{id}-{desc}`, `refactor/{desc}`

**Safety** (guarding-git-workflow enforced):
- Never force push to main/master
- Independent branches: task → branch → merge → delete

```
main ── feat/task-1 (create → complete → merge → delete)
     └─ feat/task-2 (create → complete → merge → delete)
```

---

## Skills System

8 auto-loaded Skills in `~/.claude/skills/`:

| Type | Skills |
|------|--------|
| **Guardrails** | guarding-quality, guarding-test-quality, guarding-git-workflow |
| **Sync** | syncing-docs, syncing-status |
| **Functional** | automating-e2e-tests, compressing-context, guiding-workflow |

**Test Quality**: guarding-test-quality enforces TAS ≥70% (blocks fake tests).

Trigger rules in `skill-rules.json`. Slim mode documentation (<500 lines per Skill).

---

## MCP Integration

**Decision Tree**:
1. Built-in tools first (Read/Write/Edit/Grep/Glob)
2. Official docs needed? → Context7 MCP
3. Code search / web research? → Exa MCP

**Installed**: context7, exa (verify via `claude mcp list`)

---

## Context Management

**compressing-context** skill auto-manages:
- Triggers: 5+ tasks OR token >120K
- Compression: 15K → 500 tokens (97%)
- Archive: `.ultra/context-archive/session-{timestamp}.md`
- Enables: 20-30 tasks per session

**Best practices**: Be specific, Search before read, Parallel tool calls, Delegate to agents.

---

## Project Structure

```
.ultra/
├── config.json              # Configuration (Single Source of Truth)
├── constitution.md          # Project principles
├── specs/                   # Specifications (product.md, architecture.md)
├── tasks/tasks.json         # Native task management
├── docs/                    # research/, decisions/
├── changes/                 # Feature proposals (OpenSpec pattern)
└── context-archive/         # Session archives
    └── session-index.json   # Quick session recovery (NEW)
```

**Memory**: User-level `~/.claude/CLAUDE.md`, Project-level `./.claude/CLAUDE.md`

---

## Specialized Agents

Auto-delegated for complex tasks:
- `ultra-research-agent` - Technical research
- `ultra-architect-agent` - System architecture
- `ultra-performance-agent` - Performance optimization
- `ultra-qa-agent` - Test strategy

---

## Extended Thinking & Deep Analysis

### Thinking Modes 

**ultrathink (Claude Native)**:
- Keyword triggers: `ultrathink`, `think harder`, `think intensely`
- Token budget: 31,999 tokens (maximum reasoning depth)
- Output form: Free-form, no fixed structure
- Use cases: Exploratory thinking, open-ended analysis

**/max-think (Ultra Builder Pro Custom)**:
- Command format: `/max-think "problem description"`
- Token budget: Dynamic 8K-32K (complexity-based)
- Output form: 6-dimensional structured analysis framework
- Use cases: Tech selection, architecture decisions, strategic planning

**Combined Usage**:
```bash
ultrathink /max-think "Complex problem"
# Effect: Maximum reasoning depth + Structured framework
```

**Token Configuration**:
- Default: `MAX_THINKING_TOKENS = "16000"`
- Adjust: 24k-30k for complex reasoning, 8k-10k for simple tasks
- Override: `MAX_THINKING_TOKENS=30000 claude`

---

## Documentation Access

Skills load detailed docs on-demand:
- guarding-quality → `guidelines/ultra-solid-principles.md`, `guidelines/ultra-quality-standards.md`
- guarding-git-workflow → `guidelines/ultra-git-workflow.md`

Token efficiency: ~2,600 at startup vs 30,210 full load.

---

**Core configuration always available. Detailed documentation loads on-demand.**
