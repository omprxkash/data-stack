# postgresql-patterns

**Eight self-contained PostgreSQL patterns you can run against a real database in under five minutes.**

I built this because I kept revisiting the same handful of advanced Postgres techniques across different projects — window functions, row-level security, JSONB queries, partitioning — and wanted one place where each pattern is fully explained, runnable, and honest about the trade-offs. No slides, no toy examples that skip the hard parts. Just working SQL with seed data and comments that tell you what to expect.

---

## What's covered

| # | Pattern | What you'll learn |
|---|---------|------------------|
| 01 | [Window Functions](patterns/01_window_functions/) | `ROW_NUMBER`, `RANK`, `LAG/LEAD`, running totals, moving averages, `NTILE` |
| 02 | [Row-Level Security](patterns/02_row_level_security/) | Multi-tenant isolation at the database layer using `CREATE POLICY` |
| 03 | [Partitioning](patterns/03_partitioning/) | Range, list, and hash partitioning; partition pruning via `EXPLAIN` |
| 04 | [JSONB](patterns/04_jsonb/) | Operators (`->`, `->>`, `@>`), GIN indexing, `jsonb_set` updates |
| 05 | [Full-Text Search](patterns/05_full_text_search/) | `tsvector`/`tsquery`, generated columns, `ts_rank`, `ts_headline` |
| 06 | [Audit Triggers](patterns/06_audit_triggers/) | Generic history table capturing INSERT/UPDATE/DELETE as JSONB |
| 07 | [Optimistic Locking](patterns/07_optimistic_locking/) | Version-based conflict detection; what happens when a stale update arrives |
| 08 | [Queues with SKIP LOCKED](patterns/08_queues_skip_locked/) | Reliable job queue using a plain table; no double-claiming across workers |

---

## Tech stack

- **PostgreSQL 16** (via Docker — nothing to install locally)
- **Python 3.11** runner using `psycopg2-binary`
- **pytest** for assertions

---

## Quick start

```bash
# 1. Start Postgres
docker compose up -d

# 2. Install the Python runner dependency
pip install -r runner/requirements.txt

# 3. Run all 8 patterns at once
python runner/run.py --all

# 4. Or run a single pattern
python runner/run.py 01_window_functions
```

The runner reads `DATABASE_URL` from your environment. The default matches the Docker Compose setup:
```
postgresql://patuser:patpass@localhost:5432/patterns
```

If you want to point it at a different database, just export the variable:
```bash
export DATABASE_URL=postgresql://myuser:mypass@myhost:5432/mydb
python runner/run.py --all
```

---

## Project structure

```
postgresql-patterns/
├── patterns/
│   ├── 01_window_functions/
│   │   ├── schema.sql       # table definition
│   │   ├── seed.sql         # realistic sample data
│   │   ├── examples.sql     # the pattern with expected output in comments
│   │   └── README.md        # plain-English explanation
│   ├── 02_row_level_security/
│   │   └── ...
│   └── (one folder per pattern)
├── runner/
│   ├── run.py               # executes a pattern folder's SQL in order
│   └── requirements.txt
├── tests/
│   └── test_patterns.py     # pytest suite asserting known results
├── docker-compose.yml
└── README.md
```

Each pattern folder is self-contained. `schema.sql` always runs first and drops then recreates the table, so you can re-run any pattern safely.

---

## Running the tests

```bash
# Make sure Postgres is running first
docker compose up -d

pip install pytest psycopg2-binary
pytest tests/ -v
```

The test suite runs each pattern's SQL files in order and asserts specific output
(row counts, expected values, that the update returns zero rows on a stale version, etc.).

---

## Reading the patterns

Every `examples.sql` (or `demo.sql`) file includes expected output as SQL comments so you can read the file and understand the result without running it:

```sql
-- Successful update: version matches
UPDATE inventory
SET qty = qty - 10, version = version + 1
WHERE id = 1 AND version = 1;
-- → 1 row updated

-- Stale update: version already bumped by another writer
UPDATE inventory
SET qty = qty - 10, version = version + 1
WHERE id = 1 AND version = 1;
-- → 0 rows updated (application should retry)
```

---

## Known limitations and next ideas

- **No connection pooling** — the runner opens one connection per run. In production, use PgBouncer or a pool in your application layer.
- **Single-node only** — nothing here covers replication, Citus, or logical decoding.
- **No migration tooling** — patterns use `DROP TABLE IF EXISTS` + `CREATE TABLE` so they're always re-runnable. That's intentional for demos but not how you'd manage schema changes in a real app.
- Patterns I'd like to add: CTEs with `SEARCH` / `CYCLE` for hierarchies, `LISTEN`/`NOTIFY` for real-time events, advisory locks, `pg_stat_statements` for query profiling.

---

## Contributing

Issues and PRs welcome. If you've got a pattern that's bitten you in production and you wish you'd understood sooner — that's exactly the kind of thing this repo is for.

---

**Author:** [omprxkash](https://github.com/omprxkash) · MIT License
