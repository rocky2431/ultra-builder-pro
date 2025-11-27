## Document Completeness Analysis

**Automatic validation checks**:

```typescript
interface CompletenessCheck {
  file: 'product.md' | 'architecture.md';
  sections: {
    name: string;
    required: boolean;
    status: 'complete' | 'partial' | 'missing';
    issues: string[];
  }[];
  score: number; // 0-100%
}

function analyzeProductMd(content: string): CompletenessCheck {
  return {
    file: 'product.md',
    sections: [
      {
        name: 'Problem Statement',
        required: true,
        status: checkSection(content, 'Problem Statement'),
        issues: findIssues(content, 'Problem Statement')
      },
      {
        name: 'Target Users',
        required: true,
        status: checkSection(content, 'Target Users'),
        issues: findIssues(content, 'Target Users')
      },
      // ... all sections
    ],
    score: calculateScore()
  };
}
```

**Triggers re-questioning if**:
- Any required section is missing
- Section contains `[NEEDS CLARIFICATION]` markers
- Section is too vague (< 50 words)
- Contradictory information detected

---
## Output Format

**Standard output structure**: See `@config/ultra-command-output-template.md` for the complete 6-section format.

**Command icon**: 🔬

**Mode 1 output**: 4-round iterative progress reports (see "Discovery Complete" example above)

**Mode 2 output**: Single comparison report with recommendation

---

## References

- @commands/ultra-think.md - 6-dimensional analysis framework
- @config/ultra-mcp-guide.md - MCP tool selection guide
- @skills/syncing-docs/REFERENCE.md - Documentation sync workflow
- @workflows/ultra-development-workflow.md - Complete workflow context

---
