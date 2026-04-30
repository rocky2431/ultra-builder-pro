#!/usr/bin/env python3
"""Wiki Generator — derive .ultra/wiki/{index,log}.md from project state.

Phase 3 of the dynamic project KB. Pure derivation: reads
.ultra/relations.json + .ultra/tasks/progress/*.json and writes two
human-readable markdown files that summarize the project at a glance.

  - index.md: tasks grouped by status + spec-coverage table (the "what
              is the system right now" view)
  - log.md:   tasks ordered by last_updated, newest first (the "what
              happened when" view)

Called from relations_sync.py at the end of its run, so wiki freshness
tracks the same trigger as the relations index — no extra hook to wire.

Idempotent: regenerates the files in full each call. Best-effort: silent
on any error so it can never break a hook.

PHILOSOPHY: this is the Karpathy "compounding artifact" expressed as
markdown that humans can read and grep — the structural facts already
live in JSON; this layer makes them legible.
"""

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Orphan trail bullets follow the shape produced by session_trail.build_orphan_line:
#   - 2026-04-30T08:30Z [sid:abcdef12]; branch:main; 3 files (a.ts, b.ts, c.ts); last commit: ...
ORPHAN_BULLET_RE = re.compile(
    r"^- (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)\s*"
    r"(?:\[sid:[^\]]+\])?\s*;?\s*(?P<rest>.+)$"
)
RECENT_DAYS = 30
RECENT_MAX_ENTRIES = 20


