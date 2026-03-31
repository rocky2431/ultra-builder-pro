# Step 22: Success Metrics

## MANDATORY EXECUTION RULES

- EVERY METRIC must have a specific numerical TARGET — not "improve X"
- INCLUDE both business AND user metrics
- DEFINE how each metric is MEASURED — not just what to measure
- BASELINE required — you can't improve what you haven't measured
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 21 (Features & Scope) completed with [C]
- `.ultra/specs/product.md` §1-5 exist

## CONTEXT BOUNDARIES

- Focus: How will we know if this product is succeeding?
- Metrics must be measurable, specific, and time-bound
- Connect metrics to strategic goals from step-04
- This is the LAST step of Round 2

## SEARCH STRATEGY (MANDATORY)

Execute these web searches:

```
Search: "{{product_domain}} key metrics KPIs benchmarks"
Search: "{{product_domain}} SaaS metrics success benchmarks"
Search: "{{product_domain}} user engagement retention benchmarks"
Search: "{{product_domain}} north star metric examples"
```

## EXECUTION SEQUENCE

### 1. Define North Star Metric

Ask user via AskUserQuestion:
"What single metric best captures whether this product is delivering value? (e.g., 'Weekly active workflows completed', 'Time saved per user per week')"

The North Star Metric should:
- Reflect core value delivery
- Be leading (not lagging)
- Be actionable (team can influence it)

### 2. Define Business Metrics

| Metric | What to define |
|--------|---------------|
| Revenue/adoption targets | Month 1, 3, 6, 12 |
| Growth rate | MoM or WoW targets |
| Retention | Day 1, Day 7, Day 30 |
| Conversion | Free → Paid (if applicable) |
| Unit economics | CAC, LTV, LTV/CAC ratio |

Use web search benchmarks for realistic targets.

### 3. Define User Metrics

| Metric | What to define |
|--------|---------------|
| Task completion | Success rate for key scenarios |
| Time on task | vs baseline (current workflow) |
| User satisfaction | NPS or CSAT target |
| Feature adoption | % of users using key features |
| Error rate | Failure frequency |

### 4. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/product.md` §6:

```markdown
## §6 Success Metrics

### North Star Metric
- **Metric**: [Name]
- **Definition**: [Exactly what is measured]
- **Current baseline**: [Current state or industry benchmark]
- **Target**: [Specific number]
- **Timeline**: [When to achieve]
- **Measurement method**: [How to collect this data]

### Business Metrics

| Metric | Baseline | Target (M3) | Target (M6) | Target (M12) | How Measured |
|--------|----------|-------------|-------------|--------------|-------------|
| [Revenue/Users] | [N/A or current] | [Target] | [Target] | [Target] | [Method] |
| [Growth rate] | [Benchmark] | [Target] | [Target] | [Target] | [Method] |
| [Retention D30] | [Benchmark] | [Target] | [Target] | [Target] | [Method] |
| [Conversion] | [Benchmark] | [Target] | [Target] | [Target] | [Method] |

_Benchmark sources: [URLs]_

### User Metrics

| Metric | Baseline | Target | How Measured |
|--------|----------|--------|-------------|
| Task completion rate | [Current %] | [Target %] | [Method] |
| Time on task | [Current min] | [Target min] | [Method] |
| User satisfaction (NPS) | [Industry avg] | [Target] | [Survey] |
| Feature adoption | [N/A] | [Target %] | [Analytics] |
| Error rate | [Current %] | [Target %] | [Logging] |

### Metric Prioritization

| Priority | Metric | Why |
|----------|--------|-----|
| P0 (check daily) | [North Star] | [Core value signal] |
| P0 (check daily) | [Critical metric] | [Business health] |
| P1 (check weekly) | [Important metric] | [Growth signal] |
| P2 (check monthly) | [Supporting metric] | [Quality signal] |

### Anti-Metrics (What NOT to Optimize)

| Anti-Metric | Why Not | What It Could Sacrifice |
|------------|---------|------------------------|
| [e.g., Page views] | [Vanity metric] | [Could sacrifice quality for clicks] |
| [e.g., Time in app] | [Could mean confusion] | [Could sacrifice efficiency] |

### Round 2 Summary

**Feature Definition Confidence**:
- **Story completeness**: [X]% — [One-line assessment]
- **Scope clarity**: [X]% — [One-line assessment]
- **Metric measurability**: [X]% — [One-line assessment]
- **Overall R2 confidence**: [X]%
```

### 5. Write Round 2 Research Report

**WRITE** to `.ultra/docs/research/feature-definition-{date}.md`:

```markdown
# Round 2: Feature Definition

> **Confidence**: [X]%
> **Steps completed**: 20-22
> **Completed**: [date]

## Key Findings
[3-5 bullet points]

## Stories Created
[Count by priority: Must/Should/Could]

## Scope Decisions
[Key inclusions and exclusions]

## Metrics Defined
[North Star + top 3 metrics]
```

### 6. Present to User and Gate

Show the Success Metrics summary. Ask:
- Are the targets realistic?
- Is the North Star metric right?
- Any metrics missing?

```
[C] Continue — Metrics defined, proceed to Round 3 (Architecture Design)
[R] Revise — Adjust targets or metrics
[D] Discuss — Explore specific metric benchmarks
```

**HALT — wait for user response before proceeding.**

### 7. Handle Response

- **[C]**: Load next step: `./step-30-architecture-context.md`
- **[R]**: Revise metrics, update product.md §6, re-present
- **[D]**: Deep-dive specific benchmarks, then re-present gate

## SUCCESS METRICS

- North Star metric defined with baseline and target
- Business metrics have specific targets at M3/M6/M12
- User metrics have baselines and targets
- Benchmark sources cited from web search
- Anti-metrics defined (what NOT to optimize)
- Round 2 research report written
- Output written to product.md §6

## FAILURE MODES

- Metrics without specific targets ("improve retention")
- No baseline or benchmark for comparison
- Only business metrics, no user metrics (or vice versa)
- Unrealistic targets (100% retention, 0% error rate)
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-30-architecture-context.md`
