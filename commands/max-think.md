---
description: 6-dimensional structured analysis framework (Technical, Business, Team, Ecosystem, Strategic, Meta) for complex decision-making and technology selection
argument-hint: <problem-description>
allowed-tools: Read, Grep, Glob, Bash, Task, WebFetch, WebSearch, TodoWrite
---

# /max-think - Deep Analytical Thinking

## Purpose

Activate extended thinking mode for comprehensive multi-dimensional analysis of complex problems. Uses Claude's maximum reasoning capacity for deep exploration.

---

## Quick Start

```bash
/max-think "Complex problem description"
/max-think "Should we migrate from Redux to Zustand?"
/max-think "Design distributed cache invalidation strategy"
```

---

## Workflow

### Phase 1: Problem Understanding

**Clarify the problem**:
1. Extract core question from user input
2. Identify problem domain (technical, architectural, strategic)
3. Determine complexity level (Simple, Medium, Complex, Highly Complex)
4. Gather context (if needed, use Read/Grep to examine relevant code)

**Decision**: If problem requires codebase analysis → Use Read/Grep. Otherwise → Proceed to analysis.

---

### Phase 2: Multi-Dimensional Analysis

**Extended Thinking Mode Activated**

Analyze from multiple perspectives:

#### 1. Technical Dimension
- Architecture implications
- Performance considerations
- Scalability factors
- Technical debt assessment
- Implementation complexity

#### 2. Business Dimension
- Cost-benefit analysis
- Time-to-market impact
- Resource requirements
- ROI evaluation
- Risk assessment

#### 3. Team Dimension
- Learning curve
- Team skill alignment
- Development velocity impact
- Maintenance burden
- Knowledge transfer needs

#### 4. Ecosystem Dimension
- Community support
- Library maturity
- Future viability
- Integration compatibility
- Vendor lock-in risks

#### 5. Strategic Dimension
- Long-term sustainability
- Competitive advantages
- Innovation opportunities
- Market trends alignment
- Exit strategy considerations

#### 6. Meta-Level Considerations
- Underlying assumptions validation
- Alternative frameworks exploration
- Paradigm shift implications
- Second-order effects
- Systemic interactions

---

### Phase 3: Deep Exploration

**For each dimension**:
1. **Current State Analysis**: What exists now?
2. **Future State Vision**: What could be?
3. **Gap Analysis**: What needs to change?
4. **Trade-offs**: What are we gaining/losing?
5. **Risk Factors**: What could go wrong?
6. **Mitigation Strategies**: How to address risks?

**Research if needed**:
- Use WebSearch for industry best practices
- Use WebFetch for official documentation
- Use ultra-research-agent for comprehensive comparison (if applicable)

---

### Phase 4: Scenario Planning

**Explore multiple scenarios**:

```markdown
## Scenario A: [Approach 1]
**Assumptions**: ...
**Outcomes**: ...
**Probability**: High/Medium/Low
**Impact**: Critical/Significant/Moderate/Minor

## Scenario B: [Approach 2]
**Assumptions**: ...
**Outcomes**: ...
**Probability**: ...
**Impact**: ...

## Scenario C: [Alternative]
**Assumptions**: ...
**Outcomes**: ...
**Probability**: ...
**Impact**: ...
```

---

### Phase 5: Synthesis & Recommendation

**Synthesize insights**:

```markdown
## Executive Summary (Chinese)
[1-2 paragraphs in Chinese summarizing key findings]

## Key Insights
1. **[Insight Category]**: [Finding]
2. **[Insight Category]**: [Finding]
3. **[Insight Category]**: [Finding]

## Recommendation
**Primary Choice**: [Recommended approach]
**Rationale**: [Data-driven justification]
**Confidence Level**: High/Medium/Low

**Implementation Path**:
1. [Step 1 with timeframe]
2. [Step 2 with timeframe]
3. [Step 3 with timeframe]

**Success Metrics**:
- [Metric 1]: Target value
- [Metric 2]: Target value
- [Metric 3]: Target value

## Contingency Plans
**If [Risk] occurs**:
- Action: [Mitigation]
- Fallback: [Alternative]

## Next Steps
1. [Immediate action]
2. [Short-term action]
3. [Long-term action]
```

---

## Output Format

**Output in Chinese** following Language Protocol. Structure should include:

1. **Problem Understanding**: Domain, complexity, key assumptions
2. **Multi-Dimensional Analysis**: 6 perspectives (Technical, Business, Team, Ecosystem, Strategic, Meta-level)
3. **Scenario Planning**: 3+ scenarios with assumptions, outcomes, probability, impact
4. **Synthesis & Recommendation**: Primary choice with rationale, confidence level, implementation path
5. **Risk Assessment**: Risk matrix with mitigation strategies and fallback plans
6. **Next Steps**: Immediate, short-term, and long-term actions

At runtime, Claude will output this structure in Chinese with proper formatting and emojis for visual clarity.

---

## Tool Usage Strategy

### When to Use Each Tool

**Read/Grep/Glob**:
- Problem involves existing codebase
- Need to understand current implementation
- Analyzing code patterns or architecture

