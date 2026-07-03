-- JSONB demo schema
-- Storing flexible product metadata alongside fixed columns.

DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    category    TEXT        NOT NULL,
    metadata    JSONB       NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
