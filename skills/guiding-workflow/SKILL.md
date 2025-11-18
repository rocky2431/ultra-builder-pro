---
name: guiding-workflow
description: "Guides next workflow steps based on project state and Scenario B routing. TRIGGERS: After phase completion (/ultra-research, /ultra-plan, /ultra-dev, /ultra-test, /ultra-deliver), user asks 'what's next' or seems uncertain, detecting incomplete specs with [NEEDS CLARIFICATION]. ACTIONS: Detect filesystem state (specs/, tasks.json, git status), detect Scenario B project type (New Project/Incremental Feature/Tech Decision), suggest optimal next command with rationale. DO NOT TRIGGER: Mid-task execution, during active coding, user has clear next step."
allowed-tools: Read, Glob
---

# Workflow Guide

## Purpose
Suggest the next logical command using filesystem signals and Scenario B intelligent routing context.

## When
- After a phase completes (research/plan/dev/test/deliver)
- User asks for guidance or next steps
- User seems uncertain after command completion
- After /ultra-research completes (detect project type for tailored suggestions)

## Do

### 1. Detect Project State via Filesystem

**Specification files**:
- New format: `specs/product.md`, `specs/architecture.md`
- Old format: `.ultra/docs/prd.md`, `.ultra/docs/tech.md`

**Other signals**:
- Research files: `.ultra/docs/research/*.md`
- Task plan: `.ultra/tasks/tasks.json`
- Code changes: `git status`
- Test files: `*.test.*`, `*.spec.*`
- Active changes: `.ultra/changes/task-*/`

### 2. Check Specification Completeness

- If specs have `[NEEDS CLARIFICATION]` markers → Suggest `/ultra-research`
- If specifications complete but no `tasks.json` → Suggest `/ultra-plan`
- If research complete → Suggest `/ultra-plan`

### 3. Detect Scenario B Context (NEW)

**Check recent /ultra-research execution**:
- If research report exists in `.ultra/docs/research/`, analyze project type hint
- Detect keywords:
  * "New Project" → Full workflow (research → plan → dev → test → deliver)
  * "Incremental Feature" → Skip round 1, start from solution exploration
  * "Tech Decision" → Focus on tech stack validation before plan
  * "Custom" → Respect user's selected rounds

### 4. Suggest Next Command Based on State

**Standard flow**:
- No `.ultra/` directory: Suggest `/ultra-init`
- Specs incomplete: Suggest `/ultra-research`
- Specs complete, no tasks.json: Suggest `/ultra-plan`
- After planning (tasks.json created): Suggest `/ultra-dev`
- After dev (code committed): Suggest `/ultra-test` or next `/ultra-dev`
- After testing (all tests pass): Suggest `/ultra-deliver`

**Scenario B adaptations**:
- After tech-decision-only research: Suggest validating choice in `/ultra-plan` or proceeding to implementation
- After incremental feature research: Suggest creating focused task plan in `/ultra-plan`
- After custom research: Suggest next logical step based on completed rounds

### 5. Provide Context-Aware Rationale

**Output templates**:

```
# After /ultra-research (New Project)
Current Status:
- ✅ Research complete (4-round full process)
- ✅ specs/product.md 100% complete
- ✅ specs/architecture.md 100% complete

Suggested next step: /ultra-plan
Rationale: Specs complete, can begin task planning
```

```
# After /ultra-research (Tech Decision)
Current Status:
- ✅ Tech selection complete (Round 3)
- ✅ specs/architecture.md updated

Suggested next step: /ultra-plan or direct implementation
Rationale: Tech stack determined, can plan implementation tasks
```

```
# After /ultra-plan
Current Status:
- ✅ Task planning complete
- ✅ .ultra/tasks/tasks.json generated (12 tasks)

Suggested next step: /ultra-dev
Rationale: Tasks broken down, can begin TDD development
```

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

## Don't

- Do not force workflow, respect user decisions
- Do not suggest skipping phases (unless Scenario B explicitly allows)
- Do not assume project type without filesystem evidence
- Do not suggest /ultra-research if specs are already complete

## Outputs

**Format**:
- Current project state summary (bullet points)
- Next step recommendation with clear rationale
- Optional: Alternative paths if multiple valid next steps

**Language**: Chinese (simplified) at runtime

**Tone**: Helpful, concise, action-oriented

---

## Integration with Scenario B

**guiding-workflow** now supports intelligent routing:
- Detects project type from /ultra-research output
- Adapts suggestions to user's workflow context
- Respects custom research flows
- Provides tailored rationale based on completed rounds

**Example**: If user selected "Tech Decision" in /ultra-research, guiding-workflow will suggest validating the choice or proceeding to implementation, rather than defaulting to full 4-round research flow.
