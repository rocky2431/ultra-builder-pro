"""Tests for mid_workflow_recall.py — recall queries + rate limiting."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from mid_workflow_recall import (
    query_file_observations,
    query_learned_lessons,
    load_recalled,
    mark_recalled,
    SOURCE_EXTENSIONS,
    MAX_INJECTIONS,
)


class TestQueryFileObservations:
    """query_file_observations: test failures + edit history from other sessions."""

    def test_finds_test_failures(self, seeded_conn, tmp_path):
        db_path = tmp_path / "test.db"
        # Write seeded_conn to file for the function
        import sqlite3
        file_conn = sqlite3.connect(str(db_path))
        seeded_conn.backup(file_conn)
        file_conn.close()

        result = query_file_observations(db_path, "auth.ts", "csid-999")
        assert len(result["test_failures"]) > 0
        assert "TypeError" in result["test_failures"][0]["title"]

    def test_finds_edit_history(self, seeded_conn, tmp_path):
        db_path = tmp_path / "test.db"
        import sqlite3
        file_conn = sqlite3.connect(str(db_path))
        seeded_conn.backup(file_conn)
        file_conn.close()

        result = query_file_observations(db_path, "auth.ts", "csid-999")
        assert len(result["edit_history"]) > 0

    def test_excludes_current_session(self, seeded_conn, tmp_path):
        db_path = tmp_path / "test.db"
        import sqlite3
        file_conn = sqlite3.connect(str(db_path))
        seeded_conn.backup(file_conn)
        file_conn.close()

        # csid-003 owns the test_failure observation
        result = query_file_observations(db_path, "auth.ts", "csid-003")
        # Should exclude s3's observations since it's the "current" session
        for tf in result["test_failures"]:
            assert tf.get("branch") != "main" or "csid-003" not in str(tf)

    def test_returns_empty_for_unknown_file(self, seeded_conn, tmp_path):
        db_path = tmp_path / "test.db"
        import sqlite3
        file_conn = sqlite3.connect(str(db_path))
        seeded_conn.backup(file_conn)
        file_conn.close()

        result = query_file_observations(db_path, "nonexistent.xyz", "csid-999")
        assert len(result["test_failures"]) == 0
        assert len(result["edit_history"]) == 0

    def test_returns_empty_for_missing_db(self, tmp_path):
        result = query_file_observations(tmp_path / "nope.db", "auth.ts", "x")
        assert result == {"test_failures": [], "edit_history": []}


class TestQueryLearnedLessons:
    """query_learned_lessons: search learned + completed fields."""

    def test_finds_learned_by_filename(self, seeded_conn, tmp_path):
        db_path = tmp_path / "test.db"
        import sqlite3
        file_conn = sqlite3.connect(str(db_path))
        seeded_conn.backup(file_conn)
        file_conn.close()

        results = query_learned_lessons(db_path, "auth.ts")
        assert len(results) > 0
        assert any("auth.ts" in (r.get("learned", "") or "") for r in results)

    def test_finds_by_completed_field(self, seeded_conn, tmp_path):
        db_path = tmp_path / "test.db"
        import sqlite3
        file_conn = sqlite3.connect(str(db_path))
        seeded_conn.backup(file_conn)
        file_conn.close()

        results = query_learned_lessons(db_path, "api.ts")
        assert len(results) > 0

    def test_empty_for_unknown_file(self, seeded_conn, tmp_path):
        db_path = tmp_path / "test.db"
        import sqlite3
        file_conn = sqlite3.connect(str(db_path))
        seeded_conn.backup(file_conn)
        file_conn.close()

        results = query_learned_lessons(db_path, "zzz_nonexistent.py")
        assert len(results) == 0


class TestRateLimiting:
    """Rate limiting: per-file + per-session caps."""

    def test_load_recalled_empty(self):
        recalled = load_recalled("nonexistent-session-id")
        assert recalled == set()

    def test_mark_and_load(self):
        sid = f"test-recall-{os.getpid()}"
        mark_recalled(sid, "/path/to/file.ts")
        recalled = load_recalled(sid)
        assert "/path/to/file.ts" in recalled
        # Cleanup
        tracker = os.path.join(tempfile.gettempdir(), f".claude_recall_{sid}")
        os.unlink(tracker)

    def test_max_injections_constant(self):
        assert MAX_INJECTIONS == 10


class TestSourceExtensions:
    """SOURCE_EXTENSIONS should cover common source files."""

    def test_includes_common_types(self):
        for ext in [".ts", ".tsx", ".js", ".py", ".go", ".rs", ".java", ".sol"]:
            assert ext in SOURCE_EXTENSIONS, f"Missing: {ext}"

    def test_excludes_non_source(self):
        for ext in [".json", ".md", ".txt", ".yaml", ".toml", ".lock"]:
            assert ext not in SOURCE_EXTENSIONS, f"Should exclude: {ext}"
