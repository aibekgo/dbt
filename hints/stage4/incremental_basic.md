## Hint 1

One new file: `dbt_project/models/marts/fct_order_events.sql`. The folder already exists.

The model's three pieces:
- `{{ config(materialized='incremental') }}` at the top
- A regular `select` from `{{ ref('stg__orders') }}` projecting four columns: `order_id`, `customer_id`, `order_date`, `status`
- An `{% if is_incremental() %}` block wrapping `where order_date > (select max(order_date) from {{ this }})` — entire clause inside the block, including the `where` keyword

Then `dbt build --select fct_order_events` from inside `dbt_project/`.

## Hint 2

The file in its final form:

```sql
{{ config(materialized='incremental') }}

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

Two non-obvious bits:

1. `{{ this }}` (lowercase, no quotes inside) is the model's self-reference. It's a special escape from the normal `ref()` pattern — `{{ ref('fct_order_events') }}` from inside this file would be a circular dependency.
2. The `where` keyword is **inside** the `{% if %}`. If you put `where` outside and only the predicate inside, the first-run compile produces a dangling `where` and breaks.

## Hint 3

If verification still fails:

1. `dbt build --select fct_order_events` should print `1 of 1 START sql incremental model main.fct_order_events`. The word `incremental` confirms the materialization is set.
2. `duckdb database/dev.duckdb -c "select count(*) from fct_order_events"` (from repo root) should return `99`.
3. If the build errors with *"Compilation Error: ... near 'where'"*, the `where` is outside the if-block — move it inside.
4. If the build succeeds but the verifier complains about materialization, the manifest hasn't picked up the new config. Try `dbt parse` then re-run the verifier.
5. If the build *runs twice cleanly* but the row count is still 99 the second time, that's *correct* — the seed is static, so the incremental insert finds no new rows. The verifier only asserts 99 after one (or any number of) builds.
