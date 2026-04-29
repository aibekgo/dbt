## Hint 1

One file change: `dbt_project/models/intermediate/int_order_payments.sql`. Add `{{ config(materialized='table') }}` as the first thing in the file (above the `select`).

Then `dbt run --select int_order_payments` from inside `dbt_project/` to re-issue the warehouse DDL.

## Hint 2

The file in its final form:

```sql
{{ config(materialized='table') }}

select
    order_id,
    sum(amount)              as total_amount,
    count(*)                 as payment_count
from {{ ref('stg__payments') }}
group by order_id
```

The config block must be at the top — dbt's parser looks for `config()` calls before evaluating the SQL, so a config below the select is just inert text.

## Hint 3

If verification still fails:

1. Confirm the file has the `{{ config(...) }}` block at the very top — even before any blank lines or comments.
2. `dbt run --select int_order_payments` from inside `dbt_project/` should print *"OK created sql table model main.int_order_payments"* — the word `table` is the giveaway. If it prints `view`, the config didn't take effect.
3. `duckdb ../database/dev.duckdb -c "select table_type from information_schema.tables where table_name='int_order_payments'"` should return `BASE TABLE`. If it returns `VIEW`, the previous view is still there — re-run `dbt run --select int_order_payments` and DuckDB should `drop view` then `create table`.
4. The verifier reads `target/manifest.json` after a `dbt parse` — if the manifest still says `view`, the parse didn't see the new config. Try `dbt parse` manually and recheck.
