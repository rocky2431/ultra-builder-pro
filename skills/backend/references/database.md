# Database Optimization Reference

SQL optimization, indexing strategies, and migration management.

---

## Schema Design Principles

### Normalization Levels

| Form | Description | When to Use |
|------|-------------|-------------|
| 1NF | Atomic values, no repeating groups | Always |
| 2NF | 1NF + no partial dependencies | OLTP systems |
| 3NF | 2NF + no transitive dependencies | Most applications |
| BCNF | 3NF + every determinant is a candidate key | Complex relationships |
| Denormalized | Strategic redundancy | Read-heavy, analytics |

### Naming Conventions

```sql
-- Tables: plural, snake_case
CREATE TABLE users (...);
CREATE TABLE order_items (...);

-- Columns: singular, snake_case
user_id, created_at, is_active

-- Primary keys: id or table_id
id, user_id (in foreign references)

-- Foreign keys: singular_table_id
user_id, order_id

-- Indexes: ix_table_column(s)
ix_users_email, ix_orders_user_id_created_at

-- Constraints
pk_users, fk_orders_user_id, uq_users_email, ck_users_role
```

### Data Types Best Practices

```sql
-- IDs: UUID or BIGSERIAL
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
-- or
id BIGSERIAL PRIMARY KEY

-- Strings: VARCHAR with limits
email VARCHAR(255) NOT NULL
name VARCHAR(100) NOT NULL
description TEXT  -- Only for unlimited text

-- Numbers
amount DECIMAL(12, 2)  -- Money
quantity INTEGER
rating SMALLINT CHECK (rating BETWEEN 1 AND 5)

-- Timestamps
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete

-- Booleans
is_active BOOLEAN NOT NULL DEFAULT true

-- JSON (when needed)
metadata JSONB DEFAULT '{}'::jsonb
```

---

## Indexing Strategies

### Index Types

| Type | Use Case | Example |
|------|----------|---------|
| B-tree | Default, range queries | `CREATE INDEX ix_users_name ON users(name)` |
| Hash | Equality only | `CREATE INDEX ix_users_email ON users USING HASH(email)` |
| GiST | Geometric, full-text | `CREATE INDEX ix_posts_location ON posts USING GIST(location)` |
| GIN | Arrays, JSONB | `CREATE INDEX ix_posts_tags ON posts USING GIN(tags)` |
| BRIN | Large sorted tables | `CREATE INDEX ix_logs_created ON logs USING BRIN(created_at)` |

### Composite Indexes

```sql
-- Order matters! Most selective first
CREATE INDEX ix_orders_user_status_date
ON orders(user_id, status, created_at DESC);

-- Covers queries like:
WHERE user_id = ?
WHERE user_id = ? AND status = ?
WHERE user_id = ? AND status = ? ORDER BY created_at DESC

-- Does NOT cover:
WHERE status = ?  -- Missing user_id prefix
WHERE created_at > ?  -- Missing user_id, status prefix
```

### Covering Indexes

```sql
-- Include non-key columns to avoid table lookup
CREATE INDEX ix_users_email_include
ON users(email) INCLUDE (name, role);

-- Satisfies:
SELECT name, role FROM users WHERE email = ?
-- Without accessing the table!
```

### Partial Indexes

```sql
-- Index only relevant rows
CREATE INDEX ix_orders_pending
ON orders(created_at)
WHERE status = 'pending';

-- Much smaller than full index
-- Optimizes: SELECT * FROM orders WHERE status = 'pending'
```

### Expression Indexes

```sql
-- Index computed values
CREATE INDEX ix_users_email_lower
ON users(LOWER(email));

-- Optimizes:
WHERE LOWER(email) = 'user@example.com'
```

---

## Query Optimization

### EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 10;

-- Key metrics to check:
-- - Seq Scan vs Index Scan
-- - Actual rows vs estimated rows
-- - Buffer hits vs reads
-- - Execution time
```

### Common Performance Issues

#### N+1 Query Problem

```sql
-- Bad: N+1 queries
SELECT * FROM users WHERE id = 1;
SELECT * FROM orders WHERE user_id = 1;  -- For each user

-- Good: Single query with JOIN
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.id IN (1, 2, 3, ...);

-- Or use lateral join for complex subqueries
SELECT u.*, recent_orders.*
FROM users u
LEFT JOIN LATERAL (
    SELECT *
    FROM orders o
    WHERE o.user_id = u.id
    ORDER BY o.created_at DESC
    LIMIT 5
) recent_orders ON true;
```

#### Missing Index

```sql
-- Check for sequential scans on large tables
SELECT schemaname, relname, seq_scan, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
ORDER BY seq_scan DESC;

