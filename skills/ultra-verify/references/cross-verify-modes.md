# Ultra Verify Modes

4 modes for three-way AI verification. All modes follow the orchestration flow in `orchestration-flow.md`.

## 1. Decision (`decision`)

For architecture decisions, technology choices, or design trade-offs.

**Flow:**
1. Present the decision context, constraints, and options to all three AIs independently
2. Each AI provides: recommendation, pros/cons, risks, trade-offs
3. Synthesis ranks options by consensus:
   - 3/3 recommend same → **Strong recommendation**
   - 2/3 agree → **Recommended** with dissenting view analyzed
   - All different → Present all three with trade-off matrix

**Output structure:**
- Per-AI recommendation summary
- Consensus matrix (which AI recommends what)
- Trade-off analysis
- Final recommendation with confidence level

## 2. Diagnose (`diagnose`)

For bug diagnosis, root cause analysis, or troubleshooting.

**Flow:**
1. Provide symptoms, error messages, relevant code, and recent changes to all three AIs
2. Each AI provides its top-3 hypotheses with evidence and verification steps
3. Synthesis:
   - Hypotheses appearing in 3/3 lists → **Most likely** (investigate first)
   - Hypotheses in 2/3 lists → **Probable** (investigate second)
   - Unique hypotheses → **Worth checking** (may catch edge cases)

**Output structure:**
- Ranked hypothesis list (by consensus count)
- Per-hypothesis: description, evidence, verification steps, suggested fix
- Recommended investigation order

## 3. Audit (`audit`)

For code review, security audit, or quality assessment.

**Flow:**
1. Provide the code scope to all three AIs with the same audit prompt
2. Each AI reports findings with severity and location
3. Synthesis grades findings by consensus:
   - Found by 3/3 → **Critical** — fix immediately
   - Found by 2/3 → **High** — likely real, investigate
   - Found by 1/3 → **Investigate** — may be false positive or edge case

**Output structure:**
- Findings table: description, severity, consensus count, which AIs found it
- Grouped by consensus level (Critical → High → Investigate)
- Action items prioritized by consensus

## 4. Estimate (`estimate`)

For effort estimation, complexity assessment, or timeline planning.

**Flow:**
1. Describe the task, requirements, and constraints to all three AIs
2. Each AI provides: estimate (time/effort), breakdown, assumptions, risks
3. Synthesis evaluates convergence:
   - All within 20% of each other → **High confidence** estimate (use average)
   - One outlier → **Moderate confidence** — investigate the outlier's reasoning
   - All significantly different → **Low confidence** — task needs decomposition

**Output structure:**
- Per-AI estimate with breakdown and assumptions
- Convergence analysis
- Recommended estimate with confidence level
- Risk factors that could shift the estimate