def _load_relations(root: Path) -> dict:
    rel_path = root / ".ultra" / "relations.json"
    if not rel_path.exists():
        return {}
    try:
        return json.loads(rel_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _files_for_task(task_id: str, files_index: dict) -> list:
    return sorted(
        path for path, entry in files_index.items()
        if str(task_id) in (entry.get("tasks") or [])
    )


def parse_orphan_trail(root: Path) -> list:
    """Parse .ultra/sessions/orphan-trail.md into (timestamp, summary) pairs.

    Returns [] if file missing/unreadable. Bullets that don't match the
    expected shape are dropped silently — best-effort.
    """
    trail_path = root / ".ultra" / "sessions" / "orphan-trail.md"
    if not trail_path.exists():
        return []
    try:
        text = trail_path.read_text(encoding="utf-8")
    except OSError:
        return []
    entries = []
    for line in text.split("\n"):
        m = ORPHAN_BULLET_RE.match(line.strip())
        if not m:
            continue
        entries.append((m.group("ts"), m.group("rest").strip()))
    return entries


def _collect_recent_activity(rel_data: dict, root: Path) -> list:
    """Merge task progress + orphan trail into time-sorted activity entries.

    Each entry is (timestamp_iso, source_label, detail_str). Filtered to the
    last RECENT_DAYS days, capped at RECENT_MAX_ENTRIES, newest first.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS)).isoformat()

    activities: list = []

    tasks = rel_data.get("tasks") or {}
    for tid, t in tasks.items():
        prog_path = root / ".ultra" / "tasks" / "progress" / f"task-{tid}.json"
        if not prog_path.exists():
            continue
        try:
            p = json.loads(prog_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        last = p.get("last_updated") or ""
        if not last or last < cutoff:
            continue
        files = p.get("files_touched") or []
        adv_n = len(p.get("advisories") or [])
        status = t.get("status") or "?"
        detail_parts = [f"{len(files)} files"]
        if adv_n:
            detail_parts.append(f"{adv_n} advisories")
        activities.append((last, f"task-{tid} ({status})", "; ".join(detail_parts)))

    for ts, summary in parse_orphan_trail(root):
        # Convert "2026-04-30T08:30Z" to comparable ISO. Append :00 seconds
        # if missing so lexicographic compare against cutoff stays correct.
        ts_norm = ts.replace("Z", ":00+00:00") if ts.endswith("Z") and len(ts) == 17 else ts
        if ts_norm < cutoff:
            continue
        activities.append((ts, "orphan", summary[:120]))

    activities.sort(key=lambda x: x[0], reverse=True)
    return activities[:RECENT_MAX_ENTRIES]


def _build_recent_activity_section(rel_data: dict, root: Path) -> list:
    """Markdown lines for the Recent Activity section. Empty if no entries."""
    entries = _collect_recent_activity(rel_data, root)
    if not entries:
        return []
    lines = [f"## Recent Activity (last {RECENT_DAYS} days)", ""]
    lines.append("| Date | Source | Detail |")
    lines.append("|------|--------|--------|")
    for ts, source, detail in entries:
        date = ts[:10]
        # Keep cell content single-line, escape pipes
        detail_safe = detail.replace("|", "\\|")
        lines.append(f"| {date} | {source} | {detail_safe} |")
    lines.append("")
    return lines


def _render_task_block(tid: str, task: dict, files_index: dict) -> list:
    title = task.get("title") or "?"
    status = task.get("status") or "?"
    trace = task.get("trace_to") or []
    ctx = task.get("context_file") or ""
    files = _files_for_task(tid, files_index)

    lines = [f"### task-{tid}: {title} ({status})"]
    if trace:
        for ref in trace:
            lines.append(f"- **Trace**: `{ref}`")
    if files:
        sample = ", ".join(files[:5])
        more = f" (+{len(files) - 5} more)" if len(files) > 5 else ""
        lines.append(f"- **Files** ({len(files)}): {sample}{more}")
    if ctx:
        lines.append(f"- **Context**: `tasks/{ctx}`")
    return lines


def build_index_md(rel_data: dict, root: Path | None = None) -> str:
    """Render the wiki index. If root is given, include Recent Activity table
    derived from progress.json + orphan-trail.md."""
    tasks = rel_data.get("tasks") or {}
    files_index = rel_data.get("files") or {}

    buckets = {
        "in_progress": [],
        "pending": [],
        "completed": [],
        "blocked": [],
    }
    other = []
    for tid, t in tasks.items():
        status = t.get("status") or ""
        bucket = buckets.get(status)
        if bucket is None:
            other.append((tid, t))
        else:
            bucket.append((tid, t))

    parts = [
        "# Project Wiki — Index",
        "",
        "_Auto-generated from `.ultra/relations.json`. Do not edit manually._",
        "",
        f"Last synced: {rel_data.get('last_synced', '?')}",
        "",
    ]

    for status_key, label in [
        ("in_progress", "Active Tasks"),
        ("pending", "Pending Tasks"),
        ("completed", "Completed Tasks"),
        ("blocked", "Blocked Tasks"),
    ]:
        bucket = buckets[status_key]
        if not bucket:
            continue
        parts.append(f"## {label}")
        parts.append("")
        for tid, t in sorted(bucket, key=lambda x: str(x[0])):
            parts.extend(_render_task_block(tid, t, files_index))
            parts.append("")

    if other:
        parts.append("## Other")
        parts.append("")
        for tid, t in sorted(other, key=lambda x: str(x[0])):
            parts.extend(_render_task_block(tid, t, files_index))
            parts.append("")

    # Phase 5B: Recent Activity (cross-task + orphan sessions)
    if root is not None:
        recent = _build_recent_activity_section(rel_data, root)
        parts.extend(recent)

    specs = rel_data.get("specs") or {}
    if specs:
        parts.append("## Spec Coverage")
        parts.append("")
        parts.append("| Spec section | Tasks |")
        parts.append("|--------------|-------|")
        for anchor, meta in sorted(specs.items()):
            refs = meta.get("referenced_by") or []
            tasks_str = ", ".join(f"task-{tid}" for tid in refs) if refs else "_(unreferenced)_"
            parts.append(f"| `{anchor}` | {tasks_str} |")
        parts.append("")

    advisories = rel_data.get("advisories") or []
    if advisories:
        parts.append("## Advisories")
        parts.append("")
        for adv in advisories[:20]:
            atype = adv.get("type") or "?"
            tid = adv.get("task") or "?"
            ref = adv.get("ref") or "?"
            parts.append(f"- **{atype}** task-{tid}: `{ref}`")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def build_log_md(rel_data: dict, root: Path) -> str:
    tasks = rel_data.get("tasks") or {}

    entries = []
    for tid, t in tasks.items():
        prog_path = root / ".ultra" / "tasks" / "progress" / f"task-{tid}.json"
        last = ""
        files: list = []
        adv_count = 0
        if prog_path.exists():
            try:
                p = json.loads(prog_path.read_text(encoding="utf-8"))
                last = p.get("last_updated") or ""
                files = p.get("files_touched") or []
                adv_count = len(p.get("advisories") or [])
            except (json.JSONDecodeError, OSError):
                pass
        entries.append((last, str(tid), t, files, adv_count))

    entries.sort(key=lambda x: x[0] or "", reverse=True)

    parts = [
        "# Project Wiki — Log",
        "",
        "_Auto-generated chronological view of task progress (newest first)._",
        "",
        f"Last synced: {rel_data.get('last_synced', '?')}",
        "",
    ]

    if not entries:
        parts.append("_(no tasks yet)_")
        return "\n".join(parts) + "\n"

    last_date = None
    for last, tid, t, files, adv_count in entries:
        date = last[:10] if last else "untracked"
        if date != last_date:
            parts.append(f"## {date}")
            parts.append("")
            last_date = date

        title = t.get("title") or "?"
        status = t.get("status") or "?"
        parts.append(f"### task-{tid} ({status}) — {title}")
        if files:
            sample = ", ".join(Path(f).name for f in files[:3])
            more = f", +{len(files) - 3}" if len(files) > 3 else ""
            parts.append(f"- Files touched: {sample}{more} ({len(files)})")
        if adv_count:
            parts.append(f"- Advisories: {adv_count}")
        if last:
            parts.append(f"- Last updated: {last}")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def generate_wiki(root: Path) -> bool:
    """Write wiki/index.md and wiki/log.md. Returns True on success.

    No-op (returns False) if relations.json missing or unreadable. Never
    raises — failures swallowed so this can be called from a hook.
    """
    rel_data = _load_relations(root)
    if not rel_data:
        return False

    wiki_dir = root / ".ultra" / "wiki"
    try:
        wiki_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False

    try:
        (wiki_dir / "index.md").write_text(build_index_md(rel_data, root), encoding="utf-8")
        (wiki_dir / "log.md").write_text(build_log_md(rel_data, root), encoding="utf-8")
    except OSError:
        return False
    return True


if __name__ == "__main__":
    import sys
    root_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    ok = generate_wiki(root_arg)
    sys.exit(0 if ok else 1)
