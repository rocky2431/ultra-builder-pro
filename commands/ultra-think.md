---
description: Deep analysis and problem solving with multi-dimensional thinking
argument-hint: [problem or question to analyze]
allowed-tools: Read, Grep, Glob, Bash, Task, WebFetch, WebSearch, TodoWrite
---

# /ultra-think - Deep Analytical Thinking

## Purpose

Activate extended thinking mode for comprehensive multi-dimensional analysis of complex problems. Uses Claude's maximum reasoning capacity for deep exploration with structured methodology.

---

## Quick Start

```bash
/ultra-think "Should we migrate from Redux to Zustand?"
/ultra-think "Design distributed cache invalidation strategy"
/ultra-think "Build custom auth vs use Auth0/Clerk?"
```

---

## Core Principles

Apply these thinking frameworks throughout analysis:

| Principle | Description |
|-----------|-------------|
| **First Principles** | Break down to fundamental truths, question every assumption |
| **Systems Thinking** | Consider interconnections, feedback loops, emergent behaviors |
| **Probabilistic Thinking** | Work with uncertainties and ranges, not false certainty |
| **Inversion** | Consider what to avoid, not just what to do |
| **Second-Order Thinking** | Consider consequences of consequences |
| **Cross-Domain** | Borrow solutions from other industries/domains |

---

## Workflow

### Phase 1: Problem Understanding

**Clarify the problem**:
1. Extract core question from user input
2. Identify problem domain (technical, architectural, strategic)
3. Determine complexity level (Simple, Medium, Complex, Critical)
4. Question assumptions - what are we taking for granted?
5. Surface unknowns - what don't we know that we should?

**Complexity Assessment**:
```
Complexity indicators:
+2: Multi-domain (cross-cutting concerns)
+2: Multi-scenario (3+ alternatives)
+1: Long-term (strategic impact)
+1: High-risk (significant consequences)
+1: Data-intensive (research required)

Score 0-2: Simple | 3-4: Medium | 5-6: Complex | 7+: Critical
```

**Decision**: If problem requires codebase analysis → Use Read/Grep. Otherwise → Proceed to analysis.

---

### Phase 2: Multi-Dimensional Analysis (6D Framework)

**Extended Thinking Mode Activated**

Analyze from six perspectives:

#### 1. Technical Dimension
- Architecture implications and scalability
- Performance considerations and bottlenecks
- Technical debt assessment
- Implementation complexity
- Security implications

#### 2. Business Dimension
- Cost-benefit analysis and ROI
- Time-to-market impact
- Resource requirements
- Risk vs. reward trade-offs
- Competitive advantages

#### 3. Team Dimension
- Learning curve and skill alignment
- Development velocity impact
- Maintenance burden
- Knowledge transfer needs
- Team morale and motivation

#### 4. Ecosystem Dimension
- Community support and maturity
- Library ecosystem and integrations
- Future viability and roadmap
- Vendor lock-in risks
- Industry adoption trends

#### 5. Strategic Dimension
- Long-term sustainability
- Innovation opportunities
- Market trends alignment
- Exit strategy considerations
- Competitive positioning

#### 6. Meta-Level Considerations
- Underlying assumptions validation
- Alternative frameworks exploration
- Paradigm shift implications
- Second-order effects
- Systemic interactions

---

### Phase 3: Solution Generation

**Generate 3-5 distinct approaches**:

For each solution, analyze:
- **Description**: What is this approach?
- **Pros**: Benefits and advantages
- **Cons**: Drawbacks and limitations
- **Complexity**: Implementation difficulty (Low/Medium/High)
- **Risk Level**: Potential for failure (Low/Medium/High)
- **Long-term Impact**: Future implications

**Include**:
- Conventional approaches (proven patterns)
- Creative solutions (innovative alternatives)
- Hybrid approaches (combining elements)
- Cross-domain inspiration (solutions from other fields)

---

### Phase 4: Deep Dive & Challenge

**For the most promising solutions**:

1. **Current State Analysis**: What exists now?
2. **Future State Vision**: What could be?
3. **Gap Analysis**: What needs to change?
4. **Trade-offs**: What are we gaining/losing?
5. **Failure Modes**: What could go wrong?
6. **Recovery Strategies**: How to handle failures?

**Devil's Advocate (CRITICAL)**:
- Challenge each solution's assumptions
- Identify weaknesses and blind spots
- Consider "what if" scenarios
- Stress-test under adverse conditions
- Look for unintended consequences

**Cross-Domain Thinking**:
- Draw parallels from other industries
- Apply biological/natural system analogies
- Look for innovative combinations

---

### Phase 5: Scenario Planning

**Explore multiple scenarios**:

```markdown
## Scenario A: [Approach Name]
**Assumptions**: What must be true?
**Outcomes**: Expected results
**Probability**: High/Medium/Low
**Impact**: Critical/Significant/Moderate/Minor
**Failure Mode**: What could go wrong?
**Mitigation**: How to address failure?

## Scenario B: [Approach Name]
[Same structure]

## Scenario C: [Alternative/Hybrid]
[Same structure]
```

