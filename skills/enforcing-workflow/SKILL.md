---
name: enforcing-workflow
description: "Enforces mandatory independent-branch workflow (one-task-one-branch-merge-delete). TRIGGERS: Discussing git workflow/branch strategy, AI about to suggest workflow 'options' or 'choices', discussion involves multiple tasks and branch management, keywords 'unified branch', 'batch merge', 'workflow alternatives', 'delay merge until complete'. BLOCKS: Any suggestion of unified/long-lived branches, batch merge strategies, workflow alternatives. ENFORCES: Each task = independent branch (feat/task-{id}), complete → merge → delete, main always deployable. DO NOT TRIGGER: Simple branch naming questions, individual git commands, documenting current workflow."
allowed-tools: Read
---

# Workflow Enforcement Guardian

**Purpose**: Prevent AI from suggesting alternative workflows. System uses ONLY independent-branch strategy.

## Triggers

**Activate when**:
- Discussing git workflow or branch strategy
- AI about to suggest workflow "options" or "choices"
- Discussion involves multiple tasks and branch management
- Keywords: "unified", "batch", "option", "workflow choice", "merge timing"

**Do NOT activate for**:
- Simple branch naming questions
- Individual git commands (git add, git commit, etc.)
- Documentation of current workflow

## Enforcement Rules

### IMMEDIATELY BLOCK if AI attempts to:

- Present workflow alternatives ("Option 1 vs Option 2", "Workflow A vs Workflow B")
- Suggest unified/long-lived branches for multiple tasks
- Recommend delaying merges until "all tasks complete"
- Suggest freezing main branch for batch deployment
- Propose "feature branch with multiple tasks"

### ENFORCE mandatory workflow:

**One-Task-One-Branch Pattern**:
```
main (always active, never frozen)
 ├── feat/task-1-xxx (create → complete → merge → delete)
 ├── feat/task-2-yyy (create → complete → merge → delete)
 └── feat/task-3-zzz (create → complete → merge → delete)
```

**Rules**:
- Each task = independent branch (`feat/task-{id}-{description}`)
- Complete task → merge to main → delete branch
- Main branch always deployable (for hotfixes)
- NO unified branches, NO batch merges, NO workflow choices

**Reference**: `REFERENCE.md` Section: "CRITICAL: Workflow is Non-Negotiable"

## Do

**When triggered**:

1. **Stop immediately** if about to suggest alternative workflows
2. **Remind** that independent-branch workflow is non-negotiable
3. **Explain** why (production deployability, isolated rollbacks)
4. **Redirect** to correct workflow pattern

**Output template**:

```
⚠️ [Warning Header: Workflow Non-Negotiable]

Detected attempt to suggest alternative workflow. Ultra Builder Pro uses **mandatory workflow only**:

**Independent Task Branch Pattern** (non-changeable):
- Each task = independent branch (feat/task-{id}-description)
- Complete task → merge to main → delete branch
- Main branch always deployable (for hotfixes)

**Forbidden**:
❌ Unified feature branches (multiple tasks in one branch)
❌ Delay merges until "all tasks complete"
❌ Freeze main branch waiting for batch deployment

**Rationale**:
Production requires main always deployable. Hotfixes cannot wait for 31 tasks to complete.
Independent branches support parallel work and isolated rollbacks.

Reference: REFERENCE.md
```

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**

## Don't

- Do not suggest this is "one option among many"
- Do not present pros/cons of different workflows
- Do not ask user to choose workflow strategy
- Do not compromise on workflow enforcement

## Outputs

**Format**:
- Warning header
- Explanation of mandatory workflow
- Forbidden patterns list
- Rationale
- Reference to documentation

**Language**: Chinese (simplified) at runtime

**Tone**: Firm but respectful, educational

---

## Rationale

**Why mandatory workflow?**

1. **Production Reality**: Hotfixes cannot wait for feature completion
2. **Parallel Work**: Multiple developers work independently
3. **Isolated Rollbacks**: Problematic features can be reverted independently
4. **Continuous Deployment**: Main always deployable enables CD/CD
5. **Code Review**: Smaller, focused PRs are easier to review

**Reference**: This is production-grade Git workflow, not a preference.
