---
description: Think-Driven Interactive Discovery - Deep research with 6-dimensional analysis
argument-hint: [topic]
allowed-tools: TodoWrite, Task, Read, Write, WebSearch, WebFetch, Grep, Glob, AskUserQuestion
---

# Ultra Research

Transform vague ideas into complete specifications through progressive interactive discovery.

**Philosophy**: Research is collaborative. Each decision validated with user before proceeding. All findings must have 90%+ confidence.

**ROI**: Thorough research → 90%+ accuracy → significant rework avoided

---

## Pre-Research Check

1. If `.ultra/specs/product.md` has [NEEDS CLARIFICATION] → Run Mode 1
2. If `.ultra/specs/` doesn't exist → Suggest /ultra-init first
3. If specs 100% complete → Skip to /ultra-plan

---

## Phase 0: Project Type Detection

Use AskUserQuestion to determine research scope:

| Type | Rounds |
|------|--------|
| New Project | Round 1-4 |
| Incremental Feature | Round 2-3 |
| Tech Decision | Round 3 only |
| Custom | User selects |

---

## Research Flow

```
Initiate research
        ↓
Gather context & ask questions
        ↓
Deep analysis with verification
        - Verify claims against official sources
        - Add production-ready examples
        - Rate confidence levels (must be 90%+)
        ↓
High-confidence output
        ↓
Write to .ultra/specs/
```

**Key Principle**: All research output must be:
- Evidence-based (verified sources)
- Production-focused (no demo code)
- High-confidence (90%+ for recommendations)
- Actionable (clear next steps)

---

## Mode 1: Progressive Interactive Discovery

**When**: After /ultra-init, specs need clarification

**Structure**: 4 rounds, each following 6-step cycle

### 6-Step Cycle (Every Round)

```
Step 1: Requirement Clarification (AskUserQuestion)
Step 2: Deep Analysis (/ultra-think)
Step 3: Analysis Validation (show summary with confidence)
Step 4: Iteration Decision (satisfied → continue)
Step 5: Generate Spec Content (Write to .ultra/specs/)
Step 6: Round Satisfaction Rating (1-5 stars)
```

### Round Overview

| Round | Focus | Questions | Output |
|-------|-------|-----------|------------|--------|
| 1: Problem Discovery | Problem space, users | Q1-5 | Verify market data | .ultra/specs/product.md §1-2 |
| 2: Solution Exploration | MVP features, stories | Q6-8 | Add implementation patterns | .ultra/specs/product.md §3-5 |
| 3: Technology Selection | Tech stack, architecture | Q9-11 | **Deep tech comparison** | .ultra/specs/architecture.md |
| 4: Risk & Constraints | Risks, hard constraints | Q12-13 | Risk quantification | Risk sections |


---

## Mode 2: Focused Technology Research

**When**: Specific tech decision during development


**Process**: Single-round 6D comparison with verification

### Technology Research Template

Research technology options with:
1. Compare top 3 options with evidence
2. Include official documentation references
3. Provide production-ready code examples
4. Rate each option with confidence percentage
5. Minimum 90% confidence for recommendation

Output comparison matrix with:
- Performance benchmarks
- Security considerations
- Maintenance/community status
- Integration complexity
- Production readiness score

---

## Research Quality Standards

### All Research Must Include

| Element | Requirement |
|---------|-------------|
| Sources | Every claim has verifiable source |
| Confidence | 90%+ for recommendations |
| Code | Production-ready (no TODO/demo) |
| Trade-offs | Quantified pros/cons |
| Next steps | Specific, actionable items |

### Research Must NOT Include

| Prohibited | Detection |
|------------|-----------|
| Unverified claims | No source cited |
| Low-confidence recommendations | <90% |
| Demo/placeholder code | TODO, FIXME, "example only" |
| Speculation without disclosure | Not marked as uncertain |

---

## Success Criteria

**Research Complete When**:
- ✅ `.ultra/specs/product.md` has NO [NEEDS CLARIFICATION] markers
- ✅ `.ultra/specs/architecture.md` has justified tech decisions
- ✅ All selected rounds completed
- ✅ Research reports saved to `.ultra/docs/research/`
- ✅ Overall rating ≥4 stars, no round <3 stars
- ✅ **All recommendations have 90%+ confidence**
- ✅ **All code examples are production-ready**
- ✅ **Project-level CLAUDE.md generated** (NEW)

---

## Final Step: Generate Project CLAUDE.md

**After all rounds complete, generate project-level CLAUDE.md:**

1. **Read source files**:
   - `.ultra/specs/product.md` → Project Overview
   - `.ultra/specs/architecture.md` → Tech Stack, Development Rules
   - `.ultra/docs/research/*` → Known Risks
   - `.ultra/tasks/tasks.json` → Current Focus

2. **Generate CLAUDE.md** at project root:
   - Use template from syncing-docs skill
   - Limit to ~500 words
   - Include generation timestamp

3. **Verify .gitignore**:
   - Ensure `CLAUDE.local.md` is ignored (personal config)
   - `CLAUDE.md` should be committed (shared context)

**Purpose**: Claude Code automatically reads project-level CLAUDE.md, providing consistent project context for every conversation.

---

## Output Files

| File | Content |
|------|---------|
| `.ultra/specs/product.md` | Problem, Users, Stories, Requirements, NFRs |
| `.ultra/specs/architecture.md` | Tech stack with rationale |
| `.ultra/docs/research/*.md` | Round-specific analysis reports |
| `.ultra/docs/research/metadata.json` | Quality metrics + confidence scores |
| **`CLAUDE.md` (project root)** | Project context for Claude Code (NEW) |

---

## Integration

- **Skills**: **syncing-docs (CLAUDE.md generation)**
- **Think**: Each round invokes /ultra-think for 6D analysis
- **MCP**: Round 3 uses Context7 (docs) + Exa (code examples)
- **Next**: Run /ultra-plan when research complete
- **Output**: syncing-docs generates project CLAUDE.md on completion

---

## Honest Output Requirements

Every research output must include confidence assessment:

```markdown
## Research Confidence Summary

**Overall**: 93%

**High Confidence (95%+)**:
- Technology comparison (verified against official docs)
- Performance benchmarks (reproduced locally)

**Medium Confidence (90-95%)**:
- Effort estimates (based on similar projects)
- Risk probabilities (industry data)

**Uncertainty (<90%)**:
- {item}: {confidence}% - Marked as speculation
```

---

