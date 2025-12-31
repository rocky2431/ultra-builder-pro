---
description: Think-Driven Interactive Discovery - Deep research with structured analysis
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

| Type | Rounds | Focus |
|------|--------|-------|
| Full Project | Round 1-4 | Full product + architecture |
| Feature Only | Round 1-2 | User scenarios + feature definition |
| Architecture Change | Round 3-4 | Architecture + deployment |
| Custom | User selects | Specific rounds |

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
Step 4: Round Satisfaction Rating (1-5 stars, ask user)
Step 5: Quality Gate
        - If <4 stars → Iterate (ask: what's missing? back to Step 1)
        - If ≥4 stars → Continue to Step 6
Step 6: Generate Output
        - Write to .ultra/specs/ (product.md or architecture.md)
        - Write research report to .ultra/docs/research/{round-name}-{date}.md
```

**Rating Definition**:

| Rating | Meaning | Action |
|--------|---------|--------|
| 1-2 ⭐ | Serious issues, needs major rework | Iterate |
| 3 ⭐ | Notable gaps or omissions | Iterate |
| 4 ⭐ | Acceptable, meets requirements | Continue |
| 5 ⭐ | Excellent, exceeds expectations | Continue |

**Research Report Format** (written in Step 6):

```markdown
# Round {N}: {Round Name}

> **Rating**: ⭐⭐⭐⭐ (4/5)
> **Confidence**: 92%
> **Iterations**: 1
> **Completed**: {date}

## Summary
[Key findings from this round]

## Details
[Full analysis content]

## Decisions Made
[Choices and rationale]
```

### Round Overview

| Round | Focus | Spec Output | Report Output |
|-------|-------|-------------|---------------|
| 1: User & Scenario | Personas, User Scenarios | product.md §1-3 | user-scenario-{date}.md |
| 2: Feature Definition | User Stories, Features, Metrics | product.md §4-6 | feature-definition-{date}.md |
| 3: Architecture Design | Context, Strategy, Modules | architecture.md §1-6 | architecture-design-{date}.md |
| 4: Quality & Deployment | Deployment, Quality, Risks | architecture.md §7-12 | quality-deployment-{date}.md |

### Round 1: User & Scenario Discovery

**Questions to answer**:
1. Who are the target users? (Define 2-3 Personas with goals, pain points)
2. What scenarios will users encounter? (3-5 User Scenarios with context)
3. What is the core problem being solved?

**Output**: product.md §1 (Problem Statement), §2 (Personas), §3 (User Scenarios)

### Round 2: Feature Definition

**Questions to answer**:
1. What are the User Stories? (As a [persona], I want [action], so that [benefit])
2. What features are required? (Prioritized list with acceptance criteria)
3. What features are explicitly OUT of scope? (Features Out with rationale)
4. How will we measure success? (Business metrics, user metrics, targets)

**Output**: product.md §4 (User Stories & Features), §5 (Features Out), §6 (Success Metrics)

### Round 3: Architecture Design

**Questions to answer** (aligned with arc42 §1-6):
1. What are the quality goals? (Performance, Security, Maintainability)
2. What are the constraints? (Technical, Organizational, Legal)
3. What is the system context? (External systems, interfaces)
4. What is the solution strategy? (Tech stack with rationale)
5. What are the building blocks? (Module decomposition)
6. What are the key runtime scenarios? (Sequence flows)

**Output**: architecture.md §1-6

### Round 4: Quality & Deployment

**Questions to answer** (aligned with arc42 §7-11):
1. How will it be deployed? (Infrastructure, environments)
2. What are crosscutting concerns? (Logging, Auth, Error handling)
3. What are the quality requirements? (Specific scenarios)
4. What are known risks and technical debt?

**Output**: architecture.md §7-12


---

## Mode 2: Focused Technology Research

**When**: Specific tech decision during development


**Process**: Single-round comparison with verification

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
- ✅ All selected rounds completed (each round ≥4 stars)
- ✅ Research reports saved to `.ultra/docs/research/`
- ✅ **All recommendations have 90%+ confidence**
- ✅ **All code examples are production-ready**

**Note**: No separate "overall gate" needed - each round requires ≥4 stars to continue, so completing all rounds guarantees overall quality.

**Final Quality Summary** (display after all rounds complete):

```
📊 Research Quality Summary
===========================
Round 1 (User & Scenario):    ⭐⭐⭐⭐ (4/5), 92%, 1 iteration
Round 2 (Feature Definition): ⭐⭐⭐⭐⭐ (5/5), 95%, 1 iteration
Round 3 (Architecture):       ⭐⭐⭐⭐ (4/5), 91%, 2 iterations
Round 4 (Quality & Deploy):   ⭐⭐⭐⭐ (4/5), 90%, 1 iteration

Overall: 4.25/5 avg, 92% avg confidence
Status: ✅ Complete (all rounds ≥4 stars)
Reports: .ultra/docs/research/*.md
Next: /ultra-plan
```

---

## Output Files

| File | Content |
|------|---------|
| `.ultra/specs/product.md` | Personas, User Scenarios, User Stories, Features Out, Success Metrics |
| `.ultra/specs/architecture.md` | arc42 structure (Context, Strategy, Blocks, Runtime, Deployment, Quality, Risks) |
| `.ultra/docs/research/*.md` | Round-specific analysis reports with confidence scores |

---

## Integration

- **Think**: Each round invokes /ultra-think for deep analysis
- **MCP**: Round 3 uses Context7 (docs) + Exa (code examples)
- **Next**: Run /ultra-plan when research complete

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

