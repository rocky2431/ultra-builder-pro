---
description: Think-Driven Interactive Discovery - Deep research with structured analysis
argument-hint: [topic]
allowed-tools: Task, Read, Write, WebSearch, WebFetch, Grep, Glob, AskUserQuestion
model: opus
---

# Ultra Research

## Workflow Tracking (MANDATORY)

**On command start**, create tasks for each major phase using `TaskCreate`:

| Step | Subject | activeForm |
|------|---------|------------|
| 0 | Pre-Research Check | Checking prerequisites... |
| 0.5 | Project Type Detection | Detecting project type... |
| R0 | Round 0: Product Discovery & Strategy | Discovering product-market fit... |
| R1 | Round 1: User & Scenario | Discovering user scenarios... |
| R2 | Round 2: Feature Definition | Defining features... |
| R3 | Round 3: Architecture Design | Designing architecture... |
| R4 | Round 4: Quality & Deployment | Planning quality & deployment... |

**For each Round**, create sub-tasks:
- `R{n}.1: Requirement Clarification`
- `R{n}.2: Deep Analysis`
- `R{n}.3: Analysis Validation`
- `R{n}.4: Satisfaction Rating`
- `R{n}.5: Quality Gate`
- `R{n}.6: Generate Output`

**Before each step**: `TaskUpdate` → `status: "in_progress"`
**After each step**: `TaskUpdate` → `status: "completed"`
**On context recovery**: `TaskList` → resume from last incomplete step

---

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
| Full Project | Round 0-4 | Discovery + product + architecture |
| Product Only | Round 0-2 | Discovery + user scenarios + features |
| Feature Only | Round 1-2 | User scenarios + feature definition (skip discovery) |
| Architecture Change | Round 3-4 | Architecture + deployment |
| Custom | User selects | Specific rounds |

**Round 0 skip conditions**: Skip Round 0 if user provides existing market research, validated strategy docs, or explicitly states "I already know the market". For Feature Only on existing products, Round 0 is skipped by default.

---

## Research Flow

```
Initiate research
        ↓
Round 0: Product Discovery & Strategy (optional)
        - Opportunity discovery (OST)
        - Market sizing (TAM/SAM/SOM)
        - Competitive landscape
        - Product strategy canvas
        - Key assumptions & validation plan
        ↓
Round 1-2: Product Specification
        - Gather context & ask questions
        - Deep analysis with verification
        ↓
Round 3-4: Architecture Specification
        - Verify claims against official sources
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

**Structure**: 5 rounds (Round 0-4), each following 6-step cycle

### 6-Step Cycle (Every Round)

```
Step 1: Requirement Clarification (AskUserQuestion)
Step 2: Deep Analysis (/ultra-think)
Step 3: Analysis Validation (show summary with confidence)
Step 4: Round Satisfaction Rating (1-5 stars + feedback, ask user)
Step 5: Quality Gate (ITERATION LOOP)
        - If <4 stars:
          5a. Collect specific feedback (AskUserQuestion: "Which parts need revision? What are your specific expectations?")
          5b. Revise analysis: incorporate user feedback, redo Step 2 for affected sections
          5c. Re-present revised analysis (Step 3 again)
          5d. Re-ask satisfaction rating (Step 4 again)
          5e. Repeat 5a-5d until ≥4 stars (max 3 iterations, then escalate)
        - If ≥4 stars → Continue to Step 6
Step 6: Generate Output (MANDATORY - BOTH files required)
        6a. Write to .ultra/specs/ (product.md or architecture.md)
        6b. Write research report to .ultra/docs/research/{round-name}-{date}.md
        6c. Verify BOTH files updated before proceeding to next round
