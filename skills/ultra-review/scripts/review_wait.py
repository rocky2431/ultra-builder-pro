#!/usr/bin/env python3
"""Review Wait - File-based completion waiter for /ultra-review pipeline.

Polls the session directory for expected review JSON files and/or SUMMARY.json.
Returns a one-line verdict on stdout. Blocks until complete or timeout.

Usage:
    python3 review_wait.py <session_path> agents <count>   # Wait for N review-*.json files
    python3 review_wait.py <session_path> summary           # Wait for SUMMARY.json only

Exit codes:
    0 - All expected files found
    1 - Timeout (default 5 minutes)
    2 - Invalid arguments
"""

import glob
import json
import sys
import time
from pathlib import Path

POLL_INTERVAL = 2  # seconds
DEFAULT_TIMEOUT = 300  # 5 minutes


def wait_for_agents(session_path: Path, expected_count: int, timeout: int) -> bool:
    """Wait for expected_count review-*.json files to appear."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        found = glob.glob(str(session_path / "review-*.json"))
        if len(found) >= expected_count:
            names = [Path(f).stem for f in sorted(found)]
            print(f"All {expected_count} agents complete: {', '.join(names)}")
            return True
        remaining = int(deadline - time.monotonic())
        print(
            f"\r  Waiting: {len(found)}/{expected_count} agents done "
            f"({remaining}s remaining)",
            end="", flush=True
        )
        time.sleep(POLL_INTERVAL)

    # Timeout — report what we have
    found = glob.glob(str(session_path / "review-*.json"))
    print(f"\nTimeout: {len(found)}/{expected_count} agents completed")
    return False


def wait_for_summary(session_path: Path, timeout: int) -> bool:
    """Wait for SUMMARY.json to appear."""
    summary_path = session_path / "SUMMARY.json"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if summary_path.exists() and summary_path.stat().st_size > 0:
            try:
                data = json.loads(summary_path.read_text(encoding="utf-8"))
                verdict = data.get("verdict", "UNKNOWN")
                p0 = data.get("p0", 0)
                p1 = data.get("p1", 0)
                total = data.get("total", 0)
                print(f"Review complete: {verdict} (P0:{p0} P1:{p1} total:{total})")
                return True
            except (json.JSONDecodeError, KeyError):
                pass  # File still being written
        remaining = int(deadline - time.monotonic())
        print(
            f"\r  Waiting for coordinator ({remaining}s remaining)",
            end="", flush=True
        )
        time.sleep(POLL_INTERVAL)

    print("\nTimeout: coordinator did not produce SUMMARY.json")
    return False


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    session_path = Path(sys.argv[1])
    mode = sys.argv[2]

    if not session_path.is_dir():
        print(f"Error: session directory not found: {session_path}", file=sys.stderr)
        sys.exit(2)

    timeout = DEFAULT_TIMEOUT

    if mode == "agents":
        if len(sys.argv) < 4:
            print("Error: agents mode requires <count> argument", file=sys.stderr)
            sys.exit(2)
        expected = int(sys.argv[3])
        ok = wait_for_agents(session_path, expected, timeout)
        sys.exit(0 if ok else 1)

    elif mode == "summary":
        ok = wait_for_summary(session_path, timeout)
        sys.exit(0 if ok else 1)

    else:
        print(f"Error: unknown mode '{mode}'. Use 'agents' or 'summary'.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
