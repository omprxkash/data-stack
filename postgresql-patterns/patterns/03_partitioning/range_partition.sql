-- Range partitioning by month
-- A common pattern for time-series data: one partition per month.
-- The planner prunes irrelevant partitions automatically.

DROP TABLE IF EXISTS events CASCADE;

CREATE TABLE events (
    id          BIGSERIAL,
    event_type  TEXT        NOT NULL,
    payload     JSONB       NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for Q1 2024
CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE events_2024_03 PARTITION OF events
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Default partition catches anything outside the explicit ranges
CREATE TABLE events_default PARTITION OF events DEFAULT;

-- Seed some events
INSERT INTO events (event_type, payload, created_at) VALUES
    ('page_view',  '{"path": "/home"}',    '2024-01-15 10:00:00+00'),
    ('page_view',  '{"path": "/pricing"}', '2024-01-22 14:30:00+00'),
    ('signup',     '{"plan": "free"}',     '2024-02-05 09:15:00+00'),
    ('upgrade',    '{"plan": "pro"}',      '2024-02-18 16:00:00+00'),
    ('page_view',  '{"path": "/docs"}',    '2024-03-03 11:45:00+00'),
    ('churn',      '{"reason": "price"}',  '2024-03-28 08:00:00+00');

-- Partition pruning: Postgres only scans events_2024_02
EXPLAIN (ANALYZE false, COSTS false, FORMAT TEXT)
SELECT * FROM events
WHERE  created_at >= '2024-02-01'
  AND  created_at <  '2024-03-01';

-- Shows: "Seq Scan on events_2024_02" — other partitions are excluded.

-- Count per partition
SELECT
    tableoid::regclass AS partition,
    count(*)           AS row_count
FROM   events
GROUP  BY tableoid
ORDER  BY partition;

-- Expected:
--  partition       | row_count
-- -----------------+-----------
--  events_2024_01  |         2
--  events_2024_02  |         2
--  events_2024_03  |         2

-- Note: enable_partition_pruning is ON by default (Postgres 11+). If disabled, all partitions scan.
