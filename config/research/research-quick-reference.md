# Research Quick Reference

**Purpose**: Consolidated quick reference for project types, Mode 2, and output validation.

**Files Merged**: `mode-2-focused.md`, `project-types.md`, `output-templates.md`

---

## 1. Project Type Detection (Phase 0)

**When**: At the start of every /ultra-research invocation

**Implementation**: Use AskUserQuestion tool for interactive selection

```typescript
// Note: At runtime, Claude will translate these to Chinese for user output
AskUserQuestion({
  questions: [{
    question: "Select project type for optimal research flow recommendation",
    header: "Project Type",
    multiSelect: false,
    options: [
      {
        label: "New Project (from scratch)",
        description: "Requirements unclear, need complete 4-round research (70 min)"
      },
      {
        label: "Incremental Feature (existing project)",
        description: "Existing system, only need solution exploration and tech selection (30 min)"
      },
      {
        label: "Tech Decision",
        description: "Development tech problem, only need tech evaluation (15 min)"
      },
      {
        label: "Custom Flow",
        description: "Manually select research rounds"
      }
    ]
  }]
})
```

**Routing Logic**:

| Project Type | Rounds Required | Duration | Use Case |
|--------------|----------------|----------|----------|
| **New Project** | Round 1-4 (All) | 70 min | From scratch, requirements unclear |
| **Incremental Feature** | Round 2-3 (Solution + Tech) | 30 min | Existing system, adding features |
| **Tech Decision** | Round 3 (Tech only) | 15 min | Development tech problem |
| **Custom Flow** | User selects | Variable | Flexible scenarios |

**Custom Flow Selection** (if user chooses "Custom Flow"):

```typescript
AskUserQuestion({
  questions: [{
    question: "Select needed research rounds (multi-select allowed)",
    header: "Custom Rounds",
    multiSelect: true,
    options: [
      { label: "Round 1: Problem Discovery", description: "Clarify problem essence, target users (20 min)" },
      { label: "Round 2: Solution Exploration", description: "User stories, requirements (20 min)" },
      { label: "Round 3: Technology Selection", description: "Tech stack evaluation (15 min)" },
      { label: "Round 4: Risk & Constraints", description: "Risk identification (15 min)" }
    ]
  }]
})
```

---

## 2. Mode 2: Focused Technology Research

**Usage**:
```bash
/ultra-research "React vs Vue for enterprise dashboard"
```

**Implementation**: Delegates to **ultra-research-agent** for execution

**Workflow** (executed by agent):
1. Parallel information gathering (4-8 tools in one message)
2. Six-dimension evaluation with evidence citations
3. Risk assessment (Critical / High / Medium)
4. Generate structured report (7 required items)
5. Auto-update `specs/architecture.md`
6. Save research report to `.ultra/docs/research/`

**Duration**: 10-15 minutes

**Use when**: Specific technology question during development, not building specs from scratch

**Agent Details**: See `@agents/ultra-research-agent.md`

---

## 3. Document Completeness Validation

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
```

**Triggers re-questioning if**:
- Any required section is missing
- Section contains `[NEEDS CLARIFICATION]` markers
- Section is too vague (< 50 words)
- Contradictory information detected

---

## 4. Output Format Reference

**Standard output structure**: See `@config/ultra-command-output-template.md`

**Command icon**: Research

**Mode 1 output**: 4-round iterative progress reports

**Mode 2 output**: Single comparison report with recommendation

---

## 5. Related Files

| File | Purpose | Lines |
|------|---------|-------|
| `interaction-points-core.md` | Core questions (Hybrid Model) | ~450 |
| `mode-1-discovery.md` | Full Mode 1 workflow | ~810 |
| `metadata-schema.md` | Quality metrics schema | ~680 |
| **This file** | Quick reference (merged) | ~150 |

**Total**: 4 files (~2,090 lines) vs 7 files (~2,870 lines) = **27% reduction**

---

**OUTPUT: User messages in Chinese at runtime; keep this file English-only.**
