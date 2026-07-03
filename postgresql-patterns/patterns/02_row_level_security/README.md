# Row-Level Security (RLS)

If you're building a multi-tenant SaaS app and enforcing data isolation in application code,
you're one missed `WHERE tenant_id = ?` clause away from a serious data leak.
Row-level security moves that guarantee down to the database, where it can't be forgotten.

## What's in this folder

| File | What it does |
|------|--------------|
| `schema.sql` | Creates `tenant_notes` with RLS enabled |
| `seed.sql` | Inserts notes for three tenants (acme, globex, initech) |
| `policies.sql` | Creates an `app_user` role and the isolation policy |
| `demo.sql` | Switches tenant context with `SET app.tenant_id` and runs queries |

## How it works

1. **Enable RLS on the table** — `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`
2. **Create a policy** — `CREATE POLICY ... USING (tenant_id = current_setting('app.tenant_id', true))`
3. **Application sets the session variable on connect** — `SET app.tenant_id = 'acme'`
4. Every subsequent query on that connection automatically sees only `acme` rows

```sql
-- The policy definition (from policies.sql)
CREATE POLICY tenant_isolation ON tenant_notes
    AS PERMISSIVE
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.tenant_id', true));
```

## Things to know

- **Superusers bypass RLS by default.** `ALTER TABLE ... FORCE ROW LEVEL SECURITY` applies it to everyone, which is useful for demos and for reducing accidental data exposure in dev.
- The `true` second argument to `current_setting` means "return NULL instead of raising an error if the variable isn't set" — without it you'll get an error on connections that haven't set the variable.
- You can have multiple policies per table. They combine with OR (permissive) or AND (restrictive).

## How to run

```bash
docker compose up -d
python runner/run.py 02_row_level_security
```

## Setting the variable in your app

In Python with psycopg2: `conn.execute("SET app.tenant_id = ", [tenant_id])`.
Do this right after establishing the connection, before any queries.
