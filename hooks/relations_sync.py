#!/usr/bin/env python3
"""PostToolUse Hook - Relations Sync (v7.0)

When `.ultra/specs/*` or `.ultra/tasks/*` changes, derive
`.ultra/relations.json`: a bidirectional map of task ↔ spec ↔ code.

Maintains:
  - tasks      → spec sections (forward, from task.trace_to)
  - spec       → tasks (specs[anchor].referenced_by)
  - code path  → tasks (files[rel_path].tasks; sources: Target Files in
                 task context md + files_touched in progress.json)
  - advisories: dangling trace_to references

Sensor only — never blocks. Reverse code→task index lets PreToolUse hooks
inject "this file is owned by task X, AC: ..." when an agent edits source.

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

try:
    from wiki_generator import generate_wiki
except Exception:  # pragma: no cover — never block hook on import error
    def generate_wiki(_root: Path) -> bool:  # type: ignore[no-redef]
        return False


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


def parse_target_files(context_path: Path) -> list:
    """Extract file paths from a task context's '**Target Files**:' bullet list.

    Section ends at next markdown heading (##) or next bold key (**Foo**:).
    Paths are pulled from backtick-wrapped tokens on bullet lines.
    """
    if not context_path.exists():
        return []
    try:
        text = context_path.read_text(encoding="utf-8")
    except OSError:
        return []

    files: list = []
    in_section = False
    for raw in text.split("\n"):
        line = raw.strip()
        if re.match(r"^\*\*Target [Ff]iles\*\*\s*:?", line):
            in_section = True
            for m in re.finditer(r"`([^`]+)`", line):
                files.append(m.group(1))
            continue
        if not in_section:
            continue
        if line.startswith("##") or re.match(r"^\*\*[A-Z][^*]+\*\*\s*:?", line):
            break
        if line.startswith("- ") or line.startswith("* "):
            for m in re.finditer(r"`([^`]+)`", line):
                files.append(m.group(1))
    return files


def index_files_to_tasks(tasks_data: dict, root: Path) -> dict:
    """Build code→task reverse index.

    Sources:
      - Target Files in each task's context md (plan-stage intent)
      - files_touched in progress.json (actual edit footprint)

    Paths normalized to repo-relative form. Returns dict keyed by path.
    """
    files_index: dict = {}

    def add(rel_path: str, task_id: str, source: str) -> None:
        rel = (rel_path or "").strip().lstrip("./")
        if not rel:
            return
        entry = files_index.setdefault(rel, {"tasks": [], "from": []})
        if task_id not in entry["tasks"]:
            entry["tasks"].append(task_id)
        if source not in entry["from"]:
            entry["from"].append(source)

    for task in tasks_data.get("tasks", []) or []:
        tid = task.get("id")
        if tid is None or tid == "":
            continue
        tid = str(tid)

        ctx_rel = task.get("context_file", "")
        if ctx_rel:
            ctx_path = root / ".ultra" / "tasks" / ctx_rel
            for fp in parse_target_files(ctx_path):
                add(fp, tid, "target_files")

        progress_path = root / ".ultra" / "tasks" / "progress" / f"task-{tid}.json"
        if progress_path.exists():
            try:
                progress = json.loads(progress_path.read_text(encoding="utf-8"))
                for fp in progress.get("files_touched", []) or []:
                    add(fp, tid, "files_touched")
            except (json.JSONDecodeError, OSError):
                pass

    return files_index


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
    files_index = index_files_to_tasks(tasks_data, root)

    rel = {
        "version": 2,
        "last_synced": datetime.now(timezone.utc).isoformat(),
        "tasks": {},
        "specs": {anchor: {"file": meta["file"], "heading": meta["heading"], "referenced_by": []}
                  for anchor, meta in spec_anchors.items()},
        "files": files_index,
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

    # Phase 3: derive human-readable wiki views from the same source state.
    # Best-effort — never raises, never blocks. See hooks/wiki_generator.py.
    try:
        generate_wiki(root)
    except Exception:
        pass

    print(json.dumps({}))


if __name__ == "__main__":
    main()
