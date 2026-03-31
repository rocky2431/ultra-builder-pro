---
description: Task planning with intelligent dependency analysis and complexity assessment
argument-hint: [scope]
allowed-tools: Read, Write, Edit, Bash(mkdir .ultra/*), Grep, Glob, Task, AskUserQuestion
model: opus
---

# /ultra-plan

## Workflow Tracking (MANDATORY)

**On command start**, create tasks for each major step using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 0 | Specification Validation | Validating specs... |
| 1 | Requirements Analysis | Analyzing requirements... |
| 2 | Codebase Analysis | Analyzing codebase... |
| 3 | Task Generation | Generating tasks... |
| 4 | Dependency Analysis | Analyzing dependencies... |
| 5 | Save Tasks | Saving tasks to files... |
| 6 | Generate Report | Generating report... |

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**On context recovery**: `TaskList` → resume from last incomplete step

---

## Purpose

Generate task breakdown from complete specifications (created by /ultra-research).

## Step 0: Scope Mode Selection

Use AskUserQuestion to determine planning posture before any analysis:

| Mode | Posture | When to Use |
|------|---------|-------------|
| **EXPAND** | Challenge scope upward. For each task, ask "what would make this 10x better for 2x effort?" Surface expansion opportunities as individual AskUserQuestion decisions. | New product, greenfield, user wants to think bigger |
| **SELECTIVE** | Hold current scope as baseline. Surface optional expansions individually — user cherry-picks. Neutral recommendation posture. | Most common. Existing product, feature work. |
| **HOLD** | Scope is locked. Make it bulletproof — catch every failure mode, test every edge case. Do not add or remove scope. | User has clear requirements, just needs execution plan |
| **REDUCE** | Find the minimum viable version. Cut everything non-essential. Be ruthless. | Time pressure, MVP, proof of concept |

**Default**: SELECTIVE (if user doesn't specify)

**Commitment rule**: Once mode is selected, COMMIT to it. Do not silently drift. EXPAND mode does not argue for less work. REDUCE mode does not sneak scope back in.

**Dual-scale effort** (show on every expansion decision in EXPAND/SELECTIVE mode):
`Complete: ~X LOC, AI ~Y min | Shortcut: ~X LOC, saves Y min but ___`

---

## Pre-Execution Checks

### Specification Completeness Validation

**Check all files exist and are complete**:
- `.ultra/specs/product.md`
- `.ultra/specs/architecture.md`
- `.ultra/specs/research-distillate.md` (preferred primary context — if exists, use it)

**Field-level validation checklist** (not just "file exists"):

**discovery.md** (if exists):
- [ ] §0 Problem Validation — has demand signal + confidence %
- [ ] §2 Market Assessment — has TAM/SAM/SOM with numeric values + sources
- [ ] §3 Competitive Landscape — has ≥2 competitors in comparison matrix
- [ ] §4 Product Strategy — has ≥3 strategic trade-offs stated

**product.md**:
- [ ] §2 Personas — has ≥2 personas with goals + pain points
- [ ] §3 Scenarios — has ≥3 scenarios with current + desired flow
- [ ] §4 User Stories — all stories have acceptance criteria (Given/When/Then)
- [ ] §5 Feature Scope — has Features Out section with rationale
- [ ] §6 Success Metrics — North Star metric has specific numeric target

**architecture.md**:
- [ ] §1 Quality Goals — has ≥3 goals with measurable scenarios
- [ ] §4 Solution Strategy — tech stack choices have rationale + source URL
- [ ] §5 Building Blocks — modules map to features
- [ ] §6 Runtime Scenarios — ≥1 scenario with data flow

**Validation criteria**:
- ❌ **BLOCK if**: File has [NEEDS CLARIFICATION] markers
- ❌ **BLOCK if**: File is empty or missing
- ❌ **BLOCK if**: Any checklist item above fails
- ✅ **PROCEED if**: All items pass

**If validation fails**:
```
⚠️  Specifications incomplete

Failed checks:
- [Specific checklist items that failed]

Solution: Run /ultra-research to fill gaps (step-file architecture will target specific sections)
```

### Optional Checks

- Check for `.ultra/specs/research-distillate.md` → Use as primary context (token-efficient)
- Check for existing tasks → Ask whether to replace/extend/cancel
- Clarify scope: Full project plan vs specific feature tasks

## Workflow

### 1. Requirements Analysis

**Load specifications** (prefer distillate when available):
- `.ultra/specs/research-distillate.md` - Token-efficient summary (PRIMARY if exists)
- `.ultra/specs/discovery.md` - Market context, strategy, assumptions
- `.ultra/specs/product.md` - User stories, features
- `.ultra/specs/architecture.md` - Technical decisions

**Extract**:
- Functional requirements (product.md §4)
- Technical constraints (architecture.md §2)
- Quality requirements (architecture.md §10)
- Success metrics (product.md §6)

### 2. Codebase Analysis

**Analyze existing codebase for AI-executable context**:

1. **Directory structure**: Identify src/, tests/, config/ patterns
2. **Existing patterns**: Find similar implementations to reference
3. **Tech stack detection**: Framework versions, test runners, build tools
4. **Naming conventions**: File naming, function naming, variable naming

### 3. Task Generation

**Output structure**:
```
.ultra/tasks/
├── tasks.json           # Lightweight registry
└── contexts/
    ├── task-1.md        # Full context for task 1
    ├── task-2.md        # Full context for task 2
    └── ...
```

**tasks.json fields**:

| Field | Purpose |
|-------|---------|
| `id`, `title` | Identification |
| `type` | architecture / feature / bugfix |
| `priority` | P0 / P1 / P2 / P3 |
| `complexity` | 1-10 |
| `status` | pending / in_progress / completed / blocked |
| `dependencies` | Prerequisite task IDs |
| `estimated_days` | Effort estimate |
| `context_file` | Path to context MD file |
| `trace_to` | Spec section reference |

**task-{id}.md structure**:

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
```bash
# Command to verify this task works
```

## Trace
**Source**: `.ultra/specs/product.md#section-id`

## Change Log
| Date | Change | Specs Updated | Reason |
|------|--------|---------------|--------|
| {date} | Initial creation | - | Generated by /ultra-plan |

## Completion
> _Fill when task completed_
- **Completed**: {date}
- **Commit**: {hash}
- **Summary**: {brief description}
```

**Task granularity**:
- Ideal complexity: 3-5 (completable in one session)
- Too large (>6): Break down into subtasks
- Too small (<3): Merge with related tasks

**Integration task generation**:

After generating feature tasks, insert these integration tasks:

1. **Walking Skeleton** (always Task #1, Priority P0):
   - Title: "Walking skeleton: {primary use case} end-to-end"
   - Type: `architecture`
   - Must touch all layers: entry point → use case → domain → persistence
   - Acceptance: One real request returns real data through all layers

2. **Contract Definition** (when specs show component boundaries):
   - Title: "Define contract: {component A} ↔ {component B}"
   - Type: `architecture`
   - Must PRECEDE implementation tasks for both sides
   - Acceptance: Shared interface/schema exists, contract test validates compatibility

3. **Integration Checkpoint** (every 3-4 feature tasks):
   - Title: "Integration checkpoint: verify {feature group} connectivity"
   - Type: `architecture`
   - Acceptance: All components from recent tasks communicate correctly end-to-end

### 4. Dependency Analysis

- Build dependency graph
- Detect cycles (error if found)
- Order tasks topologically
- Identify parallel opportunities
- Validate vertical slicing: Flag any task touching only one layer. If found, split into vertical slices or merge with related tasks
- Walking skeleton (Task #1) has no dependencies and blocks all feature tasks
- Contract tasks precede their consumer implementation tasks

### 5. Save Tasks (MANDATORY)

**CRITICAL**: BOTH tasks.json AND all context files MUST be created. Do not proceed until verified.

**5.1 Create directory structure**:
```bash
mkdir -p .ultra/tasks/contexts
```

**5.2 Save tasks.json**:
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

**5.3 Generate context file for EACH task**:

For every task in tasks.json, create `.ultra/tasks/contexts/task-{id}.md` using the template structure defined above.

**5.4 Verify ALL outputs exist**:
- Read tasks.json → count tasks
- List `.ultra/tasks/contexts/` → count files
- **If counts don't match → create missing context files before proceeding**

### 6. Report

Output summary:
- Total tasks generated
- Priority distribution (P0/P1/P2)
- Complexity distribution
- Dependency count
- Estimated total effort
- Traceability coverage
- First task details
- Suggest `/ultra-dev` to start

## Quality Standards

- ✅ 100% requirement coverage
- ✅ Clear acceptance criteria for all tasks
- ✅ No circular dependencies
- ✅ Realistic complexity estimates
- ✅ Action-verb task titles
- ✅ Walking skeleton is Task #1
- ✅ Every feature task touches ≥ 2 layers (vertical slice)
- ✅ Integration checkpoint every 3-4 feature tasks
- ✅ Contract tasks precede cross-boundary implementations

## Integration

- **Prerequisites**: `/ultra-research` (specs must be complete)
- **Input**: `.ultra/specs/discovery.md` (optional), `.ultra/specs/product.md`, `.ultra/specs/architecture.md`
- **Output**: `.ultra/tasks/tasks.json`, `.ultra/tasks/contexts/*.md`
- **Next**: `/ultra-dev`

**Workflow**:
```
/ultra-init → /ultra-research → /ultra-plan → /ultra-dev
```
