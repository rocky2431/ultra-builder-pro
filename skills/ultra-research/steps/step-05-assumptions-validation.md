# Step 05: Assumptions & Validation Plan

## MANDATORY EXECUTION RULES

- EXTRACT assumptions from ALL previous steps (00-04) — not just the obvious ones
- PRIORITIZE by Impact × Uncertainty — focus on "leap of faith" assumptions
- DESIGN cheap, fast experiments — not "build it and see"
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Steps 00-04 completed with [C]
- `.ultra/specs/discovery.md` §0-4 exist

## CONTEXT BOUNDARIES

- Focus: What are we assuming? What's riskiest? How do we validate cheaply?
- This is the LAST step of Round 0 — it synthesizes everything discovered so far
- After this step, user decides: proceed to Round 1 or investigate further
- Based on Alberto Savoia (Pretotyping) and Marty Cagan methodologies

## SEARCH STRATEGY (MANDATORY)

Execute these web searches:

```
Search: "{{product_domain}} validation methods pretotype MVP"
Search: "{{product_domain}} common startup mistakes failed assumptions"
Search: "landing page test fake door validation {{product_domain}}"
Search: "{{product_domain}} customer interview validation techniques"
```

## EXECUTION SEQUENCE

### 1. Extract Assumptions from Previous Steps

Review §0-4 and extract assumptions across 5 categories:

| Category | Source | What to look for |
|----------|--------|-----------------|
| **Value** | §0, §1 | Will users actually want this? |
| **Usability** | §1 | Can users figure it out without help? |
| **Feasibility** | §1 (solutions) | Can we build it with current technology? |
| **Viability** | §2 | Does the business case work at these numbers? |
| **Go-to-Market** | §3, §4 | Can we reach and convert our target users? |

### 2. Prioritize Assumptions

Map each assumption on Impact × Uncertainty:

```
                    High Impact
                        │
    VALIDATE FIRST ─────┼───── MONITOR
    (Leap of Faith)     │     (Important but clear)
                        │
   Low Uncertainty ─────┼───── High Uncertainty
                        │
    IGNORE ─────────────┼───── INVESTIGATE
    (Low stakes)        │     (Uncertain but low impact)
                        │
                    Low Impact
```

Focus on "Leap of Faith" quadrant: **High Impact + High Uncertainty**

### 3. Design Validation Experiments

For top 3-5 leap-of-faith assumptions, design cheap, fast experiments:

**Experiment Design Framework:**

| Element | Description |
|---------|-------------|
| Assumption | What exactly are we assuming? |
| Category | Value / Usability / Feasibility / Viability / GTM |
| Method | How will we test this? |
| Success criteria | What result validates the assumption? |
| Failure criteria | What result invalidates it? |
| Effort | Hours/days to execute |
| Timeline | When can we have results? |

**Preferred Methods** (cheapest first):
1. **Data analysis**: Existing data that proves/disproves the assumption
2. **Customer interviews**: 5-10 targeted conversations
3. **Fake door test**: Landing page with sign-up / "notify me" button
4. **Concierge MVP**: Manually deliver the value to 3-5 users
5. **Pretotype**: Mechanical Turk version of the product
6. **Prototype**: Clickable mockup tested with real users
7. **MVP**: Minimum viable version with real functionality

### 4. Define Decision Framework

For each experiment:

```
If experiment SUCCEEDS → [Next action]
If experiment FAILS → [Pivot / Investigate / Kill]
If results are AMBIGUOUS → [How to get clarity]
```

### 5. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/discovery.md` §5:

```markdown
## §5 Key Assumptions & Validation Plan

### Assumption Inventory

| # | Assumption | Category | Impact | Uncertainty | Priority |
|---|-----------|----------|--------|-------------|----------|
| A1 | [Statement] | Value | High | High | **Validate First** |
| A2 | [Statement] | Viability | High | High | **Validate First** |
| A3 | [Statement] | GTM | High | Medium | **Validate First** |
| A4 | [Statement] | Feasibility | Medium | High | Investigate |
| A5 | [Statement] | Usability | Medium | Medium | Monitor |
| A6 | [Statement] | Value | Low | Low | Ignore |

### Leap-of-Faith Assumptions (Top 3-5)

#### A1: [Assumption Statement]
- **Category**: [Value / Viability / GTM / Feasibility / Usability]
- **Why it matters**: [What happens if this is wrong]
- **Current evidence**: [What we know from steps 00-04]
- **Evidence gap**: [What we don't know]

**Validation Experiment:**
- **Method**: [Specific method]
- **Success criteria**: [Measurable outcome that validates]
- **Failure criteria**: [Measurable outcome that invalidates]
- **Effort**: [Hours/days]
- **Timeline**: [When results expected]

**Decision Framework:**
- ✅ If validated → [Proceed to Round 1]
- ❌ If invalidated → [Pivot to X / Investigate Y / Kill]
- ⚠️ If ambiguous → [Additional experiment Z]

#### A2: [Assumption Statement]
[Same structure]

#### A3: [Assumption Statement]
[Same structure]

### Validation Roadmap

| Week | Experiment | Assumption | Expected Result |
|------|-----------|-----------|----------------|
| 1 | [Experiment 1] | A1 | [What we'll learn] |
| 1-2 | [Experiment 2] | A2 | [What we'll learn] |
| 2-3 | [Experiment 3] | A3 | [What we'll learn] |

### Round 0 Summary

**Product Discovery Confidence**:
- **Problem validation**: [X]% — [One-line summary]
- **Opportunity space**: [X]% — [One-line summary]
- **Market size**: [X]% — [One-line summary]
- **Competitive position**: [X]% — [One-line summary]
- **Strategy clarity**: [X]% — [One-line summary]
- **Overall R0 confidence**: [X]%

**Recommendation**: [Proceed to Round 1 / Validate assumptions first / Pivot]
```

### 6. Write Round 0 Research Report

**WRITE** to `.ultra/docs/research/product-discovery-{date}.md`:

```markdown
# Round 0: Product Discovery & Strategy

> **Confidence**: [X]%
> **Steps completed**: 00-05
> **Completed**: [date]

## Key Findings
[3-5 bullet points of most important discoveries]

## Decisions Made
[Strategic choices and their rationale]

## Open Questions
[What remains uncertain]

## Assumptions to Validate
[Top 3 from §5]
```

### 7. Present to User and Gate

Show the complete Round 0 summary. Highlight:
- The top 3 leap-of-faith assumptions
- Overall confidence level
- Recommendation (proceed / validate / pivot)

```
[C] Continue — Proceed to Round 1 (User & Scenario Discovery)
[V] Validate — Pause to run validation experiments before continuing
[P] Pivot — Rethink the product direction based on findings
```

**HALT — wait for user response before proceeding.**

### 8. Handle Response

- **[C]**: Load next step: `./step-10-user-personas.md`
- **[V]**: Help design validation experiments in detail, then re-present gate when done
- **[P]**: Restart from step-00 with revised direction

## SUCCESS METRICS

- Assumptions extracted from ALL previous steps (not just surface-level)
- Each assumption categorized and prioritized
- Top 3-5 have detailed validation experiments
- Each experiment has clear success/failure criteria
- Decision framework defined for each outcome
- Round 0 research report written
- Output written to discovery.md §5

## FAILURE MODES

- Only extracting obvious assumptions (missing viability, GTM)
- Designing expensive experiments ("build an MVP") when cheaper options exist
- No clear success/failure criteria for experiments
- Missing the decision framework (what do we DO with the results?)
- Overly optimistic confidence assessment
- Not writing both spec file AND research report

## NEXT STEP

After user selects [C], read and follow: `./step-10-user-personas.md`
