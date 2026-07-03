-- List partitioning by region
-- Each partition holds rows for a fixed set of values — good for categorical data.

DROP TABLE IF EXISTS regional_sales CASCADE;

CREATE TABLE regional_sales (
    id         BIGSERIAL,
    region     TEXT         NOT NULL,
    product    TEXT         NOT NULL,
    revenue    NUMERIC(12,2) NOT NULL,
    sale_date  DATE          NOT NULL
) PARTITION BY LIST (region);

CREATE TABLE regional_sales_north PARTITION OF regional_sales
    FOR VALUES IN ('North', 'Northeast', 'Northwest');

CREATE TABLE regional_sales_south PARTITION OF regional_sales
    FOR VALUES IN ('South', 'Southeast', 'Southwest');

CREATE TABLE regional_sales_other PARTITION OF regional_sales DEFAULT;

INSERT INTO regional_sales (region, product, revenue, sale_date) VALUES
    ('North',     'Widget A', 5000.00, '2024-01-10'),
    ('Northeast', 'Widget B', 3200.00, '2024-01-15'),
    ('South',     'Widget A', 4100.00, '2024-01-12'),
    ('Southwest', 'Widget C', 2800.00, '2024-01-20'),
    ('East',      'Widget D', 1500.00, '2024-01-25');  -- goes to _other

-- Partition pruning example: only scans _south partition
EXPLAIN (ANALYZE false, COSTS false)
SELECT * FROM regional_sales WHERE region = 'South';

-- Row count by partition
SELECT tableoid::regclass AS partition, count(*) AS rows
FROM   regional_sales
GROUP  BY tableoid
ORDER  BY partition;
