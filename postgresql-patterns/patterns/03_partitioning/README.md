# Table Partitioning

Partitioning splits one logical table into multiple physical child tables.
The query planner knows which partitions can possibly contain the rows you need,
and skips the rest entirely — this is called partition pruning, and it's why
queries on a 10-billion-row partitioned table can return in milliseconds when
they'd take minutes on a plain table.

## What's in this folder

| File | What it does |
|------|--------------|
| `range_partition.sql` | Monthly partitions on `created_at` for an `events` table |
| `list_partition.sql` | Per-region partitions for a `regional_sales` table |
| `hash_partition.sql` | 4-bucket hash distribution for a `user_activity` table |

## Three partitioning strategies

### Range — use for dates and numeric ranges
```sql
CREATE TABLE events PARTITION BY RANGE (created_at);
CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```
Best for time-series data where you query by date range and want to drop old partitions cheaply.

### List — use for categorical values
```sql
CREATE TABLE regional_sales PARTITION BY LIST (region);
CREATE TABLE regional_sales_north PARTITION OF regional_sales
    FOR VALUES IN ('North', 'Northeast', 'Northwest');
```
Best when you have a fixed, known set of categories and often filter by them.

### Hash — use when there's no natural key
```sql
CREATE TABLE user_activity PARTITION BY HASH (user_id);
CREATE TABLE user_activity_p0 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```
Distributes rows evenly across N buckets. Use it to reduce index size or parallelize maintenance.

## Seeing pruning in action

```sql
EXPLAIN (COSTS false)
SELECT * FROM events
WHERE created_at >= '2024-02-01' AND created_at < '2024-03-01';
-- Output shows only "Seq Scan on events_2024_02" — the other partitions are skipped.
```

## Practical tips

- Always create a `DEFAULT` partition to catch values outside your explicit ranges/lists — otherwise an out-of-range insert will error.
- Dropping a partition (`DROP TABLE events_2024_01`) is near-instant; `DELETE FROM events WHERE ...` is not.
- Global indexes across all partitions are supported but local (per-partition) indexes are faster to build and maintain.

## How to run

```bash
docker compose up -d
python runner/run.py 03_partitioning
```

## Sub-partitioning

Postgres supports sub-partitioning: range-by-month can be sub-partitioned list-by-region.
Rarely needed, but it's there when you have two orthogonal boundaries.
