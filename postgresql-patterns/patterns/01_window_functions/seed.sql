-- Seed data: a year of sales across three reps and two regions.
-- Enough rows to make running totals, rankings, and lag comparisons meaningful.

INSERT INTO sales (rep, region, sale_date, amount) VALUES
  ('Alice', 'North', '2024-01-05',  1200.00),
  ('Alice', 'North', '2024-01-19',   850.00),
  ('Alice', 'North', '2024-02-03',  2100.00),
  ('Alice', 'North', '2024-02-28',   430.00),
  ('Alice', 'North', '2024-03-15',  1750.00),
  ('Bob',   'South', '2024-01-08',   980.00),
  ('Bob',   'South', '2024-01-22',  1340.00),
  ('Bob',   'South', '2024-02-14',   620.00),
  ('Bob',   'South', '2024-03-01',  2200.00),
  ('Bob',   'South', '2024-03-20',   770.00),
  ('Carol', 'North', '2024-01-11',  1500.00),
  ('Carol', 'North', '2024-02-07',   900.00),
  ('Carol', 'North', '2024-02-22',  1100.00),
  ('Carol', 'South', '2024-03-05',  1800.00),
  ('Carol', 'South', '2024-03-25',   650.00);

-- Total rows: 15 (enough for rank ties, partition splits, and meaningful moving averages).
