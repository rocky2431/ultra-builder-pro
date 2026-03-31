# Step 11: User Scenarios

## MANDATORY EXECUTION RULES

- DEFINE 3-5 SCENARIOS — each with trigger, flow, and outcome
- SCENARIOS ARE USER JOURNEYS — not feature lists
- CONNECT each scenario to a specific persona from step-10
- INCLUDE the emotional arc — frustration → discovery → relief
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 10 (User Personas) completed with [C]
- `.ultra/specs/product.md` §1-2 exist

## CONTEXT BOUNDARIES

- Focus: In what situations do users encounter this problem? What's the journey?
- Scenarios describe WHEN and HOW users interact, not WHAT the product does
- Each scenario should be a story the user can picture happening
- Prioritize scenarios by frequency and pain severity

## EXECUTION SEQUENCE

### 1. Identify Key Scenarios

For each persona from step-10, ask:
- What triggers them to need a solution? (the "aha" moment)
- What's the most common situation? (daily/weekly use)
- What's the most painful situation? (highest frustration)
- What's the most valuable situation? (highest ROI)

Ask user via AskUserQuestion:
"For [Primary Persona], what's the most common situation where they hit this problem? Walk me through a typical day."

### 2. Map Scenario Details

For each scenario (3-5), capture:

| Element | Description |
|---------|-------------|
| Trigger | What event causes the user to need a solution? |
| Context | Where are they? What device? What time pressure? |
| Current flow | How they handle it today (the painful way) |
| Desired flow | How they WISH they could handle it |
| Success outcome | What does "done well" look like? |
| Failure outcome | What happens if they fail? |
| Frequency | How often does this scenario occur? |
| Emotional arc | Frustration → Action → Resolution |

### 3. Prioritize Scenarios

Score by:
- **Frequency** (1-5): How often does this happen?
- **Pain severity** (1-5): How painful is the current experience?
- **Value** (1-5): How much value does solving this create?

Priority Score = Frequency × Pain × Value

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/product.md` §3:

```markdown
## §3 User Scenarios

### Scenario Overview

| # | Scenario | Persona | Frequency | Pain | Value | Score |
|---|----------|---------|-----------|------|-------|-------|
| S1 | [Name] | [P1] | 5 | 4 | 5 | 100 |
| S2 | [Name] | [P1] | 4 | 5 | 4 | 80 |
| S3 | [Name] | [P2] | 3 | 4 | 4 | 48 |
| S4 | [Name] | [P2] | 2 | 3 | 3 | 18 |

### Scenario 1: [Descriptive Name] ⭐ Primary

**Persona**: [Persona Name]
**Frequency**: [Daily / Weekly / Monthly]

**Trigger**: [What event causes this scenario]
**Context**: [Where, when, device, time pressure]

**Current Flow** (painful):
1. [Step 1 — what they do today]
2. [Step 2 — where friction occurs]
3. [Step 3 — workaround they use]
4. [Step 4 — outcome and time wasted]

> 💬 *"[User quote or typical complaint that captures the frustration]"*

**Desired Flow** (with our product):
1. [Step 1 — trigger detected]
2. [Step 2 — streamlined action]
3. [Step 3 — fast resolution]
4. [Step 4 — outcome achieved in less time]

**Success Outcome**: [What "done well" looks like — specific and measurable]
**Failure Outcome**: [What happens if they fail — consequences]
**Emotional Arc**: [Frustration with X] → [Discovery of solution] → [Relief / satisfaction]

### Scenario 2: [Descriptive Name]
[Same structure]

### Scenario 3: [Descriptive Name]
[Same structure]

### Round 1 Summary

**User & Scenario Discovery Confidence**:
- **Persona accuracy**: [X]% — [One-line assessment]
- **Scenario coverage**: [X]% — [One-line assessment]
- **Overall R1 confidence**: [X]%
```

### 5. Write Round 1 Research Report

**WRITE** to `.ultra/docs/research/user-scenario-{date}.md`:

```markdown
# Round 1: User & Scenario Discovery

> **Confidence**: [X]%
> **Steps completed**: 10-11
> **Completed**: [date]

## Key Findings
[3-5 bullet points]

## Personas Defined
[Names and one-line descriptions]

## Scenarios Prioritized
[Top 3 with scores]

## Surprises
[What was unexpected]
```

### 6. Present to User and Gate

Show the User Scenarios summary. Ask:
- Do these scenarios feel realistic?
- Is anything missing from the journey?
- Is the prioritization right?

```
[C] Continue — Scenarios validated, proceed to Round 2 (Feature Definition)
[R] Revise — Adjust scenario details or prioritization
[A] Add — Include additional scenario
```

**HALT — wait for user response before proceeding.**

### 7. Handle Response

- **[C]**: Load next step: `./step-20-user-stories.md`
- **[R]**: Revise scenarios, update product.md §3, re-present
- **[A]**: Add scenario (max 5 total), update, re-present

## SUCCESS METRICS

- 3-5 scenarios defined with full detail
- Each scenario connected to a persona
- Current flow AND desired flow documented
- Scenarios prioritized by Frequency × Pain × Value
- Round 1 research report written
- Output written to product.md §3

## FAILURE MODES

- Scenarios that describe features instead of user journeys
- Missing the "current flow" (how users cope today)
- No emotional arc (scenarios feel clinical, not human)
- All scenarios for one persona (need coverage across personas)
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-20-user-stories.md`
