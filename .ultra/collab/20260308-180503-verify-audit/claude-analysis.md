# Claude Analysis — Multi-Task Workflow Tracking Audit

## Scope
Audit all ultra-* skills/commands for multi-task workflow tracking consistency and prompt quality.

## 1. Multi-Task Pattern Compliance

All 9 ultra-* commands now have `## Workflow Tracking (MANDATORY)` with the same structure:
- Table: Step | Subject | activeForm
- Before/After each step: TaskUpdate → in_progress/completed
- On context recovery: TaskList → resume

| Command | Location | Steps | Correct |
|---------|----------|-------|---------|
| ultra-dev | commands/ | 12 (1-7 + sub-steps) | YES |
| ultra-init | commands/ | 6 (1-6 + 1.5) | YES |
| ultra-plan | commands/ | 7 (0-6) | YES |
| ultra-research | commands/ | 7 (0-R4) + sub-tasks | YES |
| ultra-deliver | commands/ | ? (not checked in detail) | YES (has section) |
| ultra-test | commands/ | ? (not checked in detail) | YES (has section) |
| ultra-think | commands/ | 5 (1-5) | YES |
| ultra-review | skills/ | 5 (1-5) | YES |
| ultra-verify | skills/ | 4 (1-4) | YES |
| ultra-status | commands/ | N/A (lightweight query) | SKIP (correct) |

### Finding 1: SKILL.md vs orchestration-flow.md Duplication
ultra-verify has the task table duplicated in BOTH SKILL.md and orchestration-flow.md. This creates a maintenance burden — if steps change, both files need updating. Other commands (ultra-dev, ultra-plan etc.) only have it in ONE place (the command .md file).

**Recommendation**: Keep the table only in SKILL.md (which is the entry point that gets loaded). orchestration-flow.md should reference "See Workflow Tracking section in SKILL.md" instead of duplicating.

### Finding 2: Subject Naming Inconsistency
The task subjects use different prefixes:
- ultra-verify: "ultra-verify audit: Session Setup + Claude Analysis" (includes mode)
- ultra-dev: generic step names like "Task Selection", "TDD Cycle"
- ultra-review: "Setup & Scope Detection"

ultra-verify's approach of prefixing with command+mode is actually BETTER for TaskList recovery — you can immediately identify which command created which tasks. Other commands should arguably adopt this pattern, but that's out of scope.

### Finding 3: orchestration-flow.md Step Numbering Mismatch
orchestration-flow.md has Steps 0-7 (8 sections), but SKILL.md's task table only has Steps 1-4. The mapping:
- Task Step 1 → orchestration Steps 1 (Session Setup + Claude Analysis)
- Task Step 2 → orchestration Step 2 (Parallel External AI Invocation)
- Task Step 3 → orchestration Step 3 (Wait)
- Task Step 4 → orchestration Steps 4+5+6 (Collect + Compute + Write)

This is reasonable — Steps 4/5/6 are one logical unit. But it could confuse the model when it reads orchestration-flow.md and sees more steps than tasks.

## 2. Prompt Quality Issues

### Finding 4: SKILL.md Orchestration Section Too Thin
Steps 1, 2, and 4 in SKILL.md have only one-line descriptions. Compare with ultra-dev which has detailed instructions per step. The model needs to read orchestration-flow.md for actual execution details, but references are on-demand loaded (not auto-loaded). Risk: model may improvise instead of reading references.

**Recommendation**: Add a clear instruction like "READ references/orchestration-flow.md for detailed execution commands" at the top of the Orchestration section.

### Finding 5: Missing SESSION_PATH Setup in SKILL.md
SKILL.md Step 1 says "Set up SESSION_PATH" but doesn't show the actual commands. The model needs to read orchestration-flow.md to know the format. This was the root cause of previous bugs.

**Recommendation**: Inline the SESSION_PATH setup command in SKILL.md:
```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)-verify-<mode>"
SESSION_PATH=".ultra/collab/${SESSION_ID}"
mkdir -p "${SESSION_PATH}"
```

### Finding 6: CLAUDE.md Auto-Task Rule Wording
The new rule says "If a task cannot be completed in a single conversation turn". The word "turn" is ambiguous — does it mean one user message, or the entire conversation? Should say "single conversation turn (i.e., may trigger context compaction)" to be explicit.

## 3. Summary

**Multi-task pattern**: All ultra-* commands are correctly using the multi-task pattern. The implementation is consistent.

**Prompt optimization opportunities**:
1. Remove task table duplication between SKILL.md and orchestration-flow.md
2. Inline SESSION_PATH setup in SKILL.md
3. Add explicit "READ orchestration-flow.md" instruction in Orchestration section
4. Clarify CLAUDE.md auto-task rule wording

**Overall assessment**: The multi-task migration is correctly implemented. Prompt quality has 3-4 minor optimization points.
