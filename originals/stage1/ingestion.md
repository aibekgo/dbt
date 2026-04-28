# Exercise — Ingest the raw CSVs

## Goal

Load the three jaffle_shop CSVs into the local DuckDB warehouse so dbt has something to model. In a real company a data engineer wires this up with Fivetran/Airbyte; for the course we ship a tiny Python script that does the same job.

## Steps

**1.** Get back to the repo root. (The previous exercise left you inside `dbt_project/`.)

```bash
cd ..        # only if you're still inside dbt_project/
pwd          # should end in /learn_dbt
```

**2.** Make sure your virtualenv is active:

```bash
source .venv/bin/activate
```

**3.** Run the ingestion script:

```bash
python scripts/ingest_raw.py
```

You should see:

```
Ingesting into database/dev.duckdb
  raw_customers: 100 rows
  raw_orders: 99 rows
  raw_payments: 113 rows
Done.
```

**4.** (Optional) Open the warehouse and poke around:

```bash
duckdb database/dev.duckdb -c "SHOW TABLES;"
duckdb database/dev.duckdb -c "SELECT * FROM raw_customers LIMIT 5;"
```

**5.** Press `v` to verify.

## What the verifier checks

- `raw_customers`, `raw_orders`, and `raw_payments` all exist somewhere in `database/dev.duckdb`'s schemas.

The verifier doesn't care *how* they got there — only that they're present. Re-running the script is idempotent (`CREATE OR REPLACE TABLE`), so feel free to run it as many times as you like.

## If it fails

| Symptom | What to check |
|---|---|
| `ModuleNotFoundError: No module named 'duckdb'` | venv not active. Run `source .venv/bin/activate`. |
| `error: Failed to spawn: scripts/ingest_raw.py` (or `python: can't open file 'scripts/ingest_raw.py'`) | You're inside `dbt_project/`. Run `cd ..` first. |
| `FileNotFoundError: Missing CSV: data/raw_customers.csv` | You're not in the repo root. `cd` to the directory that contains `data/`, `scripts/`, and `database/`. |
| `IO Error: Could not set lock on file ... dev.duckdb` | Another process (probably dbt) has the warehouse open. Close it and re-run. |

## Why this isn't `dbt seed`

`dbt seed` is dbt's built-in CSV loader — it would technically work for these files. We're avoiding it on purpose:

- `dbt seed` is for **lookup tables** that ship with the code (country codes, plan-tier mappings). It's the wrong abstraction for "raw operational data."
- A later exercise uses `dbt seed` for what it's actually good at — a small reference table — and we want that lesson to stay clean.

For now, treat `scripts/ingest_raw.py` as your stand-in for the data-engineering team.

## After you pass

Press `n` — next you'll write your first dbt model on top of these raw tables.
