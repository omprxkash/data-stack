-- JSONB query operators
-- Run after schema.sql and seed.sql.

-- 1. Arrow operators: -> returns JSONB, ->> returns text
SELECT
    name,
    metadata -> 'brand'        AS brand_json,   -- JSONB value
    metadata ->> 'brand'       AS brand_text,   -- text value
    metadata ->> 'price_usd'   AS price
FROM  products;

-- 2. Nested access with #>> (path as array)
SELECT
    name,
    metadata #>> '{dimensions, width_cm}' AS width_cm
FROM  products
WHERE metadata #>> '{dimensions, width_cm}' IS NOT NULL;

-- 3. Containment operator @>
-- Find all wireless products
SELECT name, metadata ->> 'brand' AS brand
FROM   products
WHERE  metadata @> '{"wireless": true}';

-- Expected:
--  name                       | brand
-- ----------------------------+----------
--  Mechanical Keyboard        | Keychron
--  Noise-Cancelling Headphones| Sony

-- 4. jsonb_path_query — find products tagged "productivity"
SELECT name
FROM   products,
       jsonb_path_query(metadata, '$.tags[*] ? (@ == "productivity")') AS tag
ORDER  BY name;

-- 5. Filter by nested numeric value
SELECT name, (metadata ->> 'price_usd')::numeric AS price_usd
FROM   products
WHERE  (metadata ->> 'price_usd')::numeric < 100
ORDER  BY price_usd;

-- 6. jsonb_set — update a single field without replacing the whole object
UPDATE products
SET    metadata = jsonb_set(metadata, '{price_usd}', '119.99')
WHERE  name = 'Mechanical Keyboard';

SELECT name, metadata ->> 'price_usd' AS new_price
FROM   products
WHERE  name = 'Mechanical Keyboard';
-- Expected: 119.99

-- 7. Array element access
SELECT
    name,
    metadata -> 'tags' -> 0   AS first_tag
FROM  products
WHERE  jsonb_typeof(metadata -> 'tags') = 'array';

-- Merge operator: metadata || '{"on_sale": true}' adds keys without replacing the whole object.
