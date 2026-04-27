# Exercise 13 — `dbt seed`

## Goal

Load the three jaffle_shop raw CSVs into DuckDB as tables, using `dbt seed`.

## Background

dbt **seeds** are static CSVs that ship with your project and load into the warehouse via `dbt seed`. You'd never use seeds for real production data (that comes through your ingestion tools), but they're great for:

- Lookup tables (country codes, plan tier mappings)
- Sample / fixture data while learning
- Small reference tables that rarely change

The repo ships three jaffle_shop CSVs in `data/`:
- `raw_customers.csv`
- `raw_orders.csv`
- `raw_payments.csv`

You'll copy them into `dbt_project/seeds/` so dbt can pick them up.

## Steps

**1.** From the repo root, copy the seed CSVs into the project's `seeds/` directory:

```bash
cp data/raw_*.csv dbt_project/seeds/
```

**2.** Run dbt seed:

```bash
cd dbt_project
dbt seed
cd ..
```

You should see dbt create three tables, one per CSV. The CSV's filename (without extension) becomes the table name — `raw_customers.csv` → table `raw_customers`, etc.

**3.** Press `v` to verify.

## What the verifier checks

- `dbt seed` exits 0
- The three tables `raw_customers`, `raw_orders`, `raw_payments` all exist somewhere in `dev.duckdb`'s schemas

The exact schema name is up to dbt — by default it's `main_<your_target_schema>`, but the verifier searches all schemas so you don't have to memorize it.

## Inspecting your warehouse

After `dbt seed` runs, you can poke at the DuckDB file directly:

```bash
duckdb dbt_project/dev.duckdb
```

Then in the duckdb shell:

```sql
SHOW ALL TABLES;
SELECT count(*) FROM raw_customers;
.exit
```

You should see roughly 100 customers, 99 orders, 113 payments.

## After you pass

Press `n` — next you'll write your first dbt model on top of these raw tables.
