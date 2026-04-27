# Exercise 14 — Your First Model

## Goal

Write `models/staging/stg_customers.sql` — a SQL `SELECT` that reads from `raw_customers` and renames a column. Run `dbt run` and verify the resulting table appears in DuckDB.

## What a dbt model is

A dbt **model** is a `.sql` file under `models/` containing exactly one `SELECT` statement. dbt wraps it in a `CREATE VIEW` (or `CREATE TABLE`, depending on materialization) and runs it against your warehouse. You never write `CREATE` yourself.

The convention for the first transformation layer is the **staging layer** — one model per source table, doing nothing more than:

- Renaming columns to business-friendly names
- Casting types
- Light cleanup (trim whitespace, lowercase emails)

No joins yet. Joins come in marts (Stage 2).

## Steps

**1.** Create the directory:

```bash
mkdir -p dbt_project/models/staging
```

**2.** Create the file `dbt_project/models/staging/stg_customers.sql` with this content:

```sql
select
    id          as customer_id,
    first_name,
    last_name
from {{ ref('raw_customers') }}
```

Two things to notice:

- **`{{ ref('raw_customers') }}`** — Jinja-templated reference to the seed you loaded last exercise. dbt resolves it to the fully qualified table name (e.g., `dev.main_dbt_<user>.raw_customers`) at compile time. Never hardcode warehouse-specific table names in your SQL.
- **`as customer_id`** — the source column is `id` (ambiguous and reused everywhere). Renaming it once at the staging layer means every downstream model gets `customer_id` for free.

**3.** Run dbt:

```bash
cd dbt_project
dbt run --select stg_customers
cd ..
```

You should see one node succeed in green: `1 of 1 START sql view model ... [OK ...]`.

**4.** Press `v` to verify.

## What the verifier checks

- `dbt run --select stg_customers` exits 0
- A relation named `stg_customers` exists in `database/dev.duckdb`

## Inspecting the result

```bash
duckdb database/dev.duckdb -c "SELECT * FROM stg_customers LIMIT 3;"
```

You should see customer rows with the renamed column.

## After you pass

Press `n`. The last exercise of Stage 1 sets a default materialization for everything in `staging/`.
