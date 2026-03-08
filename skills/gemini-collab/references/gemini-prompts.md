# Gemini Prompts

CLI-ready prompt invocations for each collaboration mode. Generic prompt text is in `prompt-templates.md` (ai-collab-base).

Model selection: pass any available Gemini model via `-m <model>`. Omit for default model.

## Review

```bash
git diff HEAD~1 | gemini -p "Review this diff. For each issue: severity (Critical/Warning/Info), location, description, suggested fix. Focus on bugs, security, performance, error handling." --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

### Security Review
```bash
cat "$FILE" | gemini -p "Security audit: check for injection, XSS, path traversal, auth flaws, data exposure, OWASP Top 10. For each: severity, location, exploit scenario, remediation." --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

### Performance Review
```bash
cat "$FILE" | gemini -p "Performance analysis: algorithm complexity, unnecessary allocations, N+1 queries, missing caching, blocking ops, memory leaks. Quantify impact." --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Understand

```bash
gemini -p "Analyze this project: 1) Purpose 2) Architecture patterns 3) Directory structure 4) Data flow 5) Key dependencies 6) Testing approach. Be thorough." --yolo --sandbox > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Opinion

```bash
gemini -p "Architecture decision — Context: [CONTEXT]. Constraints: [CONSTRAINTS]. Options: A) [A] B) [B]. For each: pros/cons, trade-offs, risks, your recommendation." --yolo --sandbox > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Compare

```bash
gemini -p "[QUESTION]. Provide your independent analysis with reasoning." --yolo --sandbox > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```

## Free

```bash
gemini -p "[USER_PROMPT]" --yolo > "${SESSION_PATH}/output.md" 2>"${SESSION_PATH}/error.log"
```
