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

3. **Auto-detect project type and tech stack**
   - Frontend frameworks: React, Vue, Angular, Svelte
   - Backend frameworks: Express, FastAPI, Django, Gin
   - Testing: Jest, Playwright, Pytest
   - Build tools: Vite, Webpack, esbuild
   - Package managers: npm, yarn, pnpm, pip, go, cargo

4. **Store detection results**
   - Save to `config.project.detectionContext`
   - Use in interactive confirmation (show detected values with labels)

**Triggers interactive confirmation for**:
- Existing projects with code files
- Re-initialization scenarios
- Optional: `--interactive` flag

## Workflow

### 1. Collect Project Information (Smart Detection)

**Project name**: $1 or current directory name

**Project type**: $2 or auto-detect:
```javascript
// 1. Check package.json (Node.js projects)
if (dependencies['react'] || dependencies['vue'] || dependencies['next']) → type = "web"
if (dependencies['express'] || dependencies['fastapi'] || dependencies['koa']) → type = "api"
if (package.json has 'bin' field) → type = "cli"
if (both frontend + backend dependencies exist) → type = "fullstack"

// 2. Check Python projects
if (requirements.txt exists):
  if (flask or django or fastapi in requirements) → type = "api"
  if (streamlit or gradio in requirements) → type = "web"

// 3. Check Go projects
if (go.mod exists):
  if (gin or echo or fiber in go.mod) → type = "api"

// 4. Check Rust projects
if (Cargo.toml exists):
  if ([dependencies] has actix-web or rocket) → type = "api"

// 5. Fallback: Use AskUserQuestion with detected context
if (no clear detection) → AskUserQuestion with hints from file structure
```

**Tech stack**: $3 or auto-detect:
```javascript
// Frontend detection
if (dependencies['react'] && dependencies['typescript']) → "react-ts"
if (dependencies['vue'] && dependencies['typescript']) → "vue-ts"
if (dependencies['next']) → "next-ts"
if (dependencies['svelte']) → "svelte-ts"

// Backend detection
if (dependencies['express'] && dependencies['typescript']) → "node-ts"
if (requirements.txt + flask) → "python-flask"
if (requirements.txt + fastapi) → "python-fastapi"
if (go.mod exists) → "go"
if (Cargo.toml exists) → "rust"

// Fallback: "other" or ask user with detected hints
```

**Rationale**: "Infer the most useful likely action and proceed" (Claude 4.x Best Practices)

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

2. **Ask tech stack** (single selection)
   - Show detected stack with "(detected)" label
   - Options based on detected package files
   - Fallback: Custom input

3. **Ask re-initialization handling** (if `.ultra/` exists)
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
```json
{
  "version": "4.2",
  "project": {
    "name": "[AUTO-FILLED]",
    "type": ["[AUTO-FILLED]"],  // Array format for multi-type support (NEW in 4.2)
    "stack": "[AUTO-FILLED]",
    "created": "[AUTO-FILLED]",
    "detectionContext": {       // NEW in 4.2: Store detection metadata
      "frameworks": {
        "frontend": [],
        "backend": [],
        "testing": [],
        "buildTools": []
      },
      "packageManager": null,
      "hasTests": false,
      "hasCI": false
    }
  },
  "structure": "specs",
  "context": {
    "total_limit": 200000,
    "thresholds": {
      "green": 0.60,
      "yellow": 0.70,
      "orange": 0.85,
      "red": 0.95
    },
    "compression": {
      "trigger_task_count": 5,
      "target_ratio": 0.10,
      "archive_path": ".ultra/context-archive/"
    }
  },
  "quality_gates": {
    "test_coverage": {
      "overall": 0.80,
      "critical_paths": 1.00,
      "branch": 0.75,
      "function": 0.85
    },
    "code_quality": {
      "max_function_lines": 50,
      "max_nesting_depth": 3,
      "max_complexity": 10,
      "max_duplication_lines": 3
    },
    "frontend": {
      "core_web_vitals": {
        "lcp_ms": 2500,
        "inp_ms": 200,
        "cls": 0.1
      }
    }
  },
  "git": {
    "branch_patterns": {
      "feature": "feat/task-{id}-{slug}",
      "bugfix": "fix/bug-{id}-{slug}",
      "refactor": "refactor/{slug}"
    },
    "commit": {
      "convention": "conventional-commits",
      "co_author": "Claude <noreply@anthropic.com>"
    },
    "workflow": {
      "strategy": "independent",
      "auto_branch_naming": true,
      "merge_strategy": "no-ff"
    }
  },
  "paths": {
    "tasks": ".ultra/tasks/tasks.json",
    "specs": {
      "product": "specs/product.md",
      "architecture": "specs/architecture.md"
    },
    "docs_legacy": {
      "prd": "docs/prd.md",
      "tech": "docs/tech.md"
    },
    "research": ".ultra/docs/research/",
    "decisions": "docs/decisions/",
    "context_archive": ".ultra/context-archive/",
    "changes": ".ultra/changes/"
  },
  "tools": {
    "mcp": {
      "context7": true,
      "exa": true
    },
    "skills": {
      "guarding-code-quality": true,
      "guarding-test-coverage": true,
      "guarding-git-safety": true,
      "guarding-ui-design": true,
      "syncing-docs": true,
      "automating-e2e-tests": true,
      "compressing-context": true,
      "guiding-workflow": true,
      "enforcing-workflow": true
    }
  }
}
```

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

### 6. Git Integration (Optional)

If `$4 = "git"`:
- Initialize repo: `git init`
- Create `.gitignore` (exclude backups, secrets, build artifacts)
- Create basic `README.md`
- Suggest first commit

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
