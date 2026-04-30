"""
Testcontainer-Postgres starter (Python / pytest)

Why this exists: Real DB in tests catches migration drift, schema bugs, and
concurrency issues that mocked Repositories silently miss. Prefer this to
`MagicMock(spec=Repo)` for any Repository or Service that touches data.

Required deps:
    pip install testcontainers[postgres] psycopg[binary] pytest

Verify:
    pytest tests/repo/test_user_repo_testcontainer.py -v

PHILOSOPHY: enables C2 (Enabling > Defensive) — the cheaper path becomes the
right path, so agents stop reaching for mocks under pressure.
"""

from __future__ import annotations

import psycopg
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="module")
def pg():
    """Module-scoped real Postgres. Slow on first pull, fast after."""
    with PostgresContainer("postgres:16-alpine") as c:
        with psycopg.connect(c.get_connection_url()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """)
            conn.commit()
        yield c


@pytest.fixture
def conn(pg):
    """Per-test connection with truncate-reset so each test is independent."""
    with psycopg.connect(pg.get_connection_url()) as c:
        with c.cursor() as cur:
            cur.execute("TRUNCATE users RESTART IDENTITY CASCADE")
        c.commit()
        yield c


def make_user_repo(conn):
    """Replace with import from your real Repository."""
    class UserRepo:
        def create(self, email: str) -> dict:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (email) VALUES (%s) RETURNING id, email, created_at",
                    (email,),
                )
                row = cur.fetchone()
            conn.commit()
            return {"id": row[0], "email": row[1], "created_at": row[2]}

        def find_by_id(self, user_id: int) -> dict | None:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, created_at FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
            return None if row is None else {"id": row[0], "email": row[1], "created_at": row[2]}

    return UserRepo()


def test_insert_and_fetch_round_trips(conn):
    repo = make_user_repo(conn)
    created = repo.create("a@example.com")
    found = repo.find_by_id(created["id"])
    assert found == created
