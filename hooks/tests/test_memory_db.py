"""Tests for memory_db.py — core DB operations with in-memory SQLite."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import memory_db


class TestSaveObservation:
    """save_observation: write + dedup + cap."""

    def test_saves_observation(self, memory_conn):
        result = memory_db.save_observation(
            memory_conn, "s1",
            kind="edit", title="Edit: auth.ts",
            tool_name="Edit", files=["src/auth.ts"]
        )
        assert result is True
        rows = memory_conn.execute("SELECT * FROM observations WHERE session_id = 's1'").fetchall()
        assert len(rows) == 1
        assert rows[0]["kind"] == "edit"
        assert "auth.ts" in rows[0]["files"]

    def test_dedup_same_observation(self, memory_conn):
        memory_db.save_observation(memory_conn, "s1", kind="edit", title="Edit: auth.ts")
        result = memory_db.save_observation(memory_conn, "s1", kind="edit", title="Edit: auth.ts")
        assert result is False  # deduped
        count = memory_conn.execute("SELECT COUNT(*) FROM observations WHERE session_id = 's1'").fetchone()[0]
        assert count == 1

    def test_different_titles_not_deduped(self, memory_conn):
        memory_db.save_observation(memory_conn, "s1", kind="edit", title="Edit: auth.ts")
        memory_db.save_observation(memory_conn, "s1", kind="edit", title="Edit: db.ts")
        count = memory_conn.execute("SELECT COUNT(*) FROM observations WHERE session_id = 's1'").fetchone()[0]
        assert count == 2


class TestSaveStructuredSummary:
    """save_structured_summary: structured insert with status tracking."""

    def test_saves_summary(self, memory_conn):
        # Need a session first
        memory_conn.execute(
            "INSERT INTO sessions (id, started_at, last_active) VALUES ('s1', '2026-03-20', '2026-03-20')"
        )
        memory_conn.commit()

        result = memory_db.save_structured_summary(
            memory_conn, "s1",
            request="Build a complete authentication system with JWT tokens and refresh flow",
            completed="Created auth.ts with JWT validation and token refresh | Added db.ts connection pooling",
            learned="Validate token format in auth.ts before decode to avoid crashes",
            next_steps="Add refresh token rotation and session invalidation",
            source="model", model="haiku"
        )
        assert result is True

        row = memory_conn.execute(
            "SELECT * FROM session_summaries WHERE session_id = 's1'"
        ).fetchone()
        assert row["status"] == "ready"  # total_len >= 100 required
        assert "authentication" in row["request"]
        assert "auth.ts" in row["learned"]

    def test_no_duplicate_summary(self, memory_conn):
        memory_conn.execute(
            "INSERT INTO sessions (id, started_at, last_active) VALUES ('s1', '2026-03-20', '2026-03-20')"
        )
        memory_conn.commit()
        memory_db.save_structured_summary(
            memory_conn, "s1", request="v1", completed="v1",
            learned="", next_steps="", source="model", model="haiku"
        )
        # Second save should not crash (UNIQUE constraint)
        result = memory_db.save_structured_summary(
            memory_conn, "s1", request="v2", completed="v2",
            learned="", next_steps="", source="model", model="haiku"
        )
        # Should update or return False, not crash
        assert result is not None


class TestSearch:
    """FTS5 search across sessions."""

    def test_finds_by_summary(self, seeded_conn):
        results = memory_db.search(seeded_conn, "auth module", limit=5)
        assert len(results) > 0
        assert any("s1" == r["id"] for r in results)

    def test_finds_by_branch(self, seeded_conn):
        results = memory_db.search(seeded_conn, "feat/api", limit=5)
        assert any("s2" == r["id"] for r in results)

    def test_empty_query_returns_empty(self, seeded_conn):
        results = memory_db.search(seeded_conn, "nonexistent_xyz_123", limit=5)
        assert len(results) == 0


class TestGetRecent:
    """get_recent: most recent sessions with structured summary."""

    def test_returns_recent(self, seeded_conn):
        results = memory_db.get_recent(seeded_conn, limit=2)
        assert len(results) == 2
        # Most recent first
        assert results[0]["id"] == "s3"

    def test_includes_structured_summary(self, seeded_conn):
        results = memory_db.get_recent(seeded_conn, limit=3)
        s1 = next(r for r in results if r["id"] == "s1")
        assert s1["ss_request"] == "Build auth system"


class TestGetObservations:
    """get_observations: observations for a session."""

    def test_returns_observations(self, seeded_conn):
        obs = memory_db.get_observations(seeded_conn, "s1")
        assert len(obs) == 2
        assert obs[0]["kind"] == "edit"

    def test_empty_for_unknown_session(self, seeded_conn):
        obs = memory_db.get_observations(seeded_conn, "nonexistent")
        assert len(obs) == 0


class TestCleanup:
    """cleanup: delete old sessions + cascade."""

    def test_deletes_old_sessions(self, seeded_conn):
        # All seeded sessions are from 2026-03, cleanup with 0 days retention
        deleted = memory_db.cleanup(seeded_conn, days=0)
        assert deleted == 3
        remaining = seeded_conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        assert remaining == 0

    def test_cascades_to_observations(self, seeded_conn):
        memory_db.cleanup(seeded_conn, days=0)
        obs_count = seeded_conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        assert obs_count == 0

    def test_cascades_to_summaries(self, seeded_conn):
        memory_db.cleanup(seeded_conn, days=0)
        sum_count = seeded_conn.execute("SELECT COUNT(*) FROM session_summaries").fetchone()[0]
        assert sum_count == 0


class TestSetInitialRequest:
    """set_initial_request: stores first prompt only."""

    def test_stores_request(self, memory_conn):
        memory_conn.execute(
            "INSERT INTO sessions (id, started_at, last_active) VALUES ('s1', '2026-03-20', '2026-03-20')"
        )
        memory_conn.commit()
        result = memory_db.set_initial_request(memory_conn, "s1", "Build auth")
        assert result is True
        row = memory_conn.execute("SELECT initial_request FROM sessions WHERE id = 's1'").fetchone()
        assert row["initial_request"] == "Build auth"

    def test_does_not_overwrite(self, memory_conn):
        memory_conn.execute(
            "INSERT INTO sessions (id, started_at, last_active, initial_request) "
            "VALUES ('s1', '2026-03-20', '2026-03-20', 'First request')"
        )
        memory_conn.commit()
        memory_db.set_initial_request(memory_conn, "s1", "Second request")
        row = memory_conn.execute("SELECT initial_request FROM sessions WHERE id = 's1'").fetchone()
        assert row["initial_request"] == "First request"
