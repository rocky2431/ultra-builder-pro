---
name: recall
description: Search and manage cross-session memory. Query past sessions by keyword, semantic similarity, or hybrid search. Save summaries and tags for future recall.
allowed-tools: Bash, Read
argument-hint: "<query> | --recent [N] | --date YYYY-MM-DD | --save 'summary' | --tags 'tag1,tag2' | --stats | --semantic <query> | --keyword <query>"
context: fork
---

# Recall - Cross-Session Memory (Forked Context)

## Overview

Query the session memory database to recall what happened in past sessions.
Memory is auto-captured by the Stop hook; this skill provides the retrieval interface.

**Runs in forked context**: intermediate search results do NOT pollute the main conversation.
Only the final refined summary is returned to the caller.

**DB location**: `.ultra/memory/memory.db` (project-level)
**CLI tool**: `~/.claude/hooks/memory_db.py`

## Search Modes

| Mode | Engine | Best For |
|------|--------|----------|
| **hybrid** (default) | FTS5 + Chroma RRF | General queries — combines keyword precision + semantic recall |
| **--semantic** | Chroma vectors only | Conceptual/fuzzy queries ("authentication flow", "deployment issues") |
| **--keyword** | FTS5 only | Exact matches (file names, branch names, specific terms) |

## Argument Parsing

Parse user input after `/recall`:

| Pattern | Action | Example |
|---------|--------|---------|
| `/recall <query>` | Hybrid search (FTS5 + semantic RRF) | `/recall auth bug` |
| `/recall --semantic <query>` | Pure semantic vector search | `/recall --semantic "login flow"` |
| `/recall --keyword <query>` | Pure FTS5 keyword search | `/recall --keyword session_journal` |
| `/recall --recent [N]` | Show last N sessions (default 5) | `/recall --recent 10` |
| `/recall --latest` | Show the most recent session in detail | `/recall --latest` |
| `/recall --date YYYY-MM-DD` | Sessions from specific date | `/recall --date 2026-02-15` |
| `/recall --save "summary"` | Save summary for latest session | `/recall --save "Fixed auth token refresh"` |
| `/recall --save ID "summary"` | Save summary for specific session | `/recall --save 20260215-193000 "Deployed v2"` |
| `/recall --tags "t1,t2"` | Add tags to latest session | `/recall --tags "auth,bugfix"` |
| `/recall --tags ID "t1,t2"` | Add tags to specific session | `/recall --tags 20260215-193000 "deploy"` |
| `/recall --stats` | Show database statistics | `/recall --stats` |
| `/recall --cleanup [N]` | Delete sessions older than N days | `/recall --cleanup 90` |
| `/recall` (no args) | Show last 5 sessions | `/recall` |

## Progressive Retrieval Strategy

When searching, follow this three-step approach:

1. **Initial search**: Run the appropriate search command
2. **Expand if sparse**: If <3 results, try expanding the query:
   - Add synonyms or related terms
   - Try a different search mode (semantic if keyword returned few, or vice versa)
   - Broaden the date range
3. **Synthesize**: Format the best results into a concise summary

## Execution

Run the appropriate command via Bash:

```bash
# Hybrid search (default — FTS5 + semantic RRF)
python3 ~/.claude/hooks/memory_db.py hybrid "query" --limit 10

# Semantic-only search
python3 ~/.claude/hooks/memory_db.py semantic "query" --limit 10

# Keyword-only search (FTS5)
python3 ~/.claude/hooks/memory_db.py search "query" --limit 10

# Recent sessions
python3 ~/.claude/hooks/memory_db.py recent 5

# Latest session (detailed)
python3 ~/.claude/hooks/memory_db.py latest

# Date filter
python3 ~/.claude/hooks/memory_db.py date 2026-02-15

# Save summary (use the session ID from latest or specify one)
python3 ~/.claude/hooks/memory_db.py save-summary "SESSION_ID" "summary text"

# Add tags
python3 ~/.claude/hooks/memory_db.py add-tags "SESSION_ID" "tag1,tag2"

# Stats
python3 ~/.claude/hooks/memory_db.py stats

# Cleanup old sessions
python3 ~/.claude/hooks/memory_db.py cleanup --days 90

# Reindex all sessions into Chroma (one-time backfill)
python3 ~/.claude/hooks/memory_db.py reindex-chroma
```

**Timeout**: 10000ms (should complete in < 500ms)

## Saving Summaries

When user uses `--save` without specifying a session ID:
1. First run `python3 ~/.claude/hooks/memory_db.py latest` to get the latest session ID
2. Then run `python3 ~/.claude/hooks/memory_db.py save-summary "ID" "summary"`

## Output Formatting

Present results in a clean, concise format. **Keep output under 500 tokens** — the forked context returns only the final summary.

- For `--recent`: compact list (ID, date, branch, file count, summary if exists)
- For search results: show matching sessions ranked by relevance
- For `--save` / `--tags`: confirm the action with session ID
- Always prefer quality over quantity — 3 highly relevant results beat 10 marginal ones

## Error Handling

- If no results: inform user, suggest broader search terms or different search mode
- If DB doesn't exist yet: inform user that memory starts recording after the next session stop
- If Chroma not available: fall back to keyword search automatically
- Non-zero exit: show error message from stderr
