"""Tests for session_trail.py — Phase 2 trail fold-back into task context.

Real filesystem (tmp_path), real subprocess for E2E. The unit tests target
build_trail_line and fold_into_context directly; the E2E test exercises the
full hook via stdin/stdout against a tmp git repo.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import session_trail
from session_trail import build_trail_line, fold_into_context, TRAIL_HEADING

HOOK_DIR = Path(__file__).parent.parent
TRAIL_HOOK = HOOK_DIR / "session_trail.py"


class TestBuildTrailLine:
    """build_trail_line: assemble one bullet from session_id + progress dict."""

    def test_includes_session_tag(self):
        line = build_trail_line("abcdef1234567890", {"files_touched": [], "advisories": []})
        assert "[sid:abcdef12]" in line

    def test_omits_tag_when_no_session(self):
        line = build_trail_line("", {"files_touched": [], "advisories": []})
        assert "[sid:" not in line

    def test_files_count_and_sample(self):
        line = build_trail_line("s", {
            "files_touched": ["src/a.ts", "src/b.ts", "src/c.ts", "src/d.ts"],
            "advisories": [],
        })
        assert "4 files" in line
        assert "a.ts" in line
        assert "+1" in line  # 4 - 3 sample

    def test_zero_files(self):
        line = build_trail_line("s", {"files_touched": [], "advisories": []})
        assert "0 files" in line

    def test_advisory_count(self):
        line = build_trail_line("s", {
            "files_touched": [],
            "advisories": [{"msg": "x"}, {"msg": "y"}, {"msg": "z"}],
        })
        assert "3 advisories" in line

    def test_evidence_summary(self, monkeypatch):
        monkeypatch.setattr(session_trail, "EVIDENCE_DIMENSIONS",
                            ("a", "b", "c", "d", "e", "f"))
        line = build_trail_line("s", {
            "files_touched": [],
            "advisories": [],
            "evidence_score": {"a": 90, "b": 80, "c": 50, "d": 100, "e": 0, "f": 80},
        })
        assert "evidence 4/6" in line


class TestFoldIntoContext:
    """fold_into_context: insert trail line into the right markdown section."""

    BASE_CTX = (
        "# Task 1\n\n"
        "## Context\n"
        "What we're building.\n\n"
        "## Acceptance Criteria\n"
        "- AC-1\n\n"
        "## Trace\n"
        "Source: specs/x.md\n\n"
        "## Completion\n"
        "_pending_\n"
    )

    def test_creates_section_before_completion(self):
        result = fold_into_context(self.BASE_CTX, "- 2026-01-01 [sid:abc] entry", "abc")
        assert TRAIL_HEADING in result
        # Trail section must come before Completion in document order
        trail_pos = result.index(TRAIL_HEADING)
        completion_pos = result.index("## Completion")
        assert trail_pos < completion_pos
        assert "- 2026-01-01 [sid:abc] entry" in result

    def test_appends_section_when_no_completion(self):
        text = "# Task\n\n## Context\nfoo\n"
        result = fold_into_context(text, "- entry-1", "s1")
        assert TRAIL_HEADING in result
        assert "- entry-1" in result

    def test_prepends_to_existing_section(self):
        text = (
            "# Task\n\n"
            "## Session Trail\n\n"
            "- 2026-01-01 [sid:older] old entry\n"
            "\n"
            "## Completion\n"
        )
        result = fold_into_context(text, "- 2026-02-01 [sid:newer] new entry", "newer")
        # New entry should come BEFORE old
        new_pos = result.index("new entry")
        old_pos = result.index("old entry")
        assert new_pos < old_pos

    def test_replaces_when_same_session(self):
        text = (
            "# Task\n\n"
            "## Session Trail\n\n"
            "- 2026-01-01 [sid:samesid] first try\n"
            "\n"
            "## Completion\n"
        )
        result = fold_into_context(text, "- 2026-01-01 [sid:samesid] updated", "samesid")
        assert "first try" not in result
        assert "updated" in result
        # Should still be only one entry
        assert result.count("[sid:samesid]") == 1

    def test_caps_max_entries(self):
        # Build text with 60 existing entries
        bullets = "\n".join(f"- 2026-01-{i:02d} [sid:s{i:08d}] entry-{i}" for i in range(60))
        text = (
            "# Task\n\n"
            f"## Session Trail\n\n{bullets}\n\n"
            "## Completion\n"
        )
        result = fold_into_context(text, "- 2026-02-01 [sid:newone00] new", "newone00")
        # Count entries — should be at most MAX_TRAIL_ENTRIES (50)
        from session_trail import MAX_TRAIL_ENTRIES
        # Count bullet lines in trail section
        trail_section = result.split(TRAIL_HEADING, 1)[1].split("\n## ", 1)[0]
        bullet_count = sum(1 for line in trail_section.split("\n") if line.strip().startswith("- "))
        assert bullet_count <= MAX_TRAIL_ENTRIES


class TestSessionTrailE2E:
    """Subprocess E2E: real hook via stdin against a tmp git repo."""

    def _git_init(self, repo: Path):
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)

    def _setup(self, tmp_path: Path):
        repo = tmp_path / "repo"
        repo.mkdir()
        self._git_init(repo)

        ultra = repo / ".ultra"
        (ultra / "tasks" / "contexts").mkdir(parents=True)
        (ultra / "tasks" / "progress").mkdir(parents=True)

        (ultra / "tasks" / "tasks.json").write_text(json.dumps({
            "version": "4.4",
            "tasks": [{
                "id": "1",
                "title": "demo",
                "status": "in_progress",
                "context_file": "contexts/task-1.md",
            }],
        }))
        (ultra / "tasks" / "contexts" / "task-1.md").write_text(
            "# Task 1: demo\n\n"
            "## Acceptance Criteria\n"
            "- AC-1\n\n"
            "## Completion\n"
            "_pending_\n"
        )
        (ultra / "tasks" / "progress" / "task-1.json").write_text(json.dumps({
            "task_id": "1",
            "files_touched": ["src/a.ts", "src/b.ts"],
            "advisories": [{"at": "now", "file": "src/a.ts", "msg": "TODO"}],
            "evidence_score": {"tests_written": 80, "tests_passed": 80,
                               "persistence_real": 0, "feature_flags_audit": 0,
                               "vertical_slice": 0, "spec_trace": 80},
            "last_updated": "now",
        }))
        return repo

    def _run(self, payload: dict, cwd: Path):
        proc = subprocess.run(
            [sys.executable, str(TRAIL_HOOK)],
            input=json.dumps(payload),
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.stdout, proc.stderr, proc.returncode

    def test_writes_trail_to_context(self, tmp_path):
        repo = self._setup(tmp_path)
        _, stderr, code = self._run({"session_id": "abcdef1234567890"}, repo)
        assert code == 0, f"stderr={stderr!r}"

        ctx = (repo / ".ultra" / "tasks" / "contexts" / "task-1.md").read_text()
        assert TRAIL_HEADING in ctx
        assert "[sid:abcdef12]" in ctx
        assert "2 files" in ctx
        assert "1 advisories" in ctx
        assert "evidence 3/6" in ctx
        # Trail must be before Completion
        assert ctx.index(TRAIL_HEADING) < ctx.index("## Completion")

    def test_idempotent_on_rerun(self, tmp_path):
        repo = self._setup(tmp_path)
        self._run({"session_id": "deadbeef00000000"}, repo)
        self._run({"session_id": "deadbeef00000000"}, repo)
        ctx = (repo / ".ultra" / "tasks" / "contexts" / "task-1.md").read_text()
        # Same session should produce only one trail entry
        assert ctx.count("[sid:deadbeef]") == 1

    def test_silent_when_no_active_task(self, tmp_path):
        repo = tmp_path / "empty"
        repo.mkdir()
        self._git_init(repo)
        _, _, code = self._run({"session_id": "xx"}, repo)
        assert code == 0  # no-op, silent

    def test_silent_when_no_progress(self, tmp_path):
        repo = self._setup(tmp_path)
        # Wipe progress so the no-op path triggers
        (repo / ".ultra" / "tasks" / "progress" / "task-1.json").unlink()
        _, _, code = self._run({"session_id": "xx"}, repo)
        assert code == 0
        # Context should be unchanged (no trail section added)
        ctx = (repo / ".ultra" / "tasks" / "contexts" / "task-1.md").read_text()
        assert TRAIL_HEADING not in ctx


# -- Phase 5A: orphan trail (sessions without active task) -------------------

from session_trail import (
    build_orphan_line,
    insert_orphan_line,
    fold_orphan_trail,
    ORPHAN_HEADING,
)


class TestBuildOrphanLine:
    def test_includes_branch_and_files(self):
        line = build_orphan_line("abcdef1234567890", {
            "branch": "main",
            "dirty_files": ["src/a.ts", "src/b.ts"],
            "last_commit": "abc123 fix: foo",
        })
        assert "[sid:abcdef12]" in line
        assert "branch:main" in line
        assert "2 files" in line
        assert "a.ts" in line
        assert "abc123" in line

    def test_truncates_file_sample(self):
        line = build_orphan_line("s", {
            "branch": "main",
            "dirty_files": ["a.ts", "b.ts", "c.ts", "d.ts", "e.ts"],
            "last_commit": "",
        })
        assert "5 files" in line
        assert "+2" in line  # 5 - 3 sampled

    def test_no_commit_section_when_empty(self):
        line = build_orphan_line("s", {
            "branch": "main",
            "dirty_files": ["a.ts"],
            "last_commit": "",
        })
        assert "last commit" not in line


class TestInsertOrphanLine:
    HEADER = (
        "# Orphan Trail — Sessions without active task\n\n"
        "_Auto-maintained..._\n"
    )

    def test_creates_section_when_missing(self):
        result = insert_orphan_line(self.HEADER, "- entry-1", "s1")
        assert ORPHAN_HEADING in result
        assert "- entry-1" in result

    def test_prepends_new_entry(self):
        text = self.HEADER + "\n## Sessions\n\n- old entry [sid:older123]\n"
        result = insert_orphan_line(text, "- new entry [sid:newer123]", "newer123")
        new_pos = result.index("new entry")
        old_pos = result.index("old entry")
        assert new_pos < old_pos

    def test_replaces_when_same_session(self):
        text = self.HEADER + "\n## Sessions\n\n- first [sid:samesid0]\n"
        result = insert_orphan_line(text, "- updated [sid:samesid0]", "samesid0")
        assert "first" not in result
        assert "updated" in result
        assert result.count("[sid:samesid0]") == 1

    def test_caps_at_max(self):
        bullets = "\n".join(f"- entry-{i} [sid:s{i:08d}]" for i in range(120))
        text = self.HEADER + "\n## Sessions\n\n" + bullets
        result = insert_orphan_line(text, "- newone [sid:newone00]", "newone00")
        # Cap at 100 entries
        from session_trail import MAX_ORPHAN_ENTRIES
        section = result.split(ORPHAN_HEADING, 1)[1]
        bullet_count = sum(1 for line in section.split("\n") if line.strip().startswith("- "))
        assert bullet_count <= MAX_ORPHAN_ENTRIES


class TestFoldOrphanTrail:
    """Real git repo, real fold to .ultra/sessions/orphan-trail.md."""

    def _real_repo(self, tmp_path: Path) -> Path:
        import subprocess as sp
        repo = tmp_path / "repo"
        repo.mkdir()
        sp.run(["git", "init", "-q"], cwd=repo, check=True)
        sp.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
        sp.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "README.md").write_text("init\n")
        sp.run(["git", "add", "-A"], cwd=repo, check=True)
        sp.run(["git", "commit", "-q", "-m", "init"],
               cwd=repo, check=True, capture_output=True)
        return repo

    def test_no_op_when_clean_tree(self, tmp_path):
        repo = self._real_repo(tmp_path)
        # No changes since the initial commit → fold should no-op
        wrote = fold_orphan_trail("sessionid", repo)
        assert wrote is False
        assert not (repo / ".ultra" / "sessions" / "orphan-trail.md").exists()

    def test_writes_when_dirty(self, tmp_path):
        repo = self._real_repo(tmp_path)
        # Modify README so it's dirty (.md is in source ext list)
        (repo / "README.md").write_text("changed!\n")
        wrote = fold_orphan_trail("abcdef1234567890", repo)
        assert wrote is True
        trail = (repo / ".ultra" / "sessions" / "orphan-trail.md").read_text()
        assert ORPHAN_HEADING in trail
        assert "[sid:abcdef12]" in trail
        assert "README.md" in trail

    def test_idempotent_same_session(self, tmp_path):
        repo = self._real_repo(tmp_path)
        (repo / "README.md").write_text("changed!\n")
        fold_orphan_trail("samesid00000000", repo)
        fold_orphan_trail("samesid00000000", repo)
        trail = (repo / ".ultra" / "sessions" / "orphan-trail.md").read_text()
        assert trail.count("[sid:samesid0]") == 1


class TestSessionTrailE2EOrphan:
    """Real subprocess hook against a tmp git repo with no active task."""

    def _real_repo(self, tmp_path: Path) -> Path:
        import subprocess as sp
        repo = tmp_path / "repo"
        repo.mkdir()
        sp.run(["git", "init", "-q"], cwd=repo, check=True)
        sp.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
        sp.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "README.md").write_text("init\n")
        sp.run(["git", "add", "-A"], cwd=repo, check=True)
        sp.run(["git", "commit", "-q", "-m", "init"],
               cwd=repo, check=True, capture_output=True)
        return repo

    def test_routes_to_orphan_when_no_active_task(self, tmp_path):
        import subprocess as sp
        repo = self._real_repo(tmp_path)
        # No tasks.json at all → orphan path is the only option
        (repo / "src.ts").write_text("export const x = 1;\n")
        # Make it dirty with respect to HEAD by adding + leaving unstaged
        sp.run(["git", "add", "src.ts"], cwd=repo, check=True)
        # Now it's staged → diff --cached --name-only should include it

        proc = sp.run(
            [sys.executable, str(TRAIL_HOOK)],
            input=json.dumps({"session_id": "abcdef1234567890"}),
            cwd=str(repo), capture_output=True, text=True, timeout=10,
        )
        assert proc.returncode == 0

        trail_path = repo / ".ultra" / "sessions" / "orphan-trail.md"
        assert trail_path.exists()
        text = trail_path.read_text()
        assert "[sid:abcdef12]" in text
        assert "src.ts" in text
