"""Ingest the jaffle_shop raw CSVs into the local DuckDB warehouse.

In a real company, *ingestion* is a data engineer's job. They wire up a
managed connector (Fivetran, Airbyte, Stitch) or write a custom job that
pulls data out of source systems and lands it in the warehouse as raw
tables. Analytics engineers (us) take it from there.

This course doesn't have a Fivetran subscription, so we mimic that step
with this tiny script: read the three CSVs in `data/`, write them as
raw_* tables inside `database/dev.duckdb`. Same end state as a real
ingestion pipeline, drastically simpler plumbing.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DUCKDB_PATH = ROOT / "database" / "dev.duckdb"

CSV_FILES = ["raw_customers.csv", "raw_orders.csv", "raw_payments.csv"]


def main() -> None:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_PATH))
    try:
        print(f"Ingesting into {DUCKDB_PATH.relative_to(ROOT)}")
        for csv in CSV_FILES:
            path = DATA_DIR / csv
            if not path.exists():
                raise FileNotFoundError(f"Missing CSV: {path.relative_to(ROOT)}")
            table = path.stem  # raw_customers.csv -> raw_customers
            con.execute(
                f"CREATE OR REPLACE TABLE {table} AS "
                f"SELECT * FROM read_csv_auto(?)",
                [str(path)],
            )
            n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {n} rows")
    finally:
        con.close()
    print("Done.")


if __name__ == "__main__":
    main()
