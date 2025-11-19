---
description: Think-Driven Interactive Discovery - Deep research with 6-dimensional analysis
allowed-tools: TodoWrite, Task, Read, Write, WebSearch, WebFetch, Grep, Glob
---

# Ultra Research - Think-Driven Discovery Engine

## Overview

Ultra-Research is **the most critical phase** in the development workflow. It transforms vague ideas into complete, well-researched specifications through **progressive interactive discovery**.

**Core Philosophy**: Research is a **collaborative process** between AI and user, not a one-way automated generation.

**Key Innovation**: "Analyze → Validate → Iterate" cycle - Ensure every research output aligns with user needs through gradual verification at each decision point.

**ROI**: 80-90 minute investment with 80-90% accuracy = **10+ hours rework avoided** (vs 70 min with 40-60% accuracy requiring 10h+ rework)

---

## Phase 0: Project Type Detection

**Purpose**: Route to optimal research flow based on project context.

**Implementation**: Interactive project type selection using AskUserQuestion tool.

**Available project types**:
1. **New Project** - Complete 4-round research (70 min)
2. **Incremental Feature** - Solution + Tech only (30 min)
3. **Tech Decision** - Tech evaluation only (15 min)
4. **Custom Flow** - User selects specific rounds

**Detailed routing logic**: See [Project Types Guide](../config/research/project-types.md)

---

## Research Modes

### Mode 1: Progressive Interactive Discovery (PRIMARY - Recommended)

**When**: After /ultra-init, when specs/ have [NEEDS CLARIFICATION] markers

**Duration**: 80-90 minutes (20-30 min per round with validation)

**Core Innovation**: Each round follows **6-step interactive cycle** to ensure output quality:

```
Step 1: Requirement Clarification (AskUserQuestion)
Step 2: Deep Analysis (ultra-think with 6D framework)
Step 3: Analysis Validation (AskUserQuestion - show summary, check satisfaction)
Step 4: Iteration Decision (If unsatisfied → collect feedback → back to Step 2)
Step 5: Generate Spec Content (Write to specs/)
Step 6: Round Satisfaction Rating (1-5 score)
```

**4-Round Process** (each uses 6-step cycle):

1. **Round 1: Problem Discovery** (20-25 min)
   - Clarify: Target users, core pain points, success criteria
   - Analyze: 6D problem analysis (Technical/Business/Team/Ecosystem/Strategic/Meta)
   - Validate: Problem understanding accuracy check
   - Output: `specs/product.md` Section 1-2

2. **Round 2: Solution Exploration** (20-25 min)
   - Clarify: Feature priorities, key user scenarios
   - Analyze: Generate user stories with 6D analysis
   - Validate: User story coverage and priority check
   - Output: `specs/product.md` Section 3-5

3. **Round 3: Technology Selection** (15-20 min)
   - Clarify: Tech stack constraints, team skills, performance requirements
   - Analyze: 6D tech comparison (use Context7/Exa MCP for research)
   - Validate: Tech solution selection and trade-offs confirmation
   - Output: `specs/architecture.md`

4. **Round 4: Risk & Constraints** (15-20 min)
   - Clarify: Critical risks from user perspective
   - Analyze: Risk identification and mitigation strategies
   - Validate: Risk priority and mitigation feasibility check
   - Output: Risk section in specs, research reports

**Final Validation**: Overall quality check (1-5 rating), improvement suggestions collection

**Output**:
- ✅ `specs/product.md`: 100% complete (no [NEEDS CLARIFICATION])
- ✅ `specs/architecture.md`: 100% complete with justified decisions
- ✅ Research reports: `.ultra/docs/research/` (4 reports + metadata.json)
- ✅ Quality metrics: Round satisfaction scores, overall rating, iteration count

**Detailed interactive questions**: See [Interactive Points Design](../config/research/interaction-points.md)

---

### Mode 2: Focused Technology Research (Secondary)

**When**: Specific technology decision during development

**Duration**: 10-15 minutes

**Process**: Single-round 6D comparison, auto-update architecture.md

**Detailed workflow**: See [Mode 2 Focused Guide](../config/research/mode-2-focused.md)

---

## Workflow Execution

### Pre-Research Checks

1. **Check if specs exist**:
   - If `specs/product.md` exists with [NEEDS CLARIFICATION] → Run Mode 1
   - If `specs/` doesn't exist → Suggest /ultra-init first
   - If specs are 100% complete → Skip research, suggest /ultra-plan

