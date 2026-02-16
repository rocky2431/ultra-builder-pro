#!/usr/bin/env python3
"""Review Verdict Update - Update SUMMARY.json and index.json after P0 fixes.

Usage:
    python3 review_verdict_update.py <session_path> [new_verdict]

If new_verdict is omitted, recalculates from current P0/P1 counts in SUMMARY.json:
  - P0 > 0 → REQUEST_CHANGES (no change)
  - P1 > 3 → REQUEST_CHANGES (no change)
  - P1 > 0 → COMMENT
  - else → APPROVE

Exit codes:
    0 - Updated successfully
    1 - Error (file not found, parse error, etc.)
"""

import json
import sys
from pathlib import Path


def recalculate_verdict(data: dict) -> str:
    """Recalculate verdict from finding counts."""
    summary = data.get("summary", {})
    by_severity = summary.get("by_severity", {})
    p0 = by_severity.get("P0", 0)
    p1 = by_severity.get("P1", 0)

    if p0 > 0:
        return "REQUEST_CHANGES"
    if p1 > 3:
        return "REQUEST_CHANGES"
    if p1 > 0:
        return "COMMENT"
    return "APPROVE"


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    session_path = Path(sys.argv[1])
    forced_verdict = sys.argv[2] if len(sys.argv) >= 3 else None

    summary_file = session_path / "SUMMARY.json"
    if not summary_file.exists():
        print(f"Error: {summary_file} not found", file=sys.stderr)
        sys.exit(1)

    # Update SUMMARY.json
    try:
        data = json.loads(summary_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading SUMMARY.json: {e}", file=sys.stderr)
        sys.exit(1)

    old_verdict = data.get("verdict", "UNKNOWN")

    if forced_verdict:
        new_verdict = forced_verdict
    else:
        new_verdict = recalculate_verdict(data)

    if old_verdict == new_verdict:
        print(f"Verdict unchanged: {old_verdict}")
        sys.exit(0)

    data["verdict"] = new_verdict
    summary_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"SUMMARY.json: {old_verdict} → {new_verdict}")

    # Update index.json
    reviews_dir = session_path.parent
    index_file = reviews_dir / "index.json"
    session_id = session_path.name

    if index_file.exists():
        try:
            index_data = json.loads(index_file.read_text(encoding="utf-8"))
            for entry in index_data.get("sessions", []):
                if entry.get("id") == session_id:
                    entry["verdict"] = new_verdict
                    # Update P0/P1 counts from summary
                    by_sev = data.get("summary", {}).get("by_severity", {})
                    entry["p0"] = by_sev.get("P0", 0)
                    entry["p1"] = by_sev.get("P1", 0)
                    break
            index_file.write_text(json.dumps(index_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"index.json: updated session {session_id}")
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: failed to update index.json: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
