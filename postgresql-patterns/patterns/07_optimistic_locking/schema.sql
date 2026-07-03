-- Optimistic locking demo schema
-- The version column is the guard: bump it on every write, check it on every update.

DROP TABLE IF EXISTS inventory CASCADE;

CREATE TABLE inventory (
    id          SERIAL  PRIMARY KEY,
    sku         TEXT    NOT NULL UNIQUE,
    qty         INTEGER NOT NULL DEFAULT 0,
    version     INTEGER NOT NULL DEFAULT 1
);
