# Step 03: Competitive Landscape

## MANDATORY EXECUTION RULES

- WEB SEARCH REQUIRED — identify real competitors, not imagined ones
- INCLUDE "DO NOTHING" — the biggest competitor is often the status quo
- ANALYZE 2-5 DIRECT competitors + 1-2 indirect alternatives
- BE HONEST about where competitors are stronger
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 02 (Market Assessment) completed with [C]
- `.ultra/specs/discovery.md` §0-2 exist

## CONTEXT BOUNDARIES

- Focus: Who else is solving this problem? How do we differentiate?
- Use the prioritized opportunities from step-01 to frame competitive analysis
- Analyze CURRENT competitors, not hypothetical future ones
- Include indirect competitors and the "do nothing" alternative

## SEARCH STRATEGY (MANDATORY)

Execute these web searches in parallel:

```
Search: "{{product_domain}} competitors comparison review"
Search: "{{product_domain}} alternatives tools software"
Search: "{{product_domain}} market leaders market share"
Search: "{{product_domain}} startup funding competitors"
Search: "{{product_domain}} vs [known competitor if any]"
```

For each identified competitor, execute:
```
Search: "[competitor name] pricing features review"
Search: "[competitor name] weaknesses complaints"
```

## EXECUTION SEQUENCE

### 1. Identify Competitive Players

Categorize all competitors found:

**Direct Competitors**: Products solving the same problem for the same segment
- Search for 2-5 direct competitors
- Include their funding, team size, and traction if available

**Indirect Competitors / Alternatives**: What customers use today instead
- Spreadsheets, manual processes, general-purpose tools
- Adjacent products that partially solve the problem

**"Do Nothing" Alternative**: What happens if the customer ignores the problem?
- What does inaction cost? (Reference step-00 status quo analysis)
- Why do some users choose to live with the pain?

### 2. Deep-Dive Each Competitor

For each direct competitor (2-5), research:

| Dimension | What to find |
|-----------|-------------|
| Core value prop | What do they promise? |
| Target segment | Who do they serve? |
| Pricing model | How do they charge? |
| Key strengths | What are they genuinely good at? |
| Key weaknesses | Where do users complain? (check reviews, forums) |
| Traction signals | Users, revenue, funding, growth |
| Defensibility | What makes them hard to beat? |

### 3. Porter's Five Forces (Brief)

Assess competitive intensity:

| Force | Rating (1-5) | Assessment |
|-------|-------------|-----------|
| Supplier power | | [Who controls key inputs?] |
| Buyer power | | [Can customers easily switch?] |
| New entrant threat | | [How easy to enter this market?] |
| Substitute threat | | [What alternatives exist?] |
| Rivalry intensity | | [How fierce is current competition?] |

### 4. Identify Our Competitive Edge

Based on the analysis, answer:
- Where can we win? (specific dimensions where we have an advantage)
- Where can we NOT win? (be honest — avoid head-to-head on competitor strengths)
- What is the gap that no one is filling?

### 5. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/discovery.md` §3:

```markdown
## §3 Competitive Landscape

### Competitive Overview

| Dimension | Us | [Competitor A] | [Competitor B] | [Competitor C] | Do Nothing |
|-----------|-----|---------------|---------------|---------------|------------|
| Core value prop | [ours] | [theirs] | [theirs] | [theirs] | [status quo] |
| Target segment | [ours] | [theirs] | [theirs] | [theirs] | [everyone] |
| Pricing | [ours] | [theirs] | [theirs] | [theirs] | Free |
| Key strength | [ours] | [theirs] | [theirs] | [theirs] | Familiar |
| Key weakness | [ours] | [theirs] | [theirs] | [theirs] | Inefficient |
| Traction | [ours] | [theirs] | [theirs] | [theirs] | N/A |

### Direct Competitors

#### [Competitor A]
- **What they do**: [Description]
- **Strengths**: [What they're genuinely good at]
- **Weaknesses**: [Where users complain] — Source: [URL]
- **Pricing**: [Model and price points] — Source: [URL]
- **Traction**: [Users/revenue/funding] — Source: [URL]
- **Threat level**: [High / Medium / Low] — [Why]

#### [Competitor B]
[Same structure]

#### [Competitor C]
[Same structure]

### Indirect Competitors & Alternatives
- **[Tool/Process A]**: [How it partially solves the problem]
- **[Tool/Process B]**: [How it partially solves the problem]
- **Do Nothing**: [Cost of inaction from step-00]

### Porter's Five Forces Summary

| Force | Rating | Assessment |
|-------|--------|-----------|
| Supplier power | [1-5] | [Brief assessment] |
| Buyer power | [1-5] | [Brief assessment] |
| New entrant threat | [1-5] | [Brief assessment] |
| Substitute threat | [1-5] | [Brief assessment] |
| Rivalry intensity | [1-5] | [Brief assessment] |
| **Overall competitive intensity** | **[1-5]** | **[Summary]** |

### Our Competitive Edge
- **Where we can win**: [Specific dimensions with reasoning]
- **Where we cannot win**: [Honest assessment of competitor strengths]
- **Unfilled gap**: [What no one is doing that we can do]
- **Timing advantage**: [Why now is the right time]

### Competitive Confidence
- **Overall confidence**: [X]%
- **Best-researched competitor**: [Name] — [depth of analysis]
- **Blind spot**: [What we might be missing]
```

### 6. Present to User and Gate

Show the Competitive Landscape summary. Highlight:
- The most dangerous competitor and why
- The clearest gap in the market
- Any surprising findings (e.g., a competitor we didn't expect)

```
[C] Continue — Competitive landscape mapped, proceed to Product Strategy
[R] Revise — Adjust competitor analysis or add missing competitors
[S] Search more — Deep-dive a specific competitor
```

**HALT — wait for user response before proceeding.**

### 7. Handle Response

- **[C]**: Load next step: `./step-04-product-strategy.md`
- **[R]**: Revise analysis, update discovery.md §3, re-present
- **[S]**: Execute targeted searches on specific competitor, update, re-present

## SUCCESS METRICS

- 2-5 direct competitors identified with evidence
- "Do nothing" alternative analyzed
- Comparison matrix completed for all competitors
- Porter's Five Forces assessed
- Honest assessment of where we can/cannot win
- All claims have source citations
- Output written to discovery.md §3

## FAILURE MODES

- "No competitors exist" (there are ALWAYS competitors, even if indirect)
- Only analyzing competitor strengths, ignoring weaknesses
- Only analyzing competitor weaknesses, ignoring strengths (cheerleading)
- Missing the "do nothing" alternative
- No source citations for competitor data
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-04-product-strategy.md`
