# Ultra Builder Pro 4.1

## Quick Start

**Core Workflow Commands**:
```bash
/ultra-init <name> <type> <stack>  # Initialize project
/ultra-research [topic]             # Technical investigation
/ultra-plan                         # Task planning
/ultra-dev [task-id]                # TDD development
/ultra-test                         # Comprehensive testing
/ultra-deliver                      # Deployment optimization
/ultra-status                       # Progress report
```

**Additional Commands**:
```bash
/ultra-refactor <operation> <target>  # Code refactoring with Serena MCP
/ultra-think <problem>                # Deep analytical thinking
/ultra-session-reset                  # Archive and reset session
```

**Complete workflow guide**: @workflows/ultra-development-workflow.md

---

## Language Protocol

**User-facing output**: Chinese (simplified)
**Technical terms**: English (SOLID, JWT, LCP, INP, CLS, DRY, KISS, YAGNI)
**Code/paths/commands**: English

**Example**: "Running /ultra-test, checking Core Web Vitals (LCP<2.5s)" (output in Chinese at runtime)

---

## Configuration System (NEW in 4.1)

**All thresholds and limits are centralized in `.ultra/config.json`** (auto-created by /ultra-init).

**Configuration categories**:
1. **Context management** - Token limits, compression thresholds
2. **File routing** - File size thresholds for Serena MCP routing
3. **Quality gates** - Test coverage %, code quality metrics
4. **Git workflow** - Branch naming patterns, commit conventions
5. **Paths** - All project paths (tasks, specs, docs, archives)

**Runtime behavior**:
- Skills (compressing-context, routing-serena-operations, guarding-test-coverage, guarding-code-quality) load thresholds from config at runtime
- Documentation may show example values (e.g., "≥80%"), but actual values come from config
- Project templates in `.ultra-template/` include default config.json

**Example config structure**:
```json
{
  "context": {
    "total_limit": 200000,
    "thresholds": { "green": 0.60, "yellow": 0.70, "orange": 0.85 }
  },
  "file_routing": {
    "thresholds": { "medium": 5000, "large": 8000 }
  },
  "quality_gates": {
    "test_coverage": { "overall": 0.80, "critical_paths": 1.00, "branch": 0.75 },
    "code_quality": { "max_function_lines": 50, "max_nesting_depth": 3 }
  }
}
```

**Why configuration matters**:
- Single source of truth for all thresholds
- Easy to adapt to future Claude versions (e.g., 500K token limit)
- Project-specific customization without modifying Skills
- Team alignment on quality standards

**Complete config reference**: See `.ultra-template/config.json` for all available settings.

---

## Development Workflow (CRITICAL - ALWAYS FOLLOW)

**Complete workflow sequence**:

```
/ultra-init → /ultra-research → /ultra-plan → /ultra-dev → /ultra-test → /ultra-deliver
```

**Core phases** (after initialization):

1. **/ultra-research** → Technical investigation, **auto-updates specs/architecture.md** → `.ultra/docs/research/`
2. **/ultra-plan** → Task breakdown, **auto-generates trace_to links** → `.ultra/tasks/tasks.json`
3. **/ultra-dev** → TDD development (RED-GREEN-REFACTOR), **detailed merge back status** → Code + Tests
4. **/ultra-test** → Six-dimensional coverage (≥80%), Core Web Vitals → Quality validation
5. **/ultra-deliver** → Performance optimization, security audit → Deployment ready

**Use /ultra-status anytime** to check progress and next-step suggestions.

**Key principles**:
- **TDD mandatory**: Write test first (RED), implement (GREEN), refactor (REFACTOR)
- **Independent branches**: Each task gets its own `feat/task-{id}` branch, merged immediately after completion
- **Quality gates**: All tests pass, ≥80% coverage, SOLID principles enforced before completion

**Detailed workflow guide**: @workflows/ultra-development-workflow.md

---

## Project Scenarios (Workflow Routing Context)

Ultra Builder Pro supports different project scenarios with tailored workflows:

### Scenario A: New Project
- **Characteristics**: Requirements unclear, no existing codebase
- **Workflow**: `/ultra-init` → `/ultra-research` (full 4-round) → `/ultra-plan` → `/ultra-dev`
- **Research duration**: ~70 minutes for complete discovery
- **Use when**: Starting from scratch, building new product

