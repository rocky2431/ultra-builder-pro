"""Tests for post_edit_guard.py task trace injection (GAP 1, Phase 1).

Verifies file→task reverse lookup via relations.json produces meaningful
stderr lines (task id + title + first AC bullets). monkeypatch is used to
fix get_git_toplevel — we are not testing git, only the lookup logic.

Phase 5C tests use a real `git init` so _git_short returns real branch /
commit data — those tests verify the no-task fallback path.
"""
import json
import subprocess
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

    def test_falls_back_when_files_index_empty(self, tmp_path, monkeypatch):
        # Phase 5C: in an Ultra project but file index is empty (e.g. plan
        # not yet run) → emit a single git-context fallback line.
        root = self._fake_repo(tmp_path, monkeypatch)
        (root / ".ultra").mkdir()
        (root / ".ultra" / "relations.json").write_text(json.dumps({
            "version": 1,
            "tasks": {},
            "specs": {},
        }))
        result = check_task_trace(str(root / "src/foo.ts"))
        assert len(result) == 1
        assert "[Trace] (no task)" in result[0]
        assert "foo.ts" in result[0]

    def test_falls_back_when_file_not_in_index(self, tmp_path, monkeypatch):
        # Phase 5C: in an Ultra project, file index has entries but not for
        # this file → fallback. The agent still gets situational awareness.
        root = self._fake_repo(tmp_path, monkeypatch)
        (root / ".ultra").mkdir()
        (root / ".ultra" / "relations.json").write_text(json.dumps({
            "version": 2,
            "files": {"other/file.ts": {"tasks": ["1"], "from": ["target_files"]}},
            "tasks": {},
        }))
        result = check_task_trace(str(root / "src/foo.ts"))
        assert len(result) == 1
        assert "[Trace] (no task)" in result[0]
        assert "foo.ts" in result[0]

    def test_no_fallback_when_no_relations_json(self, tmp_path, monkeypatch):
        # Non-Ultra project: stay completely silent, no fallback noise.
        self._fake_repo(tmp_path, monkeypatch)
        # No .ultra/relations.json created.
        assert check_task_trace(str(tmp_path / "src/foo.ts")) == []

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


class TestPhase5CFallback:
    """Phase 5C: real-git fallback for files not owned by any task."""

    def _real_repo(self, tmp_path: Path, monkeypatch) -> Path:
        """Init a real git repo with one commit so HEAD/branch are resolvable."""
        repo = tmp_path / "real_repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        # Initial commit so `rev-parse --abbrev-ref HEAD` returns a real branch
        (repo / "README.md").write_text("init\n")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"],
                       cwd=repo, check=True, capture_output=True)
        monkeypatch.setattr(post_edit_guard, "get_git_toplevel", lambda: str(repo))
        # Mark as Ultra project so the fallback path is reachable
        (repo / ".ultra").mkdir()
        (repo / ".ultra" / "relations.json").write_text(json.dumps({
            "version": 2, "files": {}, "tasks": {},
        }))
        return repo

    def test_fallback_includes_branch_name(self, tmp_path, monkeypatch):
        repo = self._real_repo(tmp_path, monkeypatch)
        (repo / "src").mkdir()
        fpath = repo / "src" / "foo.ts"
        fpath.write_text("export const x = 1;\n")
        result = check_task_trace(str(fpath))
        assert len(result) == 1
        line = result[0]
        assert "[Trace] (no task)" in line
        # Branch name must be resolved (not "?"); git default is main or master
        assert "branch ?" not in line
        assert "branch " in line

    def test_fallback_with_commit_history_shows_last(self, tmp_path, monkeypatch):
        repo = self._real_repo(tmp_path, monkeypatch)
        (repo / "src").mkdir()
        fpath = repo / "src" / "foo.ts"
        fpath.write_text("export const x = 1;\n")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "feat: initial foo"],
                       cwd=repo, check=True, capture_output=True)

        result = check_task_trace(str(fpath))
        assert len(result) == 1
        line = result[0]
        assert "last:" in line
        assert "feat: initial foo" in line
        assert "uncommitted" not in line

    def test_fallback_uncommitted_marker_for_new_file(self, tmp_path, monkeypatch):
        # _real_repo already produces an initial commit; a brand-new file
        # has no git log entry of its own → "uncommitted" marker expected.
        repo = self._real_repo(tmp_path, monkeypatch)
        new_file = repo / "src" / "fresh.ts"
        new_file.parent.mkdir()
        new_file.write_text("export const y = 2;\n")

        result = check_task_trace(str(new_file))
        assert len(result) == 1
        assert "uncommitted" in result[0]
