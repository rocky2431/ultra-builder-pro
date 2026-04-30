"""Tests for relations_sync.py — file→task reverse index (GAP 1, Phase 1).

Real filesystem fixtures (tmp_path), no mocks for parsing. The functions under
test only do file IO + string parsing, so testing them against a real .ultra
directory layout is faster and more honest than mocking.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from relations_sync import parse_target_files, index_files_to_tasks


class TestParseTargetFiles:
    """Extract backtick-wrapped paths under '**Target Files**:' section."""

    def test_returns_empty_for_missing_file(self, tmp_path):
        assert parse_target_files(tmp_path / "task-99.md") == []

    def test_returns_empty_when_no_section(self, tmp_path):
        ctx = tmp_path / "task-1.md"
        ctx.write_text("# Task 1\n\n## Context\nSomething\n")
        assert parse_target_files(ctx) == []

    def test_parses_single_bullet(self, tmp_path):
        ctx = tmp_path / "task-1.md"
        ctx.write_text(
            "## Implementation\n"
            "**Target Files**:\n"
            "- `src/auth.ts` (create)\n"
            "\n"
            "**Pattern**: existing\n"
        )
        assert parse_target_files(ctx) == ["src/auth.ts"]

    def test_parses_multiple_bullets(self, tmp_path):
        ctx = tmp_path / "task-1.md"
        ctx.write_text(
            "**Target Files**:\n"
            "- `src/auth.ts` (create)\n"
            "- `src/db.ts` (modify: add pool)\n"
            "- `tests/auth.test.ts` (create)\n"
            "\n"
            "**Pattern**: existing\n"
        )
        assert parse_target_files(ctx) == [
            "src/auth.ts", "src/db.ts", "tests/auth.test.ts"
        ]

    def test_stops_at_next_bold_key(self, tmp_path):
        ctx = tmp_path / "task-1.md"
        ctx.write_text(
            "**Target Files**:\n"
            "- `src/a.ts`\n"
            "**Pattern**: foo\n"
            "- `src/should_not_appear.ts`\n"
        )
        assert parse_target_files(ctx) == ["src/a.ts"]

    def test_stops_at_next_heading(self, tmp_path):
        ctx = tmp_path / "task-1.md"
        ctx.write_text(
            "**Target Files**:\n"
            "- `src/a.ts`\n"
            "## Acceptance\n"
            "- `src/should_not_appear.ts`\n"
        )
        assert parse_target_files(ctx) == ["src/a.ts"]

    def test_handles_inline_path(self, tmp_path):
        ctx = tmp_path / "task-1.md"
        ctx.write_text(
            "**Target Files**: `src/inline.ts`\n"
            "**Pattern**: foo\n"
        )
        assert parse_target_files(ctx) == ["src/inline.ts"]

    def test_lowercase_files_marker(self, tmp_path):
        # Template uses 'Target Files' but be tolerant
        ctx = tmp_path / "task-1.md"
        ctx.write_text(
            "**Target files**:\n"
            "- `src/foo.ts`\n"
            "**Pattern**: foo\n"
        )
        assert parse_target_files(ctx) == ["src/foo.ts"]


class TestIndexFilesToTasks:
    """Build code→task reverse index from contexts + progress.json."""

    def _make_ctx(self, root: Path, task_id: str, target_files: list) -> None:
        ctx_dir = root / ".ultra" / "tasks" / "contexts"
        ctx_dir.mkdir(parents=True, exist_ok=True)
        bullets = "\n".join(f"- `{f}`" for f in target_files)
        (ctx_dir / f"task-{task_id}.md").write_text(
            f"# Task {task_id}\n\n"
            "## Implementation\n"
            "**Target Files**:\n"
            f"{bullets}\n\n"
            "**Pattern**: existing\n"
        )

    def _make_progress(self, root: Path, task_id: str, touched: list) -> None:
        prog_dir = root / ".ultra" / "tasks" / "progress"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / f"task-{task_id}.json").write_text(json.dumps({
            "task_id": task_id,
            "files_touched": touched,
        }))

    def test_empty_tasks_yields_empty_index(self, tmp_path):
        assert index_files_to_tasks({"tasks": []}, tmp_path) == {}

    def test_indexes_target_files_for_single_task(self, tmp_path):
        self._make_ctx(tmp_path, "1", ["src/auth.ts", "src/db.ts"])
        tasks_data = {
            "tasks": [{"id": "1", "title": "Auth", "context_file": "contexts/task-1.md"}]
        }
        result = index_files_to_tasks(tasks_data, tmp_path)
        assert result["src/auth.ts"]["tasks"] == ["1"]
        assert result["src/auth.ts"]["from"] == ["target_files"]
        assert result["src/db.ts"]["tasks"] == ["1"]

    def test_merges_multiple_tasks_on_same_file(self, tmp_path):
        self._make_ctx(tmp_path, "1", ["src/shared.ts"])
        self._make_ctx(tmp_path, "2", ["src/shared.ts"])
        tasks_data = {
            "tasks": [
                {"id": "1", "context_file": "contexts/task-1.md"},
                {"id": "2", "context_file": "contexts/task-2.md"},
            ]
        }
        result = index_files_to_tasks(tasks_data, tmp_path)
        assert sorted(result["src/shared.ts"]["tasks"]) == ["1", "2"]

    def test_includes_files_touched_from_progress(self, tmp_path):
        self._make_ctx(tmp_path, "1", ["src/planned.ts"])
        self._make_progress(tmp_path, "1", ["src/actual.ts"])
        tasks_data = {
            "tasks": [{"id": "1", "context_file": "contexts/task-1.md"}]
        }
        result = index_files_to_tasks(tasks_data, tmp_path)
        assert "src/planned.ts" in result
        assert "src/actual.ts" in result
        assert result["src/actual.ts"]["from"] == ["files_touched"]

    def test_merges_sources_when_file_in_both(self, tmp_path):
        self._make_ctx(tmp_path, "1", ["src/file.ts"])
        self._make_progress(tmp_path, "1", ["src/file.ts"])
        tasks_data = {
            "tasks": [{"id": "1", "context_file": "contexts/task-1.md"}]
        }
        result = index_files_to_tasks(tasks_data, tmp_path)
        assert sorted(result["src/file.ts"]["from"]) == ["files_touched", "target_files"]

    def test_skips_task_without_id(self, tmp_path):
        tasks_data = {"tasks": [{"title": "no id", "context_file": "x.md"}]}
        assert index_files_to_tasks(tasks_data, tmp_path) == {}

    def test_handles_numeric_id(self, tmp_path):
        self._make_ctx(tmp_path, "5", ["src/foo.ts"])
        tasks_data = {
            "tasks": [{"id": 5, "context_file": "contexts/task-5.md"}]
        }
        result = index_files_to_tasks(tasks_data, tmp_path)
        assert result["src/foo.ts"]["tasks"] == ["5"]
