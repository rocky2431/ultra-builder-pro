---
description: Initialize Ultra Builder Pro 6.8.0 project with native task management
argument-hint: <name> <type> <stack> [git]
allowed-tools: Read, Write, Bash, Grep, Glob, Task, AskUserQuestion
model: opus
---

# /ultra-init

## Workflow Tracking (MANDATORY)

**On command start**, create tasks for each major step using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 1 | Collect Project Information | Collecting project info... |
| 1.5 | Interactive Confirmation | Confirming with user... |
| 2 | Create Project Structure | Creating .ultra/ structure... |
| 3 | Initialize Task System | Initializing tasks.json... |
| 4 | Copy Template Files | Copying templates... |
| 5 | Git Integration | Setting up Git... |
| 6 | Display Summary | Generating summary... |

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**On context recovery**: `TaskList` → resume from last incomplete step

---

## Purpose

Initialize Ultra Builder Pro 6.8.0 project structure with native task management.

## Arguments

- `$1`: Project name (if empty, use current directory name)
- `$2`: Project type (web/api/cli/fullstack/other, if empty, **auto-detect from dependencies**)
- `$3`: Tech stack (if empty, **auto-detect from package files**)
- `$4`: "git" to initialize git repo (optional)

## Pre-Execution Checks

**Phase 0: Project State Detection**

Detect project context before initialization:

1. **Check existing `.ultra/` directory**
   - If exists → Trigger re-initialization flow
   - Read existing config for comparison

2. **Detect project code files**
   - Look for language-specific config files (package.json, Cargo.toml, go.mod, pyproject.toml, etc.)

3. **Detect Git repository**
   - Check if `.git/` directory exists
   - Use in interactive confirmation (show different Git options based on detection)

4. **Auto-detect project type and tech stack**
   - Analyze dependencies and config to identify frameworks, testing tools, and build systems

5. **Use detection results in interactive confirmation**
   - Show detected values with labels

**Triggers interactive confirmation for**:
- Existing projects with code files
- Re-initialization scenarios
- Optional: `--interactive` flag

## Workflow

### 1. Collect Project Information (Smart Detection)

**Project name**: $1 or current directory name

**Project type**: $2 or auto-detect from existing files

**Detection logic**:
- Read project config files and analyze dependencies
- Infer type from frameworks: web frameworks → web, API frameworks → api, CLI tools → cli
- Mixed patterns → fullstack

**Fallback**: Use AskUserQuestion with detected context hints

**Rationale**: "Infer the most useful likely action and proceed" (Claude 4.x Best Practices)

**Tech stack**: $3 or auto-detect (supports multiple stacks for fullstack projects)

**Detection by layer** (can coexist):
- **Frontend**: Detect from dependencies (UI frameworks, build tools)
- **Backend**: Detect from dependencies (API frameworks, runtime)
- **Database**: Detect from config or dependencies

**Fallback**: Use AskUserQuestion with multi-select support

**Git initialization**: $4 = "git"

### 1.5. Interactive Confirmation

**Triggers for**:
- Existing projects with code files
- Re-initialization (`.ultra/` already exists)
- Optional: `--interactive` flag

**Process**:

1. **Ask project type** (multiSelect: true for hybrid projects)
   - Show detected types with "(detected)" label
   - Allow multi-selection (e.g., Web + API)
   - Options: Web, API, CLI, Fullstack, Other

2. **Ask tech stack** (multiSelect: true for fullstack projects)
   - Show detected stacks with "(detected)" label
   - Allow multi-selection for frontend + backend + database
   - Options based on detected package files grouped by layer
   - Fallback: Custom input

3. **Ask Git initialization** (based on detection)

   **If `.git/` detected** (hasGit: true):
   - Options:
     - "Keep existing Git repository" (default)
     - "Reinitialize Git (backup to .git.backup)"
     - "Don't use Git"

   **If `.git/` NOT detected** (hasGit: false):
   - Options:
     - "Initialize Git repository"
     - "Don't use Git"

4. **Ask re-initialization handling** (if `.ultra/` exists)
   - Overwrite (backup to `.ultra/backups/`)
   - Keep existing (update missing files only)
   - Cancel

**Implementation Note**: Use AskUserQuestion tool with Chinese prompts generated at runtime.

**Output Language**: All prompts in Chinese at runtime (not hardcoded in this file)

### 2. Create Project Structure

Create `.ultra/` by copying from template (`~/.claude/.ultra-template/`):

