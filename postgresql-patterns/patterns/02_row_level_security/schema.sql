-- Row-level security demo schema
-- One table, multiple tenants — each tenant can only see their own rows.

DROP TABLE IF EXISTS tenant_notes CASCADE;

CREATE TABLE tenant_notes (
    id          SERIAL PRIMARY KEY,
    tenant_id   TEXT        NOT NULL,
    title       TEXT        NOT NULL,
    body        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS must be enabled explicitly; it's off by default even if policies exist.
ALTER TABLE tenant_notes ENABLE ROW LEVEL SECURITY;
