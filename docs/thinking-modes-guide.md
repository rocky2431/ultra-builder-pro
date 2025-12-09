# Thinking Modes Guide

**Ultra Builder Pro 4.1** - Complete guide to Claude Code thinking modes

---

## Overview

Claude Code provides two deep analysis modes:
1. **ultrathink** - Claude native deep reasoning (unstructured output)
2. **/max-think** - 6-dimensional structured analysis framework (Ultra Builder Pro custom)

Both can be used **independently** or **combined**, suitable for different scenarios.

---

## 1. ultrathink (Native Thinking Mode)

### 📌 Core Features

- **Nature**: Claude Code CLI built-in keyword trigger system
- **Token Budget**: 31,999 tokens (fixed, maximum reasoning capacity)
- **Output Form**: Free-form, no fixed structure
- **Working Level**: CLI preprocessing layer (allocates tokens before sending to model)

### 🎯 Use Cases

- ✅ **Exploratory thinking**: Uncertain problem direction, need open-ended exploration
- ✅ **Free-form analysis**: Don't need formatted output
- ✅ **Pure reasoning**: Need maximum thinking depth but not structured framework
- ✅ **Brainstorming**: Divergent thinking, seeking inspiration

### 💡 Usage

```bash
# Method 1: Use ultrathink keyword
ultrathink How should I architect this distributed system?

# Method 2: Use alternative triggers (same effect)
think harder What's the best approach here?
think intensely Analyze this complex problem
think super hard Design a scalable solution
```

### 🔢 Token Budget Hierarchy

| Keyword | Token Budget | Use Case |
|---------|-------------|----------|
| `think` | 4,000 | Simple problems requiring deeper thought |
| `megathink` | 10,000 | Medium complexity problems |
| `ultrathink` | 31,999 | Most complex problems, maximum reasoning depth |

### ⚠️ Important Notes

- ❌ **CLI only** (not supported in web interface)
- ❌ **No structured output**: Use /max-think if need structured results
- ❌ **High token consumption**: Avoid using on simple questions

---

## 2. /max-think (Structured Analysis Command)

### 📌 Core Features

- **Nature**: Ultra Builder Pro custom slash command
- **Token Budget**: Dynamic 8K-32K (based on problem complexity)
- **Output Form**: 6-dimensional structured analysis + scenario planning + implementation path
- **Analysis Framework**: Technical, Business, Team, Ecosystem, Strategic, Meta

### 🎯 Use Cases

- ✅ **Technology selection**: React vs Vue, Redux vs Zustand, PostgreSQL vs MongoDB
- ✅ **Architecture decisions**: Monolith vs Microservices, REST vs GraphQL
- ✅ **Tool selection**: Build tools, test frameworks, CI/CD solutions
- ✅ **Strategic planning**: Technology roadmap, team capability building
- ✅ **Risk assessment**: Need multi-dimensional analysis and contingency plans

### 💡 Usage

```bash
# Standard format
/max-think "Problem description"

# Example 1: Technology selection
/max-think "Should we migrate from Redux to Zustand?"

# Example 2: Architecture decision
/max-think "Design distributed cache invalidation strategy"

# Example 3: Tool selection (with context)
/max-think "React Server Components vs traditional SSR with hydration?
Context: E-commerce platform, 100K monthly users, SEO critical"
```

### 📊 Output Structure (6 Phases)

```markdown
## 1. Problem Understanding
- Domain classification
- Complexity assessment
- Key assumptions

## 2. Multi-Dimensional Analysis (6 Dimensions)
### Technical Dimension
- Architecture implications
- Performance considerations
- Scalability factors
- Technical debt assessment

### Business Dimension
- Cost-benefit analysis
- Time-to-market impact
- ROI evaluation

### Team Dimension
- Learning curve
- Team skill alignment
- Maintenance burden

### Ecosystem Dimension
- Community support
- Library maturity
- Future viability

### Strategic Dimension
- Long-term sustainability
- Competitive advantages
- Innovation opportunities

### Meta-Level Considerations
- Underlying assumptions
- Paradigm shifts
- Second-order effects

## 3. Scenario Planning
- Scenario A: [Approach 1] (Assumptions, Outcomes, Probability, Impact)
- Scenario B: [Approach 2]
- Scenario C: [Alternative]

## 4. Synthesis & Recommendation
- Executive Summary
- Primary Choice
- Rationale
- Confidence Level (High/Medium/Low)

## 5. Implementation Path
- Step-by-step roadmap
- Success metrics
- Timeline considerations

## 6. Risk Assessment & Contingency Plans
- Risk matrix
- Mitigation strategies
- Fallback plans
```

