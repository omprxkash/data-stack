-- Hash partitioning
-- Distributes rows evenly across N buckets — good when there's no natural range or list.

DROP TABLE IF EXISTS user_activity CASCADE;

CREATE TABLE user_activity (
    id       BIGSERIAL,
    user_id  BIGINT     NOT NULL,
    action   TEXT       NOT NULL,
    ts       TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY HASH (user_id);

-- Four buckets
CREATE TABLE user_activity_p0 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_activity_p1 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE user_activity_p2 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE user_activity_p3 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Seed 20 events across 10 users
INSERT INTO user_activity (user_id, action)
SELECT
    (gs % 10) + 1 AS user_id,
    CASE gs % 3
        WHEN 0 THEN 'login'
        WHEN 1 THEN 'view_page'
        ELSE        'logout'
    END AS action
FROM generate_series(1, 20) gs;

-- Distribution should be roughly even
SELECT tableoid::regclass AS partition, count(*) AS rows
FROM   user_activity
GROUP  BY tableoid
ORDER  BY partition;

-- With hash partitioning, looking up a specific user_id only scans one partition:
EXPLAIN (ANALYZE false, COSTS false)
SELECT * FROM user_activity WHERE user_id = 5;
