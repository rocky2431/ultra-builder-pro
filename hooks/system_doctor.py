#!/usr/bin/env python3
"""System Doctor - Deep audit for Ultra Builder Pro.

Automates the manual audits that catch silent degradation:
1. CLAUDE.md cross-references vs actual files
2. settings.json hook references
3. Silent catch patterns in hooks

Memory归位 (2026-06-02): the self-built memory.db + Chroma were removed
(claude-mem now owns cross-session memory), so the former memory-quality,
summary-coverage, chroma-consistency, and daemon-log checks were dropped.

Usage: python3 hooks/system_doctor.py
"""

import json
import os
import re
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).parent
CLAUDE_DIR = HOOKS_DIR.parent

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
WARN = "\033[33mWARN\033[0m"
INFO = "\033[36mINFO\033[0m"


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
    for match in re.finditer(r'\b(code-reviewer|debugger|review-\w+|smart-contract-\w+)\b', content):
        name = match.group(1)
        if name not in agent_names and name not in ("review-pipeline", "review-graph"):
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


# -- Check 3: Silent catch audit --

def check_silent_catches():
    """Scan hook files for silent exception handling."""
    print("\n3. Silent catch patterns in hooks")
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
