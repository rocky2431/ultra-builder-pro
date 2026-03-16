As an AI architect evaluating this CLI orchestration design, I recommend **Option C (Hybrid - temp file + rename)**. It provides the technical robustness of atomic operations without the environment-specific blockers that currently plague Option B.

### Recommendation: Option C (Hybrid)
Option C is the most "production-grade" engineering choice. It leverages POSIX atomicity (`rename`) to solve the synchronization problem at the filesystem level, which is inherently more reliable than heuristic polling (Option A) or agent-wrapped writes (Option B).

---

### Detailed Analysis

#### Option A: Current (Bash + Polling + Stability Check)
*   **Pros:** Requires no changes to how the CLI tools are invoked; works with standard Unix streams.
*   **Cons:** 
    *   **Race Conditions:** "Stability check" is a heuristic, not a guarantee. A network hiccup or disk I/O lag can cause the file size to stay "stable" for 3 seconds while the process is still alive.
    *   **Latency:** Forced wait times (2 consecutive polls) add unnecessary overhead (minimum 6s delay).
    *   **Complexity:** 190 lines of Python for a simple "is it done?" check indicates high technical debt and maintenance burden.

#### Option B: Proposed (Agent-based with Atomic Write)
*   **Pros:** Shifts the responsibility of "completion" to the agent; provides a clean API for file creation.
*   **Cons:**
    *   **Hard Blocker:** The `CLAUDECODE` environment variable restriction is a critical failure point. If Codex cannot run in a nested session, this architecture effectively breaks the "three-way" requirement.
    *   **Overhead:** Spawning full agents just to capture stdout and call a Write tool is resource-heavy compared to shell redirection.

#### Option C: Hybrid (temp file + rename)
*   **Pros:**
    *   **Atomic State:** In POSIX, `mv` (rename) is atomic on the same filesystem. The poller sees the file only when the source process has finished and closed the stream.
    *   **Simplicity:** Reduces polling logic to a binary check (`os.path.exists`). No need for "stability" logic or delta calculations.
    *   **Environment Agnostic:** It bypasses the `CLAUDECODE` restriction because it relies on standard shell behavior, not nested agent sessions.
    *   **Minimal Refactor:** You keep the high-performance Bash redirects but fix the synchronization flaw.
*   **Cons:**
    *   **Cleanup:** Requires ensuring `.tmp` files are cleaned up if the command is interrupted (e.g., `trap` or a startup cleanup script).

---

### Risks & Trade-offs

| Risk | Option A | Option B | Option C |
| :--- | :--- | :--- | :--- |
| **Partial Reads** | High (Read while writing) | Low (Atomic) | Zero (Atomic rename) |
| **Process Hangs** | Poller waits forever | Agent might timeout | Poller needs timeout logic |
| **Nested Blocks** | None | **Critical (Codex)** | None |
| **Logic Complexity** | High (~190 lines) | Medium (~130 lines) | Low (~50-80 lines) |

**The "Empty File" Edge Case:**
In Option C, if a CLI tool succeeds but produces no output, `> output.tmp && mv output.tmp output.md` will still result in an empty `output.md` appearing. The poller can immediately distinguish "Still Running" (no file) from "Finished with Empty Output" (file exists, size 0).

---

### Technical Specification for Option C
To implement this effectively, the shell command should be structured as:
```bash
(gemini -p '...' > output.md.tmp && mv output.md.tmp output.md) || touch output.md.err
```
**The Poller (`verify_wait.py`) should then follow this logic:**
1.  **Initialize:** Set a global timeout (e.g., 60s).
2.  **Poll (every 1s):**
    *   If `output.md` exists: Mark as **SUCCESS**.
    *   If `output.md.err` exists: Mark as **FAILED**.
3.  **Timeout:** If neither exists after 60s, terminate and mark as **TIMEOUT/PENDING**.

This approach provides a deterministic state machine for the three-way verification without the brittleness of the current implementation.
