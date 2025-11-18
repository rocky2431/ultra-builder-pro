---
description: Initialize Ultra Builder Pro 4.0 project with native task management
argument-hint: <name> <type> <stack> [git]
allowed-tools: Read, Write, Bash, TodoWrite, Grep, Glob
---

# /ultra-init

## Purpose

Initialize Ultra Builder Pro 4.0 project structure with native task management.

## Arguments

- `$1`: Project name (if empty, use current directory name)
- `$2`: Project type (web/api/cli/fullstack/other, if empty, **auto-detect from dependencies**)
- `$3`: Tech stack (if empty, **auto-detect from package files**)
- `$4`: "git" to initialize git repo (optional)

## Pre-Execution Checks

**Phase 0: Project State Detection** (NEW in 4.2)

Detect project context before initialization:

1. **Check existing `.ultra/` directory**
   - If exists → Trigger re-initialization flow
   - Read existing config for comparison

2. **Detect project code files**
   - Node.js: `package.json`
   - Python: `requirements.txt`, `pyproject.toml`
   - Go: `go.mod`
   - Rust: `Cargo.toml`
   - Java: `pom.xml`, `build.gradle`

3. **Detect Git repository**
   - Check if `.git/` directory exists
   - Store result to `config.project.detectionContext.hasGit`
   - Use in interactive confirmation (show different Git options based on detection)

4. **Auto-detect project type and tech stack**
   - Frontend frameworks: React, Vue, Angular, Svelte
   - Backend frameworks: Express, FastAPI, Django, Gin
   - Testing: Jest, Playwright, Pytest
   - Build tools: Vite, Webpack, esbuild
   - Package managers: npm, yarn, pnpm, pip, go, cargo

5. **Store detection results**
   - Save to `config.project.detectionContext`
   - Use in interactive confirmation (show detected values with labels)

**Triggers interactive confirmation for**:
- Existing projects with code files
- Re-initialization scenarios
- Optional: `--interactive` flag

## Workflow

### 1. Collect Project Information (Smart Detection)

**Project name**: $1 or current directory name

**Project type**: $2 or auto-detect from existing files

**Detection sources**:
- Node.js: package.json dependencies (react/vue/next → web, express/koa → api, bin field → cli, hybrid → fullstack)
- Python: requirements.txt (flask/django/fastapi → api, streamlit/gradio → web)
- Go: go.mod (gin/echo/fiber → api)
- Rust: Cargo.toml (actix-web/rocket → api)
- Java: pom.xml / build.gradle dependencies

**Fallback**: Use AskUserQuestion with detected context hints

**Rationale**: "Infer the most useful likely action and proceed" (Claude 4.x Best Practices)

**Tech stack**: $3 or auto-detect (supports multiple stacks for fullstack projects)

**Detection by layer** (can coexist):
- **Frontend**: React/Vue/Next.js/Svelte + TypeScript
- **Backend**: Node.js/Python/Go/Rust + framework (Express/FastAPI/Gin/Actix)
- **Database**: PostgreSQL/MySQL/MongoDB

**Fullstack example**: `["React + TypeScript", "Node.js + Express", "PostgreSQL"]`

**Fallback**: Use AskUserQuestion with multi-select support

**Git initialization**: $4 = "git"

### 1.5. Interactive Confirmation (NEW in 4.2)

**Triggers for**:
- Existing projects with code files
- Re-initialization (`.ultra/` already exists)
- Optional: `--interactive` flag for new projects

**Process**:

1. **Ask project type** (multiSelect: true for hybrid projects)
   - Show detected types with "(detected)" label
   - Allow multi-selection (e.g., Web + API)
   - Options: Web, API, CLI, Fullstack, Other

2. **Ask tech stack** (multiSelect: true for fullstack projects)
   - Show detected stacks with "(detected)" label
   - Allow multi-selection (e.g., React + Node.js + PostgreSQL)
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
   - Overwrite (backup to `.ultra/backup/`)
   - Keep existing (update missing files only)
   - Cancel

