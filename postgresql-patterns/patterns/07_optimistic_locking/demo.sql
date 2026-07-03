-- Optimistic locking demo
-- Run after schema.sql.

-- Seed inventory
INSERT INTO inventory (sku, qty) VALUES
    ('WIDGET-A', 100),
    ('WIDGET-B',  50);

-- Simulate reading the row (application stores id=1, version=1)
SELECT id, sku, qty, version FROM inventory WHERE id = 1;
-- Expected: id=1, sku=WIDGET-A, qty=100, version=1

-- Successful update: version matches — decrement stock and bump version.
UPDATE inventory
SET    qty     = qty - 10,
       version = version + 1
WHERE  id      = 1
  AND  version = 1;  -- the version we read

GET DIAGNOSTICS; -- 1 row affected → success

-- Confirm new state
SELECT id, sku, qty, version FROM inventory WHERE id = 1;
-- Expected: qty=90, version=2

-- Simulate a lost update: another process already updated the row (version is now 2),
-- but we're still trying to apply our stale update based on version=1.
UPDATE inventory
SET    qty     = qty - 10,
       version = version + 1
WHERE  id      = 1
  AND  version = 1;  -- stale version

-- 0 rows affected → application knows to retry after re-reading the row.

-- Final state should be unchanged (still version=2, qty=90).
SELECT id, sku, qty, version FROM inventory WHERE id = 1;

-- rowcount = 1 → success, rowcount = 0 → stale version, retry required
