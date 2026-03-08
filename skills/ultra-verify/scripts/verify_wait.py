#!/usr/bin/env python3
"""Verify Wait - File-based completion waiter for /ultra-verify pipeline.

Polls the session directory for expected AI output files (gemini-output.md, codex-output.md).
Blocks until all expected files appear or timeout. Returns structured JSON on stdout.

Usage:
    python3 verify_wait.py <session_path> [--timeout SECONDS]

Expected files (checks for non-empty + stable size):
    - gemini-output.md  (Gemini completed)
    - codex-output.md   OR  codex-raw.txt (Codex completed)

Error logs are ONLY checked at timeout — CLIs may write startup info to stderr
even on successful runs (e.g., Codex MCP initialization logs).

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
DEFAULT_TIMEOUT = 1200  # 20 minutes — Codex can be very slow

OUTPUT_FILES = ("gemini-output.md", "codex-output.md", "codex-raw.txt")


def _file_size(path: Path) -> int:
    """Return file size in bytes, or -1 if file does not exist.

    Uses try/except to avoid TOCTOU race between exists() and stat().
    """
    try:
        return path.stat().st_size
    except (FileNotFoundError, OSError):
        return -1


def get_output_sizes(session_path: Path) -> dict:
    """Get current sizes of all output files for stability checking.

    Shell redirect creates empty file immediately, then content streams in.
    A file is 'stable' when size > 0 and unchanged between consecutive polls.
    """
    return {name: _file_size(session_path / name) for name in OUTPUT_FILES}


def check_gemini(session_path: Path, at_timeout: bool = False) -> dict:
    """Check if Gemini has produced output.

    During polling: only check for positive completion (output exists + non-empty).
    At timeout: also check error logs and empty files for failure/empty status.
    Error logs are ignored during polling because CLIs may write startup info to stderr.
    """
    output = session_path / "gemini-output.md"
    error = session_path / "gemini-error.log"

    output_size = _file_size(output)

    if output_size > 0:
        return {"name": "gemini", "status": "complete", "file": str(output)}

    if at_timeout:
        error_size = _file_size(error)
        if error_size > 0:
            return {"name": "gemini", "status": "failed", "file": str(error)}
        if output_size == 0:
            return {"name": "gemini", "status": "empty", "file": str(output)}

    return {"name": "gemini", "status": "pending", "file": None}


def check_codex(session_path: Path, at_timeout: bool = False) -> dict:
    """Check if Codex has produced output.

    During polling: only check for positive completion (output exists + non-empty).
    At timeout: also check error logs and empty files for failure/empty status.
    Error logs are ignored during polling because Codex writes MCP startup info to stderr.
    """
    output = session_path / "codex-output.md"
    raw = session_path / "codex-raw.txt"
    error = session_path / "codex-error.log"

    output_size = _file_size(output)
    raw_size = _file_size(raw)

    if output_size > 0:
        return {"name": "codex", "status": "complete", "file": str(output)}

    if raw_size > 0:
        return {"name": "codex", "status": "complete", "file": str(raw)}

    if at_timeout:
        error_size = _file_size(error)
        if error_size > 0:
            return {"name": "codex", "status": "failed", "file": str(error)}
        if output_size == 0:
            return {"name": "codex", "status": "empty", "file": str(output)}
        if raw_size == 0:
            return {"name": "codex", "status": "empty", "file": str(raw)}

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
            try:
                timeout = int(sys.argv[idx + 1])
            except ValueError:
                print(f"Error: --timeout must be integer: {sys.argv[idx + 1]}", file=sys.stderr)
                sys.exit(2)

    if not session_path.is_dir():
        print(f"Error: session directory not found: {session_path}", file=sys.stderr)
        sys.exit(2)

    deadline = time.monotonic() + timeout

    # Track file sizes across polls for stability detection.
    # Shell redirect creates empty file immediately; content arrives later and may
    # stream incrementally (e.g., tee). A file is "stable" when its size > 0 and
    # unchanged between two consecutive polls, meaning the writing process has finished.
    prev_sizes = get_output_sizes(session_path)

    while time.monotonic() < deadline:
        cur_sizes = get_output_sizes(session_path)
        gemini = check_gemini(session_path)
        codex = check_codex(session_path)

        # "complete" requires file size stability (unchanged across consecutive polls)
        gemini_stable = (
            gemini["status"] == "complete"
            and cur_sizes["gemini-output.md"] == prev_sizes["gemini-output.md"]
        )
        codex_stable = (
            codex["status"] == "complete"
            and cur_sizes["codex-output.md"] == prev_sizes["codex-output.md"]
            and cur_sizes["codex-raw.txt"] == prev_sizes["codex-raw.txt"]
        )

        # During polling, only "complete+stable" counts as done.
        # Error logs are NOT checked during polling — only at timeout.
        gemini_done = gemini_stable
        codex_done = codex_stable

        if gemini_done and codex_done:
            result = {
                "status": "complete",
                "gemini": gemini,
                "codex": codex,
                "elapsed_seconds": int(timeout - (deadline - time.monotonic())),
            }
            print(json.dumps(result))
            sys.exit(0)

        prev_sizes = cur_sizes

        remaining = int(deadline - time.monotonic())
        done_count = int(gemini_done) + int(codex_done)
        parts = []
        if gemini_done:
            parts.append(f"gemini:{gemini['status']}")
        elif gemini["status"] == "complete":
            parts.append("gemini:stabilizing")
        else:
            parts.append("gemini:waiting")
        if codex_done:
            parts.append(f"codex:{codex['status']}")
        elif codex["status"] == "complete":
            parts.append("codex:stabilizing")
        else:
            parts.append("codex:waiting")

        sys.stderr.write(f"\r  [{done_count}/2] {' | '.join(parts)} ({remaining}s remaining)  ")
        sys.stderr.flush()
        time.sleep(POLL_INTERVAL)

    # Timeout — final check: NOW check error logs for failure detection
    gemini = check_gemini(session_path, at_timeout=True)
    codex = check_codex(session_path, at_timeout=True)

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
