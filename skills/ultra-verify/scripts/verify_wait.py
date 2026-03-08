#!/usr/bin/env python3
"""Verify Wait - File-based completion waiter for /ultra-verify pipeline.

Polls the session directory for expected AI output files (gemini-output.md, codex-output.md).
Blocks until all expected files appear or timeout. Returns structured JSON on stdout.

Usage:
    python3 verify_wait.py <session_path> [--timeout SECONDS]

Expected files (agents write atomically via Write tool):
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

POLL_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 300  # 5 minutes


def _file_size(path: Path) -> int:
    """Return file size in bytes, or -1 if file does not exist.

    Uses try/except to avoid TOCTOU race between exists() and stat().
    """
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return -1


def check_gemini(session_path: Path) -> dict:
    """Check if Gemini has produced output or error.

    Agents write files atomically via Write tool — if a file exists and is
    non-empty, the write is complete. No stability checking needed.
    """
    output = session_path / "gemini-output.md"
    error = session_path / "gemini-error.log"

    if _file_size(output) > 0:
        return {"name": "gemini", "status": "complete", "file": str(output)}

    if _file_size(error) > 0:
        return {"name": "gemini", "status": "failed", "file": str(error)}

    return {"name": "gemini", "status": "pending", "file": None}


def check_codex(session_path: Path) -> dict:
    """Check if Codex has produced output or error.

    Agents write files atomically via Write tool — if a file exists and is
    non-empty, the write is complete. No stability checking needed.
    """
    output = session_path / "codex-output.md"
    raw = session_path / "codex-raw.txt"
    error = session_path / "codex-error.log"

    for f in (output, raw):
        if _file_size(f) > 0:
            return {"name": "codex", "status": "complete", "file": str(f)}

    if _file_size(error) > 0:
        return {"name": "codex", "status": "failed", "file": str(error)}

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
        done_count = int(gemini_done) + int(codex_done)
        parts = [
            f"gemini:{gemini['status']}",
            f"codex:{codex['status']}",
        ]

        sys.stderr.write(f"\r  [{done_count}/2] {' | '.join(parts)} ({remaining}s remaining)  ")
        sys.stderr.flush()
        time.sleep(POLL_INTERVAL)

    # Timeout — final check
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
