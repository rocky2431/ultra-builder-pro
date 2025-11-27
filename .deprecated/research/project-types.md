## Phase 0: Project Type Detection (NEW - Intelligent Routing)

**Purpose**: Route to optimal research flow based on project context

**When**: At the start of every /ultra-research invocation

**Implementation**: Use AskUserQuestion tool for interactive selection

```typescript
// Project type detection with AskUserQuestion
// Note: At runtime, Claude will translate these to Chinese for user output
// This follows Language Protocol: English instructions, Chinese output
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
// Note: At runtime, Claude will translate these to Chinese for user output
AskUserQuestion({
  questions: [{
    question: "Select needed research rounds (multi-select allowed)",
    header: "Custom Rounds",
    multiSelect: true,
    options: [
      {
        label: "Round 1: Problem Discovery",
        description: "Clarify problem essence, target users, pain point analysis (20 min)"
      },
      {
        label: "Round 2: Solution Exploration",
        description: "User stories, functional requirements, non-functional requirements (20 min)"
      },
      {
        label: "Round 3: Technology Selection",
        description: "Tech stack evaluation, 6D comparison, architecture decisions (15 min)"
      },
      {
        label: "Round 4: Risk & Constraints",
        description: "Risk identification, constraint documentation, mitigation strategies (15 min)"
      }
    ]
  }]
})
```

**Output**: Selected rounds array → Proceed to Mode 1 with dynamic round execution

---
