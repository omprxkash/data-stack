# Audit Triggers

Keeping a history of every change to a row is a requirement that comes up in almost
every serious application. A database-level trigger is the right place to implement it:
the audit record is always written, regardless of which application or user makes the change.

## What's in this folder

| File | What it does |
|------|--------------|
| `schema.sql` | `orders` table (the target) and `audit_log` (the history table) |
| `audit_trigger.sql` | Generic trigger function + binding |
| `demo.sql` | INSERT, UPDATE, DELETE examples, then reads the audit trail |

## How the trigger works

```sql
CREATE OR REPLACE FUNCTION fn_audit_log()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
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
```

- `TG_TABLE_NAME` — name of the table that fired the trigger
- `TG_OP` — `INSERT`, `UPDATE`, or `DELETE`
- `OLD` / `NEW` — the row before and after the change
- `row_to_json(OLD)::jsonb` — captures the entire row as JSONB, so schema changes don't break old records

## Attaching it to any table

The function is generic — attach it to any table with one statement:

```sql
CREATE TRIGGER trg_orders_audit
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION fn_audit_log();
```

## Things to keep in mind

- `AFTER` triggers fire after the data is written, so `OLD` and `NEW` reflect the final committed values
- Storing the full row as JSONB means you get a complete snapshot at each point in time, not just diffs
- The `audit_log` table will grow; add a `created_at` index and periodically archive or partition it
- `changed_by` defaults to `current_user` — in an app with a single DB role, consider using a session variable (like the RLS pattern) to capture the application-level user

## How to run

```bash
docker compose up -d
python runner/run.py 06_audit_triggers
```

## Archiving the audit log

The audit_log will grow indefinitely. A few strategies:
- **Partition by month** — same pattern as `03_partitioning`; drop old partitions cheaply
- **Move to cold storage** — periodically copy rows older than 90 days to S3/GCS and delete them
- **Use a separate database** — audit logs are write-heavy and read-rarely; a separate instance avoids affecting the main DB's performance
