---
name: codex-research-gen
description: "Enhances technical research with evidence-based analysis and 90%+ confidence ratings. This skill generates production-grade specifications, verifies claims against sources, and provides actionable implementation guidance."
---

# Codex Research Generator

## Purpose

Enhance technical research with **evidence-based analysis, verified information, and production-grade specifications**. Research output must be directly actionable for implementation.

**Core Principle**: Research serves implementation. Every finding must be verified, confident (90%+), and immediately usable.

---

## Trigger Conditions

1. **Command binding**: Auto-triggers with `/ultra-research`
2. **Technology decision**: When comparing libraries, frameworks, or approaches
3. **Architecture planning**: When designing system components
4. **Manual**: User requests research assistance

---

## Research Quality Standards

### What Research Must Include

| Requirement | Description |
|-------------|-------------|
| **Evidence-based** | Claims backed by official docs, benchmarks, or verified sources |
| **Confidence rated** | Every recommendation includes confidence percentage |
| **Production focus** | All examples work in production, not demos |
| **Actionable** | Clear next steps with specific implementation guidance |
| **Trade-off analysis** | Pros/cons with quantified impact where possible |

### What Research Must NOT Include

| Prohibited | Description |
|------------|-------------|
| **Speculation without disclosure** | Guesses must be clearly marked |
| **Demo-only examples** | All code must be production-ready |
| **Outdated information** | Verify currency of all sources |
| **Unverified claims** | Every claim needs a source |
| **Vague recommendations** | "Consider using X" without specifics |

---

## Research Dimensions

### 1. Technical Feasibility (25%)

```markdown
## Feasibility Analysis

**Question**: Can we implement {feature} with {technology}?

**Evidence**:
- Official documentation: {link} (verified 2024-12)
- Production case study: {company} uses this at {scale}
- Benchmark results: {numbers} under {conditions}

**Confidence**: 94%

**Conclusion**: Feasible with {caveats}
```

### 2. Risk Assessment (25%)

```markdown
## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {risk1} | High (>70%) | Critical | {specific action} |
| {risk2} | Medium (30-70%) | Moderate | {specific action} |

**Overall Risk Score**: Medium
**Confidence**: 91%
```

### 3. Implementation Complexity (25%)

```markdown
## Complexity Assessment

**Effort Estimate**: {T-shirt size} ({reasoning})

**Dependencies**:
- Required: {dep1} (already in project)
- New: {dep2} (adds {X}KB bundle size)

**Learning Curve**: {estimate} for team with {background}

**Confidence**: 88%
```

### 4. Production Readiness (25%)

```markdown
## Production Readiness

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Performance | Pass | Benchmarks show {X} under {Y} load |
| Security | Pass | OWASP compliance verified |
| Scalability | Caution | Works to {X} users, beyond needs {Y} |
| Maintainability | Pass | Active development, {X} contributors |

**Recommendation**: Production-ready with {conditions}
**Confidence**: 92%
```

---

## Codex Call Template

```bash
codex -q --json <<EOF
You are a technical research expert. Analyze this topic:

Topic: {research_topic}
Context: {project_context}
Constraints: {known_constraints}

Research Requirements:

1. **Evidence-Based Analysis**
   - Cite official documentation
   - Reference production case studies
   - Include benchmark data where available
   - Verify all claims are current (2024+)

2. **Confidence Assessment**
   - Rate each finding 0-100%
   - Explain confidence factors
   - Flag any speculation explicitly
   - Minimum 90% confidence for recommendations

3. **Production Focus**
   - All code examples must be production-ready
   - No TODO, placeholder, or demo code
   - Include error handling
   - Consider scale and performance

4. **Actionable Output**
   - Specific implementation steps
   - Required dependencies with versions
   - Configuration examples
   - Migration path if replacing existing solution

5. **Trade-off Analysis**
   - Quantified pros and cons
   - Comparison with alternatives
   - Long-term maintenance considerations

Output format:
{
  "summary": "One-paragraph conclusion",
  "confidence": 92,
  "recommendation": "Specific recommended approach",
  "evidence": [
    {"claim": "...", "source": "...", "verified": "2024-12"},
  ],
  "risks": [
    {"risk": "...", "probability": "high|medium|low", "mitigation": "..."}
  ],
  "implementation": {
    "steps": ["Step 1", "Step 2"],
    "dependencies": ["dep@version"],
    "estimatedEffort": "2-3 days",
    "codeExample": "..."
  },
  "alternatives": [
    {"name": "...", "tradeoff": "..."}
  ]
}
EOF
```

