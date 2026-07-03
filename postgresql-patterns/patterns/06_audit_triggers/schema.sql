-- Audit triggers demo schema
-- A target table and a generic audit_log that captures every change.

DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS orders CASCADE;

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer    TEXT        NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'pending',
    total       NUMERIC(10,2) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
    id          BIGSERIAL   PRIMARY KEY,
    table_name  TEXT        NOT NULL,
    operation   TEXT        NOT NULL,   -- INSERT / UPDATE / DELETE
    old_row     JSONB,
    new_row     JSONB,
    changed_by  TEXT        NOT NULL DEFAULT current_user,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
