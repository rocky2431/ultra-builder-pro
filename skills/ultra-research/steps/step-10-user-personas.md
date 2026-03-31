# Step 10: User Personas

## MANDATORY EXECUTION RULES

- WEB SEARCH REQUIRED — validate personas against real user research data
- DEFINE 2-3 PERSONAS — not 1 (too narrow), not 5+ (too diluted)
- PERSONAS ARE ABOUT GOALS AND PAIN POINTS — not demographics
- CONNECT to step-00 (Q3: Desperate Specificity) and step-01 (Opportunities)
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Round 0 completed (steps 00-05) with [C], OR user chose "Feature Only" starting at step-10
- `.ultra/specs/product.md` exists

## CONTEXT BOUNDARIES

- Focus: WHO are we building for? What drives them? What blocks them?
- Personas represent real archetypes, not fictional characters
- Each persona must connect to prioritized opportunities from step-01
- This is Round 1 start — user scenarios follow in step-11

## SEARCH STRATEGY (MANDATORY)

Execute these web searches in parallel:

```
Search: "{{product_domain}} user persona research"
Search: "{{product_domain}} target audience profile behavior"
Search: "{{product_domain}} user needs pain points survey"
Search: "{{product_domain}} jobs to be done customer segment"
```

## EXECUTION SEQUENCE

### 1. Gather User Context

Ask user via AskUserQuestion:
"Based on our discovery work, who are the 2-3 types of people who would use this most? What do you already know about them?"

Cross-reference with:
- Step-00 §0: Target User Profile
- Step-01 §1: Prioritized Opportunities
- Step-04 §4: Target Segments

### 2. Research Real User Behavior

For each potential persona, search for:
- How they currently solve the problem (workflows, tools)
- What frustrates them most (forums, reviews, social media)
- What motivates their work (career goals, KPIs)
- How they discover and adopt new tools

### 3. Build Persona Profiles

For each persona (2-3), define:

| Element | What to capture |
|---------|----------------|
| Name & Role | Descriptive title, not a real name |
| Context | Where they work, team size, industry |
| Goals | What they're trying to achieve (2-3) |
| Pain points | What blocks them (2-3, connected to opportunities) |
| Current workflow | How they solve the problem today |
| Success metric | How THEY measure their own success |
| Adoption trigger | What would make them try a new solution |
| Objections | Why they might NOT adopt (barriers) |

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/product.md` §1-2:

```markdown
## §1 Problem Statement

### Core Problem
[One paragraph describing the problem, grounded in step-00 validation]

### Who It Affects
[Brief overview connecting problem to specific user types]

### Current Impact
- **Time cost**: [Hours/week wasted on workarounds]
- **Money cost**: [$ lost to inefficiency]
- **Opportunity cost**: [What they can't do because of this problem]

## §2 User Personas

### Persona 1: [Descriptive Name] (Primary)

**Role**: [Job title / context]
**Context**: [Where they work, team dynamics, industry]

**Goals**:
1. [Primary goal — what gets them promoted]
2. [Secondary goal — what they care about daily]
3. [Tertiary goal — nice to have]

**Pain Points**:
1. [Pain 1] — Connects to Opportunity [O#] from §1
2. [Pain 2] — Connects to Opportunity [O#] from §1
3. [Pain 3] — Source: [URL or user quote]

**Current Workflow**:
> [Step-by-step description of how they solve this today]
> Tools used: [List of current tools/processes]
> Time spent: [X hours/week]

**Success Metric**: [How they measure their own success]
**Adoption Trigger**: [What would make them try our solution]
**Objections**: [Why they might resist — e.g., "too busy to learn new tool"]

### Persona 2: [Descriptive Name] (Secondary)
[Same structure]

### Persona 3: [Descriptive Name] (Tertiary — optional)
[Same structure]

### Persona Prioritization

| Persona | Urgency | Willingness to Pay | Reachability | Priority |
|---------|---------|-------------------|-------------|----------|
| [P1] | High | High | Medium | **Primary** |
| [P2] | Medium | Medium | High | **Secondary** |
| [P3] | Low | Low | High | **Tertiary** |
```

### 5. Present to User and Gate

Show the Persona profiles. Ask user to validate:
- Do these feel like real people they know?
- Is anything missing from the profiles?
- Is the prioritization correct?

```
[C] Continue — Personas validated, proceed to User Scenarios
[R] Revise — Adjust persona details or prioritization
[A] Add — Include an additional persona
```

**HALT — wait for user response before proceeding.**

### 6. Handle Response

- **[C]**: Load next step: `./step-11-user-scenarios.md`
- **[R]**: Revise personas, update product.md §1-2, re-present
- **[A]**: Add persona (max 3 total), update, re-present

## SUCCESS METRICS

- 2-3 personas defined with goals, pain points, and current workflows
- Each persona connects to opportunities from step-01
- Personas grounded in web research, not pure imagination
- Clear prioritization with rationale
- Output written to product.md §1-2

## FAILURE MODES

- Demographic-only personas ("25-35 year old male in tech")
- Too many personas (>3 dilutes focus)
- Pain points not connected to validated opportunities
- No current workflow description
- Missing adoption triggers and objections
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-11-user-scenarios.md`