### Scenario B: Incremental Feature
- **Characteristics**: Existing system, adding features or fixing bugs
- **Workflow**: `/ultra-research` (Round 2-3 only) → `/ultra-plan` → `/ultra-dev`
- **Research duration**: ~30 minutes for focused research
- **Use when**: Extending existing codebase, feature enhancement

### Scenario C: Tech Decision
- **Characteristics**: Development tech problem, need solution comparison
- **Workflow**: `/ultra-research` (Round 3 only) → Apply decision
- **Research duration**: ~15 minutes for tech evaluation
- **Use when**: Technology selection, architecture decision

**Scenario detection**: `/ultra-research` Phase 0 automatically detects project type and routes to optimal research flow. `guiding-workflow` skill uses scenario context to suggest next steps.

---

## Core Development Principles

**SOLID** (mandatory, enforced by guarding-code-quality):
- **S**: Single Responsibility - Functions <50 lines
- **O**: Open-Closed - Extend through abstraction
- **L**: Liskov Substitution - Subtypes substitutable
- **I**: Interface Segregation - Minimal interfaces
- **D**: Dependency Inversion - Depend on abstractions

**DRY**: No duplication >3 lines | **KISS**: Complexity <10 | **YAGNI**: Only current requirements

**Philosophy**: User Value > Technical Showoff, Code Quality > Development Speed

**Complete guide**: @guidelines/ultra-solid-principles.md

---

## Quality Baselines (Non-Negotiable)

**All projects**:
- ✅ SOLID/DRY/KISS/YAGNI in every change
- ✅ Test coverage ≥80% (critical paths 100%)
- ✅ Functions <50 lines, nesting <3 levels

**Frontend only**:
- ✅ Avoid default fonts (Inter/Roboto/Open Sans), use design tokens, prefer established UI libraries
- ✅ Core Web Vitals: LCP<2.5s, INP<200ms, CLS<0.1

**Complete standards**: @guidelines/ultra-quality-standards.md

---

## Git Workflow

**Branch naming**: `feat/task-{id}-{description}`, `fix/bug-{id}-{description}`, `refactor/{description}`

**Commit format**: Conventional Commits with co-authorship attribution

**Safety rules** (guarding-git-safety enforced):
- ❌ Never force push to main/master
- ✅ Always review changes before commit

**Complete guide**: @guidelines/ultra-git-workflow.md

---

## Skills System (10 Auto-Loaded)

**How it works** (official Claude Code):
- All 10 skills in `~/.claude/skills/` auto-loaded
- Claude invokes based on description matching
- No manual activation/deactivation

**Available Skills**:
1. `guarding-code-quality` - SOLID/DRY/KISS/YAGNI detection
2. `guarding-test-coverage` - 6-dimensional coverage validation
3. `guarding-git-safety` - Dangerous operation prevention
4. `guarding-ui-design` - UI anti-patterns prevention + design guidance
5. `syncing-docs` - Auto-sync docs (specs/architecture.md)
6. `automating-e2e-tests` - E2E test code generation + browser automation
7. `routing-serena-operations` - Intelligent Serena MCP routing (file size + operation type + project scale)
8. `compressing-context` - Proactive context compression (20-30 tasks/session)
9. `guiding-workflow` - Next-step suggestions based on project state
10. `enforcing-workflow` - Enforces independent-branch workflow

**Complete guide**: @config/ultra-skills-guide.md

---

## MCP Integration

**Philosophy**: Built-in tools first, MCP when advantageous

**Automatic file routing**: **routing-serena-operations** skill automatically detects large files:
- < 5,000 lines: Use Read tool normally
- 5,000-8,000 lines: Suggests Serena MCP (3 options provided)
- > 8,000 lines: Blocks Read, enforces Serena MCP

**Decision Tree**:
1. Large file? → **routing-serena-operations** auto-routes to Serena MCP (60x efficiency)
2. Can built-in tools handle it? → Use Read/Write/Edit/Grep/Glob/WebFetch
3. Need semantic code ops (>100 files)? → Serena MCP
4. Need specialized capability? → Context7/Exa MCP

**Installed Servers** (3 total, verify via `claude mcp list`):
- **serena**: Semantic layer infrastructure - Required for TDD REFACTOR, safe refactoring, knowledge management
- **context7**: Official library documentation - Primary choice for API docs
- **exa**: AI semantic search - Intelligent code context + web search (supports Chinese)

**Serena Quick Start**: @config/serena/quick-start.md

