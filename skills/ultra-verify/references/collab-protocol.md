# AI Collaboration Protocol

Shared protocol for all AI collaboration skills (Gemini, Codex, cross-verify).

## Core Principles

1. **Independent Thinker**: The external AI is not an echo chamber. Value comes from genuinely different perspectives.
2. **No Priming**: Provide raw context (code, files, requirements) without Claude's prior conclusions. Never say "Claude thinks X, do you agree?"
3. **Claude Synthesizes**: Claude orchestrates the collaboration, reads external output, and produces the final synthesis.

## File-Based Output (Zero Context Pollution)

All external AI output MUST go through files, never directly into the conversation.

**Why files, not Bash stdout:**
- Bash tool has implicit output size limits — large AI responses get truncated
- stderr/stdout mixing causes data loss
- File-based reading via Read tool has no truncation issues
- Results persist across sessions for reference

### Session Directory

```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)-<agent>-<mode>"
SESSION_PATH=".ultra/collab/${SESSION_ID}"
mkdir -p "${SESSION_PATH}"
```

### Output Files

| File | Format | Content |
|------|--------|---------|
| `metadata.json` | JSON | Session metadata (agent, mode, model, scope, timestamp) |
| `output.md` | Markdown | External AI's raw output |
| `synthesis.md` | Markdown | Claude's integrated report (final deliverable) |

**`metadata.json` schema:**
```json
{
  "id": "20260307-1100-<agent>-<mode>",
  "agent": "<agent>",
  "mode": "<mode>",
  "model": "<model>",
  "scope": "<what was analyzed>",
  "timestamp": "2026-03-07T11:00:00Z",
  "project_path": "/path/to/project"
}
```

### Output Flow

```
1. External AI writes output → SESSION_PATH/output.md
2. Claude uses Read tool → reads output.md (no size limit)
3. Claude writes metadata.json (session info)
4. Claude synthesizes → writes synthesis.md + presents summary to user
```

## Synthesis Report Template

```markdown
## {AGENT} Collab Report

**Mode**: [review/understand/opinion/compare/free]
**Scope**: [what was analyzed]
**Session**: [SESSION_PATH]

### {AGENT}'s Analysis
[Summarized and organized output — not raw dump]

### Claude's Analysis
[Claude's independent perspective on the same topic]

### Synthesis
[Merged insights, highlighting consensus and divergence]

#### Consensus (High Confidence)
- [Points both AIs agree on]

#### Divergent Views
- [Where they differ, with trade-off analysis]

#### Action Items
- [Concrete next steps based on combined analysis]
```

For simple `free` mode calls, skip the full report format — just present the response with Claude's commentary.

## Session Lifecycle

```
.ultra/collab/
  ├── 20260307-1100-gemini-review/
  │   ├── metadata.json
  │   ├── output.md
  │   └── synthesis.md
  ├── 20260307-1130-codex-review/
  │   ├── metadata.json
  │   ├── output.md
  │   └── synthesis.md
  └── ...
```

**Cleanup**: Sessions older than 7 days are safe to delete. Sessions with unresolved findings should be kept longer.

**Important**: Ensure `.ultra/` is in the project's `.gitignore`. Audit outputs may contain sensitive vulnerability analyses that should not be committed to version control.

## Error Handling

- **Command not found**: Tell user to install the CLI tool
- **Timeout (>5min)**: Check partial output in file, report what's available
- **Empty output**: Report the error, proceed with Claude-only analysis
- **Never block**: Claude continues independently on any external AI failure
