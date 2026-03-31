# Step 31: Solution Strategy & Tech Stack

## MANDATORY EXECUTION RULES

- WEB SEARCH REQUIRED — verify all technology claims
- USE Context7 MCP for framework documentation
- COMPARE TOP 3 OPTIONS for every major tech decision
- EVERY CHOICE needs RATIONALE — "it's popular" is not enough
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 30 (Architecture Context) completed with [C]
- `.ultra/specs/architecture.md` §1-3 exist

## CONTEXT BOUNDARIES

- Focus: Tech stack selection with evidence-based rationale (arc42 §4)
- Decisions must satisfy quality goals from §1
- Decisions must respect constraints from §2
- Compare options — never recommend without alternatives analyzed

## SEARCH STRATEGY (MANDATORY)

For each major technology decision:

```
Search: "[option A] vs [option B] vs [option C] {{product_domain}} 2024 2025"
Search: "[chosen framework] production performance benchmarks"
Search: "[chosen framework] scalability limitations"
Search: "[chosen database] vs alternatives for {{use_case}}"
```

Use Context7 MCP: Query official docs for each selected technology.

## EXECUTION SEQUENCE

### 1. Identify Key Technology Decisions

Based on system context (§3) and quality goals (§1):

| Decision Area | What to Decide |
|--------------|---------------|
| Language/Runtime | Primary programming language |
| Web Framework | API/web framework |
| Database | Primary data store |
| Caching | Caching layer (if needed) |
| Authentication | Auth approach |
| Hosting | Cloud/infrastructure |
| CI/CD | Build and deploy pipeline |
| Monitoring | Observability stack |

### 2. Compare Options (Top 3 per Decision)

For each decision, research and compare 3 options:

| Criterion | Option A | Option B | Option C |
|-----------|---------|---------|---------|
| Quality goal fit | [How it meets §1 goals] | ... | ... |
| Constraint fit | [How it respects §2] | ... | ... |
| Community/maturity | [Stars, contributors, releases] | ... | ... |
| Performance | [Benchmarks with source] | ... | ... |
| Learning curve | [Team skill match] | ... | ... |
| Cost | [Licensing, hosting costs] | ... | ... |

### 3. Make Decisions with Rationale

For each decision:
- **Chosen**: [Option]
- **Rationale**: [Why this one — reference quality goals and constraints]
- **Trade-off accepted**: [What we give up]
- **Risk**: [What could go wrong]
- **Migration path**: [How to change if this doesn't work]

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/architecture.md` §4:

```markdown
## §4 Solution Strategy

### Technology Decisions

#### Language & Runtime
- **Chosen**: [Language/Runtime]
- **Alternatives considered**: [Option B], [Option C]
- **Rationale**: [Why — reference §1 quality goals]
- **Trade-off**: [What we give up]
- **Source**: [Benchmark/doc URL]

#### Web Framework
- **Chosen**: [Framework]
- **Alternatives considered**: [Option B], [Option C]
- **Rationale**: [Why]
- **Trade-off**: [What we give up]
- **Source**: [URL]

#### Database
- **Chosen**: [Database]
- **Alternatives considered**: [Option B], [Option C]
- **Rationale**: [Why]
- **Trade-off**: [What we give up]
- **Source**: [URL]

#### Authentication
- **Chosen**: [Approach]
- **Alternatives considered**: [Option B], [Option C]
- **Rationale**: [Why]
- **Source**: [URL]

#### Hosting & Infrastructure
- **Chosen**: [Platform]
- **Alternatives considered**: [Option B], [Option C]
- **Rationale**: [Why]
- **Estimated cost**: [$X/month at launch scale]
- **Source**: [URL]

### Tech Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | [Tech] | [Ver] | [What it does] |
| Backend | [Tech] | [Ver] | [What it does] |
| Database | [Tech] | [Ver] | [What it does] |
| Cache | [Tech] | [Ver] | [What it does] |
| Auth | [Tech] | [Ver] | [What it does] |
| Hosting | [Tech] | - | [What it does] |
| CI/CD | [Tech] | - | [What it does] |
| Monitoring | [Tech] | - | [What it does] |

### Decision Confidence
- **Overall**: [X]%
- **Most confident**: [Decision] — [Why]
- **Least confident**: [Decision] — [Risk]
```

### 5. Present to User and Gate

```
[C] Continue — Tech stack defined, proceed to Building Blocks
[R] Revise — Reconsider specific technology choices
[D] Discuss — Deep-dive on a specific decision
```

**HALT — wait for user response before proceeding.**

### 6. Handle Response

- **[C]**: Load next step: `./step-32-building-blocks.md`
- **[R]**: Revise decisions, update architecture.md §4, re-present
- **[D]**: Deep-dive with additional research, then re-present

## SUCCESS METRICS

- Top 3 options compared for every major decision
- Every choice has explicit rationale referencing quality goals
- Trade-offs stated honestly
- All claims verified via web search or Context7
- Output written to architecture.md §4

## FAILURE MODES

- Single option considered ("just use React")
- No rationale beyond popularity
- Ignoring constraints from §2
- Not verifying version compatibility
- Technology choices that conflict with quality goals

## NEXT STEP

After user selects [C], read and follow: `./step-32-building-blocks.md`
