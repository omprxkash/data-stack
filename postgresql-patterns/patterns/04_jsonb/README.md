# JSONB

PostgreSQL's `jsonb` type stores JSON in a decomposed binary format that supports indexing,
containment checks, and path queries. It's not a replacement for normalized columns,
but it's excellent for attributes that vary per row — product metadata, config blobs,
feature flags, external API payloads.

## What's in this folder

| File | What it does |
|------|--------------|
| `schema.sql` | A `products` table with a `metadata jsonb` column |
| `seed.sql` | 5 products with rich, varied metadata objects |
| `queries.sql` | Demonstrates every major operator and function |
| `indexing.sql` | GIN index setup and how the planner uses it |

## Operators you'll use daily

| Operator | Returns | What it does |
|----------|---------|--------------|
| `->` | jsonb | Get a key or array element as JSONB |
| `->>` | text | Get a key or element as text (castable to numeric, bool, etc.) |
| `#>>` | text | Navigate a path: `metadata #>> '{dimensions, width_cm}'` |
| `@>` | bool | Containment: does left contain right? |
| `?` | bool | Does the key exist at the top level? |

## GIN index — the key to fast JSONB queries

```sql
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);
```

This single index supports `@>` (containment), `?` (key existence), and `jsonb_path_query`.
Without it, every JSONB query is a full table scan.

## Updating without overwriting

`jsonb_set` lets you change one field at a time:

```sql
UPDATE products
SET    metadata = jsonb_set(metadata, '{price_usd}', '119.99')
WHERE  name = 'Mechanical Keyboard';
```

Alternatively, `||` (the concatenation operator) merges two JSONB objects:
```sql
SET metadata = metadata || '{"on_sale": true}'
```

## What jsonb isn't good for

- Deeply normalized relational data — don't shove foreign keys into JSON
- Values you filter on constantly — a regular column with a B-tree index will always be faster
- Very large documents (>1 MB) — consider `pg_large_object` or object storage instead

## How to run

```bash
docker compose up -d
python runner/run.py 04_jsonb
```