---

### Phase 6: Synthesis & Recommendation

**Output Structure** (in Chinese):

```markdown
## 问题分析
- **核心挑战**: [Main challenge]
- **关键约束**: [Key constraints]
- **成功因素**: [Critical success factors]
- **复杂度评级**: Simple/Medium/Complex/Critical

## 多维分析摘要
| 维度 | 关键发现 | 影响评估 |
|------|----------|----------|
| 技术 | ... | High/Medium/Low |
| 业务 | ... | ... |
| 团队 | ... | ... |
| 生态 | ... | ... |
| 战略 | ... | ... |
| 元层面 | ... | ... |

## 解决方案对比

### 方案 1: [Name]
- **描述**: ...
- **优势**: ...
- **劣势**: ...
- **复杂度**: Low/Medium/High
- **风险**: Low/Medium/High

### 方案 2: [Name]
[Similar structure]

### 方案 3: [Name]
[Similar structure]

## 推荐决策
- **首选方案**: [Recommended approach]
- **理由**: [Data-driven justification]
- **置信度**: High (>80%) / Medium (50-80%) / Low (<50%)

**实施路径**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**成功指标**:
- [Metric 1]: Target value
- [Metric 2]: Target value

## 风险与应急
| 风险 | 概率 | 影响 | 缓解措施 | 备选方案 |
|------|------|------|----------|----------|
| ... | ... | ... | ... | ... |

## 不确定性声明
- **确定的事实**: [Verified facts]
- **推断**: [Logical deductions]
- **推测**: [Uncertain assumptions]
- **需要验证**: [Items requiring further research]

## 元分析
- **思考过程反思**: What did we miss?
- **偏见检查**: What biases might affect this analysis?
- **额外专业知识需求**: What expertise would improve this?

## 下一步行动
1. [Immediate action]
2. [Short-term action]
3. [Long-term action]
```

---

## Dynamic Token Allocation

Token allocation based on problem complexity:

| Complexity | Tokens | Use Case |
|------------|--------|----------|
| **Simple** | 8K | Single-dimension analysis, quick decisions |
| **Medium** | 16K | Standard 6D analysis (default) |
| **Complex** | 24K | Multi-scenario planning, architecture decisions |
| **Critical** | 32K | Strategic pivots, major refactoring |

**Manual override**:
```bash
MAX_THINKING_TOKENS=30000 /ultra-think "your complex problem"
```

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

**Codex Research (codex-research-gen)**:
- Complex technology comparison needed
- Multi-source validation required
- Systematic research with 90%+ confidence requirement

**TodoWrite**:
- Break down implementation into tasks
- Track analysis progress (optional)

---

## Session Archival

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

  // Write session file
  await Write(`.ultra/thinking-sessions/${session.id}.md`, formatSession(session));
}
```

---

## Examples

### Example 1: Architecture Decision

```bash
/ultra-think "Should we adopt microservices or keep monolithic architecture?"
```

**Expected analysis**:
- Current monolith pain points (Technical)
- Cost analysis - infrastructure, development time (Business)
- Team readiness and learning curve (Team)
- Container orchestration ecosystem maturity (Ecosystem)
- Long-term scalability strategy (Strategic)
- Assumption: "we need microservices" - is this true? (Meta)
- Cross-domain: How do banks/healthcare handle this?
- Devil's advocate: What if we optimized the monolith instead?

### Example 2: Technology Selection

```bash
/ultra-think "React Server Components vs traditional SSR with hydration?"
```

**Expected analysis**:
- Performance comparison (LCP, INP, CLS)
- Developer experience impact
- Team's React expertise level
- Next.js ecosystem support
- SEO and marketing implications
- Challenge: Is RSC mature enough for production?

### Example 3: Build vs Buy

```bash
/ultra-think "Build custom authentication vs use Auth0/Clerk?"
```

**Expected analysis**:
- Development cost comparison
- Security considerations (custom = more risk)
- Vendor lock-in risks
- Feature completeness timeline
- Compliance requirements (SOC2, GDPR)
- Cross-domain: How do fintech startups solve this?

---

## Integration with Ultra Builder Pro

**After /ultra-think**:
- If recommendation is clear → `/ultra-plan` to create task breakdown
- If research needed → `/ultra-research` for systematic investigation
- If prototyping needed → `/ultra-dev` to build proof-of-concept

**guiding-workflow** will suggest appropriate next command based on analysis outcome.

---

## Success Criteria

- [ ] Multi-dimensional analysis completed (6 perspectives)
- [ ] 3-5 distinct solutions generated
- [ ] Devil's advocate applied to each solution
- [ ] Evidence-based reasoning with sources
- [ ] Clear recommendation with confidence level
- [ ] Uncertainty explicitly stated (Fact/Inference/Speculation)
- [ ] Actionable implementation path
- [ ] Risk assessment with contingency plans
- [ ] Output in Chinese (user-facing)

---

**Remember**: Deep thinking is for complex, non-trivial problems. For simple questions, direct conversation is more efficient.