**WebSearch/WebFetch**:
- Need industry best practices
- Research recent developments
- Validate technical approaches
- Compare community opinions

**Task (ultra-research-agent)**:
- Complex technology comparison needed
- Multi-source validation required
- Systematic research with 6-dimensional analysis

**TodoWrite**:
- Break down implementation into tasks
- Track analysis progress (optional)

---

## Examples

### Example 1: Architecture Decision

```bash
/max-think "Should we adopt microservices or keep monolithic architecture?"
```

**Expected analysis**:
- Current monolith pain points
- Microservices benefits vs complexity
- Team readiness assessment
- Cost analysis (infrastructure, development time)
- Phased migration strategy
- Risk mitigation plan

---

### Example 2: Technology Selection

```bash
/max-think "React Server Components vs traditional SSR with hydration?"
```

**Expected analysis**:
- Performance comparison (LCP, INP, CLS)
- Developer experience impact
- SEO implications
- Infrastructure requirements
- Community maturity
- Learning curve for team
- Migration path from current setup

---

### Example 3: Strategic Decision

```bash
/max-think "Build custom authentication vs use Auth0/Clerk?"
```

**Expected analysis**:
- Development cost comparison
- Security considerations
- Maintenance burden
- Feature completeness
- Vendor lock-in risks
- Compliance requirements
- Long-term total cost of ownership

---

## Success Criteria

- ✅ Multi-dimensional analysis completed (6+ perspectives)
- ✅ Evidence-based reasoning with data/sources
- ✅ Clear recommendation with confidence level
- ✅ Actionable implementation path
- ✅ Risk assessment with contingency plans
- ✅ Output in Chinese (user-facing)

---

## Integration with Ultra Builder Pro

**After /max-think**:
- If recommendation is clear → `/ultra-plan` to create task breakdown
- If research needed → `/ultra-research` for systematic investigation
- If prototyping needed → `/ultra-dev` to build proof-of-concept

**guiding-workflow** will suggest appropriate next command based on analysis outcome.

---

## Dynamic Token Allocation (NEW)

Token allocation based on problem complexity:

| Complexity | Tokens | Use Case |
|------------|--------|----------|
| **Simple** | 8K | Single-dimension analysis, quick decisions |
| **Medium** | 16K | Standard 6D analysis (default) |
| **Complex** | 24K | Multi-scenario planning, architecture decisions |
| **Critical** | 32K | Strategic pivots, major refactoring |

**Auto-detection**:
```typescript
// Complexity indicators
const complexityScore = {
  multiDomain: +2,        // Cross-cutting concerns
  multiScenario: +2,      // 3+ alternatives
  longTerm: +1,           // Strategic impact
  highRisk: +1,           // Significant consequences
  dataIntensive: +1       // Research required
};

// Score → Token allocation
// 0-2: Simple (8K)
// 3-4: Medium (16K)
// 5-6: Complex (24K)
// 7+:  Critical (32K)
```

**Manual override**:
```bash
MAX_THINKING_TOKENS=30000 /max-think "your complex problem"
```

---

## Session Archival (NEW)

**Archive thinking sessions for future reference**:

After completing deep analysis, save to `.ultra/thinking-sessions/`:

```typescript
// Auto-archive for high-impact decisions
if (decision.confidence >= 0.9 || decision.impact === 'critical') {
  const session = {
    id: `session-${timestamp}-${topic-slug}`,
    timestamp: new Date().toISOString(),
    topic: problemDescription,
    complexity: detectedComplexity,
    tokensUsed: actualTokensUsed,
    dimensions: analysisResults,
    decision: finalRecommendation,
    confidence: confidenceLevel,
    alternatives: consideredAlternatives
  };

  // Update session index
  const index = await Read(".ultra/thinking-sessions/session-index.json");
  index.sessions.push(session.id);
  await Write(".ultra/thinking-sessions/session-index.json", index);

  // Write session file
  await Write(`.ultra/thinking-sessions/${session.id}.md`, formatSession(session));
}
```

**Decision Audit Integration**:
```typescript
// Record to decision-audit.json for traceability
const auditEntry = {
  id: `decision-${timestamp}`,
  decision: finalRecommendation,
  alternatives: consideredAlternatives,
  reasoning: keyInsights,
  confidence: confidenceLevel,
  source: `thinking-sessions/${session.id}.md`,
  timestamp: new Date().toISOString()
};

const audit = await Read(".ultra/docs/decision-audit.json");
audit.decisions.push(auditEntry);
await Write(".ultra/docs/decision-audit.json", audit);
```

**Benefits**:
- Traceable decision history
- Reusable analysis for similar problems
- Team knowledge preservation

---

**Remember**: Deep thinking is for complex, non-trivial problems. For simple questions, direct conversation is more efficient.

---

## Command Output Format Reference

**Standard output structure**: See `@config/ultra-command-output-template.md` for the complete 6-section format.

**Command icon**: 🤔

**Note**: max-think has custom output structure (6-dimensional analysis) as described in Output Format section above.
