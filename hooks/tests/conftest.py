"""Shared fixtures for hook tests.

Uses in-memory SQLite (real DB engine, not mocks).
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

# Add hooks directory to path for imports
HOOKS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_DIR))


@pytest.fixture
def memory_conn():
    """In-memory SQLite connection with full schema initialized."""
    import memory_db

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    # Create schema (extracted from memory_db.init_db)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            last_active TEXT NOT NULL,
            branch TEXT DEFAULT '',
            cwd TEXT DEFAULT '',
            files_modified TEXT DEFAULT '[]',
            summary TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            stop_count INTEGER DEFAULT 0,
            content_session_id TEXT DEFAULT '',
            initial_request TEXT DEFAULT ''
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
            id, branch, cwd, files_modified, summary, tags
        );

        CREATE TABLE IF NOT EXISTS session_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            source TEXT NOT NULL DEFAULT 'model',
            model TEXT DEFAULT '',
            request TEXT DEFAULT '',
            completed TEXT DEFAULT '',
            learned TEXT DEFAULT '',
            next_steps TEXT DEFAULT '',
            summary_hash TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(session_id)
        );

        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT DEFAULT '',
            tool_name TEXT DEFAULT '',
            files TEXT DEFAULT '[]',
            content_hash TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_obs_session ON observations(session_id);
        CREATE INDEX IF NOT EXISTS idx_obs_kind ON observations(kind);
        CREATE INDEX IF NOT EXISTS idx_summaries_session ON session_summaries(session_id);
    """)
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture
def seeded_conn(memory_conn):
    """In-memory DB pre-seeded with sample sessions and observations."""
    conn = memory_conn

    # Insert sample sessions
    conn.executescript("""
        INSERT INTO sessions (id, started_at, last_active, branch, cwd,
            files_modified, summary, content_session_id, initial_request)
        VALUES
        ('s1', '2026-03-20T10:00:00', '2026-03-20T11:00:00', 'main',
         '/project', '["src/auth.ts","src/db.ts"]', 'Built auth module',
         'csid-001', 'Build an auth system'),
        ('s2', '2026-03-21T10:00:00', '2026-03-21T11:00:00', 'feat/api',
         '/project', '["src/api.ts"]', 'Added API endpoints',
         'csid-002', 'Add REST API'),
        ('s3', '2026-03-22T10:00:00', '2026-03-22T11:00:00', 'main',
         '/project', '["src/auth.ts","tests/auth.test.ts"]', '',
         'csid-003', 'Fix auth bug');

        INSERT INTO sessions_fts (id, branch, cwd, files_modified, summary, tags)
        VALUES
        ('s1', 'main', '/project', 'src/auth.ts src/db.ts', 'Built auth module', ''),
        ('s2', 'feat/api', '/project', 'src/api.ts', 'Added API endpoints', ''),
        ('s3', 'main', '/project', 'src/auth.ts tests/auth.test.ts', '', '');

        INSERT INTO session_summaries (session_id, status, request, completed, learned, next_steps, created_at)
        VALUES
        ('s1', 'ready', 'Build auth system', 'Created auth.ts with JWT validation | Added db.ts connection pool',
         'Validate token in auth.ts before decode | Use connection pooling in db.ts',
         'Add refresh token support', '2026-03-20T11:00:00'),
        ('s2', 'ready', 'Add REST API', 'Created api.ts with CRUD endpoints',
         'Use zod for request validation in api.ts', '', '2026-03-21T11:00:00');

        INSERT INTO observations (session_id, kind, title, detail, tool_name, files, content_hash, created_at)
        VALUES
        ('s1', 'edit', 'Edit: src/auth.ts', '', 'Edit', '["src/auth.ts"]', 'h1', '2026-03-20T10:30:00'),
        ('s1', 'edit', 'Write: src/db.ts', '', 'Write', '["src/db.ts"]', 'h2', '2026-03-20T10:35:00'),
        ('s3', 'test_failure', 'FAIL src/auth.ts - TypeError: token undefined',
         'npm test -- auth.test.ts', 'Bash', '["src/auth.ts","tests/auth.test.ts"]', 'h3', '2026-03-22T10:30:00'),
        ('s3', 'command', 'git commit -m "fix: auth token validation"', '', 'Bash', '[]', 'h4', '2026-03-22T10:45:00');
    """)
    conn.commit()

    yield conn


def make_hook_input(**kwargs):
    """Build a hook stdin JSON payload."""
    return json.dumps(kwargs)
