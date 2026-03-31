# Step 04: Product Strategy

## MANDATORY EXECUTION RULES

- STRATEGY IS ABOUT TRADE-OFFS — what we choose NOT to do matters more
- REFERENCE previous steps — strategy must be grounded in validated problem + market + competition
- WEB SEARCH for comparable strategies in the domain
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Steps 00-03 completed with [C]
- `.ultra/specs/discovery.md` §0-3 exist

## CONTEXT BOUNDARIES

- Focus: Define strategic direction — vision, segments, value prop, trade-offs, defensibility
- This is a CONDENSED strategy canvas, not a full business plan
- Must be grounded in evidence from previous steps
- Strategy should be opinionated — "we serve everyone" is not a strategy

## SEARCH STRATEGY (MANDATORY)

Execute these web searches:

```
Search: "{{product_domain}} product strategy examples successful"
Search: "{{product_domain}} go-to-market strategy startup"
Search: "{{product_domain}} defensibility moat competitive advantage"
Search: "{{product_domain}} pricing strategy models"
```

## EXECUTION SEQUENCE

### 1. Vision Statement

Collaborate with user to craft a 2-3 sentence vision that:
- Inspires people (emotional, memorable)
- Is specific enough to guide decisions
- Is ambitious enough to attract talent and investment

**Test**: Would someone quit their job to work on this? If not, it's too boring.

Ask user via AskUserQuestion: "In 2-3 sentences, how can we inspire people? What are we aspiring to achieve?"

### 2. Target Segments

Define WHO we serve and WHO we explicitly do NOT serve.

Using personas from step-00 (Q3: Desperate Specificity):

**Serve** (defined by problems/JTBD, not demographics):
- Segment 1: [Description] — [Why they need us most]
- Segment 2: [Description] — [Why they need us]

**Do NOT serve** (equally important):
- Anti-segment 1: [Description] — [Why not]
- Anti-segment 2: [Description] — [Why not]

### 3. Value Proposition

For each target segment, use the JTBD format:

```
When [situation], they want [motivation], so they can [outcome]
```

This must connect directly to the top opportunities from step-01.

### 4. Strategic Trade-offs

**This is the most important section.** A strategy without trade-offs is a wish list.

Identify 3-5 strategic trade-offs:

| We Choose | Over | Because |
|-----------|------|---------|
| [Focus A] | [Alternative A] | [Reasoning grounded in evidence] |
| [Focus B] | [Alternative B] | [Reasoning grounded in evidence] |
| [Focus C] | [Alternative C] | [Reasoning grounded in evidence] |

Each trade-off should reference competitive analysis from step-03 — we avoid competing head-to-head on competitor strengths.

### 5. Defensibility Analysis

What makes this hard to copy? Evaluate each:

| Moat Type | Applicability | Strength | Timeline to Build |
|-----------|-------------|----------|-------------------|
| Network effects | [Yes/No] | [Assessment] | [Time] |
| Data advantage | [Yes/No] | [Assessment] | [Time] |
| Switching costs | [Yes/No] | [Assessment] | [Time] |
| Brand / trust | [Yes/No] | [Assessment] | [Time] |
| Technical IP | [Yes/No] | [Assessment] | [Time] |
| Speed / execution | [Yes/No] | [Assessment] | [Time] |

Be honest — most startups have weak defensibility early. That's okay if the execution advantage is strong.

### 6. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/discovery.md` §4:

```markdown
## §4 Product Strategy

### Vision
[2-3 sentences — inspiring, specific, ambitious]

### Target Segments

#### Primary: [Segment Name]
- **Description**: [Who they are, defined by problem/JTBD]
- **Why them**: [Why they need us most urgently]
- **Value Proposition**: When [situation], they want [motivation], so they can [outcome]

#### Secondary: [Segment Name]
- **Description**: [Who they are]
- **Why them**: [Why they need us]
- **Value Proposition**: When [situation], they want [motivation], so they can [outcome]

#### Explicitly NOT Serving
- **[Anti-segment 1]**: [Why not — e.g., "Too enterprise for our current capabilities"]
- **[Anti-segment 2]**: [Why not — e.g., "Their problem is different enough to require a different product"]

### Strategic Trade-offs

| # | We Choose | Over | Because |
|---|-----------|------|---------|
| 1 | [Focus] | [Alternative] | [Evidence-based reasoning] |
| 2 | [Focus] | [Alternative] | [Evidence-based reasoning] |
| 3 | [Focus] | [Alternative] | [Evidence-based reasoning] |
| 4 | [Focus] | [Alternative] | [Evidence-based reasoning] |

### Defensibility

| Moat Type | Applicable | Strength (1-5) | Timeline |
|-----------|-----------|----------------|----------|
| Network effects | [Yes/No] | [X] | [Time] |
| Data advantage | [Yes/No] | [X] | [Time] |
| Switching costs | [Yes/No] | [X] | [Time] |
| Brand / trust | [Yes/No] | [X] | [Time] |
| Technical IP | [Yes/No] | [X] | [Time] |
| Speed / execution | [Yes/No] | [X] | [Time] |

**Primary moat**: [Which moat type is strongest and why]
**Moat timeline**: [When defensibility becomes meaningful]

### Strategy Confidence
- **Overall confidence**: [X]%
- **Strongest element**: [What part of strategy is most grounded]
- **Riskiest bet**: [What strategic choice is most uncertain]
```

### 7. Present to User and Gate

Show the Product Strategy summary. Highlight:
- Whether the trade-offs feel right
- The defensibility assessment
- Any concerns about the strategic direction

```
[C] Continue — Strategy defined, proceed to Assumptions Validation
[R] Revise — Adjust strategy elements
[D] Discuss — Explore specific trade-offs in more depth
```

**HALT — wait for user response before proceeding.**

### 8. Handle Response

- **[C]**: Load next step: `./step-05-assumptions-validation.md`
- **[R]**: Revise strategy, update discovery.md §4, re-present
- **[D]**: Deep-dive specific trade-offs, then re-present gate

## SUCCESS METRICS

- Vision is inspiring and specific (not generic)
- Target segments defined by problems, not demographics
- Anti-segments explicitly stated
- At least 3 strategic trade-offs with evidence-based reasoning
- Defensibility honestly assessed
- Output written to discovery.md §4

## FAILURE MODES

- Generic vision ("We make the world better with AI")
- "We serve everyone" (no segment focus)
- No trade-offs stated (strategy without trade-offs is not strategy)
- Defensibility assessment is all 5/5 (unrealistic)
- Strategy not grounded in evidence from steps 00-03
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-05-assumptions-validation.md`