-- Find missing indexes
SELECT
    schemaname || '.' || relname as table,
    seq_scan as sequential_scans,
    idx_scan as index_scans,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE seq_scan > 100
    AND n_live_tup > 10000
ORDER BY seq_scan DESC;
```

#### Inefficient Pagination

```sql
-- Bad: OFFSET for large pages
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 10000;
-- Scans 10020 rows!

-- Good: Keyset pagination
SELECT * FROM orders
WHERE created_at < '2024-01-15T10:30:00Z'
ORDER BY created_at DESC
LIMIT 20;
-- Only scans 20 rows
```

#### Expensive COUNT

```sql
-- Bad: Exact count on large table
SELECT COUNT(*) FROM orders;  -- Full table scan

-- Good: Approximate count
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'orders';

-- Or use window function for pagination
SELECT *, COUNT(*) OVER() as total
FROM orders
LIMIT 20;
```

### Query Patterns

#### Batch Operations

```sql
-- Bad: Individual inserts
INSERT INTO users (email) VALUES ('a@example.com');
INSERT INTO users (email) VALUES ('b@example.com');

-- Good: Batch insert
INSERT INTO users (email) VALUES
    ('a@example.com'),
    ('b@example.com'),
    ('c@example.com');

-- With conflict handling
INSERT INTO users (email, name)
VALUES ('a@example.com', 'Alice')
ON CONFLICT (email)
DO UPDATE SET name = EXCLUDED.name, updated_at = NOW();
```

#### Avoiding SELECT *

```sql
-- Bad: Select all columns
SELECT * FROM users;

-- Good: Select only needed columns
SELECT id, email, name FROM users;

-- Especially with JOINs
SELECT u.id, u.name, o.total
FROM users u
JOIN orders o ON o.user_id = u.id;
```

---

## Connection Management

### Connection Pooling

```javascript
// Node.js with pg-pool
const pool = new Pool({
  max: 20,                    // Maximum connections
  idleTimeoutMillis: 30000,   // Close idle connections
  connectionTimeoutMillis: 2000, // Wait for connection
});

// Use pool.query for single queries
await pool.query('SELECT * FROM users WHERE id = $1', [userId]);

// Use client for transactions
const client = await pool.connect();
try {
  await client.query('BEGIN');
  await client.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2', [amount, fromId]);
  await client.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [amount, toId]);
  await client.query('COMMIT');
} catch (e) {
  await client.query('ROLLBACK');
  throw e;
} finally {
  client.release();
}
```

### Pool Size Guidelines

```
# Formula
pool_size = (core_count * 2) + effective_spindle_count

# For SSDs (typical)
pool_size = (4 cores * 2) + 1 = 9

# Recommendations
Development: 5-10 connections
Production: 20-50 connections
High traffic: 50-100 (with PgBouncer)
```

---

## Migrations

### Migration Best Practices

```sql
-- migrations/001_create_users.sql

-- Up
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users(email);

-- Down
DROP TABLE users;
```

### Safe Schema Changes

| Operation | Safe? | Mitigation |
|-----------|-------|------------|
| Add column (nullable) | Yes | - |
| Add column (NOT NULL) | No | Add nullable, backfill, add constraint |
| Drop column | No | Remove code references first |
| Add index | No | Use CONCURRENTLY |
| Rename column | No | Add new, migrate, drop old |
| Change type | No | Add new column, migrate, drop old |

```sql
-- Safe index creation (doesn't lock table)
CREATE INDEX CONCURRENTLY ix_users_status ON users(status);

-- Safe NOT NULL addition
ALTER TABLE users ADD COLUMN role VARCHAR(50);
UPDATE users SET role = 'user' WHERE role IS NULL;
ALTER TABLE users ALTER COLUMN role SET NOT NULL;
ALTER TABLE users ALTER COLUMN role SET DEFAULT 'user';
```

---

## Monitoring Queries

### Slow Query Log

```sql
-- PostgreSQL: Find slow queries
SELECT
    calls,
    round(total_exec_time::numeric, 2) as total_time_ms,
    round(mean_exec_time::numeric, 2) as mean_time_ms,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Lock Monitoring

```sql
-- Find blocking queries
SELECT
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking
    ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE blocked.pid != blocking.pid;
```

### Table Statistics

```sql
-- Table size and bloat
SELECT
    schemaname,
    relname,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

---

## Common Issues Checklist

- [ ] All foreign keys have indexes
- [ ] Frequently filtered columns are indexed
- [ ] Composite indexes match query patterns
- [ ] No unnecessary indexes (slows writes)
- [ ] Large tables have partitioning strategy
- [ ] Vacuum and analyze running regularly
- [ ] Connection pool properly sized
- [ ] Slow query log enabled
- [ ] Proper data types used (avoid TEXT for everything)
