---
name: gemini-collab
description: "Invoke Gemini CLI as an independent sub-agent for code review, project analysis, architecture second opinions, and comparative verification. Use this skill whenever the user says 'ask Gemini', 'Gemini review', 'let Gemini check', 'second opinion', 'ask another AI', 'Gemini analysis', 'dual AI', or wants an independent AI perspective on code, architecture, or project understanding. Also trigger when the user mentions 'gemini' in any collaborative context."
user-invocable: true
---

# Gemini Collab - Dual AI Collaboration

Use Gemini CLI as an independent sub-agent within Claude Code. Claude orchestrates, Gemini provides independent analysis, Claude synthesizes the final result. All output goes through files — zero context pollution.

## Prerequisites

- Gemini CLI installed (`npm install -g @anthropic-ai/gemini-cli` or `brew install gemini`)
- Authenticated (`gemini` should work in terminal)
- Verify: `gemini --version`

## Usage

```
/gemini-collab review                # Gemini reviews current changes
/gemini-collab review <file>         # Gemini reviews specific file(s)
/gemini-collab understand            # Gemini analyzes project structure
/gemini-collab opinion <topic>       # Get Gemini's take on an architecture decision
/gemini-collab compare <topic>       # Both AIs answer independently, then synthesize
/gemini-collab free <prompt>         # Free-form prompt to Gemini
```

When the user doesn't use a subcommand but mentions Gemini in a collaborative way, infer the most appropriate mode from context.

## Core Principle

Gemini is an **independent thinker**, not an echo chamber. The value comes from getting a genuinely different perspective. When constructing prompts for Gemini:

- Provide raw context (code, files, requirements) without Claude's prior conclusions
- Never prime Gemini with "Claude thinks X, do you agree?" — that biases the response
- Let Gemini form its own opinion, then Claude synthesizes both perspectives

## File-Based Output (Zero Context Pollution)

All Gemini output MUST go through files, never directly into the conversation. This prevents context window pollution and avoids truncation from Bash tool output limits.

### Session Directory

```bash
# Create session directory
SESSION_ID="$(date +%Y%m%d-%H%M%S)-gemini-<mode>"
SESSION_PATH=".ultra/collab/${SESSION_ID}"
mkdir -p "${SESSION_PATH}"
```

### Output Files

Each session produces three files:

| File | Format | Content |
|------|--------|---------|
| `metadata.json` | JSON | Session metadata (agent, mode, model, scope, timestamp) |
| `output.md` | Markdown | Gemini's raw output (preserves formatting) |
| `synthesis.md` | Markdown | Claude's integrated report (final deliverable) |

**`metadata.json` schema:**
```json
{
  "id": "20260307-1100-gemini-review",
  "agent": "gemini",
  "mode": "review",
  "scope": "settings.json",
  "timestamp": "2026-03-07T11:00:00Z",
  "project_path": "/path/to/project"
}
```

### Output Flow

```
1. Gemini writes output → SESSION_PATH/output.md
2. Claude uses Read tool → reads output.md (no size limit)
3. Claude writes metadata.json (session info)
4. Claude synthesizes → writes synthesis.md + presents summary to user
```

**Why files, not Bash stdout:**
- Bash tool has implicit output size limits — large AI responses get truncated
- stderr/stdout mixing causes data loss (e.g., `2>/dev/null` can suppress useful content)
- File-based reading via Read tool has no truncation issues
- Results persist across sessions for reference

## How to Call Gemini

Always redirect output to a file, then read with the Read tool:

```bash
# Standard pattern: redirect to file
gemini -p "Your prompt here" --yolo -o text > "${SESSION_PATH}/output.md" 2>/dev/null

# Then read with Read tool (not cat/Bash):
# Read ${SESSION_PATH}/output.md

# With file context piped in
cat file.py | gemini -p "Review this code" --yolo -o text > "${SESSION_PATH}/output.md" 2>/dev/null

# With sandbox for safety (read-only)
gemini -p "Analyze this project" --yolo --sandbox -o text > "${SESSION_PATH}/output.md" 2>/dev/null
```

**Important patterns:**
- Always use `-o text` for clean parseable output
- Always redirect to file with `> file.txt`
- Always use `--yolo` to auto-approve tool usage in headless mode
- Use `2>/dev/null` to suppress stderr noise (safe because `-o text` ensures content goes to stdout)
- Use the Read tool to read output files — NEVER rely on Bash stdout for AI output
- Use `--sandbox` when Gemini should only read, never write
- Set Bash timeout to 300000ms for large analyses
- Keep prompts focused — one task per call yields better results

## Collaboration Modes

### 1. Code Review (`review`)

