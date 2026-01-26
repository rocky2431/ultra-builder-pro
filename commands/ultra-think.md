---
description: Deep analysis with structured reasoning and human-AI collaboration
argument-hint: [problem or decision to analyze]
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch, Task, AskUserQuestion
model: opus
---

# /ultra-think

Deep analysis for complex problems and decisions.

## Instructions

Think through this problem thoroughly and in great detail:

$ARGUMENTS

**Core guidance** (high-level, not step-by-step):
- Consider multiple approaches and show your complete reasoning
- Try different methods if your first approach doesn't work
- Challenge your own assumptions and identify blind spots
- Before concluding, verify your reasoning is sound

**Interactive collaboration**:
- If the problem is ambiguous, ask clarifying questions first
- Surface implicit requirements and hidden complexities
- Present trade-offs clearly so the user can make informed decisions

## Optional Thinking Dimensions

These are reference perspectives, not required steps. Choose what's relevant:

- **Technical**: Feasibility, scalability, security, maintainability
- **Business**: Value, cost, time-to-market, competitive advantage
- **User**: Needs, experience, edge cases, accessibility
- **System**: Integration, dependencies, emergent behaviors
- **Risk**: Failure modes, mitigation, reversibility

## Output Format

> Claude responds in Chinese per CLAUDE.md.

Use `<thinking>` for internal reasoning, then provide:

```
## Problem
[1-2 sentences: core decision + key constraints]

## Analysis
[Choose relevant dimensions, deep analysis]

## Comparison
| Dimension | Option A | Option B |
|-----------|----------|----------|
[Quantified comparison, not just qualitative]

## Recommendation
- **Choice**: [option]
- **Confidence**: High/Medium/Low + rationale
- **Key Assumptions**: [assumptions the recommendation depends on]
- **Risk**: [main risk + mitigation]

## Verification
[How to verify this decision is correct? What are the test criteria?]

## Next Steps
[Specific actionable items]
```

## Evidence Requirement

Per CLAUDE.md `<evidence_first>`: External claims require verification (Context7/Exa MCP). Label assertions as:
- **Fact**: Verified from official source
- **Inference**: Deduced from facts
- **Speculation**: Needs verification

