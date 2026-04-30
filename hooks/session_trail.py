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
import subprocess
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
MAX_ORPHAN_ENTRIES = 100
TRAIL_HEADING = "## Session Trail"
ORPHAN_HEADING = "## Sessions"

# Source-code extensions used to filter dirty-file noise (excludes lockfiles,
# build outputs, generated artifacts).
ORPHAN_SOURCE_EXT = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java",
    ".sol", ".rb", ".vue", ".svelte", ".sh", ".md", ".css", ".scss",
    ".html", ".json", ".yaml", ".yml", ".toml",
}


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


# -- Orphan trail path: sessions without an active task -----------------------

def _git(args: list, cwd: Path) -> str:
    """Run git with timeout; return stdout stripped, or empty string on error."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=3,
            cwd=str(cwd),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return ""


def collect_orphan_facts(root: Path) -> dict:
    """Snapshot working state for an orphan session.

    Returns:
      branch:       current branch name
      dirty_files:  source files modified or staged (excludes untracked
                    to avoid build artifacts)
      last_commit:  short hash + subject of HEAD
    """
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=root) or "?"

    diff_out = _git(["diff", "--name-only", "HEAD"], cwd=root)
    cached_out = _git(["diff", "--cached", "--name-only"], cwd=root)
    seen: set = set()
    dirty: list = []
    for line in (diff_out + "\n" + cached_out).split("\n"):
        f = line.strip()
        if not f or f in seen:
            continue
        seen.add(f)
        if Path(f).suffix.lower() in ORPHAN_SOURCE_EXT:
            dirty.append(f)

    last = _git(["log", "-1", "--pretty=format:%h %s"], cwd=root)
    return {"branch": branch, "dirty_files": dirty, "last_commit": last}


def build_orphan_line(session_id: str, facts: dict) -> str:
    """One bullet line summarizing an orphan session."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    sid_tag = f" [sid:{session_id[:8]}]" if session_id else ""
    branch = facts.get("branch") or "?"
    files = facts.get("dirty_files") or []
    n = len(files)
    sample = ", ".join(Path(f).name for f in files[:3])
    if n > 3:
        sample += f", +{n - 3}"
    files_part = f"{n} files"
    if sample:
        files_part += f" ({sample})"
    last = (facts.get("last_commit") or "")[:60]

    parts = [f"- {ts}{sid_tag}", f"branch:{branch}", files_part]
    if last:
        parts.append(f"last commit: {last}")
    return "; ".join(parts)


def insert_orphan_line(text: str, new_line: str, session_id: str) -> str:
    """Insert/replace under ## Sessions heading. Idempotent by session_id."""
    lines = text.split("\n")
    heading_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == ORPHAN_HEADING:
            heading_idx = i
            break

    if heading_idx == -1:
        # Append heading + first bullet
        base = text.rstrip()
        sep = "\n\n" if base else ""
        return f"{base}{sep}{ORPHAN_HEADING}\n\n{new_line}\n"

    body_start = heading_idx + 1
    while body_start < len(lines) and not lines[body_start].strip():
        body_start += 1

    bullets = [l for l in lines[body_start:] if l.strip().startswith("- ")]
    sid_tag = f"[sid:{session_id[:8]}]" if session_id else None
    if sid_tag and bullets and sid_tag in bullets[0]:
        bullets[0] = new_line
    else:
        bullets.insert(0, new_line)
    bullets = bullets[:MAX_ORPHAN_ENTRIES]

    return "\n".join(lines[:heading_idx + 1] + [""] + bullets) + "\n"


def fold_orphan_trail(session_id: str, root: Path) -> bool:
    """Write a session entry to .ultra/sessions/orphan-trail.md.

    Returns True if a line was written. No-op (returns False) if no source
    file is dirty in the working tree.
    """
    facts = collect_orphan_facts(root)
    if not facts.get("dirty_files"):
        return False

    sessions_dir = root / ".ultra" / "sessions"
    try:
        sessions_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    trail_path = sessions_dir / "orphan-trail.md"

    if trail_path.exists():
        try:
            text = trail_path.read_text(encoding="utf-8")
        except OSError:
            text = ""
    else:
        text = (
            "# Orphan Trail — Sessions without active task\n\n"
            "_Auto-maintained by session_trail.py. Each line records a "
            "session that edited code without an active task. Newest first._\n"
        )

    line = build_orphan_line(session_id, facts)
    new_text = insert_orphan_line(text, line, session_id)

    if new_text == text:
        return False
    try:
        trail_path.write_text(new_text, encoding="utf-8")
    except OSError:
        return False
    return True


# -- Main dispatcher ----------------------------------------------------------

def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({}))
        return

    session_id = data.get("session_id", "") or ""

    toplevel = get_git_toplevel()
    if not toplevel:
        print(json.dumps({}))
        return
    root = Path(toplevel)

    task = get_active_task()
    if not task:
        # Orphan path: no in_progress task, but session may have edited
        # source files. Fold facts into .ultra/sessions/orphan-trail.md.
        try:
            fold_orphan_trail(session_id, root)
        except Exception:
            pass
        print(json.dumps({}))
        return
    tid = task.get("id")
    if tid is None or tid == "":
        # Same orphan fallback when task is malformed
        try:
            fold_orphan_trail(session_id, root)
        except Exception:
            pass
        print(json.dumps({}))
        return
    tid = str(tid)

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
