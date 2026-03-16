Recommendation: **Option C now, Option B later if you can remove the nested-session constraint cleanly.**

If the goal is a production-worthy `ultra-verify` orchestration layer with low operational risk, **Option C is the best immediate architecture**. It gives you the main correctness property you actually need, which is **atomic completion visibility**, without introducing agent orchestration complexity or depending on a Codex-in-agent path that is already known to fail. **Option B is architecturally cleaner in principle**, but today it is incomplete because one of your three backends cannot participate under the same mechanism. That asymmetry matters.

**Why C wins right now**
- It fixes the real flaw in Option A: polling a file that is being incrementally written.
- It preserves the existing process model: CLI tools still run as ordinary subprocesses.
- `mv` on the same filesystem is atomic, so readers observe either `no final file` or `complete final file`.
- It removes the need for file-size stability heuristics, which are inherently probabilistic.
- It avoids coupling orchestration correctness to agent behavior, skill references, or nested-Claude restrictions.

## Option A: Bash + polling + stability check

**Assessment:** workable, but the weakest design.

**Pros**
- Simple mental model: launch process, redirect stdout, poll result files.
- No extra abstraction layer.
- Works with all tools uniformly as long as they can be invoked from shell.
- Handles streaming output naturally if you want partial progress visibility.

**Cons**
- Completion detection is heuristic, not definitive.
- File-size stability across two polls is not a correctness guarantee. It only means “probably done.”
- Poll interval creates a latency/correctness trade-off.
- Empty-file semantics are awkward and easy to get wrong.
- More edge cases: truncated output, delayed flushes, hung subprocesses, CLI tools that pause before final output, shell redirection creating zero-byte files immediately.

**Technical risks**
- False positive completion if a process stalls temporarily longer than one poll interval.
- False negative delay if process completed just after a poll.
- Distinguishing “no answer,” “still running,” and “tool crashed after opening file” is messy.
- Polling logic becomes the place where process semantics are reimplemented badly.

**When A is acceptable**
- Prototyping.
- Cases where partial output visibility is a feature and occasional ambiguity is tolerable.

## Option B: Agent-based with atomic Write

**Assessment:** best conceptual model, but currently not the best deployable model.

**Pros**
- Strong completion semantics if the agent only writes once after full capture.
- Cleaner poller: existence of final artifact becomes the completion signal.
- Less shell-specific behavior leaking into orchestration.
- Easier to centralize CLI invocation rules, prompt templates, retries, and normalization in per-model agents.
- Better separation of concerns:
  - orchestrator manages scheduling and aggregation
  - agent manages model-specific invocation
  - storage layer manages atomic publication

**Cons**
- Known blocker: Codex cannot run inside Claude Code agents because of `CLAUDECODE`.
- You lose symmetry if Gemini uses agent-based atomic write but Codex cannot.
- Agent execution adds another runtime layer with its own failure modes.
- “Capture then write” may increase memory usage for very large outputs.
- You trade shell/process complexity for tool/runtime complexity.

**Technical risks**
- If agent execution fails after the subprocess finishes but before `Write`, output is lost unless you add temp persistence.
- If different agents implement slightly different conventions, cross-model comparison becomes less deterministic.
- Debugging becomes harder because failure may be in:
  - CLI tool
  - agent runtime
  - tool permissions
  - write/publication step

**When B becomes best**
- If all three backends can be invoked under the same agent contract.
- If you want a long-term orchestration platform rather than a thin process runner.
- If you intend to add retries, structured metadata, normalization, and per-provider adapters.

## Option C: Hybrid temp file + rename

**Assessment:** best practical choice.

**Pros**
- Nearly all the correctness benefit of B for file completion semantics.
- Very small delta from A.
- Keeps compatibility with direct CLI invocation.
- Eliminates stability polling and most timeout ambiguity around partial writes.
- Easy to reason about operationally.
- Easy to debug with normal shell/process tools.

**Cons**
- Still shell/subprocess based, so you retain shell quoting and process-management issues.
- You do not get the abstraction benefits of dedicated agents.
- You need discipline to ensure every writer follows the temp-then-rename contract.
- Empty output still needs explicit semantics:
  - no final file yet = not complete
  - zero-byte final file = completed with empty output
  - missing final file at timeout = incomplete/failed unless exit metadata says otherwise

**Technical risks**
- Atomic rename is only atomic on the same filesystem. Temp and final file must be in the same directory or same mount.
- If the process crashes, temp files can accumulate and need cleanup.
- `mv` is only one part of correctness; you still need subprocess exit-code tracking.
- If stderr is not captured separately, failures can still be hard to diagnose.

**When C is ideal**
- You want the smallest change that materially improves correctness.
- You need something reliable now without redesigning around agents.
- One backend cannot participate in agent execution.

## Main trade-off

This is really a choice between **architectural cleanliness** and **deployable correctness under current constraints**.

- **A** optimizes for implementation immediacy but pays for it with heuristic completion detection.
- **B** optimizes for clean layering and long-term maintainability, but your current environment makes it only partially viable.
- **C** optimizes for correctness-per-unit-change. That is usually the right engineering call here.

## What I would do

Adopt **Option C as the production architecture now**, with two additions:

1. **Track process exit status separately from file presence**
   - Write `output.md` atomically.
   - Also write a small `output.status.json` atomically with:
     - `exit_code`
     - `start_time`
     - `end_time`
     - `timed_out`
     - `stderr_path`
   - Then completion is not just “file exists,” but “status exists and process is finished.”

2. **Define empty-output semantics explicitly**
   - `status exists, exit_code == 0, output.md size == 0` => successful empty response
   - `status exists, exit_code != 0` => failed run
   - neither exists by timeout => orchestration timeout
   - temp exists without status after timeout => interrupted/crashed writer

That gives you deterministic state transitions instead of overloading file size as state.

## Bottom line

- **Best immediate recommendation:** **Option C**
- **Best long-term architecture:** **Option B**, but only after the Codex nested-session constraint is removed or bypassed with a non-agent adapter
- **Option A:** keep only as a temporary baseline, not as the stable design

If you want, I can also sketch a concrete state machine for `ultra-verify` result handling (`pending`, `running`, `completed`, `empty`, `failed`, `timed_out`, `crashed`) and the exact file contract for each run.