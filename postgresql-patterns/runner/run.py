#!/usr/bin/env python3
"""
Run one or all postgresql-patterns examples against a live Postgres instance.

Usage:
    python runner/run.py 01_window_functions
    python runner/run.py --all

Reads DATABASE_URL from the environment (default: postgresql://patuser:patpass@localhost:5432/patterns).
"""

import os
import sys
import glob
import argparse
import psycopg2

PATTERNS_DIR = os.path.join(os.path.dirname(__file__), "..", "patterns")
DEFAULT_URL = "postgresql://patuser:patpass@localhost:5432/patterns"

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


def run_pattern(folder_name: str, conn) -> None:
    folder = os.path.join(PATTERNS_DIR, folder_name)
    if not os.path.isdir(folder):
        print(f"  [!] folder not found: {folder}")
        return

    files = SQL_ORDER.get(folder_name)
    if not files:
        # fallback: run every .sql file sorted by name
        files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(folder, "*.sql")))

    print(f"\n=== {folder_name} ===")
    for filename in files:
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            print(f"  [skip] {filename} not found")
            continue
        with open(path, encoding="utf-8") as f:
            sql = f.read()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                if cur.description:
                    rows = cur.fetchall()
                    cols = [d[0] for d in cur.description]
                    print(f"  -- {filename} ({len(rows)} rows) --")
                    print("  " + " | ".join(cols))
                    print("  " + "-" * (sum(len(c) for c in cols) + 3 * (len(cols) - 1)))
                    for row in rows[:20]:
                        print("  " + " | ".join(str(v) for v in row))
                    if len(rows) > 20:
                        print(f"  ... ({len(rows) - 20} more rows)")
                else:
                    print(f"  -- {filename}: OK (no rows returned) --")
            conn.commit()
        except Exception as exc:
            conn.rollback()
            print(f"  [ERROR] {filename}: {exc}")
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run postgresql-patterns examples")
    parser.add_argument("pattern", nargs="?", help="Pattern folder name, e.g. 01_window_functions")
    parser.add_argument("--all", dest="run_all", action="store_true", help="Run every pattern")
    args = parser.parse_args()

    if not args.pattern and not args.run_all:
        parser.print_help()
        sys.exit(1)

    url = os.environ.get("DATABASE_URL", DEFAULT_URL)
    try:
        conn = psycopg2.connect(url)
    except Exception as exc:
        print(f"Could not connect to Postgres: {exc}")
        print(f"Make sure Docker is running: docker compose up -d")
        sys.exit(1)

    conn.autocommit = False

    try:
        if args.run_all:
            for folder in sorted(SQL_ORDER.keys()):
                run_pattern(folder, conn)
        else:
            run_pattern(args.pattern, conn)
    finally:
        conn.close()

    print("\nDone.")


if __name__ == "__main__":
    main()

# See runner/README or root README for full usage.
