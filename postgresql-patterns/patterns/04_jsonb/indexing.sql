-- JSONB indexing
-- GIN indexes speed up containment (@>) and jsonb_path_query searches.

-- GIN index on the whole metadata column (covers @> and ?)
CREATE INDEX IF NOT EXISTS idx_products_metadata
    ON products USING GIN (metadata);

-- Confirm the index exists
SELECT indexname, indexdef
FROM   pg_indexes
WHERE  tablename = 'products'
  AND  indexname = 'idx_products_metadata';

-- A specific expression index for repeated equality lookups on brand
CREATE INDEX IF NOT EXISTS idx_products_brand
    ON products ((metadata ->> 'brand'));

-- The planner will use idx_products_metadata for this @> query:
EXPLAIN (COSTS false)
SELECT name FROM products WHERE metadata @> '{"wireless": true}';

-- And idx_products_brand for this equality:
EXPLAIN (COSTS false)
SELECT name FROM products WHERE metadata ->> 'brand' = 'Sony';

-- Partial index example: only index wireless products
-- CREATE INDEX idx_wireless ON products ((metadata->>'wireless')) WHERE (metadata->>'wireless') = 'true';
