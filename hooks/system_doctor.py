#!/usr/bin/env python3
"""System Doctor - Deep audit for Ultra Builder Pro.

Automates the manual audits that catch silent degradation:
1. CLAUDE.md cross-references vs actual files
2. settings.json hook references
3. memory.db data quality
4. Chroma vs DB consistency
5. Summary coverage
6. Daemon error log
7. JSONL vs DB consistency

Usage: python3 hooks/system_doctor.py
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).parent
CLAUDE_DIR = HOOKS_DIR.parent
GIT_TIMEOUT = 3

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
WARN = "\033[33mWARN\033[0m"
INFO = "\033[36mINFO\033[0m"


def get_git_toplevel() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=GIT_TIMEOUT,
                           cwd=str(CLAUDE_DIR))
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def print_check(status: str, msg: str):
    print(f"  [{status}] {msg}")


# -- Check 1: CLAUDE.md cross-references --

def check_claude_md_refs():
    """Verify agent/skill/command names in CLAUDE.md exist on disk."""
    print("\n1. CLAUDE.md cross-references")
    claude_md = CLAUDE_DIR / "CLAUDE.md"
    if not claude_md.exists():
        print_check(FAIL, "CLAUDE.md not found")
        return 1

    content = claude_md.read_text(encoding="utf-8")
    issues = 0

    # Check agent references
    agent_names = set()
    agents_dir = CLAUDE_DIR / "agents"
    if agents_dir.exists():
        agent_names = {f.stem for f in agents_dir.glob("*.md")}

    # Find agent name references in CLAUDE.md
    for match in re.finditer(r'\b(code-reviewer|debugger|tdd-runner|review-\w+|smart-contract-\w+)\b', content):
        name = match.group(1)
        if name not in agent_names and name not in ("review-pipeline",):
            print_check(FAIL, f"References agent '{name}' but agents/{name}.md not found")
            issues += 1

    if issues == 0:
        print_check(PASS, f"All agent references valid ({len(agent_names)} agents on disk)")
    return issues


# -- Check 2: settings.json hook files --

def check_settings_hooks():
    """Verify all hook script files referenced in settings.json exist."""
    print("\n2. settings.json hook references")
    settings_path = CLAUDE_DIR / "settings.json"
    if not settings_path.exists():
        print_check(FAIL, "settings.json not found")
        return 1

    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    hooks = settings.get("hooks", {})
    issues = 0
    total = 0

    for event, entries in hooks.items():
        for entry in entries:
            for hook in entry.get("hooks", []):
                cmd = hook.get("command", "")
                for part in cmd.split():
                    if part.endswith(".py"):
                        total += 1
                        script = Path(os.path.expanduser(part))
                        if not script.exists():
                            print_check(FAIL, f"{event}: {script.name} not found")
                            issues += 1

    if issues == 0:
        print_check(PASS, f"All {total} hook scripts exist")
    return issues


# -- Check 3: memory.db data quality --

def check_memory_quality():
    """Audit memory.db for common data quality issues."""
    print("\n3. memory.db data quality")
    toplevel = get_git_toplevel()
    if not toplevel:
        print_check(INFO, "Not in git repo, skipping")
        return 0

    db_path = Path(toplevel) / ".ultra" / "memory" / "memory.db"
    if not db_path.exists():
        print_check(INFO, "memory.db not found (new project?)")
        return 0

    issues = 0
    conn = sqlite3.connect(str(db_path), timeout=2)
    conn.row_factory = sqlite3.Row

    # Empty branch sessions
    empty_branch = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE branch = '' OR branch IS NULL"
    ).fetchone()[0]
    if empty_branch > 0:
        print_check(WARN, f"{empty_branch} session(s) with empty branch")
        issues += 1
    else:
        print_check(PASS, "No empty-branch sessions")

    # Orphan observations (no parent session)
    orphan_obs = conn.execute(
        "SELECT COUNT(*) FROM observations WHERE session_id NOT IN (SELECT id FROM sessions)"
    ).fetchone()[0]
    if orphan_obs > 0:
        print_check(WARN, f"{orphan_obs} orphan observation(s)")
        issues += 1
    else:
        print_check(PASS, "No orphan observations")

    # Orphan summaries
    orphan_sum = conn.execute(
        "SELECT COUNT(*) FROM session_summaries WHERE session_id NOT IN (SELECT id FROM sessions)"
    ).fetchone()[0]
    if orphan_sum > 0:
        print_check(WARN, f"{orphan_sum} orphan summary(ies)")
        issues += 1
    else:
        print_check(PASS, "No orphan summaries")

    # FTS5 sync check
    db_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    fts_count = conn.execute("SELECT COUNT(*) FROM sessions_fts").fetchone()[0]
    if db_count != fts_count:
        print_check(WARN, f"FTS5 out of sync: sessions={db_count}, fts={fts_count}")
        issues += 1
    else:
        print_check(PASS, f"FTS5 in sync ({fts_count} entries)")

    conn.close()
    return issues


# -- Check 4: Summary coverage --

def check_summary_coverage():
    """Check structured summary coverage rate."""
    print("\n4. Summary coverage")
    toplevel = get_git_toplevel()
    if not toplevel:
        return 0

    db_path = Path(toplevel) / ".ultra" / "memory" / "memory.db"
    if not db_path.exists():
        return 0

    conn = sqlite3.connect(str(db_path), timeout=2)

    total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    v2 = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE content_session_id != '' AND content_session_id IS NOT NULL"
    ).fetchone()[0]
    structured = conn.execute(
        "SELECT COUNT(*) FROM session_summaries WHERE status = 'ready'"
    ).fetchone()[0]

    if v2 > 0:
        rate = structured * 100 // v2
        status = PASS if rate >= 60 else WARN
        print_check(status, f"Structured summaries: {structured}/{v2} v2 sessions ({rate}%)")
    else:
        print_check(INFO, "No v2 sessions yet")

    # Recent 7 days
    recent = conn.execute("SELECT COUNT(*) FROM sessions WHERE started_at > date('now', '-7 days')").fetchone()[0]
    recent_struct = conn.execute("""
        SELECT COUNT(*) FROM session_summaries ss
        JOIN sessions s ON ss.session_id = s.id
        WHERE s.started_at > date('now', '-7 days') AND ss.status = 'ready'
    """).fetchone()[0]

    if recent > 0:
        rate = recent_struct * 100 // recent
        status = PASS if rate >= 70 else WARN
        print_check(status, f"Last 7 days: {recent_struct}/{recent} ({rate}%)")

    conn.close()
    return 0


# -- Check 5: Chroma consistency --

def check_chroma():
    """Check Chroma entries vs DB sessions."""
    print("\n5. Chroma consistency")
    try:
        import chromadb
        toplevel = get_git_toplevel()
        if not toplevel:
            return 0

        chroma_dir = Path(toplevel) / ".ultra" / "memory" / "chroma"
        if not chroma_dir.exists():
            print_check(INFO, "Chroma directory not found")
            return 0

        client = chromadb.PersistentClient(path=str(chroma_dir))
        collection = client.get_or_create_collection("sessions")
        chroma_count = collection.count()

        db_path = Path(toplevel) / ".ultra" / "memory" / "memory.db"
        conn = sqlite3.connect(str(db_path), timeout=2)
        db_with_summary = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE summary != '' AND summary IS NOT NULL"
        ).fetchone()[0]
        conn.close()

        diff = abs(chroma_count - db_with_summary)
        if diff <= 2:
            print_check(PASS, f"Chroma={chroma_count}, DB with summary={db_with_summary}")
        else:
            print_check(WARN, f"Chroma={chroma_count}, DB with summary={db_with_summary} (gap={diff})")
            return 1
    except ImportError:
        print_check(INFO, "chromadb not installed, skipping")
    except Exception as e:
        print_check(WARN, f"Chroma check failed: {e}")
        return 1
    return 0


# -- Check 6: Daemon error log --

def check_daemon_log():
    """Check for recent daemon errors."""
    print("\n6. Daemon error log")
    toplevel = get_git_toplevel()
    paths = []
    if toplevel:
        paths.append(Path(toplevel) / ".ultra" / "memory" / "daemon-errors.log")
    paths.append(Path.home() / ".claude" / "memory" / "daemon-errors.log")

    for log_path in paths:
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8").strip()
            lines = content.split("\n") if content else []
            if len(lines) > 0:
                print_check(WARN, f"{len(lines)} daemon error(s) in {log_path.name}")
                for line in lines[-3:]:
                    print(f"    {line[:120]}")
                return 1
            else:
                print_check(PASS, "Daemon log exists but empty (no errors)")
                return 0

    print_check(PASS, "No daemon error log (no errors recorded)")
    return 0


# -- Check 7: Silent catch audit --

def check_silent_catches():
    """Scan hook files for silent exception handling."""
    print("\n7. Silent catch patterns in hooks")
    silent_pattern = re.compile(
        r'except\s*(?:\([^)]*\)|[\w.,\s]*)?\s*(?:as\s+\w+)?\s*:\s*\n\s+pass\s*$',
        re.MULTILINE
    )

    issues = 0
    for py_file in HOOKS_DIR.glob("*.py"):
        if py_file.name.startswith("_") or py_file.name == "system_doctor.py":
            continue
        content = py_file.read_text(encoding="utf-8")
        matches = list(silent_pattern.finditer(content))
        if matches:
            for m in matches:
                line_num = content[:m.start()].count('\n') + 1
                print_check(WARN, f"{py_file.name}:{line_num} — silent catch (except...pass)")
                issues += 1

    if issues == 0:
        print_check(PASS, "No silent catch patterns found")
    return issues


# -- Main --

def main():
    print("=" * 50)
    print("  Ultra Builder Pro — System Doctor")
    print("=" * 50)

    total_issues = 0
    total_issues += check_claude_md_refs()
    total_issues += check_settings_hooks()
    total_issues += check_memory_quality()
    total_issues += check_summary_coverage()
    total_issues += check_chroma()
    total_issues += check_daemon_log()
    total_issues += check_silent_catches()

    print("\n" + "=" * 50)
    if total_issues == 0:
        print(f"  Result: ALL CHECKS PASSED")
    else:
        print(f"  Result: {total_issues} issue(s) found")
    print("=" * 50)

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
