## Hint 1

One file, no YAML, no Jinja. From the repo root:

```bash
cd dbt_project
mkdir -p models/staging
touch models/staging/stg__customers.sql
```

Then write a plain `SELECT` with `from main.raw_customers` (no `ref()`, no `source()`).

## Hint 2

The full file:

```sql
select
    id          as customer_id,
    first_name,
    last_name
from main.raw_customers
```

`main` is DuckDB's default schema, where `scripts/ingest_raw.py` wrote the raw tables. We're hardcoding it on purpose for this very first model. The next exercise (`add_sources`) wires up `{{ source(...) }}` properly.

## Hint 3

If `dbt run` fails with `Relation "dev"."main"."raw_customers" does not exist`, you skipped ingestion. From the repo root:

```bash
python scripts/ingest_raw.py
```

Then come back to `dbt_project/` and re-run `dbt run --select stg__customers`. Sanity check: `dbt ls --select stg__customers` should print `dbt_project.staging.stg__customers`.
