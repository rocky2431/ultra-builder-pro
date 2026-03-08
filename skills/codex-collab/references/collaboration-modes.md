# Collaboration Modes

5 modes for dual-AI collaboration. Each mode follows the file-based output protocol defined in `collab-protocol.md`.

## 1. Code Review (`review`)

External AI independently reviews code changes, then Claude merges findings.

1. Create session directory
2. Gather the diff or file content to review
3. Send to external AI, redirect output to file
4. Read the output file with Read tool
5. Claude adds its own review perspective
6. Present unified report:
   - **Consensus**: issues both AIs agree on (highest confidence)
   - **{Agent}-only**: issues only the external AI spotted (worth investigating)
   - **Claude-only**: issues only Claude spotted
   - **Disagreements**: where the two AIs differ (discuss trade-offs)

## 2. Project Understanding (`understand`)

External AI independently analyzes the project, then Claude compares.

1. Create session directory
2. Call external AI with project analysis prompt (use sandbox/read-only mode)
3. Read the output file
4. Claude also forms its own understanding
5. Synthesize both perspectives into a comprehensive project map

## 3. Second Opinion (`opinion`)

For architecture decisions, design choices, or technical debates.

1. Create session directory
2. Describe the decision context and constraints — without revealing Claude's position
3. Read the output file
4. Claude presents both positions side by side
5. Highlight agreements, disagreements, and trade-offs

## 4. Comparative Verification (`compare`)

Both AIs independently answer the same question, then Claude synthesizes.

1. Create session directory
2. **Claude answers independently FIRST** (write answer BEFORE reading external AI's)
3. Send the same question to external AI, redirect to file
4. Read external AI's output file
5. Compare both answers and present synthesis

## 5. Free-form (`free`)

Direct prompt passthrough for any ad-hoc collaboration need.

1. Create session directory
2. Pass the user's prompt to external AI, redirect to file
3. Read and parse the response
4. Claude adds commentary, context, or follow-up as appropriate
