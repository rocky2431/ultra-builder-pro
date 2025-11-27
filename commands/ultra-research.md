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

**Detailed routing logic**: See `@config/research/project-types.md`

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

**IMPORTANT**: Each round MUST follow the 6-step cycle EXACTLY. DO NOT skip steps or optimize. DO NOT output final results until all steps complete.

---

### Round 1: Problem Discovery (20-25 min)

**MANDATORY EXECUTION SEQUENCE - Follow EXACTLY**:

#### Step 1: Requirement Clarification (MUST DO FIRST)

**HYBRID MODEL: Core Questions (Standardized) + Extension Questions (Dynamic)**

##### Part A: Core Questions (Standardized)

Load **Core Questions 1-5** from `@config/research/interaction-points-core.md`:
1. Target User Type (B2C/B2B/Internal/B2D)
2. Core Pain Point (Performance/Usability/Features/Cost/Reliability)
3. Success Metrics (User Growth/Performance/Business/Quality/Cost)
4. Project Scale (Small/Medium/Large/Very Large)
5. Time Constraints (Urgent/Normal/Flexible/Long-term)

Use AskUserQuestion tool for each core question.

##### Part B: Extension Questions (Dynamic Generation)

**Claude MUST generate 1-2 context-specific questions** based on:
- User's project description from Phase 0
- Detected keywords (e.g., "healthcare" → compliance, "startup" → team size, "fintech" → security)
- Project type selected in Phase 0

**Generation Guidelines**:
1. Format: 2-4 options per question, header ≤12 chars, label + description for each option
2. Validate before use: header.length ≤12, options 2-4, all options have label + description
3. If validation fails → retry (max 2 times) → fallback to core questions only
4. Domain Examples:
   - Healthcare: "合规要求？" (header: "Compliance", options: HIPAA/GDPR/Local/None)
   - Fintech: "监管要求？" (header: "Regulation", options: SEC/MAS/Local/None)
   - Startup: "团队规模？" (header: "Team Size", options: 1-3/4-10/11-50/50+)
   - Enterprise: "集成需求？" (header: "Integration", options: ERP/CRM/Legacy/None)

**DO NOT proceed to Step 2 until ALL questions (core + extension) are answered.**

#### Step 2: Deep Analysis (MUST DO SECOND)

Invoke `/ultra-think` with user input from Step 1:

```
SlashCommand: /ultra-think "Analyze problem for [project_name] with context:
- Target users: [from_step1]
- Pain points: [from_step1]
- Success criteria: [from_step1]

Perform 6D analysis (Technical, Business, Team, Ecosystem, Strategic, Meta)"
```

**DO NOT proceed to Step 3 until /ultra-think completes and returns structured analysis.**

#### Step 3: Analysis Validation (MUST DO THIRD)

Present analysis **summary** (NOT full 6D output) to user and use AskUserQuestion for validation:

```
Show: 2-3 key findings from Step 2
Ask: "Does this analysis align with your understanding?"
Options: Satisfied / Needs Adjustment / Critical Miss
```

**DO NOT proceed to Step 4 until user validation is collected.**

#### Step 4: Iteration Decision (MUST DO FOURTH)

Based on Step 3 response:
- If "Satisfied" → Proceed to Step 5
- If "Needs Adjustment" → Collect feedback → Back to Step 2 (max 2 iterations)
- If "Critical Miss" → Back to Step 1

**DO NOT proceed to Step 5 without handling iteration properly.**

#### Step 5: Generate Spec Content (MUST DO FIFTH)

Use Edit tool to update `.ultra/specs/product.md`:

```
Target sections:
- Section 1: Problem Statement (extract from Step 2 analysis)
- Section 2: Target Users (extract from Step 1 + Step 2)

MUST use Edit tool with specific old_string and new_string
DO NOT overwrite entire file
```

Save research report to `.ultra/docs/research/problem-analysis-{date}.md`

**DO NOT proceed to Step 6 until files are written and verified.**

