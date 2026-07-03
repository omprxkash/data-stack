# Optimistic Locking

Pessimistic locking (`SELECT ... FOR UPDATE`) holds a row lock for the entire duration
of an operation. That's fine for fast operations, but it becomes a bottleneck when users
spend time reading a form before submitting it. Optimistic locking takes a different approach:
don't lock anything when reading — just check on write that nobody else changed the row first.

## What's in this folder

| File | What it does |
|------|--------------|
| `schema.sql` | `inventory` table with a `version INTEGER` column |
| `demo.sql` | Successful update, then a stale-version conflict that gets rejected |

## The pattern in two lines

```sql
-- Read (no lock)
SELECT id, qty, version FROM inventory WHERE id = 1;
-- → id=1, qty=100, version=1 (your app stores version=1)

-- Write (check the version you read)
UPDATE inventory
SET    qty = qty - 10, version = version + 1
WHERE  id = 1 AND version = 1;  -- the version you held
-- → 1 row updated: success
-- → 0 rows updated: someone else got there first — retry
```

The `WHERE version = ?` clause is the guard. If another transaction already incremented
the version, your update matches zero rows and returns `rowcount = 0`. The application
must check `rowcount` and decide whether to retry with fresh data.

## Why this works

The version column is the contract between readers and writers. Every successful write
bumps it. A write that arrives with a stale version number is automatically rejected —
no explicit locking, no deadlocks, no waiting.

## When to use it vs. `SELECT FOR UPDATE`

| | Optimistic | Pessimistic (`FOR UPDATE`) |
|-|-----------|---------------------------|
| Best for | Low-contention, human-facing forms | High-contention batch processing |
| Blocking | None (readers never wait) | Writers wait behind the lock holder |
| Retry logic | App must handle it | Database serializes automatically |
| Deadlock risk | None | Possible if multiple tables are involved |

## How to run

```bash
docker compose up -d
python runner/run.py 07_optimistic_locking
```

## Version column naming

I call it `version` here, but `updated_at TIMESTAMPTZ` can also work as the guard if your timestamps have microsecond precision. The trade-off: `version` is always unambiguous; timestamps can collide under high concurrency or on systems with low-resolution clocks.
