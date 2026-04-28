# Exercise — Your first dbt model

## Goal

Write the simplest possible dbt model — one SQL file with a hardcoded `from` clause — and run `dbt run` to see the build loop work end-to-end. No Jinja, no YAML, no source declaration. The next exercise upgrades it.

## Steps

**1.** From the repo root, step into the project:

```bash
cd dbt_project
```

**2.** Create the staging folder and the model file:

```bash
mkdir -p models/staging
touch models/staging/stg__customers.sql
```

**3.** Open `dbt_project/models/staging/stg__customers.sql` in your editor and paste:

```sql
select
    id          as customer_id,
    first_name,
    last_name
from main.raw_customers
```

That's it — pure SQL. `main.raw_customers` is the literal DuckDB table that `scripts/ingest_raw.py` wrote. We're hardcoding it on purpose so the very first model has zero ceremony.

**4.** Build it:

```bash
dbt run --select stg__customers
```

You should see one green line: `1 of 1 START sql view model ... [OK ...]`.

**5.** Press `v` to verify.

## What `dbt run` actually did

The whole loop, in plain English:

1. **Parsed** every file under `models/`. Found one model: `stg__customers`.
2. **Compiled** it — expanded any Jinja into raw SQL. (Yours had none, so the compiled file is identical to your input. You can see it under `target/compiled/`.)
3. **Wrapped** the `SELECT` in `CREATE OR REPLACE VIEW dev.main_main.stg__customers AS (...)` and sent it to DuckDB.
4. **Wrote** the run result and any logs into `target/`.

Parse → compile → execute. Every model goes through that same three-step loop, no matter how many models or how complex the SQL.

## What the verifier checks

- `dbt run --select stg__customers` exits 0
- A relation named `stg__customers` exists in `database/dev.duckdb`

## Inspecting the result

From the repo root:

```bash
duckdb database/dev.duckdb -c "SELECT * FROM stg__customers LIMIT 3;"
```

You should see customer rows with the renamed `customer_id` column.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Relation "dev"."main"."raw_customers" does not exist` | You skipped ingestion. From the repo root: `python scripts/ingest_raw.py`. |
| `Could not find profile named 'dbt_project'` | `dbt_project/profiles.yml` is missing or has the wrong top-level key. Go back to the profiles exercise. |

## After you pass

Press `n`. The next exercise upgrades this model with a proper `_sources.yml` declaration and `{{ source(...) }}` so the table joins the DAG.
