# Codex Collab - Prompt Templates

Ready-to-use prompt templates for each collaboration mode. Adapt based on context.

## Code Review Prompts

### General Review (use `codex review` directly)
```bash
codex review --uncommitted
```

### Security-Focused Review
```bash
codex review --uncommitted "Perform a security audit. Check for: input validation gaps (injection, XSS, path traversal), authentication/authorization flaws, sensitive data exposure, insecure configurations, OWASP Top 10. For each finding: severity, location, exploit scenario, remediation."
```

### Performance Review
```bash
codex review --uncommitted "Analyze for performance issues: algorithm complexity, unnecessary allocations, N+1 queries, missing caching, blocking operations, memory leaks. Quantify impact where possible."
```

### Review Against Branch
```bash
codex review --base main "Review all changes for bugs, breaking changes, and API contract violations."
```

## Project Understanding Prompts

### Full Project Analysis
```bash
codex exec "Analyze this project comprehensively:
1. Purpose: What does this project do? Who is it for?
2. Architecture: What patterns are used?
3. Structure: Map the directory layout and each module's responsibility
4. Data Flow: Trace a typical request from entry point to response
5. Dependencies: Key libraries and why they're needed
6. Testing: What testing approach is used?
7. Build & Deploy: How is it built and deployed?
Be thorough but organized." --sandbox read-only --full-auto -o /tmp/codex-analysis.txt
```

### Module Deep-Dive
```bash
codex exec "Deep-dive into the [MODULE_NAME] module:
1. Public API / exports
2. Internal architecture
3. Dependencies (inbound and outbound)
4. State management
5. Error handling patterns
6. Edge cases and risks
7. Improvement opportunities" --sandbox read-only --full-auto -o /tmp/codex-module.txt
```

## Second Opinion Prompts

### Architecture Decision
```bash
codex exec "I need to make an architecture decision.
Context: [describe current situation]
Constraints: [list constraints]
Options:
- Option A: [describe]
- Option B: [describe]
For each option, analyze: pros/cons, short-term vs long-term trade-offs, risk factors, migration effort. Give your recommendation with reasoning." --sandbox read-only --full-auto -o /tmp/codex-opinion.txt
```

### Design Pattern Choice
```bash
codex exec "Which design pattern best fits this scenario?
Problem: [describe]
Requirements: [list]
Current code structure: [brief description]
Recommend a pattern with: why it fits, implementation sketch, what to watch out for, when this pattern would be wrong." --sandbox read-only --full-auto -o /tmp/codex-pattern.txt
```

## Comparative Prompts

### Debugging Hypothesis
```bash
codex exec "A bug has the following symptoms:
[describe symptoms, error messages, reproduction steps]
Relevant code is in [file paths].
Recent changes: [describe or reference commit].
Top 3 hypotheses for root cause, ordered by likelihood. For each: what's happening, evidence, how to verify, suggested fix." --sandbox read-only --full-auto -o /tmp/codex-debug.txt
```

### Implementation Approach
```bash
codex exec "Task: [describe what needs to be built]
Requirements: [list]
Existing codebase: [brief description]
Propose: high-level design, key files to create/modify, data structures, step-by-step plan, testing strategy, potential pitfalls." --sandbox read-only --full-auto -o /tmp/codex-impl.txt
```
