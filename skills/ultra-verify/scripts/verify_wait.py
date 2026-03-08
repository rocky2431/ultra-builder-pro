#!/usr/bin/env python3
"""Verify Wait - File-based completion waiter for /ultra-verify pipeline.

Polls the session directory for expected AI output files.
Blocks until both AIs produce output OR timeout. Returns structured JSON on stdout.

Two exit conditions only:
    1. Both AIs have output (non-empty + stable size) → exit 0, status="complete"
    2. Timeout → exit 0, status="timeout" (JSON status field tells the story)

Usage:
    python3 verify_wait.py <session_path> [--timeout SECONDS]

Exit codes:
    0 - Always (result expressed via JSON status field)
    2 - Invalid arguments (missing path, bad --timeout)
"""

import json
import sys
import time
from pathlib import Path

POLL_INTERVAL = 3  # seconds
DEFAULT_TIMEOUT = 1200  # 20 minutes — Codex can be very slow


def _file_size(path: Path) -> int:
    """Return file size in bytes, or -1 if not found."""
    try:
        return path.stat().st_size
    except (FileNotFoundError, OSError):
        return -1


def _is_output_ready(session_path: Path, name: str) -> dict:
    """Check if an AI has produced non-empty output.

    Returns (status, file) where status is "complete" or "pending".
    Error logs and empty files are NOT checked here — only at timeout.
    """
    if name == "gemini":
        output = session_path / "gemini-output.md"
        size = _file_size(output)
        if size > 0:
            return {"name": "gemini", "status": "complete", "file": str(output)}
        return {"name": "gemini", "status": "pending", "file": None}

    # codex: check both possible output files
    for filename in ("codex-output.md", "codex-raw.txt"):
        path = session_path / filename
        if _file_size(path) > 0:
            return {"name": "codex", "status": "complete", "file": str(path)}
    return {"name": "codex", "status": "pending", "file": None}


def _timeout_status(session_path: Path, name: str) -> dict:
    """Determine final status at timeout. Now check error logs and empty files."""
    if name == "gemini":
        output = session_path / "gemini-output.md"
        error = session_path / "gemini-error.log"
        if _file_size(output) > 0:
            return {"name": "gemini", "status": "complete", "file": str(output)}
        if _file_size(error) > 0:
            return {"name": "gemini", "status": "failed", "file": str(error)}
        if _file_size(output) == 0:
            return {"name": "gemini", "status": "empty", "file": str(output)}
        return {"name": "gemini", "status": "pending", "file": None}

    # codex
    for filename in ("codex-output.md", "codex-raw.txt"):
        path = session_path / filename
        if _file_size(path) > 0:
            return {"name": "codex", "status": "complete", "file": str(path)}
    error = session_path / "codex-error.log"
    if _file_size(error) > 0:
        return {"name": "codex", "status": "failed", "file": str(error)}
    for filename in ("codex-output.md", "codex-raw.txt"):
        if _file_size(session_path / filename) == 0:
            return {"name": "codex", "status": "empty", "file": str(session_path / filename)}
    return {"name": "codex", "status": "pending", "file": None}


def _is_stable(name: str, cur: dict, prev: dict) -> bool:
    """Check if output file size is unchanged between two consecutive polls.

    Shell redirect creates empty file immediately; tee writes incrementally.
    Stable = size > 0 and unchanged → writing finished.
    """
    if name == "gemini":
        return cur["gemini-output.md"] == prev["gemini-output.md"]
    # codex: both possible files must be stable
    return (cur["codex-output.md"] == prev["codex-output.md"]
            and cur["codex-raw.txt"] == prev["codex-raw.txt"])


OUTPUT_FILES = ("gemini-output.md", "codex-output.md", "codex-raw.txt")


def _get_sizes(session_path: Path) -> dict:
    return {name: _file_size(session_path / name) for name in OUTPUT_FILES}


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    session_path = Path(sys.argv[1])
    timeout = DEFAULT_TIMEOUT

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
    prev_sizes = _get_sizes(session_path)

    # Poll loop — exit condition 1: both outputs ready + stable
    while time.monotonic() < deadline:
        cur_sizes = _get_sizes(session_path)
        gemini = _is_output_ready(session_path, "gemini")
        codex = _is_output_ready(session_path, "codex")

        gemini_done = gemini["status"] == "complete" and _is_stable("gemini", cur_sizes, prev_sizes)
        codex_done = codex["status"] == "complete" and _is_stable("codex", cur_sizes, prev_sizes)

        if gemini_done and codex_done:
            elapsed = int(timeout - (deadline - time.monotonic()))
            print(json.dumps({"status": "complete", "gemini": gemini, "codex": codex, "elapsed_seconds": elapsed}))
            sys.exit(0)

        prev_sizes = cur_sizes

        # Progress display
        remaining = int(deadline - time.monotonic())
        parts = []
        for name, done, result in [("gemini", gemini_done, gemini), ("codex", codex_done, codex)]:
            if done:
                parts.append(f"{name}:complete")
            elif result["status"] == "complete":
                parts.append(f"{name}:stabilizing")
            else:
                parts.append(f"{name}:waiting")
        done_count = int(gemini_done) + int(codex_done)
        sys.stderr.write(f"\r  [{done_count}/2] {' | '.join(parts)} ({remaining}s remaining)  ")
        sys.stderr.flush()
        time.sleep(POLL_INTERVAL)

    # Exit condition 2: timeout — check error logs NOW for final status
    gemini = _timeout_status(session_path, "gemini")
    codex = _timeout_status(session_path, "codex")
    print(json.dumps({"status": "timeout", "gemini": gemini, "codex": codex, "elapsed_seconds": timeout}))
    sys.exit(0)


if __name__ == "__main__":
    main()