**v7 Harness substrate (REQUIRED by hooks — must exist or hooks point at broken paths):**
- `.ultra/PHILOSOPHY.md` — 5 commandments + 4 goals (read by agents during reasoning)
- `.ultra/north-star.md` — project goal (auto-populated by user_prompt_capture on first user prompt)
- `.ultra/templates/` — enabling templates (`testcontainer-*`, `vertical-slice.ts`, `persistence-real.ts`, etc.) — surfaced by `post_edit_guard.py` and `review-tests` agent

**Specification-Driven Structure**:
- `.ultra/specs/` - Specification source of truth
  - `discovery.md` - Problem Validation, Opportunity Space, Market Assessment, Competitive Landscape, Product Strategy, Assumptions & Validation Plan (§0-5)
  - `product.md` - Problem Statement, Personas, User Scenarios, User Stories, Features Out, Success Metrics (§1-6)
  - `architecture.md` - arc42 structure (§1-12)

**Task Management**:
- `.ultra/tasks/tasks.json` - Native task tracking
- `.ultra/tasks/contexts/task-{id}.md` - per-task context (Acceptance Criteria, Trace, Drift definition) — created by /ultra-plan from `contexts/TEMPLATE.md`
- `.ultra/tasks/progress/` - per-task progress.json files (created on-demand by post_edit_guard)

**Documentation**:
- `.ultra/docs/research/` - Research reports (/ultra-research outputs)

**Template Source**: All files copied from `~/.claude/.ultra-template/`


### 3. Initialize Task System

Create `.ultra/tasks/tasks.json`:
- Empty tasks array
- Metadata (version, project name, created timestamp)
- Stats initialization (total: 0, completed: 0)

### 4. Copy All Template Files

**Copy `~/.claude/.ultra-template/` contents to `.ultra/` (use `cp -r` to mirror the full tree):**

- **v7 harness (CRITICAL — required by hooks):**
  - `PHILOSOPHY.md` — 5 commandments + 4 goals
  - `north-star.md` — project goal, populated by user_prompt_capture on first user prompt
  - `templates/` — full directory: `README.md`, `testcontainer-postgres.{ts,py}`, `vertical-slice.ts`, `persistence-real.ts`, `feature-flag-default-audit.sh` (referenced by post_edit_guard advisories and review-tests agent)
  - Per-task acceptance criteria lives in `tasks/contexts/task-{id}.md` (`## Acceptance Criteria` section, read by `mid_workflow_recall.py` and `session_context.py`)
- Specs: `specs/discovery.md`, `specs/product.md`, `specs/architecture.md`
- Tasks: `tasks/tasks.json`, `tasks/contexts/TEMPLATE.md`
- Status: `test-report.json`, `delivery-report.json`
- Docs: `docs/research/README.md`

**Verify after copy** (ALL must exist for v7 hooks to function):
```
.ultra/PHILOSOPHY.md
.ultra/north-star.md
.ultra/templates/testcontainer-postgres.ts
.ultra/templates/persistence-real.ts
.ultra/templates/vertical-slice.ts
```
If any missing → re-run copy, do NOT proceed (hook advisories will point at broken paths).

### 5. Git Integration (Based on User Choice)

**If user chose "Initialize Git repository"** or **"Reinitialize Git"**:
- If reinitializing: Backup existing `.git/` to `.git.backup.{timestamp}`
- Initialize repo: `git init`
- Create `.gitignore`:
  - Exclude `.ultra/backups`
  - Exclude `.ultra/tasks/progress/` (v7: ephemeral evidence_score files maintained by post_edit_guard)
  - Exclude `.ultra/relations.json` (v7: derived index, regenerated by relations_sync hook)
  - Exclude `.ultra/memory/` (SQLite/Chroma runtime stores)
  - Exclude secrets, build artifacts
- Create basic `README.md` (if not exists)
- Suggest first commit: `git add . && git commit -m "feat: initialize Ultra Builder Pro 6.8.0"`

**If user chose "Keep existing Git repository"** or **"Don't use Git"**:
- Skip Git operations

### 6. Display Success Summary

Show in Chinese:
- Directories created (.ultra/specs/, .ultra/tasks/, .ultra/docs/, .ultra/templates/)
- Template files copied
- Task system initialized (tasks.json)
- Status files initialized (test-report.json, delivery-report.json)
- Specification templates ready (product.md, architecture.md with [NEEDS CLARIFICATION] markers)
- **v7 harness ready**: PHILOSOPHY.md, north-star.md (awaiting first prompt), templates/ (testcontainer-*, vertical-slice, persistence-real, feature-flag-audit)

