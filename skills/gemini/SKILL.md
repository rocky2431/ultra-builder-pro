---
name: gemini
description: Use when the user needs technical research, architecture validation, documentation generation, or read-only code review. Gemini does NOT modify code - use codex for code changes.
allowed-tools: Bash, Read, Glob, Grep, Write
---

# Gemini Skill Guide

> **Core Principle**: Gemini is for research, validation, and documentation. It does NOT modify code.
> For code changes, use the `codex` skill instead.

## Use Cases

| Task | Use Gemini | Use Codex |
|------|------------|-----------|
| Technical research | ✅ | ❌ |
| Architecture validation | ✅ | ❌ |
| Documentation generation | ✅ | ❌ |
| Code review (read-only) | ✅ | ❌ |
| Code refactoring | ❌ | ✅ |
| Bug fixing | ❌ | ✅ |
| Code optimization | ❌ | ✅ |

## Running a Task

### Defaults
- **Model**: `gemini-3-flash-preview`
- **Mode**: Read-only (no `--yolo`)
- **Output format**: `text`

### Invocation Modes

**Mode 1: Template invocation** (from commands like `/ultra-research`)
- Use template config directly, NO user interaction
- Templates define model/context/prompt

**Mode 2: Regular invocation** (user requests gemini directly)
1. Display current defaults
2. Use `AskUserQuestion`:
   - Option A: "使用默认配置" (Recommended) - gemini-3-flash-preview, read-only
   - Option B: "自定义配置" - then ask model/output format
3. Execute with chosen config

### Configuration Options

**Models**:
- `gemini-3-flash-preview` (default, latest and fastest)
- `gemini-3-pro-preview` (most powerful, deep reasoning)
- `gemini-2.5-pro` (1M context, stable)
- `gemini-2.5-flash` (balanced, stable)
- `gemini-2.5-flash-lite` (lightweight, fast)

**Output formats**:
- `text` (default) - human-readable
- `json` - structured output for automation

**Context options**:
- `@./path` - inject file content into prompt
- `--include-directories dir1 dir2` - add directories to context
- `-a, --all-files` - include all files in context

### Command template
```bash
gemini \
  -m gemini-3-flash-preview \
  -p "prompt here"
```

### With file context
```bash
gemini -p "Analyze the architecture of this codebase @./src/"
```

### With directory context
```bash
gemini --include-directories src docs -p "Review the documentation coverage"
```

### Execution rules
- **NEVER use `-y` (yolo mode)** - Gemini is read-only
- Run the command and show complete output to user
- After completion: summarize findings and suggest next steps

## Quick Reference

| Use case | Command |
|----------|---------|
| Tech research | `gemini -p "Research best practices for X"` |
| Architecture review | `gemini --include-directories src -p "Review architecture"` |
| Documentation | `gemini -p "Generate API documentation for @./src/api/"` |
| Code review | `gemini -p "Review this code for issues @./file.ts"` |
| Validation | `gemini -p "Validate this design against requirements @./spec.md"` |

## Following Up

- After every `gemini` command, summarize key findings
- Use `AskUserQuestion` to confirm next steps
- If code changes needed, suggest using `codex` skill

## Error Handling

- If `gemini` exits non-zero, show the error and ask user for direction
- If output shows concerns, summarize and recommend actions

---

## Templates

Use these predefined templates when commands reference `gemini skill with template: <name>`.

### tech-research

| Config | Value |
|--------|-------|
| Model | gemini-2.5-pro |
| Context | project files + web search |

**Purpose**: Deep technical research with evidence gathering

**Prompt**:
```
Conduct technical research on the specified topic:

[Research Protocol]
1. Search for official documentation and authoritative sources
2. Gather community best practices and real-world examples
3. Identify potential risks and trade-offs
4. Compare alternatives with evidence

[Evidence Requirements]
- Every claim must have verifiable source
- Priority: 1) Official docs 2) Benchmarks 3) Community practices
- Label findings: Fact | Inference | Speculation

[Output Format]
1. Executive Summary (2-3 sentences)
2. Key Findings (with sources)
3. Comparison Matrix (if alternatives exist)
4. Risks & Trade-offs
5. Recommendation (with confidence %)

Minimum 90% confidence required for recommendations.
```

---

### architecture-review

| Config | Value |
|--------|-------|
| Model | gemini-2.5-pro |
| Context | include source directories |

**Purpose**: Validate architecture decisions against best practices

**Prompt**:
```
Review this architecture against these criteria:

[Critical State Management]
- Is critical state (funds/permissions/external API) persistable?
- Is recovery/replay mechanism in place?
- Is observability (logging/metrics/tracing) adequate?

[Modularity & Boundaries]
- Are module boundaries clear and well-defined?
- Is coupling between modules appropriate?
- Are interfaces stable and versioned?

[Scalability & Performance]
- Are there obvious bottlenecks?
- Is horizontal scaling possible?
- Are resource limits defined?

[Security]
- Are authentication/authorization properly separated?
- Is input validation at system boundaries?
- Are secrets properly managed?

[Maintainability]
- Is the codebase navigable?
- Are patterns consistent?
- Is technical debt visible and managed?

Provide findings with file:line references.
Rate each area: Good | Needs Improvement | Critical Issue
```

---

### documentation-gen

| Config | Value |
|--------|-------|
| Model | gemini-3-flash-preview |
| Context | include source files |

**Purpose**: Generate or review documentation

**Prompt**:
```
Generate/review documentation for the specified code:

[Documentation Standards]
- Clear purpose statement
- Usage examples (production-ready, no TODO/placeholder)
- Parameter descriptions with types
- Return value documentation
- Error handling documentation
- Edge cases noted

[Quality Criteria]
- Accurate (matches actual implementation)
- Complete (all public APIs documented)
- Concise (no redundant information)
- Current (reflects latest code)

Output format: Markdown
Include code examples where helpful.
```

---

### spec-validation

| Config | Value |
|--------|-------|
| Model | gemini-2.5-pro |
| Context | include specs and implementation |

**Purpose**: Validate implementation against specifications

**Prompt**:
```
Validate the implementation against the specification:

[Compliance Check]
- Does implementation match spec requirements?
- Are all acceptance criteria covered?
- Are edge cases from spec handled?

[Gap Analysis]
- What spec requirements are NOT implemented?
- What implementation exists that's NOT in spec?
- Are there implicit assumptions not documented?

[Risk Assessment]
- What could break if spec changes?
- What's the impact of each gap?

Output:
1. Compliance Score (%)
2. Gaps List (with severity)
3. Recommendations
```

---

### code-review (read-only)

| Config | Value |
|--------|-------|
| Model | gemini-2.5-pro |
| Context | include changed files |

**Purpose**: Review code for issues WITHOUT making changes

**Prompt**:
```
Review this code (READ-ONLY - do not suggest exact code changes):

[Code Quality]
- TODO/FIXME/placeholder present?
- Deep nesting issues (>3 levels)?
- Hardcoded secrets or credentials?

[Security Concerns]
- Injection vulnerabilities?
- Auth bypass risks?
- Input validation gaps?

[Architecture Issues]
- Critical state not persisted?
- In-memory-only storage for important data?
- Breaking API changes without migration?

[Logic Problems]
- Race conditions?
- Resource leaks?
- Edge cases not handled?

[Testing Gaps]
- Core logic mocked inappropriately?
- Missing test coverage for critical paths?

Provide findings with file:line references.
Severity: Critical | High | Medium | Low
DO NOT provide code fixes - only identify issues.
If code changes needed, recommend using codex skill.
```
