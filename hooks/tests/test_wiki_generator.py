"""Tests for wiki_generator.py — Phase 3 derived views.

Real filesystem fixtures. Verifies markdown structure, status grouping,
and chronological ordering.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from wiki_generator import (
    build_index_md,
    build_log_md,
    generate_wiki,
)


class TestBuildIndexMd:
    """Index groups tasks by status and lists spec coverage."""

    def test_empty_state(self):
        md = build_index_md({"tasks": {}, "specs": {}, "files": {}})
        assert "# Project Wiki — Index" in md
        assert "## Active Tasks" not in md  # no bucket if empty

    def test_groups_by_status(self):
        rel = {
            "last_synced": "2026-04-30T08:00Z",
            "tasks": {
                "1": {"title": "A", "status": "in_progress", "trace_to": [], "context_file": "contexts/task-1.md"},
                "2": {"title": "B", "status": "pending", "trace_to": [], "context_file": ""},
                "3": {"title": "C", "status": "completed", "trace_to": [], "context_file": ""},
            },
            "specs": {},
            "files": {},
        }
        md = build_index_md(rel)
        assert "## Active Tasks" in md
        assert "## Pending Tasks" in md
        assert "## Completed Tasks" in md
        # In document order: in_progress before pending before completed
        assert md.index("Active Tasks") < md.index("Pending Tasks") < md.index("Completed Tasks")

    def test_renders_files_for_task(self):
        rel = {
            "tasks": {"1": {"title": "T", "status": "in_progress", "trace_to": [], "context_file": ""}},
            "specs": {},
            "files": {
                "src/a.ts": {"tasks": ["1"], "from": ["target_files"]},
                "src/b.ts": {"tasks": ["1"], "from": ["files_touched"]},
                "src/c.ts": {"tasks": ["2"], "from": ["target_files"]},  # other task
            },
        }
        md = build_index_md(rel)
        assert "src/a.ts" in md
        assert "src/b.ts" in md
        # task-1's block should NOT list task-2's file
        task1_block = md.split("### task-1")[1].split("###")[0] if "### task-1" in md else ""
        assert "src/c.ts" not in task1_block

    def test_renders_trace_links(self):
        rel = {
            "tasks": {"1": {
                "title": "T", "status": "in_progress",
                "trace_to": ["specs/product.md#vip-shipping"],
                "context_file": "",
            }},
            "specs": {}, "files": {},
        }
        md = build_index_md(rel)
        assert "specs/product.md#vip-shipping" in md

    def test_spec_coverage_table(self):
        rel = {
            "tasks": {},
            "specs": {
                "specs/x.md#foo": {"file": "specs/x.md", "heading": "## foo", "referenced_by": ["1", "2"]},
                "specs/x.md#bar": {"file": "specs/x.md", "heading": "## bar", "referenced_by": []},
            },
            "files": {},
        }
        md = build_index_md(rel)
        assert "## Spec Coverage" in md
        assert "task-1" in md
        assert "_(unreferenced)_" in md

    def test_advisories_section_appears_when_present(self):
        rel = {
            "tasks": {}, "specs": {}, "files": {},
            "advisories": [{"type": "dangling_trace_to", "task": "1", "ref": "specs/missing.md#x"}],
        }
        md = build_index_md(rel)
        assert "## Advisories" in md
        assert "dangling_trace_to" in md
        assert "specs/missing.md#x" in md


class TestBuildLogMd:
    """Log orders tasks chronologically (newest first), grouped by date."""

    def _setup_progress(self, tmp_path: Path, task_id: str, last_updated: str,
                       files: list, n_advisories: int = 0):
        prog_dir = tmp_path / ".ultra" / "tasks" / "progress"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / f"task-{task_id}.json").write_text(json.dumps({
            "task_id": task_id,
            "last_updated": last_updated,
            "files_touched": files,
            "advisories": [{"msg": f"a{i}"} for i in range(n_advisories)],
        }))

    def test_empty_state(self, tmp_path):
        md = build_log_md({"tasks": {}}, tmp_path)
        assert "no tasks yet" in md

    def test_orders_newest_first(self, tmp_path):
        self._setup_progress(tmp_path, "1", "2026-04-29T10:00:00Z", ["a.ts"])
        self._setup_progress(tmp_path, "2", "2026-04-30T10:00:00Z", ["b.ts"])
        rel = {
            "tasks": {
                "1": {"title": "Older", "status": "completed"},
                "2": {"title": "Newer", "status": "in_progress"},
            },
        }
        md = build_log_md(rel, tmp_path)
        # Newer task should appear first in document
        assert md.index("Newer") < md.index("Older")

    def test_groups_by_date(self, tmp_path):
        self._setup_progress(tmp_path, "1", "2026-04-29T10:00:00Z", ["a.ts"])
        self._setup_progress(tmp_path, "2", "2026-04-29T15:00:00Z", ["b.ts"])
        rel = {
            "tasks": {
                "1": {"title": "A", "status": "completed"},
                "2": {"title": "B", "status": "completed"},
            },
        }
        md = build_log_md(rel, tmp_path)
        # Should have ## 2026-04-29 once
        assert md.count("## 2026-04-29") == 1

    def test_handles_task_without_progress(self, tmp_path):
        rel = {
            "tasks": {"1": {"title": "Untracked", "status": "pending"}},
        }
        md = build_log_md(rel, tmp_path)
        assert "untracked" in md
        assert "Untracked" in md


class TestGenerateWiki:
    """End-to-end: generate_wiki writes both files from real .ultra layout."""

    def _setup(self, tmp_path: Path):
        ultra = tmp_path / ".ultra"
        ultra.mkdir()
        (ultra / "relations.json").write_text(json.dumps({
            "version": 2,
            "last_synced": "2026-04-30T08:00Z",
            "tasks": {
                "1": {
                    "title": "VIP shipping",
                    "status": "in_progress",
                    "trace_to": ["specs/product.md#vip-shipping"],
                    "context_file": "contexts/task-1.md",
                },
            },
            "specs": {},
            "files": {"src/shipping.ts": {"tasks": ["1"], "from": ["target_files"]}},
            "advisories": [],
        }))
        prog = ultra / "tasks" / "progress"
        prog.mkdir(parents=True)
        (prog / "task-1.json").write_text(json.dumps({
            "task_id": "1",
            "last_updated": "2026-04-30T08:00:00Z",
            "files_touched": ["src/shipping.ts"],
            "advisories": [],
        }))

    def test_returns_false_when_no_relations(self, tmp_path):
        assert generate_wiki(tmp_path) is False

    def test_writes_both_files(self, tmp_path):
        self._setup(tmp_path)
        assert generate_wiki(tmp_path) is True

        wiki = tmp_path / ".ultra" / "wiki"
        assert (wiki / "index.md").exists()
        assert (wiki / "log.md").exists()

        index = (wiki / "index.md").read_text()
        log = (wiki / "log.md").read_text()
        assert "VIP shipping" in index
        assert "VIP shipping" in log
        assert "src/shipping.ts" in index

    def test_idempotent_overwrites(self, tmp_path):
        self._setup(tmp_path)
        generate_wiki(tmp_path)
        first = (tmp_path / ".ultra" / "wiki" / "index.md").read_text()
        # Run again — output should be deterministic
        generate_wiki(tmp_path)
        second = (tmp_path / ".ultra" / "wiki" / "index.md").read_text()
        assert first == second


class TestRecentActivity:
    """Phase 5B: Recent Activity section merges progress.json + orphan-trail.md."""

    def _setup_progress(self, tmp_path: Path, task_id: str, last_updated: str,
                       files: list, n_advisories: int = 0):
        prog_dir = tmp_path / ".ultra" / "tasks" / "progress"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / f"task-{task_id}.json").write_text(json.dumps({
            "task_id": task_id,
            "last_updated": last_updated,
            "files_touched": files,
            "advisories": [{"msg": f"a{i}"} for i in range(n_advisories)],
        }))

    def _setup_orphan(self, tmp_path: Path, lines: list):
        sessions = tmp_path / ".ultra" / "sessions"
        sessions.mkdir(parents=True, exist_ok=True)
        body = "\n".join(lines)
        (sessions / "orphan-trail.md").write_text(
            "# Orphan Trail\n\n## Sessions\n\n" + body + "\n"
        )

    def test_parse_orphan_trail_returns_entries(self, tmp_path):
        from wiki_generator import parse_orphan_trail
        self._setup_orphan(tmp_path, [
            "- 2026-04-30T08:30Z [sid:abc12345]; branch:main; 2 files (a.ts, b.ts)",
            "- 2026-04-29T12:00Z [sid:def67890]; branch:explore; 1 files (c.ts)",
        ])
        entries = parse_orphan_trail(tmp_path)
        assert len(entries) == 2
        assert entries[0][0] == "2026-04-30T08:30Z"
        assert "branch:main" in entries[0][1]

    def test_parse_orphan_trail_skips_malformed_lines(self, tmp_path):
        from wiki_generator import parse_orphan_trail
        self._setup_orphan(tmp_path, [
            "- 2026-04-30T08:30Z [sid:abc12345]; branch:main; 2 files",
            "- not a real entry",
            "- 2026-04-29T12:00Z [sid:def67890]; branch:explore; 1 files",
        ])
        entries = parse_orphan_trail(tmp_path)
        assert len(entries) == 2  # malformed line dropped

    def test_recent_activity_merges_tasks_and_orphan(self, tmp_path):
        from datetime import datetime, timezone
        # Use a recent timestamp so it falls within the 30-day window
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00+00:00")
        date_today = now_iso[:10]
        # Build orphan timestamp matching today's date in expected format
        orphan_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

        self._setup_progress(tmp_path, "1", now_iso, ["src/a.ts"], n_advisories=1)
        self._setup_orphan(tmp_path, [
            f"- {orphan_ts} [sid:abc12345]; branch:main; 1 files (b.ts)",
        ])

        rel = {"tasks": {"1": {"title": "T", "status": "in_progress"}}}
        from wiki_generator import _build_recent_activity_section
        lines = _build_recent_activity_section(rel, tmp_path)
        md = "\n".join(lines)
        assert "Recent Activity" in md
        assert "task-1" in md
        assert "orphan" in md
        assert date_today in md

    def test_recent_activity_filters_old_entries(self, tmp_path):
        # Old timestamp (>30 days) should be excluded
        self._setup_progress(tmp_path, "1", "2020-01-01T00:00:00+00:00", ["a.ts"])
        rel = {"tasks": {"1": {"title": "T", "status": "completed"}}}
        from wiki_generator import _build_recent_activity_section
        lines = _build_recent_activity_section(rel, tmp_path)
        # No entries → empty list (section omitted)
        assert lines == []

    def test_index_md_includes_section_when_root_passed(self, tmp_path):
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00+00:00")
        self._setup_progress(tmp_path, "1", now_iso, ["src/a.ts"])
        rel = {
            "last_synced": "x",
            "tasks": {"1": {"title": "T", "status": "in_progress",
                            "trace_to": [], "context_file": ""}},
            "specs": {}, "files": {},
        }
        md = build_index_md(rel, tmp_path)
        assert "## Recent Activity" in md

    def test_index_md_omits_section_when_root_none(self):
        rel = {
            "tasks": {"1": {"title": "T", "status": "in_progress",
                            "trace_to": [], "context_file": ""}},
            "specs": {}, "files": {},
        }
        md = build_index_md(rel)  # no root
        assert "## Recent Activity" not in md


class TestRelationsSyncIntegratesWiki:
    """relations_sync.py must invoke generate_wiki at the end of its run."""

    def test_relations_sync_creates_wiki_files(self, tmp_path):
        import subprocess
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)

        ultra = repo / ".ultra"
        (ultra / "tasks" / "contexts").mkdir(parents=True)
        (ultra / "specs").mkdir(parents=True)

        (ultra / "tasks" / "tasks.json").write_text(json.dumps({
            "version": "4.4",
            "tasks": [{
                "id": "1",
                "title": "demo",
                "status": "in_progress",
                "context_file": "contexts/task-1.md",
                "trace_to": [],
            }],
        }))
        (ultra / "tasks" / "contexts" / "task-1.md").write_text(
            "# Task 1\n\n## Implementation\n**Target Files**:\n- `src/x.ts`\n"
        )

        hook = Path(__file__).parent.parent / "relations_sync.py"
        payload = {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(ultra / "tasks" / "tasks.json")},
        }
        subprocess.run(
            [sys.executable, str(hook)],
            input=json.dumps(payload),
            cwd=str(repo),
            capture_output=True, text=True, timeout=10,
        )

        assert (ultra / "wiki" / "index.md").exists()
        assert (ultra / "wiki" / "log.md").exists()
        assert "demo" in (ultra / "wiki" / "index.md").read_text()
