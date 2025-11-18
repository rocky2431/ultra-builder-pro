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
/ultra-think <problem>                # Deep analytical thinking
/ultra-session-reset                  # Archive and reset session
```

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
2. **Quality gates** - Test coverage %, code quality metrics
3. **Git workflow** - Branch naming patterns, commit conventions
4. **Paths** - All project paths (tasks, specs, docs, archives)

**Runtime behavior**:
- Skills (compressing-context, guarding-quality) load thresholds from config at runtime
- Documentation may show example values (e.g., "≥80%"), but actual values come from config
- Project templates in `.ultra-template/` include default config.json

**Example config structure**:
```json
{
  "context": {
    "total_limit": 200000,
    "thresholds": { "green": 0.60, "yellow": 0.70, "orange": 0.85 }
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

---

## Interactive Workflow (Automation-First with Strategic Questions)

**Philosophy**: "By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed." (Claude 4.x Best Practices)

**Use AskUserQuestion tool ONLY when**:
- ✅ User request is **genuinely ambiguous** (cannot be inferred from context) → Ask for clarification
- ✅ Multiple **equally valid** approaches exist with **significant trade-offs** → Present options (2-4 choices)
- ✅ During /ultra-research → **Strategic** technology selection decisions (frameworks, architectures)
- ✅ During /ultra-dev → **High-impact** implementation choices (breaking API changes, data migrations)

**DO NOT use AskUserQuestion for**:
- ❌ Project type/stack in /ultra-init → **Auto-detect from dependencies** (see smart detection logic)
- ❌ Simple parameter choices → **Use smart defaults** with inference
- ❌ Safe file operations → **Implement automatically** (create docs, compress context)
- ❌ Documentation updates → **Auto-create in `.ultra/docs/`**
- ❌ Context compression → **Auto-compress in Yellow/Orange zones**
- ❌ Merged branch deletion → **Auto-delete with safety checks**

**Key parameters**:
- 1-4 questions per call
- 2-4 options per question
- Use `multiSelect: true` for non-exclusive choices
- Keep `header` concise (max 12 chars)

**Example triggers** (strategic decisions only):
- "Which state management?" → Present Redux/Zustand/Jotai options (architectural decision)
- "Monolith or microservices?" → Clarify system architecture strategy
- "SQL or NoSQL?" → Database paradigm decision with trade-offs

**Example NON-triggers** (auto-infer instead):
- ~~"API or library project?"~~ → Auto-detect from package.json 'bin' field + dependencies
- ~~"Test framework?"~~ → Auto-detect from existing test files or dependencies
- ~~"Confirm file creation?"~~ → Auto-create in safe locations (`.ultra/docs/`)

**Official docs**: https://docs.claude.com/tools/ask-user-question

**Rationale**: Balance strategic input with autonomous execution following official guidance: "Infer the most useful likely action and proceed"

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

**SOLID** (mandatory, enforced by guarding-quality):
- **S**: Single Responsibility - Functions <50 lines
- **O**: Open-Closed - Extend through abstraction
- **L**: Liskov Substitution - Subtypes substitutable
- **I**: Interface Segregation - Minimal interfaces
- **D**: Dependency Inversion - Depend on abstractions

**DRY**: No duplication >3 lines | **KISS**: Complexity <10 | **YAGNI**: Only current requirements

**Philosophy**: User Value > Technical Showoff, Code Quality > Development Speed

**Note**: Detailed SOLID examples and enforcement rules loaded by guarding-quality skill when triggered.

---

## Quality Baselines (Non-Negotiable)

**All projects**:
- ✅ SOLID/DRY/KISS/YAGNI in every change
- ✅ Test coverage ≥80% (critical paths 100%)
- ✅ Functions <50 lines, nesting <3 levels

**Frontend only**:
- ✅ Avoid default fonts (Inter/Roboto/Open Sans), use design tokens, prefer established UI libraries
- ✅ Core Web Vitals: LCP<2.5s, INP<200ms, CLS<0.1

**Six-Dimensional Test Coverage** (enforced by guarding-quality):
1. **Functional** - Core business logic, happy paths
2. **Boundary** - Edge cases (empty/max/min), null/undefined
3. **Exception** - Error handling, invalid input
4. **Performance** - Load tests, response time
5. **Security** - Input validation, SQL/XSS prevention
6. **Compatibility** - Cross-browser, cross-platform

**Note**: Complete quality standards, UI design constraints, and test strategy loaded by guarding-quality skill when triggered.

---

## Git Workflow

**Branch naming**: `feat/task-{id}-{description}`, `fix/bug-{id}-{description}`, `refactor/{description}`

**Commit format**: Conventional Commits with co-authorship attribution

**Safety rules** (guarding-git-workflow enforced):
- ❌ Never force push to main/master
- ✅ Always review changes before commit
- ✅ Independent branches: Each task = one branch → merge → delete

**Workflow (mandatory)**:
```
main (always active, never frozen)
 ├── feat/task-1-xxx (create → complete → merge → delete)
 ├── feat/task-2-yyy (create → complete → merge → delete)
 └── feat/task-3-zzz (create → complete → merge → delete)
```

**Note**: Complete git workflow details, dangerous operation detection, and tiered risk management loaded by guarding-git-workflow skill when triggered.

---

## Skills System (6 Auto-Loaded)

**How it works** (official Claude Code):
- All 6 skills in `~/.claude/skills/` auto-loaded
- Claude invokes based on description matching
- Hooks system provides additional precision matching via `skill-rules.json`

**Available Skills** (100% gerund naming compliance):

**Guardrail Skills** (2):
1. **guarding-quality** - Code quality + test coverage + UI design (merged from 3 skills)
2. **guarding-git-workflow** - Git safety + workflow enforcement (merged from 2 skills)

**Functional Skills** (4):
3. **syncing-docs** - Auto-sync docs (specs/architecture.md)
4. **automating-e2e-tests** - E2E test code generation + browser automation
5. **compressing-context** - Proactive context compression (20-30 tasks/session)
6. **guiding-workflow** - Next-step suggestions based on project state

**Phase 3 Consolidation** (NEW in 4.1.1):
- **guarding-quality** (~150 tokens): Merged guarding-code-quality + guarding-test-coverage + guarding-ui-design, deleted originals
- **guarding-git-workflow** (~150 tokens): Merged guarding-git-safety + enforcing-workflow, deleted originals
- **Gerund naming**: 100% compliance with official best practices (all Skills use verb + -ing)
- **Token savings**: ~1,050 tokens (-45% from 11 Skills → 6 Skills)

**Skills Documentation Mode**: **Slim Mode** (recommended)
- All Skills use minimal SKILL.md (<500 lines, average 79-284 lines)
- Detailed documentation in separate `guidelines/` files
- Progressive disclosure: Load main file first, reference detailed docs only when needed
- Token efficiency: ~60% better than verbose mode

---

## MCP Integration

**Philosophy**: Built-in tools first, MCP when advantageous

**Decision Tree**:
1. Can built-in tools handle it? → Use Read/Write/Edit/Grep/Glob/WebFetch
2. Need official library documentation? → Context7 MCP
3. Need code search or web research? → Exa MCP

**Installed Servers** (2 total, verify via `claude mcp list`):
- **context7**: Official library documentation - Primary choice for API docs
- **exa**: AI semantic search - Intelligent code context + web search (supports Chinese)

**Note**: Complete MCP decision tree, tool selection guide, and usage patterns loaded by skills when needed.

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

---

## Documentation Access

**All detailed documentation is loaded on-demand by Skills**:
- **guarding-quality** loads: `guidelines/ultra-solid-principles.md`, `guidelines/ultra-quality-standards.md` (code quality, testing, UI design)
- **guarding-git-workflow** loads: `guidelines/ultra-git-workflow.md` (git safety, workflow enforcement)
- **MCP usage** reference: `config/ultra-mcp-guide.md` (when needed)
- **Skills development** reference: `config/ultra-skills-guide.md`, `config/ultra-skills-modes.md` (when creating/modifying Skills)
- **Workflow details** reference: `workflows/ultra-development-workflow.md`, `workflows/ultra-context-management.md` (when needed)

**Rationale**: Token efficiency - Load ~2,600 tokens at startup instead of 30,210 tokens. Detailed docs loaded only when Skills are triggered (60-80% of sessions don't need all documentation).

---

**Remember**: This streamlined structure optimizes token usage while preserving full system capabilities. Core configuration is always available, detailed documentation loads on-demand.
