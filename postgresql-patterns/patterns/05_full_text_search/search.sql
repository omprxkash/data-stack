-- Full-text search
-- Run after schema.sql and seed.sql.
-- The search_vec column is generated automatically; we just need the GIN index.

-- Create the GIN index on the generated tsvector column
CREATE INDEX IF NOT EXISTS idx_articles_search
    ON articles USING GIN (search_vec);

-- Basic search: find articles about "index" or "indexes"
SELECT id, title, author
FROM   articles
WHERE  search_vec @@ to_tsquery('english', 'index | indexes');

-- Expected:
--  id | title                              | author
-- ----+------------------------------------+-----------
--   2 | Understanding database indexes     | omprxkash

-- Multi-word phrase: articles mentioning "row" AND "security"
SELECT id, title
FROM   articles
WHERE  search_vec @@ to_tsquery('english', 'row & security');

-- Expected:
--  id | title
-- ----+-------------------------------------------
--   3 | Row-level security in multi-tenant apps

-- plainto_tsquery is friendlier: no need for & or |, just natural language
SELECT id, title
FROM   articles
WHERE  search_vec @@ plainto_tsquery('english', 'partition table faster');

-- Expected:
--  id | title
-- ----+-------------------------------------------
--   4 | Partitioning large tables by date

-- phraseto_tsquery preserves word order
SELECT id, title
FROM   articles
WHERE  search_vec @@ phraseto_tsquery('english', 'optimistic locking');

-- Alternative: title-only index for lighter memory footprint
-- CREATE INDEX idx_articles_title ON articles USING GIN (to_tsvector('english', title));
