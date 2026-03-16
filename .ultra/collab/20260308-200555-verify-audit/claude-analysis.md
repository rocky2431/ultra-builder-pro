# Claude Audit: ultra-verify Skill Implementation

**Scope**: verify_wait.py logic, SKILL.md orchestration instructions, orchestration-flow.md, timeout design, error handling

---

## Findings

### [OK] verify_wait.py — Error Log Handling

**Logic**: Error logs are ONLY checked when `at_timeout=True` (L69, L99). During normal polling, only positive completion (output_size > 0) triggers "complete" status.

**Verdict**: Correct. This prevents the Codex MCP stderr false positive discovered in the previous session. CLIs that write startup info to stderr will not cause premature "failed" status.

### [OK] verify_wait.py — Stability Check

**Logic**: `get_output_sizes()` tracks file sizes across polls. A file is "done" only when `status == "complete"` AND `cur_sizes[file] == prev_sizes[file]` (L147-155).

**Verdict**: Correct. This handles the shell redirect race condition where `>` creates an empty file immediately, then content streams in. Two consecutive polls with same size > 0 = writing complete.

**Minor concern**: The stability check compares size only, not content hash. In theory, a file could have different content at the same size between polls. In practice, this is negligible for CLI output that grows monotonically.

### [OK] verify_wait.py — TOCTOU Safety

**Logic**: `_file_size()` uses try/except instead of exists() + stat() (L34-42). Returns -1 for missing files.

**Verdict**: Correct. Eliminates the race condition where a file could be deleted between exists() and stat().

### [ISSUE-P2] verify_wait.py — Timeout Mismatch Between Layers

**SKILL.md L94**: "Bash timeout MUST be set to `timeout: 600000` (10 min max for Bash tool — script handles its own timeout internally)"

**verify_wait.py L29**: `DEFAULT_TIMEOUT = 1200` (20 minutes)

**Problem**: Bash tool timeout (600000ms = 10 min) < script timeout (1200s = 20 min). The Bash tool will kill the script at 10 minutes, before the script's own 20-minute timeout fires. The script's internal timeout is effectively useless.

**Impact**: If both AIs take >10 min, the Bash tool kills verify_wait.py. The script never prints its JSON output. Claude gets a Bash timeout error instead of structured JSON, breaking the Step 3→4 handoff.

**Recommendation**: Either:
- (A) Accept 10 min max and set `--timeout 600` in SKILL.md (match Bash limit)
- (B) Document that the Bash tool 600000ms limit IS the effective timeout, and the script's --timeout is a secondary safeguard only useful if Bash tool timeout is increased in the future
- (C) Note: SKILL.md says "10 min max for Bash tool" but this may not be accurate — verify actual Bash tool timeout limit

### [ISSUE-P2] verify_wait.py — codex-raw.txt Stability Not Fully Isolated

**Logic** (L151-154):
```python
codex_stable = (
    codex["status"] == "complete"
    and cur_sizes["codex-output.md"] == prev_sizes["codex-output.md"]
    and cur_sizes["codex-raw.txt"] == prev_sizes["codex-raw.txt"]
)
```

**Problem**: When Codex produces `codex-output.md` (non-audit mode), the stability check ALSO requires `codex-raw.txt` to be stable. But `codex-raw.txt` doesn't exist in non-audit mode, so `_file_size()` returns -1 for both polls. -1 == -1 is True, so it doesn't block. This is correct but fragile — the logic depends on an implementation detail of `_file_size()` returning a consistent sentinel.

**Verdict**: Works correctly but could be more explicit. Low risk.

### [OK] SKILL.md — CRITICAL PROHIBITION Section

The four rules (L77-83) clearly prevent the premature synthesis bug. The "next message" constraint (rule 1) ensures verify_wait.py runs immediately.

### [OK] SKILL.md — Forbidden Codex Patterns

L75 correctly lists `codex -p`, `codex -q`, `codex --full-auto -s read-only` as forbidden. These are real CLI errors discovered during testing.

### [OK] orchestration-flow.md — Consistency with SKILL.md

- Both specify `--timeout 1200`
- Both specify `timeout: 600000` for Bash
- Both include CRITICAL PROHIBITION
- Both describe stability verification
- orchestration-flow.md adds HARD RULES section with 5 explicit constraints

### [ISSUE-P3] collab-protocol.md — Stale Timeout Reference

L112: "**Timeout (>5min)**: Check partial output in file, report what's available"

This references a 5-minute timeout, which is outdated (now 20 minutes). Low impact since this is a generic protocol file, not the verify-specific orchestration flow.

### [OK] cross-verify-modes.md — Complete Mode Coverage

All 4 modes (decision/diagnose/audit/estimate) have clear flow definitions, output structure specs, and consensus scoring criteria. No gaps.

### [OK] confidence-system.md — Degraded Confidence

Correctly specifies that 2/2 agree = Majority (not Consensus), and 1/1 = no consensus scoring. This matches the actual behavior in the previous session's synthesis.

### [ISSUE-P3] SKILL.md — audit Mode Codex Command is Blocking

L70-72: `codex review --uncommitted 2>&1 | tee "${SESSION_PATH}/codex-raw.txt"` — This is piped through `tee`, which means it blocks until codex review finishes. Since it's launched with `run_in_background: true`, the Bash tool runs it in a subprocess, so it does NOT block Claude. However, the `tee` pipe means the output file is written incrementally, which the stability check handles correctly.

**Verdict**: Works correctly. The stability check is essential for this pattern.

---

## Summary

| Finding | Severity | Status |
|---------|----------|--------|
| Error log only at timeout | OK | Correct |
| Stability check logic | OK | Correct |
| TOCTOU safety | OK | Correct |
| Bash timeout < script timeout | P2 | Needs clarification |
| codex-raw.txt stability coupling | P2 | Works but fragile |
| CRITICAL PROHIBITION rules | OK | Correct |
| Forbidden Codex patterns | OK | Correct |
| SKILL.md ↔ orchestration-flow.md consistency | OK | Consistent |
| collab-protocol.md stale timeout | P3 | Cosmetic |
| cross-verify-modes.md completeness | OK | Complete |
| confidence-system.md degraded rules | OK | Correct |
| audit mode tee + stability | OK | Correct |

**Overall**: The implementation is functionally correct after the error log fix. The main concern is the Bash tool timeout (10 min) being shorter than the script's timeout (20 min), which creates a dead zone where the script is killed without producing JSON output. This needs clarification on the actual Bash tool timeout limit.
