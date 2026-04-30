#!/usr/bin/env python3
"""Stop Hook - Session Trail (Phase 2 of dynamic project KB).

Folds structured session facts into the active task's context md as a
'## Session Trail' entry. Pure structural fold — no LLM call.

Trail entry per session contains:
  - timestamp + session_id (8-char prefix)
  - files_touched count + sample basenames
  - advisories count
  - evidence_score summary (n/total dims ≥80)

Idempotent: same session_id replaces its own latest line, so multiple Stop
fires within one session don't bloat the trail.

Sensor only — best-effort, never raises. If no active task, no progress
file, or context md missing → no-op.

PHILOSOPHY (C5 Cognitive Coherence): the task's context becomes the
compounding artifact that survives session boundaries; future sessions
see what every prior session contributed without rereading transcripts.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
try:
    from hook_utils import (
        get_git_toplevel,
        get_active_task,
        EVIDENCE_DIMENSIONS,
    )
except Exception:  # pragma: no cover — never block hook on import error
    def get_git_toplevel() -> str:  # type: ignore[no-redef]
        return ""
    def get_active_task() -> dict | None:  # type: ignore[no-redef]
        return None
    EVIDENCE_DIMENSIONS = ()  # type: ignore[no-redef]


MAX_TRAIL_ENTRIES = 50
TRAIL_HEADING = "## Session Trail"


def build_trail_line(session_id: str, progress: dict) -> str:
    """One bullet line summarizing a session's contribution to the task."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    sid_tag = f" [sid:{session_id[:8]}]" if session_id else ""

    files = progress.get("files_touched") or []
    n_files = len(files)
    sample = ", ".join(Path(f).name for f in files[:3])
    if n_files > 3:
        sample += f", +{n_files - 3}"
    files_part = f"{n_files} files"
    if sample:
        files_part += f" ({sample})"

    adv = progress.get("advisories") or []
    n_adv = len(adv)

    scores = progress.get("evidence_score") or {}
    if EVIDENCE_DIMENSIONS:
        high = sum(1 for d in EVIDENCE_DIMENSIONS if scores.get(d, 0) >= 80)
        ev_part = f"evidence {high}/{len(EVIDENCE_DIMENSIONS)} ≥80"
    else:
        ev_part = ""

    parts = [f"- {ts}{sid_tag}", files_part, f"{n_adv} advisories"]
    if ev_part:
        parts.append(ev_part)
    return "; ".join(parts)


def fold_into_context(text: str, new_line: str, session_id: str) -> str:
    """Insert/replace the new_line in the ## Session Trail section.

    - If section missing: insert before ## Completion if present, else append.
    - If section present: if newest bullet matches session_id, replace it
      (idempotent rerun within same session); otherwise prepend the new line.
    - Cap at MAX_TRAIL_ENTRIES.
    """
    lines = text.split("\n")
    heading_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == TRAIL_HEADING:
            heading_idx = i
            break

    if heading_idx == -1:
        completion_idx = next(
            (i for i, l in enumerate(lines) if l.strip() == "## Completion"),
            -1,
        )
        insert_at = completion_idx if completion_idx >= 0 else len(lines)
        new_block = ["", TRAIL_HEADING, "", new_line, ""]
        return "\n".join(lines[:insert_at] + new_block + lines[insert_at:])

    body_start = heading_idx + 1
    while body_start < len(lines) and not lines[body_start].strip():
        body_start += 1
    body_end = body_start
    while body_end < len(lines):
        s = lines[body_end].strip()
        if s.startswith("##") or s.startswith("---"):
            break
        body_end += 1

    existing_bullets = [
        l for l in lines[body_start:body_end]
        if l.strip().startswith("- ")
    ]

    sid_tag = f"[sid:{session_id[:8]}]" if session_id else None
    if sid_tag and existing_bullets and sid_tag in existing_bullets[0]:
        existing_bullets[0] = new_line
    else:
        existing_bullets.insert(0, new_line)

    existing_bullets = existing_bullets[:MAX_TRAIL_ENTRIES]
    new_body = [TRAIL_HEADING, ""] + existing_bullets + [""]
    return "\n".join(lines[:heading_idx] + new_body + lines[body_end:])


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({}))
        return

    session_id = data.get("session_id", "") or ""

    task = get_active_task()
    if not task:
        print(json.dumps({}))
        return
    tid = task.get("id")
    if tid is None or tid == "":
        print(json.dumps({}))
        return
    tid = str(tid)

    toplevel = get_git_toplevel()
    if not toplevel:
        print(json.dumps({}))
        return
    root = Path(toplevel)

    progress_path = root / ".ultra" / "tasks" / "progress" / f"task-{tid}.json"
    if not progress_path.exists():
        print(json.dumps({}))
        return
    try:
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(json.dumps({}))
        return

    if not (progress.get("files_touched") or progress.get("advisories")):
        # Nothing happened this session for this task — no trail entry needed
        print(json.dumps({}))
        return

    ctx_rel = task.get("context_file") or ""
    if not ctx_rel:
        print(json.dumps({}))
        return
    ctx_path = root / ".ultra" / "tasks" / ctx_rel
    if not ctx_path.exists():
        print(json.dumps({}))
        return

    try:
        text = ctx_path.read_text(encoding="utf-8")
    except OSError:
        print(json.dumps({}))
        return

    line = build_trail_line(session_id, progress)
    new_text = fold_into_context(text, line, session_id)

    if new_text != text:
        try:
            ctx_path.write_text(new_text, encoding="utf-8")
        except OSError:
            pass

    print(json.dumps({}))


if __name__ == "__main__":
    main()