### 🔢 Token Budget (Dynamic Allocation)

| Complexity | Token Budget | Use Case | Example |
|-----------|-------------|----------|---------|
| **Simple** | 8K | Single-dimension analysis, quick decisions | Choose CSS framework |
| **Medium** | 16K | Standard 6D analysis (default) | Tech stack selection |
| **Complex** | 24K | Multi-scenario planning, architecture decisions | Microservices migration |
| **Critical** | 32K | Strategic decisions, major refactoring | Rewrite entire system |

**Manual Token Override**:
```bash
MAX_THINKING_TOKENS=30000 /max-think "Complex architectural problem"
```

---

## 3. Independent Usage Guide

### Scenario A: Exploratory Questions (Use ultrathink)

**When to use**:
- Don't know what to ask
- Need open-ended exploration
- Seeking inspiration and direction

**Example**:
```bash
ultrathink I'm building a real-time collaboration tool.
What are the key challenges I should consider?
```

**Expected output**:
- Free-form deep analysis
- Multi-angle problem space exploration
- Identify key challenges and opportunities

---

### Scenario B: Clear Technical Decisions (Use /max-think)

**When to use**:
- Clear problem, need structured analysis
- Need multi-dimensional comparison
- Need implementation path and risk assessment

**Example**:
```bash
/max-think "Should we use PostgreSQL or MongoDB for our e-commerce platform?
Requirements: 10K products, 50K users, complex queries, ACID compliance"
```

**Expected output**:
- 6-dimensional structured analysis
- 3+ scenario comparison (PostgreSQL, MongoDB, Hybrid)
- Clear recommendation + implementation path
- Risk assessment + contingency plans

---

## 4. Combined Usage (Maximum Power)

### 🚀 Method A: Explore First, Then Structure

**Workflow**:
```
Step 1: ultrathink open exploration
   ↓
Step 2: /max-think structured analysis
   ↓
Step 3: /ultra-plan task planning
   ↓
Step 4: /ultra-dev implementation
```

**Example**:
```bash
# Step 1: Exploration
ultrathink I'm considering microservices architecture.
What are the key factors I should analyze?

# [Wait for Claude's exploration output]

# Step 2: Structured analysis (based on exploration)
/max-think "Should we adopt microservices or keep monolithic architecture?
Context: Team size 5 devs, expected scale 10K users,
timeline 3 months, current pain: deployment bottlenecks"
```

**Benefits**:
- ✅ Exploration phase: divergent thinking, discover hidden issues
- ✅ Analysis phase: structured, ensure nothing missed
- ✅ Two-phase results complement each other

---

### 🚀 Method B: One-Shot Combination (Ultimate Mode)

**Use case**: Strategic decisions, high risk high impact

**Format**:
```bash
ultrathink /max-think "Complex problem description"
```

**Example**:
```bash
ultrathink /max-think "Design a distributed real-time collaborative
editing system with conflict resolution.
Consider: CRDTs vs OT, WebSocket vs WebRTC,
scalability (100K concurrent users), consistency guarantees"
```

**Effect**:
- ✅ ultrathink allocates **31,999 tokens** thinking budget
- ✅ /max-think provides **6-dimensional analysis framework**
- ✅ Combined = **Maximum reasoning depth + Structured output**

**Expected output**:
- Ultra-deep 6-dimensional analysis
- Comprehensive scenario planning (possibly 5+ scenarios)
- High-confidence recommendation
- Complete implementation path and risk matrix

