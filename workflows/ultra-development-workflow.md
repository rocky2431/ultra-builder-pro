# Development Workflow - Complete Guide

**Ultra Builder Pro 4.0** - Structured workflow for all development phases.

---

## Core Workflow Sequence

```
/ultra-init → /ultra-research → /ultra-plan → /ultra-dev → /ultra-test → /ultra-deliver
```

**Key Principle**: Each phase builds on the previous. Don't skip phases.

---

## Quick Reference Table

| Phase | Command | When to Use | Output |
|-------|---------|-------------|--------|
| **Init** | `/ultra-init <name> <type> <stack> [git]` | Starting new project | `.ultra/` structure + tasks.json |
| **Research** | `/ultra-research` | **MANDATORY after init** - Complete specs through 4-round discovery (50-70 min) | Complete `specs/product.md` + `specs/architecture.md` + research reports |
| **Plan** | `/ultra-plan` | **After research completes** - Specs must be 100% complete | Task breakdown in `tasks.json` |
| **Dev** | `/ultra-dev [task-id]` | Ready to code | Code + tests + git commit |
| **Test** | `/ultra-test` | Code modified, pre-merge | Test report + coverage metrics |
| **Deliver** | `/ultra-deliver` | All tasks done, ready to deploy | Deployment report + optimizations |
| **Status** | `/ultra-status` | Check progress anytime | Progress report with risks |

---

## Phase 1: Initialization (/ultra-init)

**Purpose**: Bootstrap Ultra Builder Pro project structure with native task management.

**Command**:
```bash
/ultra-init <name> <type> <stack> [git]
```

**Parameters**: name (kebab-case), type (web|api|mobile|desktop|library), stack (react-ts|vue-ts|python-fastapi|go), git (optional)

**Template System**: Copies `~/.claude/.ultra-template/` to project's `.ultra/` directory, providing standardized structure:
- `context-archive/` - For compressing-context skill session archives
- `tasks/` - Native task management (tasks.json)
- `docs/` - Documentation (prd.md, tech.md, research/, decisions/)
- `config.json` - Project configuration

**Creates**: `.ultra/` with tasks/tasks.json, docs/, config.json, context-archive/

**Next**: guiding-workflow suggests `/ultra-research`

---

## Phase 2: Research (/ultra-research)

**Purpose**: Think-Driven Interactive Discovery - Complete specifications through 6-dimensional analysis.

**MANDATORY**: This is the most critical phase. DO NOT skip.

