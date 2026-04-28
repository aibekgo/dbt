## Hint 1

One new file: `dbt_project/models/marts/fct_orders.sql`. Drives from `stg__orders`, joins `stg__customers` for the name columns and `int_order_payments` for the dollar totals. Use `left join` for both, and `coalesce(…, 0)` on the payment columns.

Then `dbt run --select +fct_orders` from inside `dbt_project/`.

## Hint 2

The file in its final form:

```sql
-- dbt_project/models/marts/fct_orders.sql
select
    o.order_id,
    o.customer_id,
    c.first_name,
    c.last_name,
    o.order_date,
    o.status,
    coalesce(p.total_amount, 0)  as amount,
    coalesce(p.payment_count, 0) as payment_count
from {{ ref('stg__orders') }} o
left join {{ ref('stg__customers') }}     c using (customer_id)
left join {{ ref('int_order_payments') }} p using (order_id)
```

`using (customer_id)` and `using (order_id)` only work because Stage 2's staging models renamed `id` and `user_id` to those names. That's the whole point of the rename — joins read naturally across the layers.

## Hint 3

If verification still fails, walk through these checks:

1. `select count(*) from fct_orders` (via `duckdb ../database/dev.duckdb -c '...'`) should be **99**. If it's 113, you joined to `stg__payments` instead of `int_order_payments`. If it's less than 99, an `inner join` is filtering rows.
2. `select count(*) from stg__orders` should also be 99. If it isn't, the previous exercise's staging model needs rebuilding — run `dbt run --select staging` first.
3. The verifier expects the columns `order_id, customer_id, first_name, last_name, order_date, status, amount, payment_count`. Missing or renamed columns will fail the column-existence query.
4. If you're getting an "ambiguous column reference" error on `using`, you probably forgot the staging rename in `stg__orders` — `user_id` should already be aliased to `customer_id` there.