**Complete guides**:
- MCP decision tree: @config/ultra-mcp-guide.md
- Serena workflows (7 phases): @config/serena/workflows.md
- Serena reference (advanced): @config/serena/reference.md

---

## Context Management

**Proactive compression**: **compressing-context** skill automatically manages context:
- Triggers after 5+ tasks in /ultra-dev OR token usage >120K
- Compresses completed task details (15K → 500 tokens = 97% reduction)
- Archives to `.ultra/context-archive/session-{timestamp}.md`
- Enables 20-30 tasks per session (vs 10-15 without compression)

**Official best practices**:
- Be specific in requests ("Write unit tests for getUserById() in src/auth.ts...")
- Search before reading (Grep → Read targeted section)
- Use parallel tool calls (Read multiple files in single message)
- Delegate to agents (ultra-research-agent, ultra-architect-agent)
- Summarize after tasks (concise summaries for future reference)
- Trust compressing-context suggestions (40-60% token savings)

**Complete guide**: @workflows/ultra-context-management.md

---

## Project Structure

**Specification-Driven Architecture** (NEW in 4.1):

```
.ultra/
├── config.json                      # Project configuration (Single Source of Truth)
├── constitution.md                  # Project principles & development standards
│
├── specs/                          # Specification-driven source of truth
│   ├── product.md                  # Product requirements & user stories
│   ├── architecture.md             # Architecture design & tech stack
│   ├── api-contracts/              # API specifications (OpenAPI, GraphQL schemas)
│   └── data-models/                # Data model definitions
│
├── tasks/
│   └── tasks.json                  # Native task management
│
├── docs/
│   ├── research/                   # Research reports (/ultra-research outputs)
│   └── decisions/                  # Architecture Decision Records (ADRs)
│
├── changes/                        # Feature proposals (OpenSpec pattern)
│
└── context-archive/                # Compressed context sessions
    └── session-{timestamp}.md      # Session archives (compressing-context skill)
```

**Key Design Decisions**:
- **specs/** replaces old docs/prd.md and docs/tech.md (specification-driven development)
- **constitution.md** defines project-wide development principles (references config.json for thresholds)
- **config.json** is the single source of truth for all numeric thresholds and limits
- **context-archive/** enables 20-30 tasks per session via compressing-context skill

**Memory organization**:
- User-level: `~/.claude/CLAUDE.md` (this file - personal)
- Project-level: `./.claude/CLAUDE.md` (team-shared, in git)

---

## Communication Protocol

**Proactive reporting when**:
- ✅ Starting/ending each phase
- ✅ Completing milestones (>20% progress)
- ✅ Discovering risks or blockers
- ✅ User decision required

**Principles**: Facts First, Risk Forward, Options Parallel, Await Confirmation

---

## Specialized Agents

**Available** (auto-delegated for complex tasks):
- `ultra-research-agent` - Technical research, solution comparison
- `ultra-architect-agent` - System architecture design
- `ultra-performance-agent` - Performance optimization
- `ultra-qa-agent` - Test strategy design

**Invocation**: Automatic based on complexity, or explicit via "Use {agent-name} agent"

---

## Extended Thinking Configuration

**Default**: `MAX_THINKING_TOKENS = "16000"` (in `~/.claude/settings.json`)

**When to adjust**:
- Keep 16,000: Most development tasks
- Increase (24k-30k): Multi-step reasoning, large refactoring
- Decrease (8k-10k): Simple tasks, faster responses

**Temporary override**: `MAX_THINKING_TOKENS=30000 claude`

**See**: `~/.claude/THINKING_TOKENS_GUIDE.md` for complete guide

---

## Detailed Documentation Index

**Guidelines** (principles and standards):
- @guidelines/ultra-solid-principles.md - SOLID/DRY/KISS/YAGNI with examples
- @guidelines/ultra-quality-standards.md - Complete quality baselines
- @guidelines/ultra-git-workflow.md - Branch naming, commits, safety rules

**Configuration** (tools and systems):
- @config/ultra-skills-guide.md - All 10 skills detailed reference
- @config/ultra-mcp-guide.md - MCP decision tree + usage patterns

**Workflows** (processes and efficiency):
- @workflows/ultra-development-workflow.md - Complete 7-phase workflow
- @workflows/ultra-context-management.md - Token optimization strategies

---

**Remember**: This modular structure optimizes token usage while preserving full system capabilities. Core workflow is front-and-center, details are one @import away.
