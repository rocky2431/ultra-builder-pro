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
- Round 1: User & Scenario Discovery (product.md §1-3)
- Round 2: Feature Definition (product.md §4-5)
- Round 3: Architecture Design (architecture.md §1-6)
- Round 4: Quality & Deployment (architecture.md §7-12)

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
- ✅ Success metrics are measurable (product.md §6)
- ✅ All required sections present and complete

**If validation fails**: Output error message (in Chinese) and suggest running /ultra-research

### 2. Codebase Analysis (New Projects Only)

**Analyze existing codebase to provide AI-executable context**:

1. **Directory structure**: Identify src/, tests/, config/ patterns
2. **Existing patterns**: Find similar implementations to reference
3. **Tech stack detection**: Framework versions, test runners, build tools
4. **Naming conventions**: File naming, function naming, variable naming

**Output**: Cached analysis for use in task generation

### 3. Task Generation (Split Architecture)

**Core principle**: Separate metadata (JSON) from context (Markdown) for better maintainability.

**Output structure**:
```
.ultra/tasks/
├── tasks.json           # Lightweight registry (metadata only)
└── contexts/
    ├── task-1.md        # Full context for task 1
    ├── task-2.md        # Full context for task 2
    └── ...
```

**tasks.json** (lightweight - only metadata):

| Field | Purpose |
|-------|---------|
| `id`, `title` | Identification |
| `type` | architecture / feature / bugfix |
| `priority`, `complexity` | Planning |
| `status` | pending / in_progress / completed / blocked |
| `dependencies` | Execution order |
| `estimated_days` | Effort estimate |
| `context_file` | Path to context MD file |
| `trace_to` | Spec linkage for human review |

**task-{id}.md** (full context - human readable):

```markdown
# Task {id}: {title}

> **Status**: pending | **Priority**: P0 | **Complexity**: 4

## Context
**What**: [Clear description]
**Why**: [Business value + Persona/Scenario link]
**Constraints**:
- [Constraint 1]
- [Constraint 2]

## Implementation
**Target Files**:
- `path/to/file.ts` (create)
- `path/to/existing.ts` (modify: description)

**Pattern**: [Reference to existing code]
**Tech Notes**: [Framework/library guidance]

## Acceptance
**Tests**:
- [ ] `test command`
- [ ] Pass: [scenario description]

**Verification**:
\`\`\`bash
curl -X POST localhost:3000/api/example
\`\`\`

## Trace
**Source**: `.ultra/specs/product.md#section-id`

## Change Log
| Date | Change | Reason |
|------|--------|--------|
```

**Benefits of split architecture**:
- tasks.json stays small (~2KB vs ~50KB)
- Context files are human-editable Markdown
- Git diff shows only changed task files
- Parallel development without merge conflicts
- AI reads only current task context (token efficient)

**Task granularity guideline**:
- Ideal complexity: 3-5 (completable in one session)
- Too large (>6): Break down using ultra-architect-agent
- Too small (<3): Merge with related tasks

### 4. Dependency Analysis

- Build dependency graph
- Detect cycles (error if found)
- Order tasks topologically
- Identify parallel opportunities

### 5. Save Tasks (Split Output)

**Step 1**: Create contexts directory (if not exists):
```bash
mkdir -p .ultra/tasks/contexts
```

**Step 2**: Save lightweight tasks.json:
```json
{
  "version": "4.4",
  "created": "YYYY-MM-DD HH:mm:ss",
  "tasks": [
    {
      "id": "1",
      "title": "Implement JWT login endpoint",
      "type": "feature",
      "priority": "P0",
      "complexity": 4,
      "status": "pending",
      "dependencies": [],
      "estimated_days": 2,
      "context_file": "contexts/task-1.md",
      "trace_to": ".ultra/specs/product.md#user-authentication"
    }
  ]
}
```

**Step 3**: Generate context file for each task (`.ultra/tasks/contexts/task-{id}.md`):
```markdown
# Task 1: Implement JWT login endpoint

> **Status**: pending | **Priority**: P0 | **Complexity**: 4

## Context
**What**: Create POST /api/auth/login endpoint with JWT token generation
**Why**: Users need secure authentication (Persona: Developer, Scenario: Daily Login)
**Constraints**:
- Use bcrypt for password verification
- JWT expires in 24h
- Return 401 on failure without exposing details

## Implementation
**Target Files**:
- `src/api/auth/login.ts` (create)
- `src/api/auth/index.ts` (modify: add route)
- `src/types/auth.ts` (create)

**Pattern**: Follow existing endpoint pattern in `src/api/users/`
**Tech Notes**: Express.js + jsonwebtoken + bcrypt

## Acceptance
**Tests**:
- [ ] `npm test -- --grep 'POST /api/auth/login'`
- [ ] Pass: valid credentials → 200 + token
- [ ] Pass: invalid password → 401

**Verification**:
\`\`\`bash
curl -X POST localhost:3000/api/auth/login -d '{"email":"test@example.com","password":"test"}'
\`\`\`

## Trace
**Source**: `.ultra/specs/product.md#user-authentication`

## Change Log
| Date | Change | Reason |
|------|--------|--------|
| {date} | Initial creation | Generated by /ultra-plan |
```

**Backward compatibility**: Old projects without `context_file` field still work (ultra-dev reads embedded context or trace_to)

### 6. Update Project Context

**After tasks saved, trigger documentation sync:**

1. **Update CLAUDE.md** (via syncing-docs skill):
   - Update "Current Focus" section with first pending task
   - Ensure project context reflects new task list

2. **Initialize feature-status.json** (via syncing-status skill):
   - Create entries for each task in `.ultra/docs/feature-status.json`
   - Set initial status to "pending" for all tasks

### 7. Report & Suggest Next Step

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
