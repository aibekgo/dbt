## Hint 1

One file change: `dbt_project/models/intermediate/int_order_payments.sql`. Change `materialized='table'` to `materialized='ephemeral'` inside the existing `{{ config(...) }}` block.

Then `dbt run --select +fct_orders --full-refresh` from inside `dbt_project/` to rebuild fct_orders with the inlined CTE.

## Hint 2

The file in its final form:

```sql
{{ config(materialized='ephemeral') }}

select
    order_id,
    sum(amount)              as total_amount,
    count(*)                 as payment_count
from {{ ref('stg__payments') }}
group by order_id
```

The `--full-refresh` matters here: without it, dbt would preserve the leftover `int_order_payments` table from the previous exercise. With it, dbt drops the old table and rebuilds `fct_orders` with the ephemeral's SQL inlined as a CTE.

## Hint 3

If verification still fails:

1. `dbt run --select +fct_orders --full-refresh` should print `1 of 2 START sql ephemeral model main.int_order_payments` (yes — *ephemeral* — followed by `2 of 2 START sql table model main.fct_orders`). The ephemeral line confirms the materialization is set.
2. `duckdb database/dev.duckdb -c "select count(*) from fct_orders"` (from repo root) should return `99`. If it returns `0`, fct_orders didn't get rebuilt — re-run with `--full-refresh`.
3. The verifier reads `target/manifest.json` for the materialization. Try `dbt parse` manually if the verifier still says `table` — the manifest may not have been refreshed.
4. If you see *"Cannot test an ephemeral model"*, you've added a test to `int_order_payments` somewhere. None of the Stage 3 exercises did this, so it's most likely a stray test in `_models.yml` — remove it or change the materialization to `view`.
