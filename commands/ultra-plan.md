---
description: Task planning with intelligent dependency analysis and complexity assessment
argument-hint: [scope]
allowed-tools: Read, Write, Bash, TodoWrite, Grep, Glob, Task
---

# /ultra-plan

## Purpose

Generate task breakdown from complete specifications (created by /ultra-research).

**IMPORTANT**: This command assumes specs are 100% complete. If specs are incomplete, you MUST run /ultra-research first.

## Pre-Execution Checks

### Mandatory: Specification Completeness Validation

**Check both files exist and are complete**:
- `.ultra/specs/product.md` (new projects) or `docs/prd.md` (old projects)
- `.ultra/specs/architecture.md` (new projects) or `docs/tech.md` (old projects)

**Validation criteria**:
- ❌ **BLOCK if**: File has [NEEDS CLARIFICATION] markers → Force return to /ultra-research
- ❌ **BLOCK if**: File is empty or missing → Force return to /ultra-research
- ❌ **BLOCK if**: Required sections are missing → Force return to /ultra-research
- ✅ **PROCEED if**: All sections complete, no [NEEDS CLARIFICATION] markers

**If validation fails**, output (example structure - output in Chinese at runtime):
```
⚠️  Specifications incomplete, cannot generate task plan

Detection results:
- .ultra/specs/product.md: [status]
- .ultra/specs/architecture.md: [status]

Issues:
- [Specific missing or incomplete sections]

Solution:
Run /ultra-research to complete specifications

/ultra-research will complete specs through 4-round Think-Driven Discovery:
- Round 1: Problem Discovery
- Round 2: Solution Exploration
- Round 3: Technology Selection
- Round 4: Risk & Constraint Mapping

After completion, specs will be 100% filled, then run /ultra-plan
```

### Optional Checks

- Detect project structure: .ultra/specs/ (new) or docs/ (old)?
- Check for recent research in `.ultra/docs/research/` → Use recommendations as basis
- Check for existing tasks in `.ultra/tasks/tasks.json` → Ask whether to replace/extend/cancel
- Clarify scope: Full project plan vs specific feature tasks

## Workflow

### 0. Detect Project Structure (Auto)

**Determine specification source**:
```
IF .ultra/specs/product.md exists:
  specification_file = ".ultra/specs/product.md"
ELSE IF docs/prd.md exists:
  specification_file = "docs/prd.md"  (old project)
ELSE:
  ERROR: No specification found → Force return to /ultra-research
```

### 1. Requirements Analysis

**Load specification** (must be complete):
- Primary: `.ultra/specs/product.md` (new projects)
- Fallback: `docs/prd.md` (old projects)
- If missing/incomplete: BLOCK and force return to /ultra-research

**Extract**:
- Functional requirements
- Technical requirements
- Constraints
- Priorities
- Success metrics

**Validate** (should already pass due to Pre-Execution Checks):
- ✅ No [NEEDS CLARIFICATION] markers remain
- ✅ All user stories have acceptance criteria
- ✅ NFRs are measurable
- ✅ All required sections present and complete

**If validation fails**: Output error message (in Chinese) and suggest running /ultra-research

### 2. Task Generation

Generate tasks with:
- **Clear title**: Action verb + specific target (e.g., "Implement user authentication with JWT")
- **Detailed description**: What, why, acceptance criteria
- **Complexity (1-10)**: Simple (1-3), Medium (4-6), Complex (7-10)
- **Priority (P0-P3)**: P0 (blockers), P1 (important), P2 (nice-to-have), P3 (future)
- **Dependencies**: List prerequisite task IDs
- **Estimated effort**: Days (dev + test + doc)
- **Type** (NEW): architecture | feature | bugfix
- **Trace to** (NEW): Auto-generated link to source requirement

**Auto-generate trace_to field** (new projects with .ultra/specs/ only):

1. **Parse specification file** (.ultra/specs/product.md):
   - Extract all markdown headers with IDs or create IDs from header text
   - Map functional requirements, user stories, and features to header IDs
   - Example: "## User Authentication" → `#user-authentication`

2. **Match task to requirement**:
   - Analyze task title and description
   - Find matching section in .ultra/specs/product.md using keyword matching
   - Example: Task "Implement JWT authentication" → `.ultra/specs/product.md#user-authentication`

