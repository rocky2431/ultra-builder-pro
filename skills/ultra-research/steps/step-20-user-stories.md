# Step 20: User Stories & Acceptance Criteria

## MANDATORY EXECUTION RULES

- DERIVE stories from scenarios (step-11) — not invented from thin air
- EVERY story has acceptance criteria — no story ships without testable conditions
- USE standard format: "As a [persona], I want [action], so that [benefit]"
- PRIORITIZE using MoSCoW: Must / Should / Could / Won't
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 11 (User Scenarios) completed with [C]
- `.ultra/specs/product.md` §1-3 exist

## CONTEXT BOUNDARIES

- Focus: What specific capabilities does the product need?
- Stories must trace back to scenarios and personas
- This is about WHAT the product does, not HOW it's built
- Acceptance criteria must be testable and specific

## EXECUTION SEQUENCE

### 1. Extract Stories from Scenarios

For each scenario from step-11, decompose into user stories:

**Mapping**: Scenario → Stories
- S1 (highest priority scenario) → 3-5 stories
- S2 → 2-4 stories
- S3 → 2-3 stories
- Total: 8-15 stories for MVP

### 2. Write Stories with Acceptance Criteria

For each story:

```
As a [Persona Name],
I want [specific action],
so that [measurable benefit].

Acceptance Criteria:
- Given [context], when [action], then [expected result]
- Given [context], when [edge case], then [expected result]
- [Performance requirement if applicable]
```

### 3. Prioritize with MoSCoW

Discuss with user via AskUserQuestion:
"Here are the stories I've derived from our scenarios. For MVP, which are Must-Have vs Nice-to-Have?"

| Priority | Definition | Guidance |
|----------|-----------|---------|
| **Must** | Product is useless without this | Blocks primary scenario |
| **Should** | Important but workaround exists | Enhances primary scenario |
| **Could** | Nice to have if time allows | Supports secondary scenarios |
| **Won't** | Explicitly excluded for now | Out of scope (with rationale) |

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/product.md` §4:

```markdown
## §4 User Stories & Features

### Story Map Overview

| ID | Story | Persona | Scenario | Priority | Complexity |
|----|-------|---------|----------|----------|-----------|
| US-01 | [Short title] | [P1] | S1 | Must | [S/M/L] |
| US-02 | [Short title] | [P1] | S1 | Must | [S/M/L] |
| US-03 | [Short title] | [P1] | S2 | Must | [S/M/L] |
| US-04 | [Short title] | [P2] | S2 | Should | [S/M/L] |
| ... | ... | ... | ... | ... | ... |

### Must-Have Stories

#### US-01: [Title]
**As a** [Persona], **I want** [action], **so that** [benefit].

**Acceptance Criteria**:
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [edge case], then [result]
- [ ] [Performance: response time < Xms]

**Traces to**: Scenario [S#], Opportunity [O#]
**Complexity**: [S/M/L] — [Brief rationale]

#### US-02: [Title]
[Same structure]

#### US-03: [Title]
[Same structure]

### Should-Have Stories

#### US-04: [Title]
[Same structure]

### Could-Have Stories

#### US-07: [Title]
[Same structure]

### Story Statistics
- **Total stories**: [N]
- **Must-have**: [N] ([X]%)
- **Should-have**: [N] ([X]%)
- **Could-have**: [N] ([X]%)
- **Traceability**: [X]% of stories trace to scenarios
```

### 5. Present to User and Gate

Show the User Stories summary. Ask:
- Are the Must-Have stories correct?
- Any stories missing?
- Are acceptance criteria testable?

```
[C] Continue — Stories validated, proceed to Features & Scope
[R] Revise — Adjust stories, priorities, or acceptance criteria
[A] Add — Include additional stories
```

**HALT — wait for user response before proceeding.**

### 6. Handle Response

- **[C]**: Load next step: `./step-21-features-scope.md`
- **[R]**: Revise stories, update product.md §4, re-present
- **[A]**: Add stories, update, re-present

## SUCCESS METRICS

- 8-15 user stories derived from scenarios
- Every story has testable acceptance criteria
- MoSCoW prioritization applied with user input
- Stories trace back to scenarios and personas
- Output written to product.md §4

## FAILURE MODES

- Stories not connected to any scenario
- Acceptance criteria are vague ("it should work well")
- All stories are Must-Have (no real prioritization happened)
- Too many stories (>20 for MVP — scope creep)
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-21-features-scope.md`