**Duration**: 50-70 minutes (best investment you'll make)

**ROI**: 70-minute investment saves 10+ hours of rework (8.3x return)

---

### Mode 1: Think-Driven Interactive Discovery (PRIMARY)

**When**: After `/ultra-init`, when specs/ have [NEEDS CLARIFICATION] markers

**4-Round Discovery Process**:

| Round | Focus | Duration | Output |
|-------|-------|----------|--------|
| **1. Problem Discovery** | 6D problem analysis (Technical/Business/Team/Ecosystem/Strategic/Meta) | 20 min | `specs/product.md` Sections 1-2 |
| **2. Solution Exploration** | Auto-generated user stories, requirements refinement | 20 min | `specs/product.md` Sections 3-5 |
| **3. Technology Selection** | 6D tech evaluation, MCP research (Context7/Exa) | 15 min | `specs/architecture.md` + research reports |
| **4. Risk & Constraint** | Risk assessment, constraint documentation | 15 min | Complete specs, 100% validation |

**Output**:
- ✅ `specs/product.md`: 100% complete (all sections filled, no [NEEDS CLARIFICATION])
- ✅ `specs/architecture.md`: 100% complete (all decisions justified)
- ✅ Research reports: Saved to `.ultra/docs/research/`

---

### Mode 2: Focused Technology Research (Secondary)

**When**: Specific technology decision during development

**Duration**: 10-15 minutes

**Process**: Single-round 6D comparison, auto-update architecture.md

---

### Scenario B: Intelligent Routing (NEW)

**Purpose**: Optimize research flow based on project type, save 57-79% time for focused scenarios.

**Phase 0 - Project Type Selection**:

Before starting research, ultra-research asks you to select project type:

| Project Type | Rounds Executed | Duration | Use Case |
|--------------|----------------|----------|----------|
| **New Project** | Round 1-4 (All) | 70 min | From scratch, requirements unclear |
| **Incremental Feature** | Round 2-3 (Solution + Tech) | 30 min | Existing system, adding features |
| **Tech Decision** | Round 3 (Tech only) | 15 min | Development tech problem |
| **Custom Flow** | User selects | Variable | Flexible scenarios |

**Key Features**:

1. **Dynamic Routing**: Execute only necessary rounds based on project type
2. **Satisfaction Checks**: After each round, choose to proceed/regenerate/end early
3. **Retry Mechanism**: Quality gate on every round (80% satisfaction rate)
4. **Time Savings**: 40-55 minutes for focused research (vs forced 4-round flow)

**How It Works**:

```
New Project → Round 1 → Round 2 → Round 3 → Round 4 (70 min)
Incremental Feature → Round 2 → Round 3 (30 min, skip problem discovery)
Tech Decision → Round 3 (15 min, only tech evaluation)
Custom Flow → User-selected rounds (flexible)
```

**After Each Round**:
- ✅ Satisfied → Proceed to next round
- 🔄 Not satisfied → Regenerate current round
- 🛑 End research → Exit early with partial specs

**Integration with guiding-workflow**:
- guiding-workflow detects Scenario B project type from research output
- Tailored next-step suggestions based on completed rounds
- Respects custom research flows

---

**Next**: guiding-workflow suggests `/ultra-plan` (only after specs 100% complete)

---

## Phase 3: Planning (/ultra-plan)

**Purpose**: Generate task breakdown from complete specifications (created by /ultra-research).

**IMPORTANT**: Assumes specs are 100% complete. If incomplete, you MUST run /ultra-research first.

**Prerequisites**:
- ✅ `specs/product.md` complete (created by /ultra-research Round 1-2)
- ✅ `specs/architecture.md` complete (created by /ultra-research Round 3-4)
- ❌ BLOCKS if [NEEDS CLARIFICATION] markers present → Forces return to /ultra-research

**Inputs**:
- Primary: `specs/product.md` and `specs/architecture.md` (new projects)
- Fallback: `docs/prd.md` and `docs/tech.md` (old projects)

**Process**:
1. Validate specifications are 100% complete
2. Parse requirements (functional + non-functional)
3. Decompose into atomic tasks with traceability
4. Estimate complexity (Simple/Medium/Complex)
5. Identify dependencies
6. Assess risks

**Output** (`tasks.json`):
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "status": "pending",
      "complexity": "simple",
      "dependencies": [],
      "estimatedHours": 2
    }
  ],
  "metadata": { "totalTasks": 12, "totalEstimatedHours": 48 }
}
```

**Next**: guiding-workflow suggests `/ultra-dev`

---

## Phase 4: Development (/ultra-dev)

**Purpose**: TDD-driven development with automatic task management and git integration.

**Command**: `/ultra-dev [task-id]` (if empty, auto-selects next pending task)

**TDD Cycle (MANDATORY)**:

| Phase | Action | Verify |
|-------|--------|--------|
| **RED** | Write failing test (all 6 dimensions) | Tests fail |
| **GREEN** | Write minimal code to pass | Tests pass |
| **REFACTOR** | Improve code quality (SOLID/DRY/KISS/YAGNI) | Tests still pass |

**Six Test Dimensions**: All required (Functional, Boundary, Exception, Performance, Security, Compatibility). See `guidelines/quality-standards.md` for complete details.

**Automatic Actions**:
- Mark task `in_progress` in tasks.json
- Create branch: `feat/task-{id}-{slug}`
- After GREEN: Commit with conventional format
- Update task status + implementation notes
- **After Quality Gates pass**: Merge to main and delete branch

**Quality Gates**: All tests passing, code quality checks passed, 6-dimensional coverage complete, documentation updated

**Merge & Cleanup** (after Quality Gates):
```bash
git checkout main && git pull origin main
git merge --no-ff feat/task-{id}-{slug}
git push origin main
git branch -d feat/task-{id}-{slug}
git push origin --delete feat/task-{id}-{slug}
```
Mark task as `completed` in tasks.json

**built-in tools** (for large codebases >100 files): find_symbol, find_referencing_symbols, rename_symbol

**Next**: If more tasks → `/ultra-dev`, else → `/ultra-test`

---

## Phase 5: Testing (/ultra-test)

**Purpose**: Comprehensive 6-dimensional test execution with coverage validation.

**Triggers**: Code modified, before merging to main, task marked complete

**Test Coverage**: Six-dimensional coverage required (Functional, Boundary, Exception, Performance, Security, Compatibility). Overall ≥80%, Critical paths 100%, Branch coverage ≥75%. See `guidelines/quality-standards.md` for dimension details.

**Frontend - Core Web Vitals** (Playwright + Lighthouse CLI):
```bash
# Navigate with Playwright (if login needed)
mcp__playwright__playwright_navigate({url: "http://localhost:3000", headless: false})

