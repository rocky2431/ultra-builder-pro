# Gemini Collab - Prompt Templates

Ready-to-use prompt templates for each collaboration mode. These are starting points — adapt based on specific context.

## Code Review Prompts

### General Review
```
Review this code carefully. For each issue found, provide:
1. Severity (Critical / Warning / Info)
2. Location (file and line if possible)
3. Description of the problem
4. Suggested fix

Focus areas: bugs, security vulnerabilities, performance issues, error handling gaps, and readability concerns. Be specific and actionable.
```

### Security-Focused Review
```
Perform a security audit of this code. Check for:
- Input validation gaps (injection, XSS, path traversal)
- Authentication/authorization flaws
- Sensitive data exposure (hardcoded secrets, logging PII)
- Insecure dependencies or configurations
- OWASP Top 10 vulnerabilities

For each finding: severity, location, exploit scenario, and remediation.
```

### Performance Review
```
Analyze this code for performance issues:
- Algorithm complexity (time and space)
- Unnecessary allocations or copies
- N+1 queries or redundant I/O
- Missing caching opportunities
- Blocking operations that could be async
- Memory leaks or resource cleanup

Quantify impact where possible (e.g., "O(n^2) loop on line X, problematic for n>1000").
```

## Project Understanding Prompts

### Full Project Analysis
```
Analyze this project comprehensively:

1. **Purpose**: What does this project do? Who is it for?
2. **Architecture**: What patterns are used? (MVC, Clean Architecture, etc.)
3. **Structure**: Map the directory layout and explain each module's responsibility
4. **Data Flow**: Trace a typical request from entry point to response
5. **Dependencies**: Key libraries and why they're needed
6. **Configuration**: How is the project configured? (env vars, config files)
7. **Testing**: What testing approach is used? Coverage strategy?
8. **Build & Deploy**: How is it built and deployed?

Be thorough but organized. Use headers and bullet points.
```

### Module Deep-Dive
```
Deep-dive into the [MODULE_NAME] module:

1. Public API / exports — what does it expose?
2. Internal architecture — how is it organized?
3. Dependencies — what does it depend on? What depends on it?
4. State management — what state does it hold? How?
5. Error handling — how does it handle failures?
6. Edge cases — what could go wrong?
7. Improvement opportunities — what would you refactor?
```

## Second Opinion Prompts

### Architecture Decision
```
I need to make an architecture decision.

Context: [describe current situation]
Constraints: [list constraints — time, team size, existing tech, etc.]
Options being considered:
- Option A: [describe]
- Option B: [describe]
- Option C: [describe, if applicable]

For each option, analyze:
1. Pros and cons
2. Short-term vs long-term trade-offs
3. Risk factors
4. Migration/adoption effort
5. Your recommendation with reasoning
```

### Design Pattern Choice
```
Which design pattern best fits this scenario?

Problem: [describe the problem]
Requirements: [list requirements]
Current code structure: [brief description]

Recommend a pattern with:
- Why it fits this case
- Implementation sketch
- What to watch out for
- When this pattern would be wrong
```

## Comparative Prompts

### Debugging Hypothesis
```
A bug has the following symptoms:
[describe symptoms, error messages, reproduction steps]

Relevant code:
[paste relevant code sections]

Recent changes:
[paste recent diff if applicable]

Provide your top 3 hypotheses for the root cause, ordered by likelihood. For each:
1. What you think is happening
2. Evidence supporting this hypothesis
3. How to verify/disprove it
4. Suggested fix
```

### Implementation Approach
```
Task: [describe what needs to be built]
Requirements: [list requirements]
Existing codebase context: [brief description of relevant code]

Propose an implementation approach:
1. High-level design
2. Key files to create/modify
3. Data structures and interfaces
4. Step-by-step implementation plan
5. Testing strategy
6. Potential pitfalls
```
