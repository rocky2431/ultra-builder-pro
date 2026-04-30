/**
 * Vertical-Slice integration test (TypeScript)
 *
 * Why this exists: proves HTTP entry → use case → domain → DB → response works
 * end-to-end. ONE such test per feature is the difference between "single tasks
 * pass / project doesn't run" (the failure mode v7 was built to fix) and
 * actual deliverable software.
 *
 * Required deps:
 *   pnpm add -D supertest @testcontainers/postgresql pg vitest
 *
 * Verify:
 *   pnpm vitest run src/__tests__/auth.vertical-slice.test.ts
 *
 * PHILOSOPHY: enables C4 (Incremental Validation) — the `vertical_slice`
 * dimension in progress.json is satisfied by tests like this.
 */

import { PostgreSqlContainer, StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import { Pool } from 'pg';
import request from 'supertest';
import { afterAll, beforeAll, describe, expect, test } from 'vitest';

// Replace with your real app/server factory
import { buildApp } from '../app';

let container: StartedPostgreSqlContainer;
let pool: Pool;
let app: ReturnType<typeof buildApp>;

beforeAll(async () => {
  container = await new PostgreSqlContainer('postgres:16-alpine').start();
  pool = new Pool({ connectionString: container.getConnectionUri() });
  // Run migrations
  await pool.query(`CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT UNIQUE)`);
  app = buildApp({ db: pool });
}, 60_000);

afterAll(async () => {
  await pool.end();
  await container.stop();
});

describe('vertical slice: POST /signup', () => {
  test('inserts a row, returns 201, body matches input email', async () => {
    const before = await pool.query('SELECT count(*) FROM users');
    const beforeCount = parseInt(before.rows[0].count, 10);

    const res = await request(app)
      .post('/signup')
      .send({ email: 'vertical@example.com' })
      .expect(201);

    // 1. response shape
    expect(res.body.email).toBe('vertical@example.com');
    expect(res.body.id).toBeGreaterThan(0);

    // 2. real DB write occurred
    const after = await pool.query('SELECT count(*) FROM users');
    expect(parseInt(after.rows[0].count, 10)).toBe(beforeCount + 1);

    // 3. data is persistable / queryable
    const row = await pool.query('SELECT email FROM users WHERE id = $1', [res.body.id]);
    expect(row.rows[0].email).toBe('vertical@example.com');
  });
});