---

## Dual-Engine Research Flow

```
Claude Code initiates research topic
        ↓
Claude Code gathers initial context
        ↓
Codex deepens research
        - Verifies claims against sources
        - Adds production examples
        - Rates confidence levels
        ↓
Claude Code reviews Codex findings
        ↓
Combined high-confidence output (90%+)
        ↓
Write to specs/
```

---

## Output Format (Runtime: Chinese)

```markdown
## Codex Research Report

**Topic**: {research_topic}
**Date**: {timestamp}
**Overall Confidence**: {X}%

### Executive Summary

{One paragraph with key findings and recommendation}

### Evidence Analysis

| Claim | Source | Verified | Confidence |
|-------|--------|----------|------------|
| {claim1} | {official_docs} | 2024-12 | 95% |
| {claim2} | {benchmark} | 2024-11 | 88% |

### Recommendation

**Approach**: {specific recommendation}
**Confidence**: {X}%
**Rationale**: {evidence-based reasoning}

### Implementation Guide

#### Prerequisites
- {dep1}@{version}
- {dep2}@{version}

#### Step 1: {action}
\`\`\`typescript
// Production-ready code
{code}
\`\`\`

#### Step 2: {action}
...

### Risk Mitigation

| Risk | Mitigation | Owner |
|------|------------|-------|
| {risk1} | {specific_action} | Dev Team |

### Alternatives Considered

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| {alt1} | {pros} | {cons} | {reason} |

### Uncertainty Notes

Items with confidence < 90%:
- {item}: {confidence}% - {reason for uncertainty}

### Next Steps

1. [ ] {specific action with owner}
2. [ ] {specific action with owner}
```

---

## Quality Gates

| Metric | Requirement |
|--------|-------------|
| Overall confidence | >= 90% |
| Source verification | All claims have sources |
| Code quality | Production-ready, no placeholders |
| Actionability | Clear next steps defined |

---

## Configuration

```json
{
  "codex-research-gen": {
    "minConfidence": 0.9,
    "requireSources": true,
    "maxSpeculationPercent": 0.1,
    "outputPath": ".ultra/docs/research/",
    "codeStandard": "production",
    "prohibitedPatterns": [
      "TODO",
      "FIXME",
      "placeholder",
      "demo",
      "example only"
    ]
  }
}
```

---

## Integration with /ultra-research

### Round 3: Technology Selection (Enhanced)

```
Claude Code identifies technology options
        ↓
Codex researches each option
        - Official docs verification
        - Production case studies
        - Benchmark comparison
        ↓
Codex generates comparison matrix
        ↓
Claude Code presents to user
        ↓
User selects with confidence-rated data
```

### Research Quality Checklist

Before finalizing any research output:

- [ ] All claims have verifiable sources
- [ ] Overall confidence >= 90%
- [ ] Code examples are production-ready
- [ ] Risks identified with mitigations
- [ ] Clear, actionable next steps
- [ ] Alternatives documented with trade-offs

---

## Honest Output Requirements

Every research report must include:

```markdown
## Confidence Assessment

**Overall Confidence**: 92%

**High Confidence (95%+)**:
- API compatibility (verified against official docs)
- Performance benchmarks (reproduced locally)

**Medium Confidence (85-95%)**:
- Scalability estimates (based on similar systems)
- Team adoption timeline (industry averages)

**Speculation (<85%)**:
- Long-term maintenance cost (market trends uncertain)

**Verification Recommended**:
- Run benchmark in your specific environment
- Consult with {vendor} for enterprise support details
```
