---
description: Initialize Ultra Builder Pro 5.0 project with native task management
argument-hint: <name> <type> <stack> [git]
allowed-tools: Read, Write, Bash, TodoWrite, Grep, Glob, AskUserQuestion
model: opus
---

# /ultra-init

## Purpose

Initialize Ultra Builder Pro 4.4 project structure with native task management.

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

**Specification-Driven Structure**:
- `.ultra/specs/` - Specification source of truth
  - `product.md` - Problem Statement, Personas, User Scenarios, User Stories, Features Out, Success Metrics (§1-6)
  - `architecture.md` - arc42 structure (§1-12)

**Task Management**:
- `.ultra/tasks/tasks.json` - Native task tracking

**Documentation**:
- `.ultra/docs/research/` - Research reports (/ultra-research outputs)

**Template Source**: All files copied from `~/.claude/.ultra-template/`


### 3. Initialize Task System

Create `.ultra/tasks/tasks.json`:
- Empty tasks array
- Metadata (version, project name, created timestamp)
- Stats initialization (total: 0, completed: 0)

### 4. Copy All Template Files

**Copy `~/.claude/.ultra-template/` contents to `.ultra/`:**

- Specs: `specs/product.md`, `specs/architecture.md`
- Tasks: `tasks/tasks.json`, `tasks/contexts/TEMPLATE.md`
- Status: `test-report.json`, `delivery-report.json`
- Docs: `docs/research/README.md`

### 5. Git Integration (Based on User Choice)

**If user chose "Initialize Git repository"** or **"Reinitialize Git"**:
- If reinitializing: Backup existing `.git/` to `.git.backup.{timestamp}`
- Initialize repo: `git init`
- Create `.gitignore`:
  - Exclude `.ultra/backups`
  - Exclude secrets, build artifacts
- Create basic `README.md` (if not exists)
- Suggest first commit: `git add . && git commit -m "feat: initialize Ultra Builder Pro 4.4"`

**If user chose "Keep existing Git repository"** or **"Don't use Git"**:
- Skip Git operations

### 6. Display Success Summary

Show in Chinese:
- Directories created (.ultra/specs/, .ultra/tasks/, .ultra/docs/)
- Template files copied
- Task system initialized (tasks.json)
- Status files initialized (test-report.json, delivery-report.json)
- Specification templates ready (product.md, architecture.md with [NEEDS CLARIFICATION] markers)

**CRITICAL NEXT STEP - Research Phase (DO NOT SKIP)**:

⚠️  **Run `/ultra-research` BEFORE planning or development**

**Why Research is Essential**:
- Init creates basic templates with [NEEDS CLARIFICATION] markers
- Research completes these templates through interactive discovery
- Skipping research leads to: vague requirements, wrong tech choices, missing constraints

**Think-Driven Interactive Discovery**:
  - Round 1: User & Scenario - Define personas and user scenarios (§1-3)
  - Round 2: Feature Definition - Define features and success metrics (§4-6)
  - Round 3: Architecture Design - Design system architecture (arch §1-6)
  - Round 4: Quality & Deployment - Define quality and deployment (arch §7-12)

**ROI**: Thorough research saves significant rework

**After Research Completes**:
  - .ultra/specs/product.md: 100% complete (no [NEEDS CLARIFICATION] markers)
  - .ultra/specs/architecture.md: 100% complete with justified decisions
  - Research reports saved to .ultra/docs/research/

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

**Think-Driven Interactive Discovery**:
- Round 1: User & Scenario - Define personas and user scenarios (§1-3)
- Round 2: Feature Definition - Define features and success metrics (§4-6)
- Round 3: Architecture Design - Design system architecture (arch §1-6)
- Round 4: Quality & Deployment - Define quality and deployment (arch §7-12)

**Output**:
- ✅ .ultra/specs/product.md: 100% complete (all [NEEDS CLARIFICATION] filled)
- ✅ .ultra/specs/architecture.md: 100% complete with justified decisions
- ✅ Research reports: Saved to .ultra/docs/research/

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
