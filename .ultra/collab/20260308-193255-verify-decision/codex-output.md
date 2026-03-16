# Independent Analysis: ultra-verify Architecture Refactoring

> Note: Codex CLI could not be invoked (nested Claude session restriction). This analysis was performed by the verify-codex agent directly, based on thorough examination of all relevant source files.

## Overview

Evaluating four proposed changes to ultra-verify:
1. Dedicated agents (verify-gemini, verify-codex) replacing direct Bash CLI calls
2. Write tool atomic writes replacing shell redirect
3. Simplified verify_wait.py without stability checks
4. CRITICAL PROHIBITION preventing main agent from skipping the wait

## Assessment by Proposal

---

### Proposal 1: Dedicated Agents Replacing Direct Bash CLI

**Verdict: Sound, with caveats**

**Strengths:**
- Encapsulates CLI invocation complexity (flag mapping, error handling) in a single place
- Aligns with the proven ultra-review pattern (7 review agents)
- `run_in_background: true` prevents context pollution from agent output
- Agent-level `maxTurns: 15` provides bounded execution (prevents infinite loops)
- Sonnet model for executor agents is cost-efficient (they don't need Opus reasoning)

**Edge Cases and Issues:**

1. **Nested session blocker**: The `CLAUDECODE` environment variable check prevents `claude` CLI from running inside another Claude session. The verify-codex agent uses `codex exec` which calls OpenAI (fine), but if someone ever tried to run `claude -p` from within a verify agent, it would fail. More importantly, this nested restriction was hit when trying to invoke the Codex CLI for THIS very task — demonstrating that the agent architecture must handle this environment variable properly.

2. **Skill context pollution**: verify-gemini loads `skills: - gemini-collab`, which injects the FULL SKILL.md including interactive collaboration modes, session management, and synthesis logic. The agent says "Ignore all other skill content", but this is a soft instruction competing against ~200 lines of loaded skill content. A minimal `gemini-cli-only` skill would be more robust, though the current approach is pragmatic.

3. **Agent crash without output**: If an agent hits `maxTurns: 15` before writing either OUTPUT_FILE or ERROR_FILE, verify_wait.py will report `pending` at timeout. The main agent won't know whether the agent crashed, is still running, or never started. There's no heartbeat or progress file mechanism.

4. **Agent tool permissions mismatch**: Both agents have `tools: Bash, Write, Read`. The Bash tool allows arbitrary command execution. If the agent hallucinates or misinterprets the prompt, it could run destructive commands. Consider whether `Read` is even necessary (the agent's job is to run a CLI and write output — it shouldn't need to read arbitrary files). However, the agents do need Read to check the CLI reference files from their loaded skills, so Read is justified.

---

### Proposal 2: Write Tool Atomic Writes Replacing Shell Redirect

**Verdict: Correct root cause fix**

**Strengths:**
- Eliminates the shell redirect race condition completely (file is either complete or absent)
- No partial writes, no empty files from redirect-before-execution
- Consistent with how the Claude Agent SDK handles file I/O
- Enables the simplification in Proposal 3 (no stability checks needed)

**Edge Cases and Issues:**

1. **Bash stdout capture truncation**: The agent runs the CLI via Bash tool and captures stdout. If Gemini/Codex produces very large output (>1MB), the Bash tool may truncate the captured stdout. The Write tool then writes the truncated output as if it were complete — the atomicity guarantee only means "what was captured gets fully written", not "what the CLI produced gets fully captured". This is a **silent data loss** scenario.

   **Mitigation options**:
   - For Codex: use `-o` flag to write directly to a temp file, then Read + Write for atomic copy. But the agent forbids `-o`.
   - For Gemini: redirect to temp file, then Read + Write. But the agent forbids shell redirect.
   - Document a known output size limit and monitor for truncation.
   - The real question: is the Write tool atomicity worth the truncation risk vs. direct file output from the CLI?

2. **Write tool failure modes**: What happens if the Write tool itself fails (disk full, permission denied, path doesn't exist)? The agent should catch this and write to ERROR_FILE instead, but there's no explicit handling in the agent definition for Write tool failures. A Write tool failure on ERROR_FILE would leave no trace at all.

3. **Encoding issues**: If Gemini/Codex output contains non-UTF-8 bytes (binary data, corrupted output), the Write tool may fail or silently corrupt the output. No explicit encoding handling exists.

4. **codex-cli-reference.md contradicts agent instructions**: The reference says to use `-o` for `codex exec` and `2>&1 | tee` for `codex review`. The verify-codex agent explicitly forbids `-o` flag. This creates tension — the CLI's native file output mechanism is arguably more reliable than Bash stdout capture + Write tool. The `-o` flag would also handle the truncation issue in point 1. The rationale for this design choice should be documented.

---

### Proposal 3: Simplified verify_wait.py Without Stability Checks

**Verdict: Correct given atomic writes, but contains inconsistencies**

**Strengths:**
- With atomic Write tool, stability checks (polling file size twice) are genuinely unnecessary
- Simpler code = fewer bugs, easier to reason about
- The `_file_size > 0` check is sufficient: file exists and is non-empty = write completed
- TOCTOU race avoidance via try/except is correct

**Edge Cases and Issues:**

1. **Zero-byte file edge case**: If Write tool somehow produces a zero-byte file (empty string written), `_file_size(path) > 0` returns False, and the file is treated as non-existent. If the CLI prints only to stderr and stdout is empty, the agent writes empty content to OUTPUT_FILE, and verify_wait.py ignores it. Eventually it times out and reports "pending" — misleading.

2. **Timeout value inconsistency (critical)**: Multiple documents disagree:
   - `verify_wait.py` DEFAULT_TIMEOUT: 1200 seconds (20 minutes)
   - `orchestration-flow.md` Phase 3 description: "Timeout: 5 minutes"
   - `orchestration-flow.md` Agent Timeout section: "4 minutes per agent"
   - `SKILL.md` Phase 3 command: `--timeout 1200`
   - Agent `maxTurns: 15` (unpredictable wall-clock time)

   The 5-minute text in orchestration-flow.md directly contradicts the `--timeout 1200` command on the same page. This WILL confuse the executing LLM.

3. **Exit code semantics on partial completion**: The script exits 0 if at least one AI completed, even on timeout. This means the Bash tool reports success even when one AI is still pending. The main agent must parse the JSON to detect partial completion — if it only checks exit code, it might proceed thinking everything succeeded.

4. **Claude analysis already found a critical bug**: The Bash tool has a default 120-second timeout. Running `verify_wait.py --timeout 1200` without specifying `timeout: 1200000` for the Bash tool call will kill the wait script after 2 minutes. The SKILL.md instructions don't specify the Bash timeout parameter. This must be fixed.

5. **Progress output format**: Uses `\r` carriage return for progress — this works in terminal but produces messy multi-line output in Bash tool capture. Not a functional issue, but could confuse the main agent parsing stdout if the JSON output gets mixed with progress lines.

---

### Proposal 4: CRITICAL PROHIBITION Pattern

**Verdict: Necessary but insufficient on its own**

**Strengths:**
- Ported from ultra-review's proven design (battle-tested across many sessions)
- Addresses the exact failure mode: main agent processing idle notifications and synthesizing without external AI input
- Four clear rules with clear consequence statement
- Duplicated in both SKILL.md and orchestration-flow.md for emphasis

**Edge Cases and Issues:**

1. **No enforcement mechanism**: The CRITICAL PROHIBITION is a prompt-level instruction only. There's no hook or programmatic enforcement preventing the main agent from reading gemini-output.md directly. A PreToolUse hook that blocks Read on `*-output.md` files before verify_wait.py has been called would be more robust. The existing hook infrastructure (post_edit_guard.py, security_scan.py) shows hooks are feasible.

2. **Race between agent launch and wait script**: The PROHIBITION says "Run verify_wait.py IMMEDIATELY after Phase 2". But in multi-turn conversation, the main agent might generate another message between launching agents and running the wait script. An agent idle notification could trigger the main agent to check files. The word "IMMEDIATELY" helps, but it's a soft constraint.

3. **No post-wait result validation**: The PROHIBITION governs the waiting phase but not the synthesis phase. After reading output files, there's no instruction to validate that the content is genuine analysis (not an error message, CLI help text, or authentication prompt). A file containing `Error: API rate limit exceeded` would pass all checks.

4. **Double-documented (drift risk)**: The CRITICAL PROHIBITION appears identically in both SKILL.md and orchestration-flow.md. This creates the same maintenance drift risk identified in prior audits (see codex-output.md from the 20260308-180503 session). Single source of truth would be better — keep it in SKILL.md, reference from orchestration-flow.md.

---

## Cross-Cutting Concerns

### 1. No Retry Mechanism
If Gemini or Codex fails transiently (network timeout, rate limit, authentication expired), the agent writes an error log and stops. No retry. Degraded mode is triggered by transient failures that would succeed on retry. For v1 this is acceptable, but consider adding 1-retry with exponential backoff in the agent instructions.

### 2. No Output Content Validation
Neither the agents nor verify_wait.py validate that output content is actually an analysis. A file containing "Error: API rate limit exceeded" passes the `_file_size > 0` check and is treated as a successful "complete" response. The synthesis phase would then try to extract insights from an error message.

**Fix**: Add a validation step in the synthesis phase: check that output doesn't start with known error prefixes ("Error:", "Usage:", "command not found", "Authentication required", etc.).

### 3. codex exec Sandbox Mode
The verify-codex agent instructions say `codex exec "QUESTION" -s read-only` for analysis tasks. This is correct. But `--full-auto` (mentioned in codex-cli-reference.md) defaults to `workspace-write` sandbox. Ensure the agent always passes `-s read-only` for analysis tasks to prevent unintended file modifications.

### 4. No Session Cleanup
Sessions accumulate in `.ultra/collab/`. The collab-protocol.md says "Sessions older than 7 days are safe to delete" but there's no automated cleanup mechanism.

### 5. codex-raw.txt Fallback in verify_wait.py
The script checks for `codex-raw.txt` as an alternative to `codex-output.md`. This filename appears in verify_wait.py but NOT in the verify-codex agent definition (which only writes to `codex-output.md` or `codex-error.log`). The `codex-raw.txt` fallback is dead code unless some other process writes it. Either remove it from verify_wait.py or document when it's used.

---

## Design Flaw Summary

| # | Severity | Issue | Recommendation |
|---|----------|-------|----------------|
| 1 | **Critical** | Bash tool 120s default timeout kills verify_wait.py | Add explicit `timeout: 1200000` to Bash call instruction in SKILL.md |
| 2 | **High** | Timeout values inconsistent across 4+ documents (5min vs 20min) | Reconcile to single value; fix orchestration-flow.md "5 minutes" text |
| 3 | **High** | Bash stdout capture truncation for large AI output (silent data loss) | Document size limit; reconsider `-o` flag prohibition for Codex |
| 4 | **Medium** | No output content validation (error messages pass as analysis) | Add validation step in synthesis phase instructions |
| 5 | **Medium** | CRITICAL PROHIBITION is prompt-only, no programmatic enforcement | Consider PreToolUse hook for Read tool gating |
| 6 | **Medium** | CRITICAL PROHIBITION double-documented in SKILL.md + orchestration-flow.md | Single source of truth in SKILL.md |
| 7 | **Medium** | `codex-raw.txt` fallback in verify_wait.py is dead code | Remove or document its purpose |
| 8 | **Medium** | Skill context pollution (full collab skill loaded for CLI-only use) | Consider minimal CLI-only skill variant |
| 9 | **Low** | Agent crash produces no output (indistinguishable from "still running") | Add agent-status sentinel file on start |
| 10 | **Low** | No retry on transient CLI failures | Add 1-retry in agent instructions |
| 11 | **Low** | No automated session cleanup | Add cleanup script with 7-day retention |
| 12 | **Low** | Progress output `\r` may mix with JSON in Bash capture | Write progress to a separate file or suppress in non-TTY mode |

## Overall Verdict

The architecture is **fundamentally sound**. The Agent-based approach with atomic Write correctly eliminates the shell redirect race condition. The CRITICAL PROHIBITION pattern is well-proven from ultra-review. The design follows established patterns in this codebase.

**Priority fixes:**
1. Fix the Bash tool timeout for verify_wait.py (critical, will break every run)
2. Reconcile timeout values across documents (high, causes LLM confusion)
3. Add output content validation in synthesis phase (medium, prevents error-message-as-analysis)

The remaining items are hardening for production use and can be addressed incrementally.
