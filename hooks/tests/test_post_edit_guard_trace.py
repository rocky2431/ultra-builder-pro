"""Tests for post_edit_guard.py task trace injection (GAP 1, Phase 1).

Verifies file→task reverse lookup via relations.json produces meaningful
stderr lines (task id + title + first AC bullets). monkeypatch is used to
fix get_git_toplevel — we are not testing git, only the lookup logic.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import post_edit_guard
from post_edit_guard import _extract_ac_bullets, check_task_trace


class TestExtractAcBullets:
    """First N acceptance criteria bullets from task context md."""

    def test_returns_empty_for_missing_file(self, tmp_path):
        assert _extract_ac_bullets(tmp_path / "nope.md") == []

    def test_returns_empty_when_no_ac_section(self, tmp_path):
        ctx = tmp_path / "ctx.md"
        ctx.write_text("# Task 1\n\n## Context\nSomething\n")
        assert _extract_ac_bullets(ctx) == []

    def test_extracts_bullets(self, tmp_path):
        ctx = tmp_path / "ctx.md"
        ctx.write_text(
            "## Acceptance Criteria\n\n"
            "- AC-1: User can sign in\n"
            "- AC-2: Invalid credentials show error\n"
            "\n"
            "## Trace\nfoo\n"
        )
        result = _extract_ac_bullets(ctx, max_lines=2)
        assert len(result) == 2
        assert "AC-1" in result[0]
        assert "AC-2" in result[1]

    def test_skips_inline_html_comment(self, tmp_path):
        ctx = tmp_path / "ctx.md"
        ctx.write_text(
            "## Acceptance Criteria\n"
            "<!-- inline note -->\n"
            "- AC-1: Real bullet\n"
        )
        result = _extract_ac_bullets(ctx)
        assert len(result) == 1
        assert "AC-1" in result[0]

    def test_skips_multiline_html_comment(self, tmp_path):
        ctx = tmp_path / "ctx.md"
        ctx.write_text(
            "## Acceptance Criteria\n"
            "<!-- This is a\nmulti-line note -->\n"
            "- AC-1: Real bullet\n"
        )
        result = _extract_ac_bullets(ctx)
        assert len(result) == 1
        assert "AC-1" in result[0]

    def test_respects_max_lines(self, tmp_path):
        ctx = tmp_path / "ctx.md"
        ctx.write_text(
            "## Acceptance Criteria\n"
            "- One\n- Two\n- Three\n- Four\n"
        )
        assert len(_extract_ac_bullets(ctx, max_lines=2)) == 2

    def test_stops_at_next_h2(self, tmp_path):
        ctx = tmp_path / "ctx.md"
        ctx.write_text(
            "## Acceptance Criteria\n"
            "- AC-1\n"
            "## Trace\n"
            "- not-an-ac\n"
        )
        result = _extract_ac_bullets(ctx)
        assert result == ["- AC-1"]


class TestCheckTaskTrace:
    """file → task lookup via relations.json."""

    def _fake_repo(self, tmp_path: Path, monkeypatch) -> Path:
        monkeypatch.setattr(post_edit_guard, "get_git_toplevel", lambda: str(tmp_path))
        return tmp_path

    def test_returns_empty_when_no_git(self, tmp_path, monkeypatch):
        monkeypatch.setattr(post_edit_guard, "get_git_toplevel", lambda: "")
        assert check_task_trace(str(tmp_path / "src/foo.ts")) == []

    def test_returns_empty_when_no_relations_file(self, tmp_path, monkeypatch):
        self._fake_repo(tmp_path, monkeypatch)
        assert check_task_trace(str(tmp_path / "src/foo.ts")) == []

    def test_returns_empty_when_relations_has_no_files_index(self, tmp_path, monkeypatch):
        root = self._fake_repo(tmp_path, monkeypatch)
        (root / ".ultra").mkdir()
        (root / ".ultra" / "relations.json").write_text(json.dumps({
            "version": 1,
            "tasks": {},
            "specs": {},
        }))
        assert check_task_trace(str(root / "src/foo.ts")) == []

    def test_returns_empty_when_file_not_in_index(self, tmp_path, monkeypatch):
        root = self._fake_repo(tmp_path, monkeypatch)
        (root / ".ultra").mkdir()
        (root / ".ultra" / "relations.json").write_text(json.dumps({
            "version": 2,
            "files": {"other/file.ts": {"tasks": ["1"], "from": ["target_files"]}},
            "tasks": {},
        }))
        assert check_task_trace(str(root / "src/foo.ts")) == []

    def test_returns_trace_lines_when_matched(self, tmp_path, monkeypatch):
        root = self._fake_repo(tmp_path, monkeypatch)
        ultra = root / ".ultra"
        (ultra / "tasks" / "contexts").mkdir(parents=True)
        (ultra / "tasks" / "contexts" / "task-1.md").write_text(
            "# Task 1: VIP shipping\n\n"
            "## Acceptance Criteria\n"
            "- AC-1: VIP user free shipping\n"
            "- AC-2: Non-VIP normal rate\n"
        )
        (ultra / "relations.json").write_text(json.dumps({
            "version": 2,
            "files": {"src/shipping.ts": {"tasks": ["1"], "from": ["target_files"]}},
            "tasks": {
                "1": {
                    "title": "VIP shipping",
                    "status": "in_progress",
                    "context_file": "contexts/task-1.md",
                }
            },
        }))
        result = check_task_trace(str(root / "src/shipping.ts"))
        joined = "\n".join(result)
        assert "task-1" in joined
        assert "VIP shipping" in joined
        assert "AC-1" in joined
        assert "AC-2" in joined
        assert "in_progress" in joined

    def test_handles_multiple_tasks_per_file(self, tmp_path, monkeypatch):
        root = self._fake_repo(tmp_path, monkeypatch)
        ultra = root / ".ultra"
        (ultra / "tasks" / "contexts").mkdir(parents=True)
        for tid, title in [("1", "First"), ("2", "Second")]:
            (ultra / "tasks" / "contexts" / f"task-{tid}.md").write_text(
                f"# Task {tid}\n\n## Acceptance Criteria\n- AC for {title}\n"
            )
        (ultra / "relations.json").write_text(json.dumps({
            "version": 2,
            "files": {"src/shared.ts": {"tasks": ["1", "2"], "from": ["target_files"]}},
            "tasks": {
                "1": {"title": "First", "status": "completed", "context_file": "contexts/task-1.md"},
                "2": {"title": "Second", "status": "in_progress", "context_file": "contexts/task-2.md"},
            },
        }))
        result = check_task_trace(str(root / "src/shared.ts"))
        joined = "\n".join(result)
        assert "task-1" in joined
        assert "task-2" in joined
        assert "First" in joined
        assert "Second" in joined

    def test_includes_source_hint(self, tmp_path, monkeypatch):
        root = self._fake_repo(tmp_path, monkeypatch)
        ultra = root / ".ultra"
        ultra.mkdir()
        (ultra / "relations.json").write_text(json.dumps({
            "version": 2,
            "files": {"src/foo.ts": {"tasks": ["1"], "from": ["target_files", "files_touched"]}},
            "tasks": {"1": {"title": "X", "status": "pending", "context_file": ""}},
        }))
        result = check_task_trace(str(root / "src/foo.ts"))
        joined = "\n".join(result)
        assert "target_files" in joined
        assert "files_touched" in joined

    def test_silent_on_invalid_relations_json(self, tmp_path, monkeypatch):
        root = self._fake_repo(tmp_path, monkeypatch)
        (root / ".ultra").mkdir()
        (root / ".ultra" / "relations.json").write_text("not valid json {")
        assert check_task_trace(str(root / "src/foo.ts")) == []
