---
name: codex-doc-reviewer
description: "Reviews and enhances documentation for technical accuracy, completeness, and practicality. This skill adds production-grade code examples, FAQ sections, best practices, and troubleshooting guides."
---

# Codex Document Reviewer

## Purpose

Review and enhance documentation for **technical accuracy, completeness, clarity, and practical utility**. Good documentation enables users to succeed with the product.

**Core Principle**: Documentation is a product. It must be accurate, complete, and immediately useful.

---

## Trigger Conditions

1. **Command binding**: Auto-triggers with `/ultra-deliver`
2. **File detection**: After `.md` file creation/modification
3. **Manual**: User requests documentation review

---

## Collaboration Flow

```
Step 1: Claude Code drafts documentation
        ↓
Step 2: Codex reviews for quality
        - Technical accuracy
        - Completeness
        - Clarity
        ↓
Step 3: Codex enhances content
        - More code examples
        - FAQ section
        - Best practices
        - Troubleshooting
        ↓
Step 4: Claude Code final review
        - Style consistency
        - Language polish
        - Final approval
```

---

## Review Dimensions (100-Point Scale)

### 1. Technical Accuracy (35%)

| Check | Description |
|-------|-------------|
| Code examples correct | Examples run without errors |
| API descriptions accurate | Parameters, returns, exceptions correct |
| Version match | Documentation matches current code version |
| Terminology accurate | Technical terms used correctly |

### 2. Completeness (30%)

| Check | Description |
|-------|-------------|
| Feature coverage | All public APIs documented |
| Scenario coverage | Common use cases explained |
| Error handling | Error conditions and handling documented |
| Configuration | All config options with defaults documented |

### 3. Clarity (20%)

| Check | Description |
|-------|-------------|
| Structure clear | Well-organized, easy to navigate |
| Language concise | No redundancy, easy to understand |
| No ambiguity | Descriptions precise, no misinterpretation |
| Format correct | Proper Markdown formatting |

### 4. Practicality (15%)

| Check | Description |
|-------|-------------|
| Quick start | Concise getting-started guide |
| Code examples | Sufficient, copy-paste ready |
| FAQ | Common questions answered |
| Best practices | Recommended usage patterns |

---

## Production-Grade Documentation Requirements

### Documentation Must Include

1. **Working Code Examples**: Every API must have runnable examples
2. **Error Scenarios**: Document what can go wrong and how to fix it
3. **Configuration Reference**: All options with types, defaults, descriptions
4. **Migration Guide**: For breaking changes between versions
5. **Performance Considerations**: When operations are expensive

### Documentation Must NOT Include

1. **Placeholder text**: "TODO: add description"
2. **Broken examples**: Code that doesn't compile/run
3. **Outdated information**: References to removed features
4. **Vague descriptions**: "This does stuff"
5. **Missing error handling**: Examples that ignore errors

---

## Codex Call Templates

### Phase 1: Review

```bash
codex -q --json <<EOF
You are a technical documentation expert. Review this documentation:

Document Content:
\`\`\`markdown
{document_content}
\`\`\`

Related Code:
\`\`\`typescript
{related_code}
\`\`\`

Review across these dimensions:

1. **Technical Accuracy** (35 points)
   - Do code examples work?
   - Are API descriptions correct?
   - Does it match current code?

2. **Completeness** (30 points)
   - Are all features covered?
   - Is error handling documented?
   - Are configuration options listed?

3. **Clarity** (20 points)
   - Is structure clear?
   - Any ambiguity?

4. **Practicality** (15 points)
   - Sufficient examples?
   - Easy to get started?

Output format:
{
  "score": {
    "accuracy": X,
    "completeness": X,
    "clarity": X,
    "practicality": X,
    "total": X
  },
  "issues": [
    {"location": "Section X", "issue": "description", "suggestion": "fix"}
  ],
  "missing": [
    "Missing content 1",
    "Missing content 2"
  ],
  "verdict": "PASS|ENHANCE|REWRITE"
}
EOF
```

### Phase 2: Enhancement

```bash
codex -q <<EOF
Based on review results, enhance this documentation:

Original Document:
\`\`\`markdown
{document_content}
\`\`\`

Add the following:
1. More code examples covering {missing_scenarios}
2. FAQ section for {common_issues}
3. Best practices recommendations
4. Troubleshooting guide
5. Common pitfalls to avoid

Requirements:
- All code examples must be production-grade (no TODO, no placeholders)
- Examples must handle errors properly
- Include realistic use cases, not toy examples
- Confidence level >= 90% for all content

Output the enhanced complete document.
EOF
```

---

## Output Format (Runtime: Chinese)

### Review Report

```markdown
## Codex Documentation Review Report

**Review Time**: {timestamp}
**Document**: {document_path}

### Scores

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Technical Accuracy | X/100 | 35% | X |
| Completeness | X/100 | 30% | X |
| Clarity | X/100 | 20% | X |
| Practicality | X/100 | 15% | X |
| **Total** | - | - | **X/100** |

### Issues

#### Technical Errors
- [ ] Section X: {issue} → {fix suggestion}

#### Missing Content
- [ ] Missing {content description}

### Verdict

**{PASS | ENHANCE | REWRITE}**
```

### Enhancement Output

```markdown
## Enhanced Content (Codex Generated)

### Additional Examples

#### Example 1: {scenario}
\`\`\`typescript
{production_grade_code}
\`\`\`

### FAQ

**Q: {common question}**
A: {detailed answer with code if applicable}

### Best Practices

1. **{practice name}**: {explanation}

### Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| {symptom} | {cause} | {fix} |

### Common Pitfalls

- **{pitfall}**: {how to avoid}
```

---

## Quality Gates

| Metric | Requirement |
|--------|-------------|
| Total Score | >= 80 |
| No broken examples | Code must run |
| No TODO markers | 0 placeholders |
| Version match | Docs match code |

---

## Configuration

```json
{
  "codex-doc-reviewer": {
    "minScoreToPass": 80,
    "autoEnhance": true,
    "enhanceIfScoreBelow": 90,
    "docTypes": [".md", ".mdx", ".rst"],
    "skipPaths": ["**/node_modules/**", "**/dist/**"],
    "requiredSections": ["Quick Start", "API Reference", "Error Handling"],
    "confidenceThreshold": 0.9
  }
}
```

---

## Honest Output

All documentation output includes confidence assessment:

```markdown
## Documentation Enhancement Report

**Confidence**: 94%

**Sections Enhanced**: 4
**Examples Added**: 8
**FAQ Items**: 5

**High Confidence** (>95%):
- API Reference examples (verified against code)
- Error codes and messages (extracted from source)

**Medium Confidence** (85-95%):
- Best practices (based on common patterns)
- Performance tips (inferred from implementation)

**Verification Required**:
- Run all code examples before publishing
- Review troubleshooting steps with actual error scenarios
```
