"""Tests for mid_workflow_recall.py — Grep advisory + rate limiting.

Memory归位 (2026-06-02): query_file_observations / query_learned_lessons were
removed (memory.db is gone — claude-mem now owns cross-session recall), so their
tests were dropped. Remaining surface: rate limiting, source-extension gating,
and the symbol-query heuristic that drives the Grep routing advisory.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from mid_workflow_recall import (
    load_recalled,
    mark_recalled,
    SOURCE_EXTENSIONS,
    MAX_INJECTIONS,
    _looks_like_symbol_query,
)


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


class TestSymbolQueryHeuristic:
    """_looks_like_symbol_query: gates the Grep symbol-routing advisory."""

    def test_matches_symbol_declarations(self):
        assert _looks_like_symbol_query("class UserRepo")
        assert _looks_like_symbol_query("function authenticate")
        assert _looks_like_symbol_query("getUserById")

    def test_rejects_fuzzy_text(self):
        assert not _looks_like_symbol_query("TODO")
        assert not _looks_like_symbol_query("error.*timeout")
        assert not _looks_like_symbol_query("foo bar")
