## Hint 1

Two changes:

1. Create `dbt_project/models/staging/_sources.yml` with the source declaration.
2. Edit `dbt_project/models/staging/stg__customers.sql` so its `from` line uses `{{ source('raw', 'raw_customers') }}` instead of the hardcoded `main.raw_customers`.

Then `dbt run --select stg__customers` from inside `dbt_project/`.

## Hint 2

The two files in their final form:

```yaml
# dbt_project/models/staging/_sources.yml
version: 2

sources:
  - name: raw
    schema: main
    tables:
      - name: raw_customers
      - name: raw_orders
      - name: raw_payments
```

```sql
-- dbt_project/models/staging/stg__customers.sql
select
    id          as customer_id,
    first_name,
    last_name
from {{ source('raw', 'raw_customers') }}
```

`schema: main` is the key field — that's where `scripts/ingest_raw.py` writes. If you put `schema: raw` instead, dbt will look for a `raw` schema that doesn't exist and error out.

## Hint 3

Sanity checks after the run:

- `dbt ls --resource-type source` should print three lines: `dbt_project.raw.raw_customers`, `raw_orders`, `raw_payments`.
- `dbt ls --select source:raw+` should also print `dbt_project.staging.stg__customers` — proving dbt now sees the dependency.
- If the verifier fails, double-check the file lives at exactly `dbt_project/models/staging/_sources.yml` and is at least ~80 bytes (the verifier checks size).
