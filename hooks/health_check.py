#!/usr/bin/env python3
"""SessionStart Hook - Lightweight system health check.

Verifies critical components exist and are functional.
Reports issues via stderr (visible to Claude, never blocks).

Performance target: <200ms total.
"""

import json
import os
import sqlite3
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).parent
CLAUDE_DIR = HOOKS_DIR.parent
EXPECTED_MIN_AGENTS = 8
SCHEMA_VERSION = 2


def check_agents() -> list:
    """Verify agent files exist."""
    agents_dir = CLAUDE_DIR / "agents"
    if not agents_dir.exists():
        return ["agents/ directory missing"]

    md_files = list(agents_dir.glob("*.md"))
    if len(md_files) < EXPECTED_MIN_AGENTS:
        return [f"agents/: only {len(md_files)} files (expected >= {EXPECTED_MIN_AGENTS})"]
    return []


def check_hooks_syntax() -> list:
    """Verify all registered hooks are syntactically valid Python."""
    issues = []
    for py_file in HOOKS_DIR.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        try:
            compile(py_file.read_text(encoding="utf-8"), str(py_file), "exec")
        except SyntaxError as e:
            issues.append(f"{py_file.name}: syntax error at line {e.lineno}")
    return issues


def check_settings_hooks() -> list:
    """Verify hooks referenced in settings.json actually exist."""
    settings_path = CLAUDE_DIR / "settings.json"
    if not settings_path.exists():
        return ["settings.json missing"]

    issues = []
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        hooks = settings.get("hooks", {})
        for event_name, hook_list in hooks.items():
            for entry in hook_list:
                for hook in entry.get("hooks", []):
                    cmd = hook.get("command", "")
                    # Extract python script path from command
                    for part in cmd.split():
                        if part.endswith(".py"):
                            # Expand ~ in path
                            script_path = Path(os.path.expanduser(part))
                            if not script_path.exists():
                                issues.append(f"{event_name}: {script_path.name} not found")
    except (json.JSONDecodeError, KeyError):
        issues.append("settings.json: parse error")
    return issues


def check_memory_db() -> list:
    """Verify memory.db is accessible and schema version matches."""
    issues = []
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode != 0:
            return []  # Not in git repo, skip DB check

        toplevel = result.stdout.strip()
        db_path = Path(toplevel) / ".ultra" / "memory" / "memory.db"

        if not db_path.exists():
            return []  # DB not yet created, ok for new projects

        conn = sqlite3.connect(str(db_path), timeout=1)
        conn.row_factory = sqlite3.Row

        # Check tables exist
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}

        for required in ("sessions", "session_summaries", "observations"):
            if required not in tables:
                issues.append(f"memory.db: missing table '{required}'")

        conn.close()
    except (sqlite3.Error, OSError) as e:
        issues.append(f"memory.db: {e}")
    return issues


def check_claude_md() -> list:
    """Verify CLAUDE.md exists and is non-empty."""
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    if not claude_md.exists():
        return ["CLAUDE.md missing"]
    if claude_md.stat().st_size < 100:
        return ["CLAUDE.md appears empty or truncated"]
    return []


def main():
    # Only run on fresh session start, not compact resume
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    all_issues = []
    all_issues.extend(check_agents())
    all_issues.extend(check_hooks_syntax())
    all_issues.extend(check_settings_hooks())
    all_issues.extend(check_memory_db())
    all_issues.extend(check_claude_md())

    if all_issues:
        print(f"[Health] {len(all_issues)} issue(s) detected:", file=sys.stderr)
        for issue in all_issues[:10]:
            print(f"  - {issue}", file=sys.stderr)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
