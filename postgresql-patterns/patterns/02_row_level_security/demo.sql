-- RLS demo: switch tenants by setting the session variable, see filtered rows.

-- As a superuser (running as the Postgres default role), demonstrate
-- that FORCE ROW LEVEL SECURITY makes the policy apply to everyone.

-- Switch to acme — should see 2 rows.
SET app.tenant_id = 'acme';
SELECT id, tenant_id, title FROM tenant_notes;

-- Expected:
--  id | tenant_id | title
-- ----+-----------+------------
--   1 | acme      | Q1 Goals
--   2 | acme      | Team Offsite

-- Switch to globex — should see 2 different rows.
SET app.tenant_id = 'globex';
SELECT id, tenant_id, title FROM tenant_notes;

-- Expected:
--  id | tenant_id | title
-- ----+-----------+-------------------
--   3 | globex    | Security Audit
--   4 | globex    | New Hire Onboard

-- Switch to initech — should see 2 different rows.
SET app.tenant_id = 'initech';
SELECT id, tenant_id, title FROM tenant_notes;

-- Expected:
--  id | tenant_id | title
-- ----+-----------+---------------
--   5 | initech   | Budget Review
--   6 | initech   | Roadmap Draft

-- Confirm total rows in the table (superuser without session var sees all).
RESET app.tenant_id;
SELECT count(*) AS total_rows FROM tenant_notes;
-- Expected: 6
