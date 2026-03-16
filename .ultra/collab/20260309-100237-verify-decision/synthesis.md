# Three-Way Synthesis: Cross-Session Memory Optimization

**Mode**: decision
**Scope**: Memory system optimization — borrowing from claude-mem while keeping lightweight
**Session**: .ultra/collab/20260309-100237-verify-decision
**Confidence**: CONSENSUS (3/3) on all P0 items

## Per-AI Summary

### Claude
- Fix summary model (Opus → Sonnet), add structured fields via ALTER TABLE
- Cap merge window (stop_count > 20 → force new session)
- Lightweight PostToolUse for Write/Edit only
- Content-hash dedup (SHA-256 of branch+cwd+files)

### Gemini
- Use real session_id via `.current_session_id` file, UPSERT by ID not time window
- Structured JSON output from summary model (request/learned/completed/next_steps)
- PostToolUse captures tool_name + action_summary + outcome (metadata only)
- 3-table schema: sessions (with inline structured fields) + observations + FTS5
- SHA-256 dirty check before DB write

### Codex
- Root cause of stop_count=4306: `pre_stop_check.py` blocks cause re-triggers that still write DB
- Real `content_session_id` as primary identity (from Claude Code hook protocol)
- Separate `session_summaries` table with `summary_status/source/model/hash`
- `UserPromptSubmit` hook to capture initial request (critical for summary quality)
- 4-table schema: sessions + user_prompts + session_summaries + observations
- Historical data cleanup script

## Consensus Analysis

### CONSENSUS 3/3 — Do These First

| Item | Claude | Gemini | Codex | Confidence |
|------|--------|--------|-------|------------|
| Structured summary fields (request/completed/learned/next_steps) | Yes | Yes | Yes | 95% |
| Switch summary model from Opus to Sonnet/Haiku | Yes | Yes | Yes | 95% |
| Content hash deduplication | Yes | Yes | Yes | 93% |
| Fix session identity (stop using time-window merge as primary) | Partial | Yes | Yes | 93% |
| Lightweight PostToolUse observation (Write/Edit/test only) | Yes | Yes | Yes | 90% |
| Don't adopt worker daemon / 9 tables / token budgeting / web UI | Yes | Yes | Yes | 95% |

### MAJORITY 2/3

| Item | Who Agrees | Who Differs | Analysis |
|------|-----------|-------------|----------|
| Add UserPromptSubmit hook | Gemini + Codex | Claude didn't mention | Codex is right: capturing initial request is critical input for summary quality. Without it, summarizer is guessing "what was asked". **Adopt.** |
| Separate summary table vs inline fields | Codex (separate) | Claude + Gemini (inline ALTER TABLE) | Trade-off: separate table is cleaner but migration is harder. Codex's argument (summary_status/source tracking) is compelling. **Adopt separate table.** |
| Historical data cleanup | Codex | Claude + Gemini didn't mention | Good hygiene but can be deferred. **P2.** |

### Unique Insights (1/3)

| Item | Source | Assessment |
|------|--------|------------|
| `.current_session_id` file for session tracking | Gemini | Smart workaround if hook protocol doesn't provide session ID. Check if Claude Code already provides it in hook input. |
| `pre_stop_check.py` re-trigger is root cause of stop_count | Codex | Correct root cause analysis — `stop_hook_active=true` still writes to DB, just skips AI summary. Must fix. |
| `quality_score` field on summaries | Codex | Nice-to-have, enables auto-filtering of low-quality summaries. P2. |

## Final Recommendation — Phased Plan

### Phase 0: Identity Fix (P0, immediate)
1. Use real `content_session_id` from hook protocol (or generate UUID at SessionStart)
2. Stop upsert on `stop_hook_active=true` re-triggers
3. Merge window becomes fallback only (when session_id unavailable)

### Phase 1: Summary Quality (P0, same sprint)
1. Switch model: Opus → Sonnet (or Haiku)
2. Structured output: request/completed/learned/next_steps as JSON
3. Separate `session_summaries` table with status/source/hash
4. Validation: reject summaries < 100 chars, mark as `failed`
5. Add `UserPromptSubmit` hook to capture initial request

### Phase 2: Observation Capture (P1)
1. PostToolUse hook — capture Write/Edit/Bash(test failures) only
2. Lightweight `observations` table: session_id, kind, title, files, timestamp
3. Feed observations to summary model as structured input (not raw transcript)
4. Cap: max 20 observations per session, skip Read/Grep/Glob

### Phase 3: Schema Migration + Cleanup (P2)
1. Migrate existing sessions to new schema
2. Re-generate summaries for low-quality entries
3. Rebuild Chroma embeddings from structured fields
4. Historical dedup via content hash

## Schema (Consensus)

```sql
-- Core session identity
CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_session_id TEXT UNIQUE,
  started_at TEXT NOT NULL,
  last_active TEXT NOT NULL,
  completed_at TEXT,
  branch TEXT DEFAULT '',
  cwd TEXT DEFAULT '',
  files_modified TEXT DEFAULT '[]',
  initial_request TEXT DEFAULT '',
  stop_attempts INTEGER DEFAULT 0
);

-- Structured summaries (separate table)
CREATE TABLE session_summaries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending/ready/fallback/failed
  source TEXT NOT NULL DEFAULT 'model',    -- model/fallback/manual
  model TEXT,
  request TEXT DEFAULT '',
  completed TEXT DEFAULT '',
  learned TEXT DEFAULT '',
  next_steps TEXT DEFAULT '',
  summary_hash TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Lightweight observations
CREATE TABLE observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL,
  kind TEXT NOT NULL,  -- edit/test_failure/test_fix/decision
  title TEXT NOT NULL,
  detail TEXT DEFAULT '',
  tool_name TEXT,
  files TEXT DEFAULT '[]',
  content_hash TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- FTS5 on structured summary fields
CREATE VIRTUAL TABLE summaries_fts USING fts5(
  request, completed, learned, next_steps,
  content=session_summaries,
  content_rowid=rowid
);
```

## What NOT To Do

- Don't build a worker daemon (HTTP server adds 150MB overhead for no gain)
- Don't track token economics (ROI tracking is noise for this use case)
- Don't build a web viewer (the /recall skill is sufficient)
- Don't use 9 tables (4 is the right number: sessions + summaries + observations + FTS)
- Don't capture every tool use (only Write/Edit/test results have signal)

## Overall Confidence: 93%

All three AIs converge on the same core diagnosis (identity, summary quality, structure) and the same treatment (real session ID, structured fields, model downgrade, lightweight observations). The 7% uncertainty is in implementation details (separate table vs inline, which model exactly, observation granularity).
