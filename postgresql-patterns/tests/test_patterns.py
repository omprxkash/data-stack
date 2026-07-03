"""
Integration tests for postgresql-patterns.

Each test runs a pattern's SQL files in order against a real Postgres instance
and asserts a known result. DATABASE_URL must be set (or the default must be reachable).

Run with: pytest tests/ -v
"""

import os
import glob
import pytest
import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://patuser:patpass@localhost:5432/patterns"
)

PATTERNS_DIR = os.path.join(os.path.dirname(__file__), "..", "patterns")

SQL_ORDER = {
    "01_window_functions":    ["schema.sql", "seed.sql", "examples.sql"],
    "02_row_level_security":  ["schema.sql", "seed.sql", "policies.sql", "demo.sql"],
    "03_partitioning":        ["range_partition.sql", "list_partition.sql", "hash_partition.sql"],
    "04_jsonb":               ["schema.sql", "seed.sql", "queries.sql", "indexing.sql"],
    "05_full_text_search":    ["schema.sql", "seed.sql", "search.sql", "ranking.sql"],
    "06_audit_triggers":      ["schema.sql", "audit_trigger.sql", "demo.sql"],
    "07_optimistic_locking":  ["schema.sql", "demo.sql"],
    "08_queues_skip_locked":  ["schema.sql", "enqueue.sql", "claim.sql"],
}


@pytest.fixture(scope="module")
def conn():
    c = psycopg2.connect(DATABASE_URL)
    c.autocommit = False
    yield c
    c.close()


def run_sql_file(conn, path: str) -> None:
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def run_pattern(conn, folder_name: str) -> None:
    folder = os.path.join(PATTERNS_DIR, folder_name)
    for filename in SQL_ORDER[folder_name]:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            run_sql_file(conn, path)


# ---------------------------------------------------------------------------
# Pattern 01 — Window Functions
# ---------------------------------------------------------------------------

def test_window_functions_row_count(conn):
    run_pattern(conn, "01_window_functions")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM sales")
        (count,) = cur.fetchone()
    assert count == 15, f"Expected 15 sales rows, got {count}"


def test_window_functions_running_total(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                rep,
                SUM(amount) OVER (PARTITION BY rep ORDER BY sale_date
                                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running
            FROM sales
            WHERE rep = 'Alice'
            ORDER BY sale_date
        """)
        rows = cur.fetchall()
    # Last running total for Alice = sum of all her sales
    _, last_running = rows[-1]
    with conn.cursor() as cur:
        cur.execute("SELECT SUM(amount) FROM sales WHERE rep = 'Alice'")
        (total,) = cur.fetchone()
    assert last_running == total


# ---------------------------------------------------------------------------
# Pattern 02 — Row-Level Security
# ---------------------------------------------------------------------------

def test_rls_total_row_count(conn):
    run_pattern(conn, "02_row_level_security")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM tenant_notes")
        (count,) = cur.fetchone()
    assert count == 6


def test_rls_tenant_filter(conn):
    with conn.cursor() as cur:
        cur.execute("SET app.tenant_id = 'acme'")
        cur.execute("SELECT count(*) FROM tenant_notes")
        (count,) = cur.fetchone()
    conn.commit()
    # With RLS active, acme should see exactly 2 rows
    # (superuser with FORCE RLS bypasses — but filter still applies with session var)
    assert count == 2


# ---------------------------------------------------------------------------
# Pattern 03 — Partitioning
# ---------------------------------------------------------------------------

def test_partitioning_range_total(conn):
    run_pattern(conn, "03_partitioning")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM events")
        (count,) = cur.fetchone()
    assert count == 6


def test_partitioning_list_total(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM regional_sales")
        (count,) = cur.fetchone()
    assert count == 5


def test_partitioning_hash_total(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM user_activity")
        (count,) = cur.fetchone()
    assert count == 20


# ---------------------------------------------------------------------------
# Pattern 04 — JSONB
# ---------------------------------------------------------------------------

def test_jsonb_product_count(conn):
    run_pattern(conn, "04_jsonb")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM products")
        (count,) = cur.fetchone()
    assert count == 5


def test_jsonb_containment(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM products WHERE metadata @> '{\"wireless\": true}'")
        (count,) = cur.fetchone()
    assert count == 2


def test_jsonb_price_update(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT (metadata ->> 'price_usd')::numeric FROM products WHERE name = 'Mechanical Keyboard'"
        )
        (price,) = cur.fetchone()
    assert price == 119.99


# ---------------------------------------------------------------------------
# Pattern 05 — Full-Text Search
# ---------------------------------------------------------------------------

def test_fts_article_count(conn):
    run_pattern(conn, "05_full_text_search")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM articles")
        (count,) = cur.fetchone()
    assert count == 6


def test_fts_basic_search(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM articles WHERE search_vec @@ to_tsquery('english', 'partition')"
        )
        (count,) = cur.fetchone()
    assert count >= 1


def test_fts_multi_word(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM articles WHERE search_vec @@ plainto_tsquery('english', 'optimistic locking')"
        )
        (count,) = cur.fetchone()
    assert count >= 1


# ---------------------------------------------------------------------------
# Pattern 06 — Audit Triggers
# ---------------------------------------------------------------------------

def test_audit_trigger_log_count(conn):
    run_pattern(conn, "06_audit_triggers")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM audit_log")
        (count,) = cur.fetchone()
    assert count == 4  # INSERT, UPDATE, INSERT, DELETE


def test_audit_trigger_operations(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT operation FROM audit_log ORDER BY id"
        )
        ops = [row[0] for row in cur.fetchall()]
    assert ops == ["INSERT", "UPDATE", "INSERT", "DELETE"]


# ---------------------------------------------------------------------------
# Pattern 07 — Optimistic Locking
# ---------------------------------------------------------------------------

def test_optimistic_locking_successful_update(conn):
    run_pattern(conn, "07_optimistic_locking")
    with conn.cursor() as cur:
        cur.execute("SELECT qty, version FROM inventory WHERE sku = 'WIDGET-A'")
        qty, version = cur.fetchone()
    assert qty == 90
    assert version == 2


def test_optimistic_locking_stale_update_rejected(conn):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE inventory
            SET qty = qty - 10, version = version + 1
            WHERE sku = 'WIDGET-A' AND version = 1
        """)
        affected = cur.rowcount
    conn.commit()
    assert affected == 0, "Stale version update should affect 0 rows"


# ---------------------------------------------------------------------------
# Pattern 08 — Queues with SKIP LOCKED
# ---------------------------------------------------------------------------

def test_queue_enqueue_count(conn):
    run_pattern(conn, "08_queues_skip_locked")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM jobs")
        (count,) = cur.fetchone()
    assert count == 5


def test_queue_no_double_claim(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM jobs WHERE status = 'processing'")
        (processing,) = cur.fetchone()
    # After claim.sql ran, at least 1 job should be processing and none should be double-claimed
    assert processing >= 1
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM jobs WHERE queue = 'email' AND status = 'pending'"
        )
        (remaining,) = cur.fetchone()
    # Two workers claimed 2 email jobs; 1 email job should remain pending
    assert remaining == 1