#### Step 6: Round Satisfaction Rating (MUST DO LAST)

Use AskUserQuestion to collect rating:

```
Question: "Rate your satisfaction with Round 1 (Problem Discovery)"
Options: 5/4/3/2/1 stars
If rating < 4: Collect improvement suggestions
```

Record to `.ultra/docs/research/metadata.json` (partial, will complete after all rounds)

**DO NOT proceed to Round 2 until rating is collected.**

---

### Round 2: Solution Exploration (20-25 min)

**MANDATORY EXECUTION SEQUENCE - Follow EXACTLY**:

#### Step 1: Requirement Clarification (MUST DO FIRST)

**HYBRID MODEL: Core Questions (Standardized) + Extension Questions (Dynamic)**

##### Part A: Core Questions (Standardized)

Load **Core Questions 6-8** from `@config/research/interaction-points-core.md`:
6. MVP Feature Scope (Core Functionality/User Management/Data Management/Integration/Analytics)
7. Non-Functional Requirements Priority (Performance/Security/Scalability/Reliability/Accessibility)
8. User Scenario Count (1-3/4-6/7-10/10+ scenarios)

Use AskUserQuestion tool for each core question.

##### Part B: Extension Questions (Dynamic Generation)

**Claude MUST generate 1-2 context-specific questions** based on:
- User's answers from Round 1 (pain points, scale, timeline)
- Project type characteristics
- Domain-specific considerations

**Generation Guidelines**:
1. Format: 2-4 options per question, header ≤12 chars, label + description for each option
2. Validate before use: header.length ≤12, options 2-4, all options have label + description
3. If validation fails → retry (max 2 times) → fallback to core questions only
4. Domain Examples:
   - High Scale Projects: "数据量级？" (header: "Data Volume", options: <1TB/1-10TB/10-100TB/>100TB)
   - Real-time Apps: "延迟要求？" (header: "Latency", options: <50ms/50-200ms/200-500ms/>500ms)
   - Multi-tenant SaaS: "租户隔离？" (header: "Isolation", options: Schema/Database/App-level/Physical)
   - Mobile First: "离线支持？" (header: "Offline", options: Full/Partial/Read-only/None)

**DO NOT proceed to Step 2 until ALL questions (core + extension) are answered.**

#### Step 2: Deep Analysis (MUST DO SECOND)

Invoke `/ultra-think` with user input + Round 1 context:

```
SlashCommand: /ultra-think "Generate user stories for [project_name] based on:
- MVP features: [from_step1]
- Key scenarios: [from_step1]
- NFRs: [from_step1]
- Problem context: [from_round1]

Perform 6D solution analysis and generate prioritized user stories"
```

**DO NOT proceed to Step 3 until /ultra-think completes.**

#### Step 3: Analysis Validation (MUST DO THIRD)

Present user stories summary and use AskUserQuestion:

```
Show: Generated user stories (titles only, not full descriptions)
Ask: "Do these user stories cover your expected functionality?"
Options: Satisfied / Needs Adjustment / Critical Miss
```

**DO NOT proceed to Step 4 until user validation is collected.**

#### Step 4: Iteration Decision (MUST DO FOURTH)

Based on Step 3 response (same logic as Round 1)

#### Step 5: Generate Spec Content (MUST DO FIFTH)

Use Edit tool to **append** to `.ultra/specs/product.md`:

```
Target sections:
- Section 3: User Stories (from Step 2 analysis)
- Section 4: Functional Requirements (derived from stories)
- Section 5: Non-Functional Requirements (from Step 1)

MUST use Edit tool to append, NOT overwrite Round 1 content
```

Save research report to `.ultra/docs/research/solution-exploration-{date}.md`

**DO NOT proceed to Step 6 until files are updated.**

#### Step 6: Round Satisfaction Rating (MUST DO LAST)

Collect rating for Round 2 (same process as Round 1)

---

### Round 3: Technology Selection (15-20 min)

**MANDATORY EXECUTION SEQUENCE - Follow EXACTLY**:

#### Step 1: Requirement Clarification (MUST DO FIRST)

**HYBRID MODEL: Core Questions (Standardized) + Extension Questions (Dynamic)**

##### Part A: Core Questions (Standardized)

Load **Core Questions 9-11** from `@config/research/interaction-points-core.md`:
9. Technology Stack Constraints (Specific language/framework/cloud/database/No constraints)
10. Team Skills (Frontend/Backend/DevOps/Database/Beginner)
11. Performance Requirements (Low Latency/High Throughput/Core Web Vitals/Cost Efficiency/Standard)

Use AskUserQuestion tool for each core question.

##### Part B: Extension Questions (Dynamic Generation)

**Claude MUST generate 1-2 context-specific questions** based on:
- Project scale and performance needs from Round 1
- MVP features and NFRs from Round 2
- Domain-specific technology considerations

**Generation Guidelines**:
1. Format: 2-4 options per question, header ≤12 chars, label + description for each option
2. Validate before use: header.length ≤12, options 2-4, all options have label + description
3. If validation fails → retry (max 2 times) → fallback to core questions only
4. Domain Examples:
   - AI/ML Projects: "模型部署？" (header: "Deployment", options: Cloud API/Self-hosted/Edge/Hybrid)
   - Blockchain: "共识机制？" (header: "Consensus", options: PoW/PoS/PoA/BFT)
   - Video Streaming: "编码方案？" (header: "Codec", options: H.264/H.265/VP9/AV1)
   - IoT: "通信协议？" (header: "Protocol", options: MQTT/CoAP/HTTP/WebSocket)

**DO NOT proceed to Step 2 until ALL questions (core + extension) are answered.**

#### Step 2: Deep Analysis (MUST DO SECOND)

Invoke `/ultra-think` with MCP tool usage:

```
SlashCommand: /ultra-think "Evaluate technology stack for [project_name]:
- Requirements from Round 1-2
- Tech constraints: [from_step1]
- Team skills: [from_step1]
- Performance needs: [from_step1]

Use Context7 MCP for official docs, Exa MCP for code examples.
Perform 6D tech comparison (pros/cons/trade-offs)"
```

**DO NOT proceed to Step 3 until /ultra-think completes.**

#### Step 3: Analysis Validation (MUST DO THIRD)

Present technology recommendations summary:

```
Show: Recommended stack with top 3 pros and top 3 trade-offs
Ask: "Do you agree with the recommended technology stack?"
Options: Satisfied / Needs Adjustment / Critical Miss
```

**DO NOT proceed to Step 4 until user validation is collected.**

#### Step 4: Iteration Decision (MUST DO FOURTH)

Based on Step 3 response (same logic as Round 1)

#### Step 5: Generate Spec Content (MUST DO FIFTH)

Use Write tool to create `.ultra/specs/architecture.md`:

```
Target content:
- Tech stack with rationale
- Architecture decisions (justified with 6D analysis)
- Trade-offs and mitigation strategies

MUST create new file (Round 3 is first time writing architecture.md)
```

Save research report to `.ultra/docs/research/tech-evaluation-{date}.md`

**DO NOT proceed to Step 6 until files are created.**

#### Step 6: Round Satisfaction Rating (MUST DO LAST)

Collect rating for Round 3 (same process as Round 1)

---

### Round 4: Risk & Constraints (15-20 min)

**MANDATORY EXECUTION SEQUENCE - Follow EXACTLY**:

#### Step 1: Requirement Clarification (MUST DO FIRST)

**HYBRID MODEL: Core Questions (Standardized) + Extension Questions (Dynamic)**

##### Part A: Core Questions (Standardized)

Load **Core Questions 12-13** from `@config/research/interaction-points-core.md`:
12. Critical Risks (Technical Complexity/Time Constraints/Budget/Scalability/Security/Vendor Lock-in)
13. Hard Constraints (Fixed Deadline/Fixed Budget/Compliance/Technology Restrictions/Team Size)

