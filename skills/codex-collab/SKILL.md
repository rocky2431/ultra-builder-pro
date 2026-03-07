---
name: codex-collab
description: "Invoke OpenAI Codex CLI as an independent sub-agent for code review, project analysis, architecture second opinions, and comparative verification. Use this skill whenever the user says 'ask Codex', 'Codex review', 'let Codex check', 'OpenAI opinion', 'ask o3/o4', or wants an independent AI perspective from OpenAI's models. Also trigger when the user mentions 'codex' in any collaborative context."
user-invocable: true
---

# Codex Collab - Dual AI Collaboration (OpenAI)

Use OpenAI's Codex CLI as an independent sub-agent within Claude Code. Claude orchestrates, Codex provides independent analysis powered by OpenAI models (o3/o4-mini), Claude synthesizes the final result. All output goes through files — zero context pollution.

## Prerequisites

- Codex CLI installed (`npm install -g @openai/codex`)
- Authenticated (`codex login`)
- Verify: `codex --version`

## Usage

```
/codex-collab review                # Codex reviews current uncommitted changes
/codex-collab review <file>         # Codex reviews specific file(s)
/codex-collab review --base main    # Codex reviews changes against main branch
/codex-collab understand            # Codex analyzes project structure
/codex-collab opinion <topic>       # Get Codex's take on an architecture decision
/codex-collab compare <topic>       # Both AIs answer independently, then synthesize
/codex-collab free <prompt>         # Free-form prompt to Codex
```

When the user doesn't use a subcommand but mentions Codex in a collaborative way, infer the most appropriate mode from context.

## Core Principle

Codex is an **independent thinker**, not an echo chamber. The value comes from getting a genuinely different perspective — especially since Codex uses OpenAI models which may have different training biases, strengths, and reasoning patterns compared to Claude. When constructing prompts for Codex:

- Provide raw context (code, files, requirements) without Claude's prior conclusions
- Never prime Codex with "Claude thinks X, do you agree?" — that biases the response
- Let Codex form its own opinion, then Claude synthesizes both perspectives

## File-Based Output (Zero Context Pollution)

All Codex output MUST go through files, never directly into the conversation. This prevents context window pollution and avoids truncation from Bash tool output limits.

### Session Directory

```bash
# Create session directory
SESSION_ID="$(date +%Y%m%d-%H%M%S)-codex-<mode>"
SESSION_PATH=".ultra/collab/${SESSION_ID}"
mkdir -p "${SESSION_PATH}"
```

### Output Files

Each session produces three files:

| File | Format | Content |
|------|--------|---------|
| `metadata.json` | JSON | Session metadata (agent, mode, model, scope, timestamp) |
| `output.md` | Markdown | Codex's output (review findings or analysis, preserves formatting) |
| `synthesis.md` | Markdown | Claude's integrated report (final deliverable) |

For `codex review`, an additional `raw.txt` captures the full stdout+stderr (includes process logs).

**`metadata.json` schema:**
```json
{
  "id": "20260307-1100-codex-review",
  "agent": "codex",
  "mode": "review",
  "model": "gpt-5.4",
  "scope": "uncommitted changes",
  "timestamp": "2026-03-07T11:00:00Z",
  "project_path": "/path/to/project"
}
```

### Output Flow

```
1. Codex writes output → SESSION_PATH/output.md (or raw.txt for review)
2. Claude uses Read tool → reads file (no size limit)
3. Claude extracts review findings from raw output → writes output.md
4. Claude writes metadata.json (session info)
5. Claude synthesizes → writes synthesis.md + presents summary to user
```

**Why files, not Bash stdout:**
- Bash tool has implicit output size limits — large AI responses get truncated
- `codex review` mixes verbose process logs (MCP startup, shell commands) with actual review findings in stdout/stderr
- `2>/dev/null` can accidentally suppress useful content from Codex
- File-based reading via Read tool has no truncation issues
- Results persist across sessions for reference

## How to Call Codex

### 1. `codex review` — Built-in Code Review (preferred for review tasks)

`codex review` does NOT support the `-o` flag. Must capture via shell redirection:

```bash
SESSION_PATH=".ultra/collab/$(date +%Y%m%d-%H%M%S)-codex-review"
mkdir -p "${SESSION_PATH}"

# Capture ALL output (stdout + stderr) to raw file
codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/raw.txt"

# Then use Read tool to read the file
# The raw output contains process logs — extract the review from the end
# (typically after the last line starting with "codex", contains the actual findings)
# Save the extracted review as output.md
```

**Review scope options:**
```bash
codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/codex-raw.txt"
codex review --base main 2>&1 | tee "${SESSION_PATH}/codex-raw.txt"
codex review --commit abc123 2>&1 | tee "${SESSION_PATH}/codex-raw.txt"
codex review --uncommitted "Focus on security" 2>&1 | tee "${SESSION_PATH}/codex-raw.txt"
```

This is Codex's killer feature — a purpose-built review mode that understands git diffs natively. Always prefer this over `exec` for code review tasks.

**Extracting the review from raw output:**
The raw output contains MCP startup logs, shell exec logs, and the final review. The actual review findings are typically at the end, after the last line starting with `codex`. Read the file and extract from the review summary onward.