**CRITICAL NEXT STEP - Research Phase (DO NOT SKIP)**:

⚠️  **Run `/ultra-research` BEFORE planning or development**

**Why Research is Essential**:
- Init creates basic templates with [NEEDS CLARIFICATION] markers
- Research completes these templates through interactive discovery
- Skipping research leads to: vague requirements, wrong tech choices, missing constraints

**Step-File Architecture** (17 steps, each with mandatory web search + structured output):
  - Steps 00-05: Product Discovery — Problem validation, opportunities, market sizing, competition, strategy, assumptions
  - Steps 10-11: User & Scenario — Personas with goals/pain points, user journey scenarios
  - Steps 20-22: Feature Definition — User stories, feature scope, success metrics
  - Steps 30-32: Architecture — Quality goals, tech stack decisions, module decomposition
  - Steps 40-41: Quality & Deploy — Infrastructure, CI/CD, risks, quality scenarios
  - Step 99: Synthesis — Validate completeness, generate research distillate for /ultra-plan

**ROI**: Each step writes structured output immediately to spec files with source citations

**After Research Completes**:
  - .ultra/specs/discovery.md: Validated opportunities, market data, strategy, and assumptions (§0-§5)
  - .ultra/specs/product.md: 100% complete (no [NEEDS CLARIFICATION] markers, §1-§6)
  - .ultra/specs/architecture.md: 100% complete with justified decisions (§1-§12)
  - .ultra/specs/research-distillate.md: Token-efficient summary for /ultra-plan consumption
  - .ultra/docs/research/*.md: Per-round research reports with confidence scores

**Then Run**: `/ultra-plan` to generate task breakdown from complete specs

**Important**: .ultra/specs/product.md is the source of truth

## Usage Examples

```bash
/ultra-init                           # Interactive mode (auto-detect)
/ultra-init MyProject                 # With project name
/ultra-init MyProject web             # With project type
/ultra-init MyProject api git         # With git initialization
```

## Success Criteria

- ✅ All directories created
- ✅ Config files valid JSON
- ✅ Git initialized (if requested)
- ✅ Templates generated
- ✅ User guidance provided

## Next Steps (CRITICAL - Follow This Order)

### Step 1: Run `/ultra-research` (MANDATORY)

**DO NOT skip research!** This is the most important phase.

**Step-File Architecture** (17 focused steps with mandatory web search + structured output templates):
- Steps 00-05: Product Discovery — Problem, opportunities, market, competition, strategy, assumptions
- Steps 10-11: User & Scenario — Personas, user journey scenarios
- Steps 20-22: Feature Definition — Stories, scope, metrics
- Steps 30-32: Architecture — Context, tech stack, modules
- Steps 40-41: Quality & Deploy — Infrastructure, risks
- Step 99: Synthesis — Completeness validation + research distillate

**Output**:
- ✅ .ultra/specs/discovery.md: §0-§5 with source citations
- ✅ .ultra/specs/product.md: §1-§6 complete (all [NEEDS CLARIFICATION] filled)
- ✅ .ultra/specs/architecture.md: §1-§12 with justified decisions
- ✅ .ultra/specs/research-distillate.md: Token-efficient context for /ultra-plan
- ✅ .ultra/docs/research/*.md: Per-round reports with confidence scores

**Why This Matters**:
- Without research: Vague requirements → rework, wrong tech → refactor, missing constraints → fixes
- With research: Complete specs → accurate tasks, right tech → fast dev, known risks → proactive mitigation

### Step 2: Run `/ultra-plan` (After Research Completes)

Generate task breakdown from complete specifications:
- Reads .ultra/specs/product.md (now 100% complete)
- Reads .ultra/specs/architecture.md (now 100% complete)
- Generates tasks with dependencies and complexity estimates
- Saves to .ultra/tasks/tasks.json

### Step 3: Run `/ultra-dev` to Start Development

TDD workflow with quality gates and automatic git integration.

**Specification-Driven Workflow**:
- `.ultra/specs/product.md` - WHAT to build (completed in research)
- `.ultra/specs/architecture.md` - HOW to build (completed in research)
- `.ultra/tasks/tasks.json` - Task breakdown (generated from specs)
- `.ultra/tasks/contexts/` - Task context with change history

## Output Format

> Claude responds in Chinese per CLAUDE.md.

**Command icon**: 🏗️
