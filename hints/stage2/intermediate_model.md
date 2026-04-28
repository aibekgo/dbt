## Hint 1

One new file: `dbt_project/models/intermediate/int_order_payments.sql`. The folder doesn't exist yet — `mkdir -p` it first.

The model selects from `{{ ref('stg__payments') }}`, groups by `order_id`, and emits three columns: `order_id`, `total_amount` (sum of `amount`), and `payment_count` (count of rows).

Then `dbt run --select int_order_payments` from inside `dbt_project/`.

## Hint 2

The file in its final form:

```sql
-- dbt_project/models/intermediate/int_order_payments.sql
select
    order_id,
    sum(amount)              as total_amount,
    count(*)                 as payment_count
from {{ ref('stg__payments') }}
group by order_id
```

99 rows out, one per `order_id`. The `total_amount` is in dollars because `stg__payments` already divided by `100.0`.

## Hint 3

If verification still fails:

1. Confirm the file path is exactly `dbt_project/models/intermediate/int_order_payments.sql`. dbt scans `model-paths: ["models"]` and any subfolder is fine, but the file has to actually be on disk.
2. `dbt run --select int_order_payments` must succeed. If you get *"depends on a node named 'stg__payments' which was not found"*, the previous exercise's file isn't in place yet — go back and finish `more_staging`.
3. The verifier runs `select count(*) from int_order_payments` and expects `99`. If you get `113`, the `group by` is missing. If you get `1`, you grouped on a constant.
4. The model has no explicit `intermediate:` config in `dbt_project.yml`, so it defaults to `view` — that's the conventional choice and you don't need to add a `{{ config(...) }}` block.
