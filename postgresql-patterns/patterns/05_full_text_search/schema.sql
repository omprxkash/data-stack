-- Full-text search demo schema
-- Articles with a generated tsvector column so the index stays fresh automatically.

DROP TABLE IF EXISTS articles CASCADE;

CREATE TABLE articles (
    id          SERIAL PRIMARY KEY,
    title       TEXT        NOT NULL,
    body        TEXT        NOT NULL,
    author      TEXT        NOT NULL,
    published   DATE        NOT NULL DEFAULT CURRENT_DATE,
    search_vec  TSVECTOR
        GENERATED ALWAYS AS (
            to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
        ) STORED
);