Use AskUserQuestion tool for each core question.

##### Part B: Extension Questions (Dynamic Generation)

**Claude MUST generate 1-2 context-specific questions** based on:
- Identified risks and constraints from previous rounds
- Project timeline and budget implications
- Domain-specific regulatory or operational constraints

**Generation Guidelines**:
1. Format: 2-4 options per question, header ≤12 chars, label + description for each option
2. Validate before use: header.length ≤12, options 2-4, all options have label + description
3. If validation fails → retry (max 2 times) → fallback to core questions only
4. Domain Examples:
   - Regulated Industries: "审计频率？" (header: "Audit Freq", options: Monthly/Quarterly/Yearly/None)
   - Global Projects: "时区支持？" (header: "Time Zones", options: Single/Regional/Global/24/7)
   - Open Source: "许可限制？" (header: "License", options: MIT/Apache/GPL/Proprietary)
   - Critical Systems: "故障容忍？" (header: "Fault", options: Zero-downtime/Hot-standby/Cold-standby/Best-effort)

**DO NOT proceed to Step 2 until ALL questions (core + extension) are answered.**

#### Step 2: Deep Analysis (MUST DO SECOND)

Invoke `/ultra-think` with full project context:

```
SlashCommand: /ultra-think "Identify risks and constraints for [project_name]:
- User concerns: [from_step1]
- Hard constraints: [from_step1]
- Complete context from Round 1-3

Perform 6D risk analysis with mitigation strategies"
```

**DO NOT proceed to Step 3 until /ultra-think completes.**

#### Step 3: Analysis Validation (MUST DO THIRD)

Present risk assessment summary:

```
Show: Top 5 risks with mitigation strategies
Ask: "Do these risks and mitigation strategies address your concerns?"
Options: Satisfied / Needs Adjustment / Critical Miss
```

**DO NOT proceed to Step 4 until user validation is collected.**

#### Step 4: Iteration Decision (MUST DO FOURTH)

Based on Step 3 response (same logic as Round 1)

#### Step 5: Generate Spec Content (MUST DO FIFTH)

Use Edit tool to **append** risk sections:

```
Update:
- .ultra/specs/product.md (add Risk Management section)
- .ultra/specs/architecture.md (add Technical Risks section)

MUST use Edit tool to append to existing content
```

Save research report to `.ultra/docs/research/risk-assessment-{date}.md`

**DO NOT proceed to Step 6 until files are updated.**

#### Step 6: Round Satisfaction Rating (MUST DO LAST)

Collect rating for Round 4 (same process as Round 1)

---

**Final Validation**: Overall quality check (1-5 rating), improvement suggestions collection

**Output**:
- ✅ `specs/product.md`: 100% complete (no [NEEDS CLARIFICATION])
- ✅ `specs/architecture.md`: 100% complete with justified decisions
- ✅ Research reports: `.ultra/docs/research/` (4 reports + metadata.json)
- ✅ Quality metrics: Round satisfaction scores, overall rating, iteration count

**Detailed interactive questions**: See `@config/research/interaction-points.md`

---

### Mode 2: Focused Technology Research (Secondary)

**When**: Specific technology decision during development

**Duration**: 10-15 minutes

**Process**: Single-round 6D comparison, auto-update architecture.md

**Detailed workflow**: See `@config/research/mode-2-focused.md`

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

1. **Validate spec completeness**: See `@config/research/output-templates.md`

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

**Quality Metrics**: Automatically saved to `.ultra/docs/research/metadata.json`

**Collected data**:
- Project type and rounds executed
- Round satisfaction scores (1-5 stars per round)
- Iteration counts (number of retries per round)
- Overall satisfaction rating and total duration
- Improvement suggestions from user

**Example**: `{"overallSatisfaction": 4.5, "roundSatisfaction": {"round1": 4.5, ...}, "totalDuration": "85 minutes"}`

**Complete schema**: See `@config/research/metadata-schema.md`

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

**Detailed templates**: See `@config/research/output-templates.md`

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
