# Step 01: Opportunity Discovery

## MANDATORY EXECUTION RULES

- WEB SEARCH REQUIRED — verify opportunities against real market data
- Frame opportunities from CUSTOMER perspective, not product perspective
- Generate multiple solutions per opportunity — never commit to the first idea
- WRITE output to spec file BEFORE presenting to user
- ALL output in English (spec files); conversation in Chinese

## PREREQUISITES

- Step 00 (Problem Validation) completed with [C]
- `.ultra/specs/discovery.md` §0 exists

## CONTEXT BOUNDARIES

- Focus: Map the opportunity space using Opportunity Solution Tree (Teresa Torres)
- Opportunities are CUSTOMER NEEDS, not features
- Frame as: "I struggle to..." / "I wish I could..." / "It frustrates me that..."
- Based on *Continuous Discovery Habits* methodology

## SEARCH STRATEGY (MANDATORY)

Execute these web searches in parallel:

```
Search: "{{product_domain}} user pain points complaints"
Search: "{{product_domain}} customer needs unmet"
Search: "{{product_domain}} market gaps opportunities"
Search: "{{product_domain}} user research findings"
```

Citation requirement: Every factual claim MUST include `Source: [URL]`
No-source claims → mark as `⚠️ Speculation`

## EXECUTION SEQUENCE

### 1. Define Desired Outcome

Ask user via AskUserQuestion:
"What single measurable business/product outcome are we pursuing? (e.g., 'Reduce customer onboarding time by 50%', 'Reach $1M ARR in 12 months')"

If user is unsure, help them formulate one from step-00 findings.

### 2. Map Opportunity Space

Using web search results + step-00 insights, identify 5-8 customer opportunities.

**Frame each opportunity from customer perspective:**
- BAD: "Add AI-powered search" (this is a solution)
- GOOD: "I struggle to find relevant results in large document collections" (this is an opportunity)

### 3. Prioritize Opportunities

Score each opportunity using Dan Olsen's Opportunity Score:

```
Opportunity Score = Importance × (1 - Satisfaction)
```

Where:
- **Importance** (1-10): How much does this matter to the target user?
- **Satisfaction** (0-1): How well do current solutions address this? (0 = not at all, 1 = perfectly)

Rank by score. Focus on top 2-3 opportunities.

### 4. Solution Brainstorm

For each top opportunity (top 2-3), generate 3+ solution approaches from different perspectives:

| Perspective | Approach |
|------------|---------|
| PM perspective | User workflow optimization |
| Designer perspective | Experience/interaction innovation |
| Engineer perspective | Technical capability leverage |

**Rule**: Never commit to the first idea. The best solution often emerges from comparing alternatives.

### 5. Write Output

**WRITE IMMEDIATELY** to `.ultra/specs/discovery.md` §1:

```markdown
## §1 Opportunity Space

### Desired Outcome
- **Outcome**: [Single measurable outcome]
- **Metric**: [How we measure it]
- **Timeline**: [When we expect to see movement]

### Opportunity Map

| # | Opportunity (Customer Framing) | Importance | Satisfaction | Score | Source |
|---|-------------------------------|-----------|-------------|-------|--------|
| O1 | "I struggle to..." | 9 | 0.2 | 7.2 | [URL] |
| O2 | "I wish I could..." | 8 | 0.3 | 5.6 | [URL] |
| O3 | "It frustrates me that..." | 7 | 0.4 | 4.2 | [URL] |
| O4 | ... | ... | ... | ... | ... |
| O5 | ... | ... | ... | ... | ... |

### Prioritized Opportunities (Top 3)

#### Opportunity 1: [Customer-framed description]
- **Importance**: [X]/10 — [Why this matters]
- **Current satisfaction**: [X] — [How users cope today]
- **Score**: [X]
- **Evidence**: [Source URL]

**Solution Approaches:**
1. **PM approach**: [Description] — Pros: [...] Cons: [...]
2. **Design approach**: [Description] — Pros: [...] Cons: [...]
3. **Engineering approach**: [Description] — Pros: [...] Cons: [...]

#### Opportunity 2: [Customer-framed description]
[Same structure]

#### Opportunity 3: [Customer-framed description]
[Same structure]

### Opportunities Deprioritized
| # | Opportunity | Score | Reason for Deprioritization |
|---|------------|-------|-----------------------------|
| O4 | ... | ... | [Why not now] |
| O5 | ... | ... | [Why not now] |

### Key Insight
[One paragraph: What is the non-obvious insight from this opportunity analysis?]
```

### 6. Present to User and Gate

Show the Opportunity Space summary. Highlight:
- The top 3 opportunities and why they ranked highest
- Any surprising findings from web research
- Which solution approaches seem most promising

```
[C] Continue — Opportunity space mapped, proceed to Market Assessment
[R] Revise — Adjust opportunity scoring or add missing opportunities
[D] Discuss — Explore specific opportunities in more depth
```

**HALT — wait for user response before proceeding.**

### 7. Handle Response

- **[C]**: Load next step: `./step-02-market-assessment.md`
- **[R]**: Revise scoring/opportunities, update discovery.md §1, re-present
- **[D]**: Deep-dive into specific opportunity, then re-present gate

## SUCCESS METRICS

- Desired outcome is specific and measurable
- At least 5 opportunities identified, framed from customer perspective
- Opportunity scores calculated with importance and satisfaction ratings
- Top 3 opportunities each have 3+ solution approaches
- All factual claims have source citations
- Output written to discovery.md §1

## FAILURE MODES

- Framing opportunities as features/solutions instead of customer needs
- Scoring without web research evidence
- Only generating 1 solution per opportunity
- Accepting user's first solution idea without exploring alternatives
- Missing citation sources for market claims
- Not writing output before presenting to user

## NEXT STEP

After user selects [C], read and follow: `./step-02-market-assessment.md`
