# Step 00: Problem Validation

## MANDATORY EXECUTION RULES

- NEVER skip this step — unvalidated problems lead to wasted research
- DO NOT generate solutions — this step validates the PROBLEM only
- ASK questions ONE AT A TIME via AskUserQuestion — do not batch
- PUSH on vague answers — "interesting" is not validation, "paying for it" is
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- `.ultra/specs/discovery.md` exists (created by /ultra-init)
- User has provided initial product idea or description

## CONTEXT BOUNDARIES

- Focus: Is this problem real, painful, and worth solving?
- NOT about solutions, features, or architecture
- NOT about market size (that's step-02)
- You are a skeptical advisor, not a cheerleader

## EXECUTION SEQUENCE

### 1. Detect Product Stage

Ask via AskUserQuestion to determine which forcing questions apply:

| Stage | Indicators | Questions |
|-------|-----------|-----------|
| Pre-product (idea, no users) | No existing product | Q1, Q2, Q3 |
| Has users (not paying) | Product exists, free users | Q2, Q4, Q5 |
| Has paying customers | Revenue exists | Q4, Q5, Q6 |
| Pure engineering/infra | Internal tool, no market | Q2, Q4 only |

### 2. Ask Forcing Questions (ONE AT A TIME)

For each applicable question, ask via AskUserQuestion. Push until you hear the "evidence" column — not the "red flags" column.

#### Q1: Demand Reality
**Ask**: "What is the strongest evidence someone actually wants this — not 'is interested,' but would be genuinely upset if it disappeared?"
- **Push until you hear**: Specific behavior — paying, expanding usage, panicking when it breaks
- **Red flags**: "People say it's interesting", waitlist signups, VC enthusiasm

#### Q2: Status Quo
**Ask**: "What are users doing RIGHT NOW to solve this — even badly? What does that workaround cost them?"
- **Push until you hear**: Specific workflow — hours wasted, dollars lost, tools duct-taped together
- **Red flags**: "Nothing — no solution exists" (if nobody is doing anything, the problem may not be painful enough)

#### Q3: Desperate Specificity
**Ask**: "Name the actual human who needs this most. Title? What gets them promoted? What gets them fired?"
- **Push until you hear**: A name, a role, a specific consequence they face
- **Red flags**: Category-level answers: "enterprises", "SMBs", "marketing teams"

#### Q4: Narrowest Wedge
**Ask**: "What is the smallest version someone would pay real money for — this week, not after you build the platform?"
- **Push until you hear**: One feature, one workflow, shippable in days
- **Red flags**: "Need full platform first", "can't strip it down"

#### Q5: Observation & Surprise
**Ask**: "Have you watched someone use this without helping them? What surprised you?"
- **Push until you hear**: A specific surprise that contradicted assumptions
- **Red flags**: "We sent a survey", "nothing surprising"

#### Q6: Future-Fit
**Ask**: "If the world looks meaningfully different in 3 years, does your product become more essential or less?"
- **Push until you hear**: Specific claim about how user's world changes and why that increases value
- **Red flags**: "Market growing 20% per year", "AI makes everything better"

### 3. Smart-Skip Rules

- If an earlier answer already covers a later question, skip it
- If user says "just do it" or provides a fully formed plan → fast-track with note
- Maximum 4 questions per session — prioritize by stage

### 4. Synthesize & Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/discovery.md` §0:

```markdown
## §0 Problem Validation Summary

### Product Stage
- **Stage**: [Pre-product / Has users / Has paying customers / Engineering/Infra]
- **Evidence**: [What indicates this stage]

### Demand Signal
- **Strength**: [Strong / Moderate / Weak / Unvalidated]
- **Evidence**: [Specific behaviors observed]
- **Risk**: [What could invalidate this demand]

### Status Quo Analysis
- **Current solutions**: [What users do today]
- **Cost of workaround**: [Time, money, friction]
- **Switching motivation**: [Why they'd change]

### Target User Profile
- **Primary**: [Specific role/person description]
- **Stakes**: [What gets them promoted / fired]
- **Pain frequency**: [Daily / Weekly / Occasional]

### Narrowest Wedge
- **MVP scope**: [Single feature/workflow]
- **Willingness to pay**: [Evidence level]
- **Ship timeline**: [Days / Weeks / Months]

### Validation Confidence
- **Overall**: [X]%
- **Strongest signal**: [What gives most confidence]
- **Biggest risk**: [What could be wrong]
- **Recommended next step**: [Proceed / Investigate further / Pivot]
```

### 5. Present to User and Gate

Show the Problem Validation Summary to user.

Present assessment honestly — if the problem feels weak, say so. Better to catch it now.

```
[C] Continue — Problem validated, proceed to Opportunity Discovery
[R] Revise — Discuss specific concerns before proceeding
[P] Pivot — Problem is weak, explore different angle
```

**HALT — wait for user response before proceeding.**

### 6. Handle Response

- **[C]**: Load next step: `./step-01-opportunity-discovery.md`
- **[R]**: Discuss concerns, revise §0, re-present
- **[P]**: Help user reframe the problem, restart step-00

## SUCCESS METRICS

- Product stage correctly identified
- At least 2 forcing questions asked and answered with evidence
- Problem Validation Summary written to discovery.md §0
- Confidence assessment is honest (not inflated)
- User has explicitly confirmed [C] before proceeding

## FAILURE MODES

- Asking all 6 questions regardless of stage (wastes user time)
- Accepting vague answers without pushing ("people are interested" → push harder)
- Skipping this step because user seems confident
- Inflating confidence to keep user happy
- Not writing output before presenting to user
- Proceeding without explicit [C] confirmation

## NEXT STEP

After user selects [C], read and follow: `./step-01-opportunity-discovery.md`
