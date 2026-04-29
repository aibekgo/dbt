## Hint 1

One new file: `dbt_project/snapshots/orders_snapshot.sql`. The `snapshots/` folder is part of the default dbt scaffold so it should already exist (empty before this exercise).

The file structure is unusual — content is wrapped in `{% snapshot orders_snapshot %} ... {% endsnapshot %}` tags. Inside: a config block (with `target_schema`, `unique_key`, `strategy='check'`, `check_cols=['status']`) and a `select * from {{ ref('stg__orders') }}`.

Then `dbt snapshot --select orders_snapshot` from inside `dbt_project/`.

## Hint 2

The file in its final form:

```sql
{% snapshot orders_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='order_id',
        strategy='check',
        check_cols=['status']
    )
}}

select * from {{ ref('stg__orders') }}

{% endsnapshot %}
```

The four config keys are all required for `check`-strategy snapshots:
- `target_schema='snapshots'` — separate schema
- `unique_key='order_id'` — primary key for matching
- `strategy='check'` — column-comparison detection
- `check_cols=['status']` — which column(s) to watch

## Hint 3

If verification still fails:

1. `ls dbt_project/snapshots/` — should list `orders_snapshot.sql`. The file extension is `.sql`, not `.yml`.
2. `dbt snapshot --select orders_snapshot` should print *"OK snapshotted snapshots.orders_snapshot"*. The schema (`snapshots`) is dbt-created on first run.
3. `duckdb database/dev.duckdb -c "select count(*) from snapshots.orders_snapshot"` (from repo root) should return `99`.
4. `duckdb database/dev.duckdb -c "describe snapshots.orders_snapshot"` should show columns including `dbt_scd_id`, `dbt_updated_at`, `dbt_valid_from`, `dbt_valid_to` alongside `order_id`, `customer_id`, `order_date`, `status`.
5. If `dbt snapshot` errors with *"Snapshots require either a 'check' or 'timestamp' strategy"*, the `strategy='check'` line is missing or misspelled. If it errors with *"'check' strategy requires 'check_cols'"*, add `check_cols=['status']`.
