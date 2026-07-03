-- Audit trigger demo
-- Run after schema.sql and audit_trigger.sql.

-- INSERT — creates audit row with old_row=NULL
INSERT INTO orders (customer, status, total)
VALUES ('Alice', 'pending', 249.99);

-- UPDATE — captures both old and new state
UPDATE orders SET status = 'shipped' WHERE customer = 'Alice';

-- Another INSERT
INSERT INTO orders (customer, status, total)
VALUES ('Bob', 'pending', 99.00);

-- DELETE — captures the deleted row in old_row
DELETE FROM orders WHERE customer = 'Bob';

-- Inspect the audit trail
SELECT
    id,
    table_name,
    operation,
    old_row ->> 'status' AS old_status,
    new_row ->> 'status' AS new_status,
    changed_by,
    changed_at
FROM  audit_log
ORDER BY id;

-- Expected:
--  id | table_name | operation | old_status | new_status | changed_by | changed_at
-- ----+------------+-----------+------------+------------+------------+-------------------
--   1 | orders     | INSERT    | (null)     | pending    | patuser    | 2024-xx-xx ...
--   2 | orders     | UPDATE    | pending    | shipped    | patuser    | 2024-xx-xx ...
--   3 | orders     | INSERT    | (null)     | pending    | patuser    | 2024-xx-xx ...
--   4 | orders     | DELETE    | pending    | (null)     | patuser    | 2024-xx-xx ...

-- Full JSONB diff for the UPDATE
SELECT
    old_row,
    new_row
FROM  audit_log
WHERE operation = 'UPDATE'
LIMIT 1;