3. **trace_to format**:
   - New projects: `.ultra/specs/product.md#section-id`
   - Architecture tasks: `.ultra/specs/architecture.md#technology-decision`
   - Old projects: Omit trace_to field (backward compatibility)

4. **Validation**:
   - Verify linked section exists in specification file
   - Warn if no matching requirement found (manual review needed)
   - Ensure 100% requirement coverage (every spec section has at least one task)

**For complex tasks** (>6): Consider delegating to `ultra-architect-agent` for breakdown.

### 3. Dependency Analysis

- Build dependency graph
- Detect cycles (error if found)
- Order tasks topologically
- Identify parallel opportunities

### 4. Save Tasks

Save to `.ultra/tasks/tasks.json`:
```json
{
  "version": "4.3",
  "created": "YYYY-MM-DD HH:mm:ss",
  "tasks": [
    {
      "id": "1",
      "title": "Task title",
      "description": "Details",
      "complexity": 5,
      "priority": "P0",
      "dependencies": [],
      "estimated_days": 2,
      "status": "pending",
      "type": "feature",
      "trace_to": ".ultra/specs/product.md#user-story-001"
    }
  ]
}
```

**Note**: `type` and `trace_to` are optional for backward compatibility

### 5. Update Project Context

**After tasks saved, trigger documentation sync:**

1. **Update CLAUDE.md** (via syncing-docs skill):
   - Update "Current Focus" section with first pending task
   - Ensure project context reflects new task list

2. **Initialize feature-status.json** (via syncing-status skill):
   - Create entries for each task in `.ultra/docs/feature-status.json`
   - Set initial status to "pending" for all tasks

### 6. Report & Suggest Next Step

Output summary in Chinese:
- Total tasks generated
- Priority distribution (P0/P1/P2)
- Complexity distribution
- Dependency count, cyclic dependencies
- Estimated total effort
- Parallel opportunities
- **Traceability** (new projects):
  - Tasks with trace_to links: X/Y (percentage)
  - Specification coverage: All sections covered / Missing coverage warnings
  - Orphaned requirements: Spec sections with no tasks (if any)
- First task details
- Suggest running `/ultra-dev` to start

## Quality Standards

- ✅ 100% requirement coverage
- ✅ Clear acceptance criteria for all tasks
- ✅ No circular dependencies
- ✅ Realistic complexity estimates
- ✅ Action-verb task titles

## Integration

- **Prerequisites**:
  - `/ultra-research` must complete first (creates specs 100% complete)
  - OR specs manually created and complete (old workflow)
- **Skills**:
  - `syncing-docs`: Updates CLAUDE.md "Current Focus" section
  - `syncing-status`: Initializes feature-status.json entries
- **Input**:
  - `.ultra/specs/product.md` (new projects, created by /ultra-research)
  - `.ultra/specs/architecture.md` (new projects, created by /ultra-research)
  - `docs/prd.md` (old projects, backward compatibility)
  - `docs/tech.md` (old projects, backward compatibility)
- **Output**:
  - `.ultra/tasks/tasks.json` (task definitions)
  - `.ultra/docs/feature-status.json` (status tracking)
  - `CLAUDE.md` (updated "Current Focus")
- **Context**: Research reports in `.ultra/docs/research/` (created by /ultra-research)
- **Next**: `/ultra-dev` to start development

**Workflow Sequence**:
```
/ultra-init → /ultra-research → /ultra-plan → /ultra-dev
```

## Backward Compatibility

**Old projects** (without .ultra/specs/):
- Reads from `docs/prd.md` and `docs/tech.md`
- tasks.json created without `type` and `trace_to` fields
- No /ultra-research requirement (manual spec creation acceptable)
- Zero breaking changes for existing projects

**New projects** (with .ultra/specs/):
- Requires /ultra-research to create `.ultra/specs/product.md` and `.ultra/specs/architecture.md` first
- Reads from `.ultra/specs/product.md` and `.ultra/specs/architecture.md`
- tasks.json includes `type` and `trace_to` fields
- 100% specification completeness enforced

**Migration Path** (old → new):
- Run `/ultra-init` to create .ultra/specs/ structure
- Copy `docs/prd.md` → `.ultra/specs/product.md`
- Copy `docs/tech.md` → `.ultra/specs/architecture.md`
- Future planning will use new structure

## Output Format


**Command icon**: 📋

**Example output**: See template Section 7.3 for ultra-plan specific example.
