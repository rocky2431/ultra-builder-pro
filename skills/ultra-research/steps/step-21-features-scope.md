# Step 21: Features & Scope Definition

## MANDATORY EXECUTION RULES

- EXPLICITLY DEFINE what is OUT of scope — this prevents scope creep
- GROUP stories into features — features are implementable units
- EVERY exclusion needs a RATIONALE — "not now" is not enough
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 20 (User Stories) completed with [C]
- `.ultra/specs/product.md` §1-4 exist

## CONTEXT BOUNDARIES

- Focus: Group stories into features, define scope boundaries
- Features are clusters of related stories that deliver a capability
- "Features Out" is as important as "Features In"
- Reference step-04 (Strategic Trade-offs) for scope decisions

## EXECUTION SEQUENCE

### 1. Group Stories into Features

Cluster related user stories into features:

```
Feature A: [Name]
├── US-01: [Story]
├── US-02: [Story]
└── US-03: [Story]

Feature B: [Name]
├── US-04: [Story]
└── US-05: [Story]
```

Each feature should be:
- Independently valuable (delivers user value on its own)
- Estimable (can assess complexity)
- Testable (can verify it works end-to-end)

### 2. Define Scope Boundaries

For each potential feature, classify:

| Classification | Meaning |
|---------------|---------|
| **In scope (MVP)** | Must-have stories, ships in v1 |
| **In scope (v2)** | Should-have stories, planned for later |
| **Out of scope** | Won't build — with explicit rationale |

### 3. Document "Features Out"

For each excluded feature, document:
- What it is
- Why it's excluded (reference strategic trade-offs from step-04)
- When it might be reconsidered
- What users should do instead

This prevents:
- Future scope creep ("but we said we'd do X")
- Re-debating settled decisions
- Building things that conflict with strategy

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/product.md` §5:

```markdown
## §5 Feature Scope

### Features In (MVP)

#### Feature 1: [Name]
- **Description**: [What this feature does]
- **Stories**: US-01, US-02, US-03
- **User value**: [What user can do with this]
- **Priority**: Must-Have
- **Complexity**: [S/M/L]

#### Feature 2: [Name]
- **Description**: [What this feature does]
- **Stories**: US-04, US-05
- **User value**: [What user can do with this]
- **Priority**: Must-Have
- **Complexity**: [S/M/L]

#### Feature 3: [Name]
[Same structure]

### Features In (v2 — Planned)

#### Feature 4: [Name]
- **Description**: [What this feature does]
- **Stories**: US-07, US-08
- **Rationale for deferral**: [Why not MVP]
- **Trigger to build**: [When to reconsider]

### Features Out (Explicitly Excluded)

| Feature | Rationale | Reconsider When | Alternative |
|---------|-----------|----------------|-------------|
| [Feature X] | [Why excluded — reference strategy §4] | [Condition] | [What users do instead] |
| [Feature Y] | [Why excluded] | [Condition] | [Alternative] |
| [Feature Z] | [Why excluded] | [Condition] | [Alternative] |

### Scope Summary
- **MVP features**: [N] features, [N] stories
- **v2 features**: [N] features, [N] stories
- **Excluded features**: [N] features
- **Scope confidence**: [X]%
```

### 5. Present to User and Gate

Show the Feature Scope summary. Ask:
- Is the MVP scope right? Too big? Too small?
- Are the exclusions correct?
- Any missing features?

```
[C] Continue — Scope locked, proceed to Success Metrics
[R] Revise — Adjust feature grouping or scope boundaries
[E] Expand — Move something from v2 to MVP
[T] Trim — Move something from MVP to v2
```

**HALT — wait for user response before proceeding.**

### 6. Handle Response

- **[C]**: Load next step: `./step-22-success-metrics.md`
- **[R]**: Revise features, update product.md §5, re-present
- **[E]/[T]**: Adjust scope, update, re-present

## SUCCESS METRICS

- Stories grouped into coherent features
- Clear MVP vs v2 scope boundary
- Every exclusion has a rationale and reconsideration trigger
- Features trace to user stories and scenarios
- Output written to product.md §5

## FAILURE MODES

- No "Features Out" section (everything is in scope)
- Features that don't map to any user stories
- Exclusion rationale is just "not now" (needs specific reason)
- MVP scope is too large (>5-7 features for a first version)
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-22-success-metrics.md`