**Implementation Note**: Use AskUserQuestion tool with Chinese prompts generated at runtime. Store detection results in `config.project.detectionContext` for reference.

**Output Language**: All prompts in Chinese at runtime (not hardcoded in this file)

### 2. Create Project Structure

Create `.ultra/` by copying from template (`.claude/.ultra-template/`):

**Core Files**:
- `config.json` - Project configuration (single source of truth)
- `constitution.md` - Project principles & development standards

**Specification-Driven Structure**:
- `specs/` - Specification source of truth
  - `product.md` - Product requirements & user stories
  - `architecture.md` - Architecture design & tech stack
  - `api-contracts/` - API specifications
  - `data-models/` - Data model definitions

**Task Management**:
- `tasks/tasks.json` - Native task tracking

**Documentation**:
- `docs/research/` - Research reports (/ultra-research outputs)
- `docs/decisions/` - Architecture Decision Records (ADRs with template)

**Additional Directories**:
- `changes/` - Feature proposals (OpenSpec pattern)
- `context-archive/` - Compressed context sessions

**Template Source**: All files copied from `.claude/.ultra-template/`

**Note**: Old projects using `docs/prd.md` and `docs/tech.md` are supported via fallback mechanism in commands

### 3. Initialize Configuration

Create `.ultra/config.json` (copied from `.claude/.ultra-template/config.json`):

**Key sections**:
- `project`: Name, type (array for hybrid projects), stack (array for fullstack), creation timestamp, detection context
- `context`: Token limits (200K), compression thresholds (green 60%, yellow 70%, orange 85%)
- `quality_gates`: Test coverage (≥80%), code quality (max 50 lines/function, max 3 nesting), Core Web Vitals (LCP<2.5s)
- `git`: Branch patterns (feat/task-{id}-{slug}), commit convention (conventional-commits), workflow strategy (independent)
- `paths`: Specifications (.ultra/specs/), tasks, research, decisions, context archive
- `tools`: MCP servers (context7, exa) and Skills enablement (9 skills)

**Auto-filled placeholders**:
- Project name, type, stack (from user input or detection)
- Created timestamp
- Detection context (frameworks, package manager, hasTests, hasCI, hasGit, detectedStacks)

**Complete schema**: See `.ultra-template/config.json` for full configuration structure

### 4. Initialize Task System

Create `.ultra/tasks/tasks.json`:
- Empty tasks array
- Metadata (version, project name, created timestamp)
- Stats initialization (total: 0, completed: 0)

### 5. Copy All Template Files

**Simply copy entire `.claude/.ultra-template/` directory to project's `.ultra/`**:

All files and directories are copied as-is from the template:
- Core files: `config.json`, `constitution.md`
- Specs: `specs/product.md`, `specs/architecture.md`, subdirectories
- Tasks: `tasks/tasks.json`
- Docs: `docs/decisions/`, `docs/research/`
- Additional: `changes/`, `context-archive/`

**Auto-fill placeholders**:
- Update `config.json` with actual project name, type, stack, created date
- Update `constitution.md` with "Last Updated" timestamp

**Backward Compatibility**:
Old projects using `docs/prd.md` and `docs/tech.md` are still supported via config-based fallback in commands (no symlinks created)

### 6. Git Integration (Based on User Choice)

**If user chose "Initialize Git repository"** or **"Reinitialize Git"**:
- If reinitializing: Backup existing `.git/` to `.git.backup.{timestamp}`
- Initialize repo: `git init`
- Create `.gitignore` (exclude .ultra/backups, secrets, build artifacts)
- Create basic `README.md` (if not exists)
- Suggest first commit: `git add . && git commit -m "feat: initialize Ultra Builder Pro 4.2"`

**If user chose "Keep existing Git repository"** or **"Don't use Git"**:
- Skip Git operations
- Log decision to `config.project.detectionContext.hasGit`

### 7. Display Success Summary

