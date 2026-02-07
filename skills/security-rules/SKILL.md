---
name: security-rules
description: Ultra Builder Pro security rules
user-invocable: false
---

# Security Rules

These rules are mandatory for all code review and security-related work.

## Input Validation

All external input MUST be validated:
- **Syntactic**: correct format (email, date, UUID)
- **Semantic**: valid in business context (start < end, price > 0)
- Validate early, reject invalid input immediately

## Forbidden Patterns

| Pattern | Risk | Alternative |
|---------|------|-------------|
| SQL string concatenation | SQL Injection | Parameterized queries (`$1`, `?`) |
| User input → HTML directly | XSS | textContent, sanitizer library |
| Hardcoded secrets/keys | Credential leak | Environment variables, secret manager |
| Trust client-supplied role | Privilege escalation | Derive from session/token server-side |
| Dynamic code evaluation with user input | Code injection | Use safe parsers (JSON.parse, etc.) |
| Regex with user input | ReDoS | Validate/escape regex input |

## Required Practices

| Area | Rule |
|------|------|
| SQL | Parameterized queries only |
| Output | Escape/sanitize all user-derived content |
| Auth | Use established auth libraries |
| Secrets | Environment variables or secret manager |
| Sessions | Secure, HttpOnly, SameSite cookies |
| CORS | Explicit allowlist, never wildcard in production |
| File upload | Validate type, size, sanitize filename |

## Error Handling Security

- Never expose stack traces to end users
- Never include sensitive data in error messages
- Log security events with sufficient context for investigation
- Use typed errors, not generic messages

## Review Checklist

When reviewing code, check for:
1. SQL injection vectors (string concatenation in queries)
2. XSS vectors (unescaped user input in HTML/templates)
3. Hardcoded credentials, API keys, or secrets
4. Missing authentication/authorization checks
5. Missing input validation on external boundaries
6. Insecure direct object references (IDOR)
7. Missing rate limiting on sensitive endpoints
8. Sensitive data in logs or error messages
9. Missing CSRF protection on state-changing operations
10. Insecure deserialization
