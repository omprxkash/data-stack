-- Ranking and highlighting full-text results
-- Run after schema.sql, seed.sql, and search.sql.

-- ts_rank orders results by relevance — higher is better.
-- The query here matches articles about "database" or "postgres".
SELECT
    id,
    title,
    ts_rank(search_vec, query) AS relevance
FROM
    articles,
    to_tsquery('english', 'database | postgres | postgresql') query
WHERE
    search_vec @@ query
ORDER BY
    relevance DESC;

-- Expected (approximate, ranks can vary):
--  id | title                                  | relevance
-- ----+----------------------------------------+-----------
--   1 | Getting started with PostgreSQL        |  0.09...
--   2 | Understanding database indexes         |  0.07...
--   ...

-- ts_headline wraps matched terms in <b> tags (or custom delimiters).
SELECT
    title,
    ts_headline(
        'english',
        body,
        to_tsquery('english', 'partition'),
        'StartSel=**, StopSel=**, MaxFragments=1, MaxWords=20'
    ) AS snippet
FROM  articles
WHERE search_vec @@ to_tsquery('english', 'partition');

-- Expected:
--  title                            | snippet
-- ----------------------------------+-------------------------------------------------
--  Partitioning large tables by date| Declarative **partitioning** in Postgres lets...

-- ts_rank_cd uses cover density (better for longer documents)
SELECT
    id,
    title,
    ts_rank_cd(search_vec, query) AS cover_density_rank
FROM
    articles,
    to_tsquery('english', 'lock | locking') query
WHERE
    search_vec @@ query
ORDER BY
    cover_density_rank DESC;

-- ts_rank normalization: the second argument controls length normalization.
-- 0 (default) = ignore doc length; 1 = divide by 1+log(length); 2 = divide by length.