### 2. `codex exec` — General Non-Interactive Mode

`codex exec` supports `-o` for clean output capture:

```bash
SESSION_PATH=".ultra/collab/$(date +%Y%m%d-%H%M%S)-codex-exec"
mkdir -p "${SESSION_PATH}"

# -o writes ONLY the final message (clean, no process logs)
codex exec "Your prompt here" --full-auto -o "${SESSION_PATH}/codex-output.txt" 2>/dev/null

# Then use Read tool to read the file
```

**Important patterns:**
- Use `--full-auto` for auto-approval with workspace-write sandbox (safe default)
- Use `--sandbox read-only` when Codex should only analyze, never modify files
- Use `-o` to capture clean output (exec mode only)
- Set Bash timeout to 300000ms for large analyses
- Default model is typically o3-mini; use `-m o3` or `-m o4-mini` to override

## Collaboration Modes

### 1. Code Review (`review`)

Codex independently reviews code changes using its built-in review system, then Claude merges findings.

**Steps:**
1. Create session directory
2. Determine the review scope (uncommitted, branch diff, specific commit)
3. Call `codex review`, capture all output to file
4. Read the output file with Read tool, extract review findings
5. Claude adds its own review perspective
6. Present a unified report highlighting:
   - **Consensus**: issues both AIs agree on (highest confidence)
   - **Codex-only**: issues only Codex spotted (worth investigating)
   - **Claude-only**: issues only Claude spotted
   - **Disagreements**: where the two AIs differ (discuss trade-offs)

### 2. Project Understanding (`understand`)

Codex independently analyzes the project, then Claude compares with its own understanding.

**Steps:**
1. Create session directory
2. Call `codex exec` with `-o` in read-only sandbox
3. Read the output file
4. Claude also forms its own understanding
5. Synthesize both perspectives into a comprehensive project map

**Example:**
```bash
SESSION_PATH=".ultra/collab/$(date +%Y%m%d-%H%M%S)-codex-understand"
mkdir -p "${SESSION_PATH}"
codex exec "Analyze this project. Describe: 1) Purpose 2) Architecture patterns 3) Directory structure 4) Key dependencies 5) Entry points and data flow. Be thorough." --sandbox read-only --full-auto -o "${SESSION_PATH}/codex-output.txt" 2>/dev/null
```

### 3. Second Opinion (`opinion`)

For architecture decisions, design choices, or technical debates.

**Steps:**
1. Create session directory
2. Describe the decision context and constraints to Codex — without revealing Claude's position
3. Read the output file
4. Claude presents both positions side by side
5. Highlight where they agree, disagree, and the trade-offs of each approach

### 4. Comparative Verification (`compare`)

Both AIs independently answer the same question, then Claude synthesizes.

**Steps:**
1. Create session directory
2. Claude answers independently FIRST (write answer BEFORE reading Codex's)
3. Send the same question to Codex, output to file
4. Read Codex's output file
5. Compare both answers and present synthesis

This mode is especially valuable for debugging — OpenAI's o3 model has strong reasoning capabilities that may catch different classes of bugs.

### 5. Free-form (`free`)

Direct prompt passthrough for any ad-hoc collaboration need.

## Output Format

Always present Codex collaboration results in this structure:

```markdown
## Codex Collab Report

**Mode**: [review/understand/opinion/compare/free]
**Scope**: [what was analyzed]
**Model**: [which OpenAI model was used, if known]
**Session**: [SESSION_PATH]

### Codex's Analysis
[Summarized and organized Codex output — not raw dump]

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

For simple `free` mode calls, skip the full report format — just present Codex's response with Claude's commentary.

## Session Lifecycle

```
.ultra/collab/
  ├── 20260307-1100-codex-review/
  │   ├── metadata.json
  │   ├── raw.txt               # Full stdout+stderr (review mode only)
  │   ├── output.md             # Extracted review findings
  │   └── synthesis.md          # Claude's integrated report
  ├── 20260307-1130-codex-understand/
  │   ├── metadata.json
  │   ├── output.md
  │   └── synthesis.md
  └── 20260307-1200-gemini-review/  # Gemini sessions coexist
      ├── metadata.json
      ├── output.md
      └── synthesis.md
```

**Cleanup**: Sessions older than 7 days are safe to delete. Review sessions with unresolved findings should be kept longer.

## Error Handling

- If `codex` command not found: tell the user to install it (`npm install -g @openai/codex`)
- If authentication fails: tell the user to run `codex login`
- If Codex times out (>5min): check partial output in file, report what's available
- If output file is empty after execution: report the error, proceed with Claude-only analysis
- Never block the workflow on Codex failure — Claude continues independently

## Tips for Best Results

- **Use `codex review` for code review** — it's purpose-built and outperforms general `exec` for this task
- **Always use files**: `-o` for exec, `2>&1 | tee file` for review — never rely on Bash stdout
- **Read with Read tool**: Always use the Read tool to read output files, not cat/Bash
- **Scope appropriately**: Codex works best with focused context, not entire codebases at once
- **Use `--sandbox read-only`** for analysis-only tasks to prevent accidental writes
- **Model selection matters**: o3 is stronger for complex reasoning; o4-mini is faster for simpler tasks
