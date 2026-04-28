# Exercise — Build `stg__orders` and `stg__payments`

## Goal

Round out the staging layer by adding one model per remaining source table:

- `dbt_project/models/staging/stg__orders.sql` — selects from `source('jaffle_shop', 'raw_orders')`.
- `dbt_project/models/staging/stg__payments.sql` — selects from `source('stripe', 'raw_payments')`.

Both are light: rename ambiguous columns, cast Stripe's cents to dollars. No joins, no business logic.

## Steps

**1.** Create `dbt_project/models/staging/stg__orders.sql` with these contents:

```sql
select
    id          as order_id,
    user_id     as customer_id,
    order_date,
    status
from {{ source('jaffle_shop', 'raw_orders') }}
```

Two renames:

- `id → order_id` — disambiguates against the `id` in `raw_payments` and `raw_customers`.
- `user_id → customer_id` — matches the column name in `stg__customers`, so joins downstream read naturally.

**2.** Create `dbt_project/models/staging/stg__payments.sql`:

```sql
select
    id                       as payment_id,
    order_id,
    payment_method,
    amount / 100.0           as amount
from {{ source('stripe', 'raw_payments') }}
```

- `id → payment_id` — same disambiguation rule.
- `amount / 100.0` — Stripe stores money in cents. Dividing once here means every downstream model already gets dollars. Use `100.0` (decimal) so DuckDB casts to `DOUBLE` and you don't get integer truncation.

**3.** Build everything in the staging folder:

```bash
cd dbt_project
dbt run --select staging
```

You should see three green lines — `stg__customers`, `stg__orders`, `stg__payments` — plus a "Done" summary.

**4.** Sanity-check the new tables exist with the expected columns:

```bash
dbt show --select stg__orders --limit 3
dbt show --select stg__payments --limit 3
```

You should see `order_id` and `customer_id` in the orders preview, and `payment_id` plus a decimal `amount` in the payments preview.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt run --select staging` exits 0 — confirms both new files compile and execute.
- `stg__orders` and `stg__payments` exist as objects in `dev.duckdb`.
- A small SELECT against each table returns a row, proving the renamed columns landed.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: 'raw' is not a source declared in this project` | You're still using `source('raw', ...)`. Update to `source('jaffle_shop', ...)` or `source('stripe', ...)`. |
| `Binder Error: Referenced column "user_id" not found` | Misspelled column name. Check `data/raw_orders.csv` — the column is `user_id`. |
| Payment amounts are huge integers (e.g. `1000` for $10) | You forgot the `/ 100.0` cast, or used `100` instead of `100.0` (integer division). |
| `model 'stg__payments' references unknown source 'jaffle_shop.raw_payments'` | Wrong source. Payments belong to `stripe`. |

## After you pass

Press `n`. Next we'll start a new model layer — intermediates — by aggregating payments per order in `int_order_payments`.
