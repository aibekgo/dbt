## Hint 1

One file. From the repo root:

```bash
cd dbt_project
mkdir -p models/staging
touch models/staging/stg_customers.sql
```

Then paste the SELECT into that file. No YAML, no `{{ source(...) }}` macro for now — just a plain SQL query.

## Hint 2

The model is literally three columns from one raw table:

```sql
select
    id          as customer_id,
    first_name,
    last_name
from main.raw_customers
```

`main` is DuckDB's default schema, where `scripts/ingest_raw.py` wrote the raw tables. We hardcode it for this very first model so you can see dbt run end-to-end with zero ceremony. Stage 2 wires up `{{ source(...) }}` properly.

## Hint 3

If `dbt run` fails with `Relation "dev"."main"."raw_customers" does not exist`, you skipped ingestion. From the repo root:

```bash
python scripts/ingest_raw.py
```

…then come back to `dbt_project/` and re-run `dbt run --select stg_customers`. Sanity check: `dbt ls --select stg_customers` should print `dbt_project.staging.stg_customers`.
