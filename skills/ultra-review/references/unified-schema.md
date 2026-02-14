# Ultra Review - Unified JSON Schema v1

All review agents MUST output findings in this exact format. No deviations.

## Schema

```json
{
  "$schema": "ultra-review-findings-v1",
  "agent": "<agent-name>",
  "session": "<timestamp>-<branch>",
  "timestamp": "<ISO 8601>",
  "scope": {
    "files_analyzed": ["src/foo.ts", "src/bar.ts"],
    "total_lines_analyzed": 342,
    "diff_only": true
  },
  "summary": {
    "total_findings": 5,
    "by_severity": { "P0": 1, "P1": 2, "P2": 1, "P3": 1 },
    "verdict": "REQUEST_CHANGES"
  },
  "findings": [
    {
      "id": "<agent-name>-001",
      "severity": "P0",
      "confidence": 95,
      "category": "security",
      "subcategory": "injection",
      "title": "SQL injection via string concatenation",
      "file": "src/api/handler.ts",
      "line": 45,
      "line_end": 47,
      "code_snippet": "const query = `SELECT * FROM users WHERE id = ${userId}`",
      "description": "User-controlled input directly interpolated into SQL query string.",
      "suggestion": "Use parameterized query: db.query('SELECT * FROM users WHERE id = $1', [userId])",
      "claude_md_rule": "security.forbidden_patterns.sql_string_concat"
    }
  ],
  "positive_observations": [
    "Clean separation between domain and infrastructure layers"
  ],
  "metadata": {
    "duration_ms": 15000,
    "model": "claude-opus-4-6",
    "turns_used": 12
  }
}
```

## Field Definitions

### Top-Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `$schema` | string | YES | Always `"ultra-review-findings-v1"` |
| `agent` | string | YES | Agent name: `review-code`, `review-tests`, `review-errors`, `review-types`, `review-comments`, `review-simplify` |
| `session` | string | YES | Session ID provided in the task prompt |
| `timestamp` | string | YES | ISO 8601 timestamp when review completed |
| `scope` | object | YES | What was analyzed |
| `summary` | object | YES | Aggregate counts |
| `findings` | array | YES | Individual findings (can be empty) |
| `positive_observations` | array | YES | Good patterns found (can be empty) |
| `metadata` | object | YES | Execution metadata |

### Finding Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Unique ID: `<agent-name>-<NNN>` (zero-padded 3 digits) |
| `severity` | enum | YES | `P0` (critical), `P1` (high), `P2` (medium), `P3` (low) |
| `confidence` | int | YES | 0-100. Only include findings with confidence >= 75 |
| `category` | enum | YES | See Category Enum below |
| `subcategory` | string | NO | Free-text refinement of category |
| `title` | string | YES | One-line summary (max 80 chars) |
| `file` | string | YES | Relative file path from repo root |
| `line` | int | YES | Start line number |
| `line_end` | int | NO | End line number (if multi-line) |
| `code_snippet` | string | YES | Relevant code (max 5 lines) |
| `description` | string | YES | Detailed explanation |
| `suggestion` | string | YES | Concrete fix or recommendation |
| `claude_md_rule` | string | NO | Reference to CLAUDE.md rule if applicable |

### Category Enum

| Value | Used By |
|-------|---------|
| `security` | review-code, review-errors |
| `error-handling` | review-errors, review-code |
| `code-quality` | review-code, review-simplify |
| `test-quality` | review-tests |
| `type-design` | review-types |
| `comments` | review-comments |
| `simplification` | review-simplify |
| `performance` | review-code, review-simplify |
| `architecture` | review-code, review-types |
| `forbidden-pattern` | review-code, review-tests, review-comments |

### Verdict Rules

| Condition | Verdict |
|-----------|---------|
| Any P0 finding | `REQUEST_CHANGES` |
| P1 count > 3 | `REQUEST_CHANGES` |
| P1 count > 0 | `COMMENT` |
| No P0 or P1 | `APPROVE` |

### Severity Mapping

| Level | Name | Criteria | Action |
|-------|------|----------|--------|
| **P0** | Critical | Security vulnerability, data loss, correctness bug, empty catch block | Must block merge |
| **P1** | High | Logic error, SOLID violation, performance regression, mock violation, catch returning null | Should fix before merge |
| **P2** | Medium | Code smell, maintainability, deep nesting, optional chaining hiding errors | Fix or create follow-up |
| **P3** | Low | Style, naming, minor suggestion, informational type quality notes | Optional |

## Output Rules

1. Write the JSON to the file path provided in the task prompt
2. JSON MUST be valid - use `JSON.stringify` equivalent formatting
3. Only report findings with confidence >= 75
4. Do NOT output the JSON to the conversation - write it to the file only
5. After writing the file, output a one-line summary: `"Wrote N findings (P0:X P1:X P2:X P3:X) to <filepath>"`