```

**CRITICAL**: Step 5 is a **mandatory iteration loop**. The round is NOT complete until the user rates ≥4 stars. Simply asking "are you satisfied?" and proceeding is a violation. You MUST:
1. Collect **specific** feedback on what needs to change
2. **Actually revise** the analysis based on that feedback
3. **Re-present** the revised version for user validation
4. **Re-rate** — only proceed when ≥4 stars

**Rating Definition**:

| Rating | Meaning | Action |
|--------|---------|--------|
| 1-2 ⭐ | Serious issues, needs major rework | Iterate: collect feedback → revise → re-validate |
| 3 ⭐ | Notable gaps or omissions | Iterate: collect feedback → revise → re-validate |
| 4 ⭐ | Acceptable, meets requirements | Continue to Step 6 |
| 5 ⭐ | Excellent, exceeds expectations | Continue to Step 6 |

**Research Report Format** (written in Step 6):

```markdown
# Round {N}: {Round Name}

> **Rating**: ⭐⭐⭐⭐ (4/5)
> **Confidence**: 92%
> **Iterations**: 2 (initial: 2⭐ → revised: 4⭐)
> **Completed**: {date}

## Summary
[Key findings from this round]

## Details
[Full analysis content]

## Decisions Made
[Choices and rationale]

## Iteration History (if iterations > 1)
| Iteration | Rating | User Feedback | Changes Made |
|-----------|--------|---------------|--------------|
| 1 | 2⭐ | "Missing specific deployment topology" | Added deployment topology diagram |
| 2 | 4⭐ | "Satisfied" | — |
```

### Step 6 Detailed: Generate Output (MANDATORY)

**CRITICAL**: BOTH spec file AND research report MUST be written. Do not proceed to next round until verified.

**6a. Update Specification File**:
- Round 0 → Update `.ultra/specs/discovery.md`
- Round 1-2 → Update `.ultra/specs/product.md`
- Round 3-4 → Update `.ultra/specs/architecture.md`
- Replace [NEEDS CLARIFICATION] markers with actual content
- **Verify**: Read spec file → confirm sections updated, no [NEEDS CLARIFICATION] in completed sections

**6b. Write Research Report**:
- Create `.ultra/docs/research/{round-name}-{date}.md`
- Use the Research Report Format above
- Include rating, confidence, iterations count
- **Verify**: Read report file → confirm file exists and has required sections

**6c. Output Verification Checklist**:
- [ ] Spec file updated (product.md or architecture.md)
- [ ] Research report created ({round-name}-{date}.md)
- [ ] Both files readable and properly formatted

**If any item unchecked → fix before proceeding to next round**

### Round Overview

| Round | Focus | Spec Output | Report Output |
|-------|-------|-------------|---------------|
| 0: Product Discovery | Opportunities, Market, Strategy, Assumptions | discovery.md §1-5 | product-discovery-{date}.md |
| 1: User & Scenario | Personas, User Scenarios | product.md §1-3 | user-scenario-{date}.md |
| 2: Feature Definition | User Stories, Features, Metrics | product.md §4-6 | feature-definition-{date}.md |
| 3: Architecture Design | Context, Strategy, Modules | architecture.md §1-6 | architecture-design-{date}.md |
| 4: Quality & Deployment | Deployment, Quality, Risks | architecture.md §7-12 | quality-deployment-{date}.md |

### Round 0: Product Discovery & Strategy

**When**: New products, pivots, entering new markets, or when the "why" and "for whom" are not yet validated. Skipped for feature-only work on existing products.

#### 0.0 Problem Validation (Forcing Questions)

**Before exploring opportunities and markets, validate the problem itself.** Ask these questions ONE AT A TIME via AskUserQuestion. Push on each until the answer is specific and evidence-based.

**Smart routing by product stage** (determine stage first via AskUserQuestion):
- Pre-product (idea, no users) → Q1, Q2, Q3, then proceed to 0.1
- Has users (not yet paying) → Q2, Q4, Q5, then proceed to 0.1
- Has paying customers → Q4, Q5, Q6, then proceed to 0.1
- Pure engineering/infra → Q2, Q4 only, then proceed to 0.1

**The Six Forcing Questions**:

| # | Question | Push Until You Hear | Red Flags |
|---|----------|--------------------:|-----------|
| Q1 | **Demand Reality**: What is the strongest evidence someone actually wants this — not "is interested," but would be genuinely upset if it disappeared? | Specific behavior: paying, expanding usage, panicking when it breaks | "People say it's interesting", waitlist signups, VC enthusiasm |
| Q2 | **Status Quo**: What are users doing RIGHT NOW to solve this — even badly? What does that workaround cost them? | Specific workflow: hours wasted, dollars lost, tools duct-taped together | "Nothing — no solution exists" (if nobody is doing anything, the problem may not be painful enough) |
| Q3 | **Desperate Specificity**: Name the actual human who needs this most. Title? What gets them promoted? What gets them fired? | A name, a role, a specific consequence they face | Category-level answers: "enterprises", "SMBs", "marketing teams" |
| Q4 | **Narrowest Wedge**: What is the smallest version someone would pay real money for — this week, not after you build the platform? | One feature, one workflow, shippable in days | "Need full platform first", "can't strip it down" |
| Q5 | **Observation & Surprise**: Have you watched someone use this without helping them? What surprised you? | A specific surprise that contradicted assumptions | "We sent a survey", "nothing surprising" |
| Q6 | **Future-Fit**: If the world looks meaningfully different in 3 years, does your product become more essential or less? | Specific claim about how user's world changes and why that increases value | "Market growing 20% per year", "AI makes everything better" |

**Smart-skip**: If earlier answers already cover a later question, skip it.
**Escape hatch**: If user says "just do it" or provides a fully formed plan → fast-track to 0.1.

**Output**: Problem Validation Summary — include in discovery.md §0 before Opportunity Space.

**Questions to answer**:

#### 0.1 Opportunity Discovery (Opportunity Solution Tree)

Based on Teresa Torres' *Continuous Discovery Habits*:

1. **Desired Outcome**: What measurable business/product outcome are we pursuing? (single, clear metric)
2. **Opportunity Space**: What customer needs, pain points, or desires exist? Frame from customer perspective: "I struggle to..." / "I wish I could..."
3. **Opportunity Prioritization**: Rank opportunities using Opportunity Score: `Importance x (1 - Satisfaction)` (Dan Olsen). Focus on top 2-3.
4. **Solution Brainstorm**: For each prioritized opportunity, generate 3+ solutions from PM/Designer/Engineer perspectives. Never commit to the first idea.

**Key principle**: Opportunities, not features. Prioritize problems, not solutions.

#### 0.2 Market Assessment

Estimate market size using dual approach:

1. **Top-Down (TAM)**: Total industry size → narrow to relevant slice
2. **Bottom-Up (SAM)**: Unit economics (customers x price x frequency) → cross-validate
3. **SOM**: Realistic achievable share in 1-3 years given competitive position and GTM capacity
4. **Growth Drivers**: Technology, regulatory, demographic, or behavioral shifts that expand/contract the market

Use WebSearch for current industry data. Cite sources — no unsupported numbers.

| Metric | Current Estimate | 2-3 Year Projection |
|--------|-----------------|---------------------|
| TAM    |                 |                     |
| SAM    |                 |                     |
| SOM    |                 |                     |

#### 0.3 Competitive Landscape

Analyze competitive environment:

1. **Direct Competitors**: Products solving the same problem for the same segment (2-5 competitors)
2. **Indirect Competitors / Alternatives**: What customers use today instead (including "do nothing")
3. **Competitive Advantages**: Where we can win (and where we can't)
4. **Porter's Five Forces** (brief): Supplier power, Buyer power, New entrants, Substitutes, Rivalry intensity

Output as comparison matrix:

| Dimension | Us | Competitor A | Competitor B | Alternative |
|-----------|-----|-------------|-------------|-------------|
| Core value prop | | | | |
| Target segment | | | | |
| Pricing model | | | | |
| Key weakness | | | | |

#### 0.4 Product Strategy (Strategy Canvas, condensed)

Define strategic direction across 5 key dimensions:

1. **Vision**: How can we inspire people? What are we aspiring to achieve? (2-3 sentences, emotional and memorable)
2. **Target Segments**: Who we serve (defined by problems/JTBD, not demographics) and who we explicitly do NOT serve
3. **Value Proposition**: For each segment — When [situation], they want [motivation], so they can [outcome]
4. **Strategic Trade-offs**: What we choose NOT to do and why. This is more important than what we choose to do.
5. **Defensibility**: What makes this hard to copy? (network effects, data, switching costs, IP, brand)

#### 0.5 Key Assumptions & Validation Plan

Extract and prioritize the riskiest assumptions from 0.1-0.4:

1. **Assumption Extraction**: Surface assumptions across categories:
   - **Value**: Will users want this?
   - **Usability**: Can users figure it out?
   - **Feasibility**: Can we build it?
   - **Viability**: Does the business case work?
   - **Go-to-Market**: Can we reach and convert users?

2. **Prioritization**: Map on Impact x Uncertainty matrix. Focus on "leap of faith" assumptions (high impact, high uncertainty).

3. **Experiment Design**: For top 3-5 assumptions, design cheap, fast validation experiments:

| # | Assumption | Category | Method | Success Criteria | Effort | Timeline |
|---|-----------|----------|--------|-----------------|--------|----------|

**Methods**: Pretotypes (Alberto Savoia), fake doors, landing page tests, concierge MVPs, user interviews, data analysis, A/B tests.

**Decision Framework**:
- If experiment succeeds → proceed to Round 1 (User & Scenario)
- If experiment fails → pivot opportunity, re-evaluate, or kill

**Output**: discovery.md §1 (Opportunity Space), §2 (Market Assessment), §3 (Competitive Landscape), §4 (Product Strategy), §5 (Assumptions & Validation Plan)

**Note**: Round 0 actively uses WebSearch to gather real market data, competitor information, and industry reports. Claims without sources are marked as Speculation.

---

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
- ✅ `.ultra/specs/discovery.md` has validated opportunities and strategy (if Round 0 included)
- ✅ `.ultra/specs/product.md` has NO [NEEDS CLARIFICATION] markers
- ✅ `.ultra/specs/architecture.md` has justified tech decisions
- ✅ All selected rounds completed (each round ≥4 stars)
- ✅ Research reports saved to `.ultra/docs/research/`
- ✅ **All recommendations have 90%+ confidence**
- ✅ **All code examples are production-ready**
- ✅ **Key assumptions identified and validation plan defined** (if Round 0 included)

---

**Final Quality Summary** (display when all conditions met):

```
📊 Research Quality Summary
===========================
Round 0 (Product Discovery):  ⭐⭐⭐⭐ (4/5), 88%, 1 iteration
Round 1 (User & Scenario):    ⭐⭐⭐⭐ (4/5), 92%, 1 iteration
Round 2 (Feature Definition): ⭐⭐⭐⭐⭐ (5/5), 95%, 1 iteration
Round 3 (Architecture):       ⭐⭐⭐⭐ (4/5), 91%, 2 iterations
Round 4 (Quality & Deploy):   ⭐⭐⭐⭐ (4/5), 90%, 1 iteration

Overall: 4.20/5 avg, 91% avg confidence
Status: ✅ Complete (all rounds ≥4 stars)
Reports: .ultra/docs/research/*.md
Next: /ultra-plan
```

---

## Output Files

| File | Content |
|------|---------|
| `.ultra/specs/discovery.md` | Opportunity Space, Market Assessment, Competitive Landscape, Product Strategy, Assumptions & Validation Plan |
| `.ultra/specs/product.md` | Personas, User Scenarios, User Stories, Features Out, Success Metrics |
| `.ultra/specs/architecture.md` | arc42 structure (Context, Strategy, Blocks, Runtime, Deployment, Quality, Risks) |
| `.ultra/docs/research/*.md` | Round-specific analysis reports with confidence scores |

---

## Integration

- **Think**: Each round invokes /ultra-think for deep analysis
- **MCP**: Round 0 uses WebSearch/Exa (market data, competitors). Round 3 uses Context7 (docs) + Exa (code examples)
- **Next**: Run /ultra-plan when research complete
- **Methodology sources**: Round 0 draws from Teresa Torres (OST), Dan Olsen (Opportunity Score), Alberto Savoia (Pretotyping), Marty Cagan (Product Strategy)

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

