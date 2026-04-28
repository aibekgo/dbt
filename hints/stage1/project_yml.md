## Hint 1

Two changes:

1. Edit `dbt_project/dbt_project.yml` — replace the `models:` block at the bottom so `staging:` is `view` and `marts:` is `table`.
2. Create a new model `dbt_project/models/marts/dim_customers.sql` that selects from `{{ ref('stg__customers') }}`.

Then `dbt run` from inside `dbt_project/` and press `v`.

## Hint 2

The two file states:

```yaml
# dbt_project/dbt_project.yml — the bottom block
models:
  dbt_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

```sql
-- dbt_project/models/marts/dim_customers.sql
select
    customer_id,
    first_name,
    last_name
from {{ ref('stg__customers') }}
```

The leading `+` on `+materialized` is required — without it, dbt looks for a folder called `materialized/` and silently does nothing. The project name (`dbt_project:`) must match the `name:` field at the top of the same YAML file.

## Hint 3

If `dbt run` complains that `stg__customers` doesn't exist, just run `dbt run` once (no `--select`) so dbt builds everything in dependency order.

To confirm the materializations are different *before* pressing `v`:

```bash
duckdb ../database/dev.duckdb -c "
  select table_name, table_type
  from information_schema.tables
  where table_schema = 'main_main';
"
```

You should see `stg__customers` as `VIEW` and `dim_customers` as `BASE TABLE`. If `dim_customers` shows up as a view, the `marts:` block in `dbt_project.yml` isn't being picked up — usually a missing `+`, indentation drift, or a mismatched project name.
