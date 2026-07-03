-- Window functions demo schema
-- A simple sales table is all we need to show off every major window technique.

DROP TABLE IF EXISTS sales CASCADE;

CREATE TABLE sales (
    id          SERIAL PRIMARY KEY,
    rep         TEXT        NOT NULL,
    region      TEXT        NOT NULL,
    sale_date   DATE        NOT NULL,
    amount      NUMERIC(10,2) NOT NULL
);
