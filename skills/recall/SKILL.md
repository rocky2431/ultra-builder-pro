---
name: recall
description: Search and manage cross-session memory. Query past sessions by keyword, date, or recency. Save summaries and tags for future recall.
allowed-tools: Bash, Read
argument-hint: "<query> | --recent [N] | --date YYYY-MM-DD | --save 'summary' | --tags 'tag1,tag2' | --stats"
---

# Recall - Cross-Session Memory

## Overview

Query the session memory database to recall what happened in past sessions.
Memory is auto-captured by the Stop hook; this skill provides the retrieval interface.

**DB location**: `.ultra/memory/memory.db` (project-level)
**CLI tool**: `~/.claude/hooks/memory_db.py`

## Argument Parsing

Parse user input after `/recall`:

| Pattern | Action | Example |
|---------|--------|---------|
| `/recall <query>` | FTS5 keyword search | `/recall auth bug` |
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

## Execution

Run the appropriate command via Bash:

```bash
# Search
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
```

**Timeout**: 10000ms (should complete in < 200ms)

## Saving Summaries

When user uses `--save` without specifying a session ID:
1. First run `python3 ~/.claude/hooks/memory_db.py latest` to get the latest session ID
2. Then run `python3 ~/.claude/hooks/memory_db.py save-summary "ID" "summary"`

## Output Formatting

Present results in a clean table or list format. Keep output concise:
- For `--recent`: show compact list (ID, date, branch, file count, summary if exists)
- For search results: show matching sessions with highlighted relevance
- For `--save` / `--tags`: confirm the action with session ID

## Tips for the User

After presenting results, optionally suggest:
- "Use `/recall --save \"summary\"` to add a summary to the latest session"
- "Use `/recall keyword` to search for specific topics"
- Summaries improve future search relevance

## Error Handling

- If no results: inform user, suggest broader search terms
- If DB doesn't exist yet: inform user that memory starts recording after the next session stop
- Non-zero exit: show error message from stderr
