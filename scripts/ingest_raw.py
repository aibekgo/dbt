"""Ingest the jaffle_shop raw CSVs into the local DuckDB warehouse.

In a real company, *ingestion* is a data engineer's job. They wire up a
managed connector (Fivetran, Airbyte, Stitch) or write a custom job that
pulls data out of source systems and lands it in the warehouse as raw
tables. Analytics engineers (us) take it from there.

This course doesn't have a Fivetran subscription, so we mimic that step
with this tiny script: read the three CSVs in `data/`, write them as
raw_* tables inside `database/<target>.duckdb`.

Usage:
    python scripts/ingest_raw.py            # writes to database/dev.duckdb (default)
    python scripts/ingest_raw.py prod       # writes to database/prod.duckdb
    python scripts/ingest_raw.py <path>     # writes to <path>
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CSV_FILES = ["raw_customers.csv", "raw_orders.csv", "raw_payments.csv"]


def resolve_path(arg: str | None) -> Path:
    if arg is None:
        return ROOT / "database" / "dev.duckdb"
    if "/" not in arg and not arg.endswith(".duckdb"):
        return ROOT / "database" / f"{arg}.duckdb"
    return Path(arg)


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    duckdb_path = resolve_path(arg)
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(duckdb_path))
    try:
        print(f"Ingesting into {duckdb_path.relative_to(ROOT)}")
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
