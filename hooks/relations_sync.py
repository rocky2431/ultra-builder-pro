#!/usr/bin/env python3
"""PostToolUse Hook - Relations Sync (v7.0)

When `.ultra/specs/*` or `.ultra/tasks/tasks.json` changes, derive
`.ultra/relations.json`: an at-a-glance map of task ↔ spec section ↔ code.

Detects dangling references (task.trace_to → deleted/moved spec section) and
emits stderr advisory. Sensor only — never blocks.

PHILOSOPHY: enables C4 (Incremental Validation) for the `spec_trace` evidence
dimension, and supports Cognitive Coherence (specs/tasks/code/docs aligned).
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hook_utils import get_git_toplevel


def _slugify(heading: str) -> str:
    """Convert '## Foo Bar (Baz)' to 'foo-bar-baz' (GitHub-flavored anchor)."""
    cleaned = heading.lstrip("#").strip().lower()
    cleaned = re.sub(r"[^\w\s-]", "", cleaned)
    return re.sub(r"[\s_]+", "-", cleaned).strip("-")


def index_spec_anchors(specs_dir: Path) -> dict:
    """Walk .ultra/specs/*.md, index every heading as an anchor."""
    anchors: dict = {}
    if not specs_dir.exists():
        return anchors
    for md in sorted(specs_dir.glob("*.md")):
        try:
            content = md.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = f"specs/{md.name}"
        in_code_fence = False
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue
            if stripped.startswith("#"):
                anchor = _slugify(stripped)
                if anchor:
                    key = f"{rel}#{anchor}"
                    anchors.setdefault(key, {"file": str(md.relative_to(specs_dir.parent.parent)), "heading": stripped})
    return anchors


def normalize_ref(ref: str) -> str:
    """Normalize a trace_to value to 'specs/file.md#anchor' form."""
    ref = ref.strip().lstrip("./")
    if ref.startswith(".ultra/"):
        ref = ref[len(".ultra/"):]
    return ref


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({}))
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or ""

    relevant = (
        "/.ultra/specs/" in file_path
        or file_path.endswith("/.ultra/tasks/tasks.json")
        or "/.ultra/tasks/" in file_path
    )
    if not relevant:
        print(json.dumps({}))
        return

    toplevel = get_git_toplevel()
    if not toplevel:
        print(json.dumps({}))
        return
    root = Path(toplevel)

    tasks_path = root / ".ultra" / "tasks" / "tasks.json"
    if not tasks_path.exists():
        print(json.dumps({}))
        return

    try:
        tasks_data = json.loads(tasks_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(json.dumps({}))
        return

    spec_anchors = index_spec_anchors(root / ".ultra" / "specs")

    rel = {
        "version": 1,
        "last_synced": datetime.now(timezone.utc).isoformat(),
        "tasks": {},
        "specs": {anchor: {"file": meta["file"], "heading": meta["heading"], "referenced_by": []}
                  for anchor, meta in spec_anchors.items()},
        "advisories": [],
    }

    for task in tasks_data.get("tasks", []) or []:
        tid = task.get("id")
        if not tid:
            continue
        raw_trace = task.get("trace_to") or []
        if isinstance(raw_trace, str):
            raw_trace = [raw_trace]
        trace_to = [normalize_ref(r) for r in raw_trace]
        rel["tasks"][str(tid)] = {
            "title": task.get("title", ""),
            "status": task.get("status", ""),
            "trace_to": trace_to,
            "context_file": task.get("context_file", ""),
        }
        for ref in trace_to:
            if ref in rel["specs"]:
                rel["specs"][ref]["referenced_by"].append(str(tid))
            else:
                rel["advisories"].append({
                    "type": "dangling_trace_to",
                    "task": str(tid),
                    "ref": ref,
                })

    out_path = root / ".ultra" / "relations.json"
    try:
        out_path.write_text(
            json.dumps(rel, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError:
        pass

    if rel["advisories"]:
        for adv in rel["advisories"][:5]:
            print(
                f"[Relations] dangling trace_to in task {adv['task']}: '{adv['ref']}' — "
                f"spec section not found. Update task or restore section.",
                file=sys.stderr,
            )

    print(json.dumps({}))


if __name__ == "__main__":
    main()
