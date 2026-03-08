#!/usr/bin/env python3
"""Verify Wait - File-based completion waiter for /ultra-verify pipeline.

Polls the session directory for expected AI output files (gemini-output.md, codex-output.md).
Blocks until all expected files appear or timeout. Returns structured JSON on stdout.

Usage:
    python3 verify_wait.py <session_path> [--timeout SECONDS]

Expected files (checks for non-empty):
    - gemini-output.md  OR  gemini-error.log (Gemini completed or failed)
    - codex-output.md   OR  codex-raw.txt    OR  codex-error.log (Codex completed or failed)

Exit codes:
    0 - All AIs completed (success or known failure)
    1 - Timeout with incomplete results
    2 - Invalid arguments
"""

import json
import sys
import time
from pathlib import Path

POLL_INTERVAL = 3  # seconds — external CLIs are slower than subagents
DEFAULT_TIMEOUT = 300  # 5 minutes


def check_gemini(session_path: Path) -> dict:
    """Check if Gemini has produced output or error."""
    output = session_path / "gemini-output.md"
    error = session_path / "gemini-error.log"

    if output.exists() and output.stat().st_size > 0:
        return {"name": "gemini", "status": "complete", "file": str(output)}

    # Check if error log indicates failure (non-empty error + no output)
    if error.exists() and error.stat().st_size > 0 and not output.exists():
        return {"name": "gemini", "status": "failed", "file": str(error)}

    # Output file exists but is empty — Gemini ran but produced nothing
    if output.exists() and output.stat().st_size == 0:
        return {"name": "gemini", "status": "empty", "file": str(output)}

    return {"name": "gemini", "status": "pending", "file": None}


def check_codex(session_path: Path) -> dict:
    """Check if Codex has produced output or error."""
    output = session_path / "codex-output.md"
    raw = session_path / "codex-raw.txt"
    error = session_path / "codex-error.log"

    if output.exists() and output.stat().st_size > 0:
        return {"name": "codex", "status": "complete", "file": str(output)}

    if raw.exists() and raw.stat().st_size > 0:
        return {"name": "codex", "status": "complete", "file": str(raw)}

    if error.exists() and error.stat().st_size > 0 and not output.exists() and not raw.exists():
        return {"name": "codex", "status": "failed", "file": str(error)}

    if output.exists() and output.stat().st_size == 0:
        return {"name": "codex", "status": "empty", "file": str(output)}

    return {"name": "codex", "status": "pending", "file": None}


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    session_path = Path(sys.argv[1])
    timeout = DEFAULT_TIMEOUT

    # Parse optional --timeout
    if "--timeout" in sys.argv:
        idx = sys.argv.index("--timeout")
        if idx + 1 < len(sys.argv):
            timeout = int(sys.argv[idx + 1])

    if not session_path.is_dir():
        print(f"Error: session directory not found: {session_path}", file=sys.stderr)
        sys.exit(2)

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        gemini = check_gemini(session_path)
        codex = check_codex(session_path)

        gemini_done = gemini["status"] != "pending"
        codex_done = codex["status"] != "pending"

        if gemini_done and codex_done:
            result = {
                "status": "complete",
                "gemini": gemini,
                "codex": codex,
                "elapsed_seconds": int(timeout - (deadline - time.monotonic())),
            }
            print(json.dumps(result))
            sys.exit(0)

        remaining = int(deadline - time.monotonic())
        done_count = sum([gemini_done, codex_done])
        parts = []
        if gemini_done:
            parts.append(f"gemini:{gemini['status']}")
        else:
            parts.append("gemini:waiting")
        if codex_done:
            parts.append(f"codex:{codex['status']}")
        else:
            parts.append("codex:waiting")

        sys.stderr.write(f"\r  [{done_count}/2] {' | '.join(parts)} ({remaining}s remaining)  ")
        sys.stderr.flush()
        time.sleep(POLL_INTERVAL)

    # Timeout — report what we have
    gemini = check_gemini(session_path)
    codex = check_codex(session_path)

    result = {
        "status": "timeout",
        "gemini": gemini,
        "codex": codex,
        "elapsed_seconds": timeout,
    }
    print(json.dumps(result))

    # Exit 0 if at least one completed, exit 1 if both still pending
    any_done = gemini["status"] != "pending" or codex["status"] != "pending"
    sys.exit(0 if any_done else 1)


if __name__ == "__main__":
    main()
