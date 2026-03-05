---
description: Deep analysis with structured adversarial reasoning and human-AI collaboration
argument-hint: [problem or decision to analyze]
allowed-tools: Read, Grep, Glob, Bash, Write, WebSearch, WebFetch, AskUserQuestion, mcp__exa__web_search_exa, mcp__exa__get_code_context_exa, mcp__context7__resolve-library-id, mcp__context7__query-docs
model: opus
---

# /ultra-think

Respond in Chinese per CLAUDE.md. Deep analysis for complex problems and decisions.

## Problem

<problem>
$ARGUMENTS
</problem>

## Analysis Protocol

### Step 1: Scope Check

If the problem is ambiguous or underspecified, ask up to 3 clarifying questions via AskUserQuestion before proceeding. If the problem is simple enough for a direct answer, skip the full framework and respond concisely.

### Step 2: Evidence Gathering

For any factual claim about technology, APIs, or best practices, verify via Context7/Exa MCP before asserting. Label each assertion:
- **Fact**: Verified from official source
- **Inference**: Deduced from facts
- **Speculation**: Needs verification (list verification steps)

### Step 3: Multi-Perspective Analysis

Generate at least 3 distinct approaches. For each, analyze through whichever lenses are relevant:

- **Technical**: Feasibility, scalability, security, maintainability
- **Business**: Value, cost, time-to-market, competitive advantage
- **User**: Needs, experience, edge cases, accessibility
- **System**: Integration, dependencies, emergent behaviors

### Step 4: Adversarial Stress-Testing

Apply these techniques to pressure-test your reasoning:

- **Steel Man**: Before recommending, build the strongest possible case FOR the option you're inclined to reject
- **Pre-Mortem**: Assume the recommended option has failed in 6 months. List the 3 most likely causes
- **Sensitivity**: Identify which assumption, if wrong, would reverse your recommendation
- **Second-Order**: What new problems does the recommended option create 6-12 months out?

### Step 5: Synthesis

Produce a recommendation with quantified confidence (0-100%) and explicit uncertainty bounds.

## Output Structure

Adapt the following to fit the problem type. Skip sections that don't apply.

### Problem Statement
[1-2 sentences: core decision + key constraints]

### Analysis
[Deep analysis using relevant lenses from Step 3]

### Options Comparison (if applicable)
| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
[Quantified where possible. Omit this table for diagnostic/investigative problems.]

### Adversarial Findings
- **Strongest counter-argument**: [steel man for rejected option]
- **Pre-mortem top risk**: [most likely failure mode + mitigation]
- **Assumption sensitivity**: [which assumption is load-bearing]

### Recommendation
- **Choice**: [option]
- **Confidence**: [X]% because [rationale]
- **Key Assumptions**: [what must be true for this to work]
- **What would change my mind**: [specific evidence or outcome that would reverse this recommendation]

### Verification Plan
[Concrete steps to validate this decision: metrics, tests, time-boxed experiments]

### Next Steps
[Ordered, actionable items]
