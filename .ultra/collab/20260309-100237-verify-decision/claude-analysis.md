# Claude Analysis: Cross-Session Memory System Optimization

## Current System Assessment

### What Works Well
1. **Lightweight hooks** — Python scripts, <100ms per hook, no daemon overhead
2. **Simple schema** — 1 table (sessions) + FTS5 + Chroma, easy to understand
3. **Double-fork AI summary** — Non-blocking daemon, doesn't pollute /resume
4. **Head+Tail transcript sampling** — 4K head + 11K tail preserves both context and resolution
5. **30-min merge window** — Prevents duplicate sessions from multiple stops
6. **SessionStart injection** — Last session one-liner + branch memory (~200 tokens total)

### What Doesn't Work Well
1. **Summary quality inconsistent** — Range from 39 chars to 1633 chars. Some sessions get git commit fallback (39-66 chars) instead of AI summary
2. **stop_count anomalies** — Session `20260220-153712` has 4306 stops, `20260308-071826` has 107. Merge window not working for long-running sessions
3. **Duplicate records** — Two sessions with nearly identical summaries (005217 vs 001312)
4. **No observation capture** — Only captures session-level summary. No per-tool-use observations. If a session has 50 tool calls, we remember 1 summary
5. **Summary model too expensive** — Using Opus for summaries is overkill and slow. Haiku/Sonnet would produce adequate summaries faster
6. **No structured summary fields** — Summary is a free-text blob. Can't query "what was decided" vs "what was accomplished"

## Claude-Mem Analysis

### Worth Borrowing
1. **Structured summary schema** — `request/investigated/learned/completed/next_steps` fields instead of free text. Enables targeted queries like "what decisions were made?"
2. **PostToolUse observation capture** — Captures tool usage as observations with `type` classification (bugfix/feature/decision/discovery/change). Much richer than session-only
3. **Content hash deduplication** — SHA-256 slice within 30s window prevents duplicate observations
4. **Token budgeting** — Tracks `discovery_tokens` per observation, shows ROI in context header
5. **3-layer search skill** — Search (index) → Timeline (context) → Fetch (detail) minimizes token waste

### Too Heavy / Not Worth It
1. **Worker daemon on port 37777** — HTTP server for hook IPC adds 150-200MB overhead. Our direct Python approach is simpler
2. **9 tables + 20 indexes** — Over-normalized for the value. Sessions + observations + summaries is enough
3. **Multi-IDE support** — Cursor/OpenClaw transcript processor adds complexity we don't need (Claude Code only)
4. **Web viewer UI** — Nice but non-essential. Our `/recall` skill covers search needs
5. **SDK agent for summary generation** — Spawning a full Agent SDK process for summary is overkill

## Recommended Optimization Plan

### Priority 1: Fix Summary Quality (High Impact, Low Effort)

**Problem:** 8% of sessions have low-quality summaries (<100 chars). AI summary daemon sometimes fails silently.

**Solution:**
- Switch from Opus to Sonnet for summary generation (faster, cheaper, adequate quality)
- Add retry: if summary < 100 chars, retry once
- Add validation: structured format check before storing
- Log failures to stderr for diagnostics

### Priority 2: Add Structured Summary Fields (High Impact, Medium Effort)

**Problem:** Free-text summary can't be queried by category.

**Solution:** Add columns to sessions table:
```sql
ALTER TABLE sessions ADD COLUMN accomplished TEXT DEFAULT '';
ALTER TABLE sessions ADD COLUMN decisions TEXT DEFAULT '';
ALTER TABLE sessions ADD COLUMN issues TEXT DEFAULT '';
ALTER TABLE sessions ADD COLUMN unfinished TEXT DEFAULT '';
```

Parse AI summary (which already uses ## headers) into these fields. FTS5 indexes them separately. Query: "show me all decisions" → search `decisions` field only.

### Priority 3: Fix Merge Window for Long Sessions (Medium Impact, Low Effort)

**Problem:** stop_count of 4306 means merge window is merging everything into one mega-session.

**Solution:** Cap merge: if `stop_count > 20`, force new session regardless of time window. Long-running sessions that stop 4000+ times are clearly different logical sessions.

### Priority 4: Lightweight Observation Capture (Medium Impact, Medium Effort)

**Problem:** We only remember 1 summary per session. 50 tool calls → 1 memory point.

**Solution:** Add a PostToolUse hook that captures significant tool uses:
- Only capture Write/Edit (file modifications), not Read/Glob/Grep
- Store: `{session_id, tool_name, file_path, timestamp}`
- Table: `observations (id, session_id, tool_name, file_path, created_at)`
- Lightweight: no AI processing needed, just structured logging
- Skip capture if file is in `.ultra/` or `node_modules/`

### Priority 5: Content-Hash Deduplication (Low Impact, Low Effort)

**Problem:** Duplicate sessions with similar summaries.

**Solution:** Before inserting new session, compute SHA-256 of `branch + cwd + files[:5]`. If hash matches within merge window, always merge.

### NOT Recommended
- Worker daemon — complexity not justified for our use case
- Per-observation AI compression — too expensive, summary is enough
- Web viewer — `/recall` skill is sufficient
- Token budgeting — nice-to-have but not critical

## Confidence Assessment

| Recommendation | Confidence | Reasoning |
|---------------|------------|-----------|
| Fix summary model (Opus→Sonnet) | 95% | Opus is overkill for summaries. Sonnet is 10x faster, adequate quality |
| Structured summary fields | 90% | Claude-mem proves this works well. Migration is simple ALTER TABLE |
| Fix merge window cap | 95% | 4306 stops is clearly a bug. Simple cap fixes it |
| Lightweight observations | 85% | Value proven by claude-mem, but adds complexity. Start minimal |
| Content-hash dedup | 90% | Simple, proven pattern |
