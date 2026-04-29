## Hint 1

One file change: `dbt_project/models/marts/fct_order_events.sql`. Replace the single-arg config block (`{{ config(materialized='incremental') }}`) with a multi-arg version that adds `unique_key='order_id'` and `incremental_strategy='merge'`.

Then `dbt build --select fct_order_events` from inside `dbt_project/`.

## Hint 2

The file in its final form:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

select
    order_id,
    customer_id,
    order_date,
    status
from {{ ref('stg__orders') }}

{% if is_incremental() %}
where order_date > (select max(order_date) from {{ this }})
{% endif %}
```

Three keyword arguments separated by commas. Whitespace and line breaks don't matter; this multi-line form is just for readability.

## Hint 3

If verification still fails:

1. `dbt build --select fct_order_events` should exit 0. If it errors with a `MERGE` syntax problem, check that the `unique_key` value is a single-quoted string (`unique_key='order_id'`), not a list — multi-column keys use lists, but here it's a single column.
2. `duckdb database/dev.duckdb -c "select count(*) from fct_order_events"` (from repo root) should return `99`.
3. `duckdb database/dev.duckdb -c "select count(distinct order_id) from fct_order_events"` should *also* return `99`. If it returns less, you have duplicates — most likely `incremental_strategy` isn't being read as `merge`. Check the spelling of the config key.
4. The verifier doesn't directly check the manifest config for `unique_key` / `incremental_strategy`. It infers correctness from "rows = distinct rows = 99". If both are 99 and `dbt build` is green, you're done.
