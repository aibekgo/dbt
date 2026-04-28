## Hint 1

Two new files, both under `dbt_project/models/staging/`:

- `stg__orders.sql` — `select … from {{ source('jaffle_shop', 'raw_orders') }}`. Rename `id` to `order_id` and `user_id` to `customer_id`.
- `stg__payments.sql` — `select … from {{ source('stripe', 'raw_payments') }}`. Rename `id` to `payment_id`, divide `amount` by `100.0`.

Then `dbt run --select staging` from inside `dbt_project/` to build all three staging models.

## Hint 2

The two files in their final form:

```sql
-- dbt_project/models/staging/stg__orders.sql
select
    id          as order_id,
    user_id     as customer_id,
    order_date,
    status
from {{ source('jaffle_shop', 'raw_orders') }}
```

```sql
-- dbt_project/models/staging/stg__payments.sql
select
    id                       as payment_id,
    order_id,
    payment_method,
    amount / 100.0           as amount
from {{ source('stripe', 'raw_payments') }}
```

`100.0` (with the decimal) is important — `amount / 100` would do integer division and you'd lose any cents.

## Hint 3

If verification still fails:

1. Did you save both files at exactly `dbt_project/models/staging/stg__orders.sql` and `dbt_project/models/staging/stg__payments.sql`? Typos in the path are easy.
2. `dbt run --select staging` from inside `dbt_project/` should finish with three green lines. If one fails, the error message names the file.
3. The verifier runs `select order_id, customer_id, order_date, status from stg__orders limit 1` and `select payment_id, order_id, payment_method, amount from stg__payments limit 1` — if a column is missing or misspelled in your `select`, those queries error out.
4. Check `data/raw_orders.csv` and `data/raw_payments.csv` for the source-side column names if you're unsure.