2. **Detect project type**: Use Phase 0 to route to optimal flow

3. **Set expectations**: Inform user of estimated duration based on project type

---

### Research Execution Flow (Progressive Interactive Model)

```
Phase 0: Project Type Detection (AskUserQuestion)
    ↓
Route to Rounds (based on project type: New/Incremental/Tech/Custom)
    ↓
┌─────────────── For Each Round ───────────────┐
│                                              │
│ Step 1: Requirement Clarification           │
│   ├─ AskUserQuestion (2-4 questions)        │
│   ├─ Collect user inputs & constraints      │
│   └─ Set analysis scope                     │
│         ↓                                    │
│ Step 2: Deep Analysis                       │
│   ├─ Invoke /ultra-think with user context  │
│   ├─ 6D analysis framework                  │
│   └─ Generate structured output             │
│         ↓                                    │
│ Step 3: Analysis Validation                 │
│   ├─ Present analysis summary (not full)    │
│   ├─ AskUserQuestion: Satisfaction check    │
│   └─ Collect adjustment needs if any        │
│         ↓                                    │
│ Step 4: Iteration Decision                  │
│   ├─ If satisfied → Continue to Step 5      │
│   ├─ If needs adjustment → Back to Step 2   │
│   │   (with feedback as constraints)        │
│   └─ If critical miss → Back to Step 1      │
│         ↓                                    │
│ Step 5: Generate Spec Content               │
│   ├─ Write to specs/product.md or          │
│   │   specs/architecture.md                 │
│   └─ Save research report to                │
│       .ultra/docs/research/                  │
│         ↓                                    │
│ Step 6: Round Satisfaction Rating           │
│   ├─ AskUserQuestion: Rate 1-5 stars        │
│   ├─ Record to metadata.json                │
│   └─ If rating < 4, collect improvement     │
│       suggestions                            │
│                                              │
└──────────────────────────────────────────────┘
    ↓
[Repeat for next round]
    ↓
All Rounds Complete
    ↓
Final Validation (AskUserQuestion)
    ├─ Overall quality rating (1-5)
    ├─ Specs completeness confirmation
    └─ Improvement suggestions collection
    ↓
Save Research Metadata
    ├─ Round satisfaction scores
    ├─ Iteration counts per round
    ├─ Overall rating
    └─ Total duration
    ↓
Trigger guiding-workflow → Suggest /ultra-plan
```

**Key Improvements**:
- ✅ **3 validation points** per round (vs 0 before)
- ✅ **Iteration loop** for quality assurance
- ✅ **Progressive disclosure** (summaries, not full dumps)
- ✅ **Quality metrics** collection for continuous improvement

---

### Post-Research Actions

1. **Validate spec completeness**: See [Output Templates](../config/research/output-templates.md)

2. **Save research reports**:
   - Problem analysis → `.ultra/docs/research/problem-analysis-{date}.md`
   - Solution exploration → `.ultra/docs/research/solution-exploration-{date}.md`
   - Tech evaluation → `.ultra/docs/research/tech-evaluation-{date}.md`
   - Risk assessment → `.ultra/docs/research/risk-assessment-{date}.md`

3. **Trigger guiding-workflow**: Suggest next step based on project scenario

---

## Integration with Ultra-Think

**Auto-invocation**: Every research round automatically invokes /ultra-think for deep analysis.

**Think configuration**:
- Problem Discovery: 6D problem analysis (Technical, Business, Team, Ecosystem, Strategic, Meta)
- Solution Exploration: 6D solution analysis with user story generation
- Technology Selection: 6D tech comparison with auto-research (Context7, Exa MCP)
- Risk Assessment: 6D risk identification with mitigation strategies

**Output format**: /ultra-think returns structured analysis in Chinese (user-facing)

**Integration point**: Research command processes think output and generates spec sections

---

## Success Criteria

**Research Complete When**:
- ✅ `specs/product.md` exists with NO [NEEDS CLARIFICATION] markers
- ✅ `specs/architecture.md` exists with justified tech decisions
- ✅ All selected rounds completed (based on project type)
- ✅ Research reports saved to `.ultra/docs/research/`
- ✅ **Quality metrics meet thresholds**: Overall rating ≥4 stars, no round <3 stars

**Quality Gates (Progressive Validation)**:

**Per-Round Gates**:
1. **Step 3 Gate**: Analysis validation - User confirms analysis accuracy (satisfied/needs-adjustment/critical-miss)
2. **Step 4 Gate**: Iteration decision - Maximum 2 iterations per round (prevent infinite loops)
3. **Step 6 Gate**: Round satisfaction - Score ≥3 required to proceed (if <3, suggest restart round)

**Final Gates**:
1. **Completeness Gate**: No [NEEDS CLARIFICATION] markers in any spec file
2. **Overall Satisfaction Gate**: Final rating ≥4 stars (if <4, suggest improvements)
3. **Metadata Recording Gate**: All quality metrics saved to `.ultra/docs/research/metadata.json`

**Quality Metrics Collected**:
```json
{
  "projectType": "New Project | Incremental Feature | Tech Decision | Custom",
  "roundsExecuted": [1, 2, 3, 4],
  "roundSatisfaction": {
    "round1": 4.5,
    "round2": 5.0,
    "round3": 4.0,
    "round4": 4.5
  },
  "iterationCounts": {
    "round1": 1,
    "round2": 0,
    "round3": 2,
    "round4": 1
  },
  "overallSatisfaction": 4.5,
  "totalDuration": "85 minutes",
  "improvementSuggestions": [
    "Round 3 tech options could include more detail on performance benchmarks"
  ]
}
```

**Escalation Policy**:
- If round rating <3: Offer to restart round with different approach
- If 2+ rounds <4: Suggest switching to Fast Mode (reduce interaction)
- If overall rating <4 after completion: Collect detailed feedback, suggest round revisit

---

## Output Format

**Console output** (in Chinese):
- Round completion status
- Spec file generation progress
- Research report save confirmation
- Next step suggestion (via guiding-workflow)

**File outputs**:
- `specs/product.md` (Sections 1-5: Problem, Users, Stories, Requirements, NFRs)
- `specs/architecture.md` (Tech Stack with rationale)
- `.ultra/docs/research/*.md` (4 research reports)

**Detailed templates**: See [Output Templates Guide](../config/research/output-templates.md)

---

## Philosophy: Collaborative Research-First Development

**Why progressive interactive research is mandatory**:

1. **Cost of Rework**: 10+ hours wasted on wrong tech choices or unclear requirements
2. **Alignment Through Validation**: User participation ensures shared understanding (vs AI assumptions)
3. **Decision Quality**: 6D analysis + user validation = high-confidence decisions
4. **Knowledge Capture**: Research reports + satisfaction metrics serve as project memory

**Paradigm Shift**:

**Old Model** (Automated Generation):
```
Skip research → OR → Auto-generate research → Code → Realize wrong direction → Rewrite (10h loss)
  ↓                          ↓
70 min saved              70 min spent
40-60% accuracy          40-60% accuracy
```

**New Model** (Progressive Interactive):
```
Phase 0 → Round 1-4 (each with 6-step validation) → Code confidently → Ship successfully
  ↓           ↓                                          ↓
5 min      80-90 min spent                          0-2h rework (vs 10h+)
         80-90% accuracy (validated at each step)
```

**ROI Comparison**:

| Model | Time Investment | Accuracy | Rework Cost | Net ROI |
|-------|----------------|----------|-------------|---------|
| Skip | 0 min | 0% | 10-15h | **-10h** |
| Auto-generate | 70 min | 40-60% | 10h+ | **-9h** |
| **Progressive** | **85 min** | **80-90%** | **0-2h** | **+8h** |

**Key Insight**: 15 extra minutes of interaction saves 8 hours of rework = **32x ROI on interaction time**

**Anti-patterns to avoid**:
- ❌ Skip research (0% accuracy)
- ❌ Accept AI output without validation (40-60% accuracy)
- ❌ Batch all validation to the end (too late to pivot)

**Best practice**:
- ✅ Progressive validation at each decision point
- ✅ Iterative refinement when user feedback signals misalignment
- ✅ Quality metrics collection for continuous improvement

---

## References

**Official Claude Code best practices**:
- Progressive disclosure (modular research guides)
- Think-driven analysis (leverage extended thinking)
- User validation (interactive questioning throughout)

**Ultra Builder Pro workflows**:
- @workflows/ultra-development-workflow.md - Complete workflow sequence
- @guidelines/ultra-solid-principles.md - Architecture evaluation criteria
- @config/ultra-mcp-guide.md - MCP tool usage (Context7, Exa for research)

---

**Next Step**: After research completes, `guiding-workflow` skill will suggest `/ultra-plan` (if specs are 100% complete).
