/**
 * Real-persistence Repository skeleton (TypeScript)
 *
 * Why this exists: in-memory `Map` Repositories are a v7 anti-pattern. They
 * pass tests, don't survive restart, hide migration bugs, and silently break
 * production. This template shows the minimum real Repository.
 *
 * Required deps:
 *   pnpm add pg
 *   # Optional ORM: drizzle / prisma / kysely
 *
 * PHILOSOPHY: enables C4 progress.json `persistence_real` dimension. Pair with
 * testcontainer-postgres.ts for the test side.
 */

import type { Pool, PoolClient } from 'pg';

// Domain entity — keep separate from row shape
export type User = {
  id: number;
  email: string;
  createdAt: Date;
};

// Optional: row→entity mapper if column names differ from field names
function rowToUser(row: { id: number; email: string; created_at: Date }): User {
  return { id: row.id, email: row.email, createdAt: row.created_at };
}

export class UserRepo {
  constructor(private readonly pool: Pool) {}

  async create(input: { email: string }): Promise<User> {
    const { rows } = await this.pool.query<{
      id: number;
      email: string;
      created_at: Date;
    }>(
      `INSERT INTO users (email) VALUES ($1)
       RETURNING id, email, created_at`,
      [input.email],
    );
    return rowToUser(rows[0]);
  }

  async findById(id: number): Promise<User | null> {
    const { rows } = await this.pool.query<{
      id: number;
      email: string;
      created_at: Date;
    }>(
      `SELECT id, email, created_at FROM users WHERE id = $1`,
      [id],
    );
    return rows[0] ? rowToUser(rows[0]) : null;
  }

  // Multi-statement work — pass in a client to keep it on a single connection
  async withTransaction<T>(work: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      const result = await work(client);
      await client.query('COMMIT');
      return result;
    } catch (e) {
      await client.query('ROLLBACK');
      throw e;
    } finally {
      client.release();
    }
  }
}

// What this template intentionally does NOT do (and why):
// - No `Map<number, User>` field. That is the in-memory anti-pattern v7 surfaces.
// - No silent error swallowing (catch + return-null). Errors propagate; callers handle.
// - No mock-friendly singleton. Inject the Pool so testcontainers work cleanly.
