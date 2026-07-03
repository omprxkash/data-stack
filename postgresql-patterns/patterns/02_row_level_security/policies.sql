-- Row-level security policies
-- Run after schema.sql and seed.sql.

-- Create a low-privilege application role that cannot bypass RLS.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user NOLOGIN;
    END IF;
END
$$;

GRANT SELECT, INSERT, UPDATE, DELETE ON tenant_notes TO app_user;

-- The policy: a row is visible only when its tenant_id matches the
-- session variable 'app.tenant_id' that the application sets on connect.
DROP POLICY IF EXISTS tenant_isolation ON tenant_notes;
CREATE POLICY tenant_isolation ON tenant_notes
    AS PERMISSIVE
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.tenant_id', true));

-- Superusers bypass RLS by default; force even them through it for demos.
ALTER TABLE tenant_notes FORCE ROW LEVEL SECURITY;