Show in Chinese:
- Directories created (specs/, changes/, tasks/, docs/)
- Configuration files generated (config.json, constitution.md)
- Task system initialized (tasks.json)
- Specification templates ready (product.md, architecture.md with [NEEDS CLARIFICATION] markers)

**CRITICAL NEXT STEP - Research Phase (DO NOT SKIP)**:

⚠️  **Run `/ultra-research` BEFORE planning or development**

**Why Research is Essential**:
- Init creates basic templates with [NEEDS CLARIFICATION] markers
- Research completes these templates through 6-dimensional interactive discovery
- Skipping research leads to: vague requirements, wrong tech choices, missing constraints

**Think-Driven Interactive Discovery** (50-70 minutes):
  - Round 1: Problem Discovery (20 min) - Understand WHY and WHAT
  - Round 2: Solution Exploration (20 min) - Define features and user stories
  - Round 3: Technology Selection (15 min) - Choose tech stack with 6D analysis
  - Round 4: Risk & Constraint Mapping (15 min) - Identify risks and mitigation

**ROI**: 70-minute investment saves 10+ hours of rework (8x+ return)

**After Research Completes**:
  - specs/product.md: 100% complete (no [NEEDS CLARIFICATION] markers)
  - specs/architecture.md: 100% complete with justified decisions
  - Research reports saved to docs/research/

**Then Run**: `/ultra-plan` to generate task breakdown from complete specs

**Important**: specs/product.md is the source of truth (docs/prd.md is a symlink for compatibility)

## Usage Examples

```bash
/ultra-init                                      # Interactive mode
/ultra-init MyProject web "Next.js + TS" git    # Full params
/ultra-init MyProject web                        # Partial params
/ultra-init MyProject api "FastAPI"              # Without git
```

## Success Criteria

- ✅ All directories created
- ✅ Config files valid JSON
- ✅ Git initialized (if requested)
- ✅ Templates generated
- ✅ User guidance provided

## Next Steps (CRITICAL - Follow This Order)

### Step 1: Run `/ultra-research` (MANDATORY - 50-70 minutes)

**DO NOT skip research!** This is the most important phase.

**Think-Driven Interactive Discovery**:
- Round 1: Problem Discovery (20 min) - 6D analysis of problem space
- Round 2: Solution Exploration (20 min) - Generate user stories with 6D analysis
- Round 3: Technology Selection (15 min) - Compare tech options with 6D matrix
- Round 4: Risk & Constraint Mapping (15 min) - Identify risks with mitigation

**Output**:
- ✅ specs/product.md: 100% complete (all [NEEDS CLARIFICATION] filled)
- ✅ specs/architecture.md: 100% complete with justified decisions
- ✅ Research reports: Saved to docs/research/

**Why This Matters**:
- Without research: Vague requirements → 2h rework, wrong tech → 5h refactor, missing constraints → 3h fixes
- With research: Complete specs → accurate tasks, right tech → fast dev, known risks → proactive mitigation
- ROI: 10 hours saved / 1.2 hours invested = **8.3x return**

### Step 2: Run `/ultra-plan` (After Research Completes)

Generate task breakdown from complete specifications:
- Reads specs/product.md (now 100% complete)
- Reads specs/architecture.md (now 100% complete)
- Generates tasks with dependencies and complexity estimates
- Saves to .ultra/tasks/tasks.json

### Step 3: Run `/ultra-dev` to Start Development

TDD workflow with quality gates and automatic git integration.

### Optional: Customize `.ultra/constitution.md`

Review and adjust the 9 core principles for your project.

**Specification-Driven Workflow**:
- `specs/product.md` - WHAT to build (completed in research)
- `specs/architecture.md` - HOW to build (completed in research)
- `tasks.json` - Task breakdown (generated from specs)
- `changes/` - Feature proposals (during development)

## Output Format

**Standard output structure**: See `@config/ultra-command-output-template.md` for the complete 6-section format.

**Command icon**: 🏗️

**Example output**: See template Section 7.1 for ultra-init specific example.
