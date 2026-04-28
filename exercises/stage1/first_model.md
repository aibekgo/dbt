# Exercise — Your first dbt model

## Goal

Write one tiny SQL file under `dbt_project/models/`, run `dbt run`, and watch dbt turn your `SELECT` into a view in DuckDB.

That's the whole exercise.

> **Heads-up:** the lesson covers sources, `{{ source(...) }}`, and the DAG — those are the production way. For your *very first* model we're keeping it minimal: a hardcoded table reference, no source declaration. Stage 2 swaps in proper sources.

## Steps

**1.** From the repo root, step into the project:

```bash
cd dbt_project
```

**2.** Create the staging folder and the model file:

```bash
mkdir -p models/staging
touch models/staging/stg_customers.sql
```

**3.** Open `dbt_project/models/staging/stg_customers.sql` in your editor and paste:

```sql
select
    id          as customer_id,
    first_name,
    last_name
from main.raw_customers
```

That's it — no Jinja, no config block, no DDL. Just a `SELECT` from the raw table that ingestion landed in DuckDB's `main` schema.

**4.** Build it:

```bash
dbt run --select stg_customers
```

You should see one node succeed in green: `1 of 1 START sql view model ... [OK ...]`.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt run --select stg_customers` exits 0
- A relation named `stg_customers` exists in `database/dev.duckdb`

## Inspecting the result

```bash
duckdb ../database/dev.duckdb -c "SELECT * FROM stg_customers LIMIT 3;"
```

You should see customer rows with the renamed `customer_id` column.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Relation "dev"."main"."raw_customers" does not exist` | You skipped the ingestion step. From the repo root: `python scripts/ingest_raw.py`. |
| `Could not find profile named 'dbt_project'` | `dbt_project/profiles.yml` is missing or has the wrong top-level key. Go back to the profiles exercise. |
| `Compilation Error ... Unrecognized macro` | You probably typed `{{ ref('raw_customers') }}` or `{{ source(...) }}`. For this first run, use the plain `from main.raw_customers` shown above. |

## After you pass

Press `n`. The last exercise of Stage 1 sets a default materialization for everything in `staging/` — making this view-vs-table choice declarative across the whole folder.