---

## 5. Decision Tree

```
Is problem clear?
├─ No → Use ultrathink for exploration
│         ↓
│      Problem clear → Use /max-think for structured analysis
│
└─ Yes → Need structured output?
         ├─ No → Use ultrathink (if need deep reasoning)
         │
         └─ Yes → Problem complexity?
                  ├─ Simple → Direct conversation (no tools needed)
                  ├─ Medium → /max-think
                  └─ High complexity + High impact → ultrathink + /max-think
```

### Quick Selection Table

| Problem Type | ultrathink | /max-think | Combined | Direct Chat |
|-------------|-----------|-----------|----------|-------------|
| Exploratory (don't know what to ask) | ✅ | ❌ | ❌ | ❌ |
| Clear tech selection | ❌ | ✅ | ❌ | ❌ |
| Simple question (how to use an API) | ❌ | ❌ | ❌ | ✅ |
| Complex architecture (need depth + structure) | ❌ | ❌ | ✅ | ❌ |
| Strategic decision (high risk high impact) | ❌ | ❌ | ✅ | ❌ |
| Need multi-scenario comparison | ❌ | ✅ | ❌ | ❌ |
| Need implementation path & risk assessment | ❌ | ✅ | ❌ | ❌ |
| Brainstorming | ✅ | ❌ | ❌ | ❌ |

---

## 6. Token Budget & Cost Comparison

### Token Consumption Analysis

| Mode | Thinking Tokens | Output Tokens | Total (Est.) | Relative Cost |
|------|----------------|---------------|--------------|---------------|
| **Standard chat** | ~1K | ~2K | ~3K | 1x |
| **think** | 4K | ~2K | ~6K | 2x |
| **megathink** | 10K | ~3K | ~13K | 4x |
| **ultrathink** | 31,999 | ~4K | ~36K | 12x |
| **/max-think (Simple)** | 8K | ~5K | ~13K | 4x |
| **/max-think (Medium)** | 16K | ~8K | ~24K | 8x |
| **/max-think (Complex)** | 24K | ~12K | ~36K | 12x |
| **ultrathink + /max-think** | 31,999 + 24K | ~15K | ~71K | 24x |

### 💰 Cost Optimization Tips

1. **Simple questions**: Direct chat (1x cost)
2. **Medium complexity**: /max-think Simple mode (4x cost)
3. **Complex decisions**: /max-think Medium/Complex (8-12x cost)
4. **Strategic decisions**: Combined usage (24x cost, but worth it)

---

## 7. Best Practices

### ✅ DO (Recommended)

1. **Prioritize problem classification**
   - First judge problem type and complexity
   - Choose appropriate tool (don't overuse)

2. **Progressive usage**
   - Simple problem → Direct chat
   - Need exploration → ultrathink
   - Need decision → /max-think
   - Strategic decision → Combined

3. **Provide sufficient context**
   ```bash
   /max-think "Should we use GraphQL or REST?
   Context:
   - Team: 5 backend devs (Node.js experience)
   - Scale: 50K API calls/day
   - Clients: Web + iOS + Android
   - Timeline: 2 months to MVP
   - Current: REST but hitting performance issues"
   ```

4. **Leverage /max-think's dynamic token allocation**
   - Let system auto-detect complexity
   - Simple problems auto-use 8K
   - Complex problems auto-upgrade to 24K-32K

5. **Session archival**
   - Important decisions auto-archive to `.ultra/thinking-sessions/`
   - Available for future reference and audit

### ❌ DON'T (Avoid)

1. **Don't abuse ultrathink**
   - ❌ "ultrathink How do I install npm?" (waste tokens)
   - ✅ Direct: "How do I install npm?"

2. **Don't use /max-think on simple questions**
   - ❌ `/max-think "What is React?"`
   - ✅ Direct: "What is React?"

3. **Don't confuse the two purposes**
   - ultrathink = exploration + deep reasoning
   - /max-think = decision + structured analysis

4. **Don't skip context**
   - ❌ `/max-think "Which database?"` (too vague)
   - ✅ `/max-think "Which database for real-time chat app with 10K users?"`

5. **Don't enable MAX_THINKING_TOKENS globally for all requests**
   - Current config: `MAX_THINKING_TOKENS=64000` (globally enabled)
   - Problem: All conversations consume massive tokens
   - Suggestion: Only specify manually when needed

---

## 8. Integration with Ultra Builder Pro Workflow

### Complete Workflow

```
Phase 0: Problem Exploration
  ultrathink "Explore the problem space"
     ↓
Phase 1: Decision Analysis
  /max-think "Structured decision-making"
     ↓
Phase 2: Research Validation
  /ultra-research [topic]  # If deep technical research needed
     ↓
Phase 3: Task Planning
  /ultra-plan
     ↓
Phase 4: TDD Development
  /ultra-dev [task-id]
     ↓
Phase 5: Comprehensive Testing
  /ultra-test
     ↓
Phase 6: Deployment Optimization
  /ultra-deliver
```

### Command Synergy

| Current Phase | Use Tool | Next Step Suggestion |
|--------------|----------|---------------------|
| Exploration | ultrathink | → /max-think or /ultra-research |
| Decision | /max-think | → /ultra-plan (if recommendation clear)<br>→ /ultra-research (if research needed) |
| Research | /ultra-research | → /max-think (re-decide)<br>→ /ultra-plan (start planning) |
| Planning | /ultra-plan | → /ultra-dev |
| Development | /ultra-dev | → /ultra-test |
| Testing | /ultra-test | → /ultra-deliver or fix bugs |
| Deployment | /ultra-deliver | → Done or next feature |

---

## 9. FAQ

### Q1: What's the fundamental difference between ultrathink and /max-think?

**A:**
- **ultrathink**: Claude Code **native feature**, allocates max thinking tokens (31,999), free-form output
- **/max-think**: Ultra Builder Pro **custom command**, provides 6-dimensional analysis framework, structured output

### Q2: Why does typing "ultrathink" trigger /max-think?

**A:** Previous /max-think description contained "thinking" and "extended reasoning" keywords, causing Claude auto-match. Now fixed:
- Old: `Deep analytical thinking for complex problems using extended reasoning`
- New: `6-dimensional structured analysis framework for complex decision-making`

### Q3: When should I use combined mode?

**A:** Recommend combined `ultrathink /max-think` for:
- ✅ Strategic architecture decisions (e.g., rewrite entire system)
- ✅ High-risk tech selection (e.g., choose core tech stack)
- ✅ Complex trade-off analysis (need ultra-deep reasoning + structured framework)
- ✅ Team-level decisions (affecting entire team direction)

### Q4: Is MAX_THINKING_TOKENS=64000 setting problematic?

**A:** Potential issues:
- ⚠️ Current setting: All conversations use 64K thinking tokens
- ⚠️ Impact: Even simple questions (like "hello") consume massive tokens
- ✅ Suggestion: Remove global setting, specify manually only when needed
  ```bash
  # Remove from settings.json
  # "env": { "MAX_THINKING_TOKENS": "64000" }

  # Specify manually when needed
  MAX_THINKING_TOKENS=30000 /max-think "complex problem"
  ```

### Q5: How to view my thinking session history?

**A:** /max-think auto-archives high-impact decisions:
```bash
# View archives
ls ~/.claude/.ultra/thinking-sessions/

# View index
cat ~/.claude/.ultra/thinking-sessions/session-index.json

# View specific session
cat ~/.claude/.ultra/thinking-sessions/session-2025-12-09-architecture-decision.md
```

---

## 10. Real-World Examples

### Example 1: Technology Selection (Independent /max-think)

**Scenario**: Choose state management solution

```bash
/max-think "Should we migrate from Redux to Zustand for our React app?

Context:
- Current: Redux + Redux Toolkit + Redux Saga
- App: E-commerce dashboard (20 components, 5 main features)
- Team: 3 frontend devs (React experience, limited Redux knowledge)
- Pain points: Boilerplate code, steep learning curve
- Timeline: 3 months to complete migration
- Concern: State complexity might grow in future"
```

**Expected output**:
- 6D analysis (technical, cost, learning curve, ecosystem, etc.)
- 3 scenarios (Keep Redux, Migrate to Zustand, Hybrid approach)
- Clear recommendation + confidence level
- Phased migration path
- Risk assessment (how to handle complex async logic)

---

### Example 2: Architecture Exploration (ultrathink then /max-think)

**Scenario**: Design real-time collaboration system

```bash
# Step 1: Exploration
ultrathink I need to build a real-time collaborative editing system
similar to Google Docs. What are the fundamental challenges and
approaches I should consider?

# [Wait for output: might cover CRDTs, OT, conflict resolution, scalability...]

# Step 2: Structured decision (based on exploration)
/max-think "Design real-time collaborative editing system architecture.

Approaches identified:
- CRDTs (Conflict-free Replicated Data Types)
- OT (Operational Transformation)

Context:
- Expected users: 10K concurrent editors
- Document types: Text, rich formatting, comments
- Latency requirement: <100ms sync time
- Offline support: Required
- Team: 4 backend + 2 frontend devs
- Timeline: 6 months MVP

Which approach should we use and why?"
```

---

### Example 3: Strategic Decision (Combined)

**Scenario**: Decide whether to rewrite legacy system

```bash
ultrathink /max-think "Should we rewrite our monolithic PHP legacy system
or incrementally refactor?

Context:
- Current system: PHP 7.2 monolith, 150K LOC, 8 years old
- Problems: Slow (3s page load), hard to test, no modern practices
- Business: 50K active users, $2M ARR, growing 20% YoY
- Team: 6 devs (3 PHP veterans, 3 modern stack devs)
- Timeline: Board wants modernization in 12 months
- Risk tolerance: Low (cannot afford downtime)
- Budget: $500K available

Options:
1. Full rewrite to Node.js + React
2. Incremental strangler pattern migration
3. Keep PHP but modernize (PHP 8.3 + framework)

Analyze technical, business, team, and risk dimensions thoroughly."
```

**Expected output**:
- Ultra-deep 6D analysis (ultrathink boost)
- 5+ detailed scenarios (full rewrite, incremental migration, modernize PHP, hybrid, etc.)
- High-confidence recommendation (based on risk-benefit analysis)
- Phased roadmap (possibly 12-18 months)
- Comprehensive risk matrix and contingency plans
- Financial analysis (development cost vs maintenance cost)

---

## 11. Configuration Optimization

### Current Configuration Analysis

```json
// ~/.claude/settings.json
{
  "env": {
    "MAX_THINKING_TOKENS": "64000"  // ⚠️ Globally enabled
  },
  "alwaysThinkingEnabled": true      // ⚠️ Always enabled
}
```

**Issues**:
- All conversations use 64K thinking tokens
- Even simple questions trigger deep thinking
- Extremely high token consumption, increased cost

### Recommended Configuration

```json
// ~/.claude/settings.json
{
  "alwaysThinkingEnabled": false,     // ✅ Enable on-demand
  // Remove MAX_THINKING_TOKENS global setting
}
```

**Specify manually when using**:
```bash
# When need deep thinking
MAX_THINKING_TOKENS=30000 claude

# Or for specific command
ultrathink Your complex problem
/max-think "Your structured analysis"
```

---

## 12. Summary

### Key Takeaways

1. **ultrathink** and **/max-think** are **complementary** tools, not replacements
2. **Independent use**: Choose appropriate tool based on problem type
3. **Combined use**: For strategic decisions, combine for best results
4. **Cost awareness**: Avoid overuse, choose appropriate tools and token budget

### Memory Aid

```
Exploration → ultrathink (free & deep)
Decision → max-think (structured & complete)
Strategic → both combined (ultimate power)
Simple → direct chat (efficient & fast)
```

---

**Last Updated**: 2025-12-09
**Version**: 1.0
**Related Docs**: @commands/max-think.md, @CLAUDE.md
