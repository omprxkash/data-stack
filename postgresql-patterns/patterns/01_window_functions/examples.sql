-- Window function examples
-- Run after schema.sql and seed.sql.

-- 1. ROW_NUMBER — rank each rep's sales by amount within their region
SELECT
    rep,
    region,
    sale_date,
    amount,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS rn
FROM  sales
ORDER BY region, rn;

-- 2. RANK vs DENSE_RANK — ties handled differently
SELECT
    rep,
    amount,
    RANK()       OVER (ORDER BY amount DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rank
FROM  sales
ORDER BY amount DESC;

-- 3. Running total per rep (cumulative sum over time)
SELECT
    rep,
    sale_date,
    amount,
    SUM(amount) OVER (PARTITION BY rep ORDER BY sale_date
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM  sales
ORDER BY rep, sale_date;

-- Expected (Alice excerpt):
--  rep   | sale_date  | amount  | running_total
-- -------+------------+---------+---------------
--  Alice | 2024-01-05 | 1200.00 |       1200.00
--  Alice | 2024-01-19 |  850.00 |       2050.00
--  Alice | 2024-02-03 | 2100.00 |       4150.00
--  ...

-- 4. 3-sale moving average per rep
SELECT
    rep,
    sale_date,
    amount,
    ROUND(
        AVG(amount) OVER (PARTITION BY rep ORDER BY sale_date
                          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
        2
    ) AS moving_avg_3
FROM  sales
ORDER BY rep, sale_date;

-- 5. LAG / LEAD — compare each sale to the previous and next
SELECT
    rep,
    sale_date,
    amount,
    LAG(amount,  1) OVER (PARTITION BY rep ORDER BY sale_date) AS prev_sale,
    LEAD(amount, 1) OVER (PARTITION BY rep ORDER BY sale_date) AS next_sale,
    amount - LAG(amount, 1) OVER (PARTITION BY rep ORDER BY sale_date) AS change_vs_prev
FROM  sales
ORDER BY rep, sale_date;

-- 6. NTILE — bucket each sale into a performance quartile globally
SELECT
    rep,
    amount,
    NTILE(4) OVER (ORDER BY amount) AS quartile
FROM  sales
ORDER BY quartile, amount;

-- 7. First / last value per region
SELECT DISTINCT
    region,
    FIRST_VALUE(rep) OVER (PARTITION BY region ORDER BY amount DESC
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS top_rep,
    LAST_VALUE(rep)  OVER (PARTITION BY region ORDER BY amount DESC
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS bottom_rep
FROM  sales;

-- Frame clause recap:
--   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  → cumulative
--   ROWS BETWEEN 2 PRECEDING AND CURRENT ROW           → rolling window (3 rows)
--   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING → full partition