Gemini independently reviews code changes, then Claude merges findings.

**Steps:**
1. Create session directory
2. Gather the diff or file content to review
3. Send to Gemini, redirect output to file (see `references/prompts.md` for templates)
4. Read the output file with Read tool
5. Claude adds its own review perspective
6. Present a unified report highlighting:
   - **Consensus**: issues both AIs agree on (highest confidence)
   - **Gemini-only**: issues only Gemini spotted (worth investigating)
   - **Claude-only**: issues only Claude spotted
   - **Disagreements**: where the two AIs differ (discuss trade-offs)

**Example invocation:**
```bash
SESSION_PATH=".ultra/collab/$(date +%Y%m%d-%H%M%S)-gemini-review"
mkdir -p "${SESSION_PATH}"
git diff HEAD~1 | gemini -p "Review this diff. Focus on: bugs, security issues, performance problems, and code style. Be specific — cite line numbers and explain why each issue matters." --yolo -o text > "${SESSION_PATH}/output.md" 2>/dev/null
```

### 2. Project Understanding (`understand`)

Gemini independently analyzes the project, then Claude compares with its own understanding.

**Steps:**
1. Create session directory
2. Call Gemini with a project analysis prompt in sandbox mode
3. Read the output file
4. Claude also forms its own understanding
5. Synthesize both perspectives into a comprehensive project map

**Example invocation:**
```bash
SESSION_PATH=".ultra/collab/$(date +%Y%m%d-%H%M%S)-gemini-understand"
mkdir -p "${SESSION_PATH}"
gemini -p "Analyze this project. Describe: 1) Purpose and main functionality 2) Architecture and key patterns 3) Directory structure and module responsibilities 4) Key dependencies and why they're used 5) Entry points and data flow. Be thorough." --yolo --sandbox -o text > "${SESSION_PATH}/output.md" 2>/dev/null
```

### 3. Second Opinion (`opinion`)

For architecture decisions, design choices, or technical debates.

**Steps:**
1. Create session directory
2. Describe the decision context and constraints to Gemini — without revealing Claude's position
3. Read the output file
4. Claude presents both positions side by side
5. Highlight where they agree, disagree, and the trade-offs of each approach

### 4. Comparative Verification (`compare`)

Both AIs independently answer the same question, then Claude synthesizes.

**Steps:**
1. Create session directory
2. Claude answers independently FIRST (write answer BEFORE reading Gemini's)
3. Send the same question to Gemini, redirect to file
4. Read Gemini's output file
5. Compare both answers and present synthesis

### 5. Free-form (`free`)

Direct prompt passthrough for any ad-hoc collaboration need.

**Steps:**
1. Create session directory (or use `/tmp/` for ephemeral queries)
2. Pass the user's prompt to Gemini, redirect to file
3. Read and parse the response
4. Claude adds commentary, context, or follow-up as appropriate

## Output Format

Always present Gemini collaboration results in this structure:

```markdown
## Gemini Collab Report

**Mode**: [review/understand/opinion/compare/free]
**Scope**: [what was analyzed]
**Session**: [SESSION_PATH]

### Gemini's Analysis
[Summarized and organized Gemini output — not raw dump]

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

For simple `free` mode calls, skip the full report format — just present Gemini's response with Claude's commentary.

## Session Lifecycle

```
.ultra/collab/
  ├── 20260307-1100-gemini-review/
  │   ├── metadata.json
  │   ├── output.md
  │   └── synthesis.md
  ├── 20260307-1130-gemini-understand/
  │   ├── metadata.json
  │   ├── output.md
  │   └── synthesis.md
  └── 20260307-1200-codex-review/     # Codex sessions coexist
      ├── metadata.json
      ├── output.md
      └── synthesis.md
```

**Cleanup**: Sessions older than 7 days are safe to delete. Review sessions with unresolved findings should be kept longer.

## Error Handling

- If `gemini` command not found: tell the user to install it (`npm i -g @anthropic-ai/gemini-cli` or `brew install gemini`)
- If Gemini times out (>5min): check partial output in file, report what's available
- If output file is empty after execution: report the error, proceed with Claude-only analysis
- Never block the workflow on Gemini failure — Claude continues independently

## Tips for Best Results

- **Specific prompts beat vague ones**: "Review this function for null pointer risks" > "Review this code"
- **Scope appropriately**: Send relevant files, not the entire codebase
- **Use sandbox mode** (`--sandbox`) for analysis-only tasks to prevent accidental writes
- **Large projects**: Break analysis into module-by-module calls rather than one massive prompt
- **Always read with Read tool**: Never rely on Bash stdout for Gemini output — use files