# Measure with Lighthouse CLI
lighthouse http://localhost:3000 --only-categories=performance --output=json

# Validate: LCP < 2500ms, TBT < 200ms, CLS < 0.1
```

**Test Report** (in Chinese): Six-dimensional coverage status, coverage %, Core Web Vitals scores, pass/fail

**Next**: If all pass → `/ultra-deliver`, else → Fix and re-test

---

## Phase 6: Delivery (/ultra-deliver)

**Purpose**: Deployment preparation with performance optimization, security audit, and documentation sync.

**Triggers**: All tasks completed, all tests passing (≥80% coverage), user ready to deploy

**Four Deliverables**:

1. **Performance Optimization**: Bundle size analysis, code splitting, runtime optimization (hot paths, re-renders, DB queries), frontend (image optimization, font loading, critical CSS)

2. **Security Audit**: Dependency vulnerability scan (`npm audit`, `pip-audit`), code review (SQL injection, XSS, hardcoded secrets), infrastructure (HTTPS, CORS, rate limiting)

3. **Documentation Update**: README.md, CHANGELOG.md, ADRs to `.ultra/docs/decisions/`, technical debt recorded (via syncing-docs skill)

4. **Deployment Preparation** - Pre-deployment checklist:
   - [ ] All tests passing
   - [ ] Coverage ≥80%
   - [ ] No security vulnerabilities
   - [ ] Documentation updated
   - [ ] Environment variables configured
   - [ ] Database migrations ready
   - [ ] Rollback plan prepared

**Output**: `.ultra/docs/delivery-report.md` (in Chinese) with performance metrics, security audit results, documentation updates, deployment checklist status

---

## Phase 7: Status Monitoring (/ultra-status)

**Purpose**: Real-time progress tracking with risk analysis.

**Shows**: Overall completion %, task breakdown (completed/in-progress/pending/blocked), current work details, risk warnings, next step suggestions

**Use Cases**: Check progress anytime, identify blockers, generate progress reports (in Chinese)

---

## Workflow Best Practices

### 1. Research is Mandatory - Don't Skip
**Wrong**: `/ultra-init` → `/ultra-plan` → `/ultra-dev` (skipping research)
**Right**: `/ultra-init` → `/ultra-research` (50-70 min) → `/ultra-plan` → `/ultra-dev`

**Why Research Matters**: Init creates templates → Research completes specs (4-round 6D analysis) → Plan generates tasks. Skipping = vague requirements, wrong tech, missing constraints. ROI: 8.3x (saves 10+ hours rework)

### 2. Follow TDD Strictly
RED-GREEN-REFACTOR is mandatory. No shortcuts.

### 3. Commit Regularly
- After each GREEN phase
- Before refactoring
- After task completion

### 4. Let Skills Enforce Quality
Auto-activated skills:
- **guarding-quality** - During /ultra-dev and /ultra-test
- **syncing-docs** - During /ultra-deliver
- **guiding-workflow** - After each phase

---

## Tool Selection by Project Size

| Project Size | File Ops | Code Search | Refactoring | Perf Testing |
|--------------|----------|-------------|-------------|--------------|
| **Small (<50 files)** | Read/Write/Edit | Grep/Glob | Edit | Bash + Lighthouse |
| **Large (>100 files)** | Read/Write/Edit | built-in tools find_symbol | built-in tools rename_symbol | Playwright + Lighthouse |

**MCP Decision Tree**:
1. Can built-in tools handle it? → Use built-in
2. Need semantic ops? → Use built-in tools
3. Need specialized capability? → Use appropriate MCP (Context7, Playwright, etc.)

---

## Command Quick Reference

```bash
/ultra-init my-app web react-ts git    # Initialize project
/ultra-research "Redux vs Zustand"     # Research tech options
/ultra-plan                            # Plan tasks
/ultra-dev 5                           # Develop specific task
/ultra-test                            # Test everything
/ultra-deliver                         # Prepare for deployment
/ultra-status                          # Check status
```

---

**Remember**: Workflow discipline prevents technical debt and ensures sustainable development velocity.
