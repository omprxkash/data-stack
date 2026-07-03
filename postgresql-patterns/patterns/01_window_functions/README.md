# Window Functions

Window functions are one of the most useful tools in SQL that most developers underuse.
Unlike `GROUP BY` aggregates that collapse rows into one, window functions compute a value
for each row while still giving you access to all the other rows in a defined partition.
Once you get comfortable with them, you'll find yourself reaching for them all the time.

## What's in this folder

| File | What it does |
|------|--------------|
| `schema.sql` | Creates a `sales` table with rep, region, date, and amount |
| `seed.sql` | 15 sales rows across 3 reps and 2 regions over Q1 2024 |
| `examples.sql` | Seven window function patterns with expected output in comments |

## Patterns covered

- **`ROW_NUMBER`** — unique sequential number per partition (great for pagination or "top N per group")
- **`RANK` vs `DENSE_RANK`** — handles ties differently: RANK skips numbers, DENSE_RANK doesn't
- **Running totals** — `SUM() OVER (... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`
- **Moving average** — a 3-sale rolling average using `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`
- **`LAG` / `LEAD`** — reference the previous or next row without a self-join
- **`NTILE`** — divide rows into N equal buckets (quartiles, deciles, etc.)
- **`FIRST_VALUE` / `LAST_VALUE`** — grab the top or bottom value within a partition

## The key concept: `OVER (PARTITION BY ... ORDER BY ...)`

```sql
SUM(amount) OVER (
    PARTITION BY rep           -- reset the sum for each rep
    ORDER BY sale_date         -- compute left-to-right chronologically
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

- `PARTITION BY` — splits rows into independent groups (like `GROUP BY` but rows are preserved)
- `ORDER BY` — determines calculation order within the partition
- The frame clause (`ROWS BETWEEN ...`) — controls which rows contribute to the current row's calculation

## How to run

```bash
docker compose up -d
python runner/run.py 01_window_functions
```

## Named windows

If you use the same `PARTITION BY / ORDER BY` in several places, define it once:

```sql
SELECT
    rep, amount,
    ROW_NUMBER() OVER w,
    SUM(amount)  OVER w
FROM  sales
WINDOW w AS (PARTITION BY region ORDER BY sale_date);
```

Cleaner and easier to change in one place.
