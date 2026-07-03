-- Audit trigger function and binding
-- Run after schema.sql.

-- Generic trigger function: captures old/new row as JSONB for any table.
CREATE OR REPLACE FUNCTION fn_audit_log()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, old_row, new_row)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD)::jsonb ELSE NULL END,
        CASE WHEN TG_OP IN ('UPDATE', 'INSERT') THEN row_to_json(NEW)::jsonb ELSE NULL END
    );
    RETURN NEW;
END;
$$;

-- Attach the trigger to the orders table for all three operations.
DROP TRIGGER IF EXISTS trg_orders_audit ON orders;
CREATE TRIGGER trg_orders_audit
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION fn_audit_log();

-- AFTER trigger: OLD and NEW already reflect committed values

-- Note: triggers must be added to each partition individually; they don't inherit from the parent.
