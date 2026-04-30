/**
 * Testcontainer-Postgres starter (TypeScript / vitest or jest)
 *
 * Why this exists: Real DB in tests catches migration drift, schema bugs, and
 * concurrency issues that mocked Repositories silently miss. Prefer this to
 * `jest.fn()` / `vi.fn()` for any Repository or Service that touches data.
 *
 * Required deps:
 *   pnpm add -D @testcontainers/postgresql pg
 *
 * Verify:
 *   pnpm vitest run src/repo/__tests__/userRepo.testcontainer.test.ts
 *
 * PHILOSOPHY: enables C2 (Enabling > Defensive) — the cheaper path becomes the
 * right path, so agents stop reaching for mocks under pressure.
 */

import { PostgreSqlContainer, StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import { Pool } from 'pg';
import { afterAll, beforeAll, beforeEach, describe, expect, test } from 'vitest';

let container: StartedPostgreSqlContainer;
let pool: Pool;

beforeAll(async () => {
  container = await new PostgreSqlContainer('postgres:16-alpine').start();
  pool = new Pool({ connectionString: container.getConnectionUri() });
  // Replace with your migration runner (drizzle/prisma/knex/raw SQL)
  await pool.query(`
    CREATE TABLE users (
      id SERIAL PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `);
}, 60_000); // pulling postgres image can be slow on first run

afterAll(async () => {
  await pool.end();
  await container.stop();
});

beforeEach(async () => {
  // Reset between tests so each is independent
  await pool.query('TRUNCATE users RESTART IDENTITY CASCADE');
});

describe('UserRepo (real Postgres)', () => {
  test('insert and fetch round-trips', async () => {
    // Replace with your actual Repository
    const repo = makeUserRepo(pool);
    const created = await repo.create({ email: 'a@example.com' });
    const found = await repo.findById(created.id);
    expect(found).toEqual(created);
  });
});

// Drop your real Repository factory here
function makeUserRepo(pool: Pool) {
  return {
    async create(input: { email: string }) {
      const { rows } = await pool.query(
        'INSERT INTO users (email) VALUES ($1) RETURNING *',
        [input.email],
      );
      return rows[0];
    },
    async findById(id: number) {
      const { rows } = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
      return rows[0] ?? null;
    },
  };
}
