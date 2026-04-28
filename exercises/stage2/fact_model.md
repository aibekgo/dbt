# Exercise — Build `fct_orders`

## Goal

Build the first fact table in the project. `fct_orders` has **one row per order**, joins in customer attributes from `stg__customers`, and rolls in payment totals from `int_order_payments`. After this, an analyst could query `fct_orders` directly to answer "who spent how much, on what, when."

## Steps

**1.** Create `dbt_project/models/marts/fct_orders.sql`:

```sql
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

Things to look at while you're typing:

- **`stg__orders` is the driving table.** It sets the grain (one row per order). Both other models are `left join`-ed in.
- **`coalesce(…, 0)`** — defensive defaults so analyst-facing queries don't have to handle nulls.
- **`using (customer_id)` / `using (order_id)`** — works because Stage 2's renames made the column names line up across staging models. If they didn't, you'd write `on o.customer_id = c.customer_id` instead.
- No materialization block — `models/marts/` inherits `+materialized: table` from `dbt_project.yml`.

**2.** Build the whole chain:

```bash
cd dbt_project
dbt run --select +fct_orders
```

The `+` prefix means "this model and everything upstream" — dbt will rebuild any staging or intermediate models that aren't fresh, in the right order, before building the fact.

You should see four green nodes: `stg__customers`, `stg__orders`, `stg__payments`, `int_order_payments`, then `fct_orders`.

**3.** Sanity-check the grain matches `stg__orders`:

```bash
duckdb ../database/dev.duckdb -c "
  select
    (select count(*) from stg__orders)   as orders_count,
    (select count(*) from fct_orders)    as fact_count;
"
```

Both should be `99`. If `fact_count` is bigger, a join fanned out (likely you used `stg__payments` instead of `int_order_payments`). If smaller, an `inner join` filtered rows out.

**4.** Spot-check a few rows look right:

```bash
dbt show --select fct_orders --limit 5
```

Each row should have a customer name, an `amount` in dollars (e.g. `26.00`), and a `payment_count` between 1 and 3 for orders with payments.

**5.** Press `v`.

## What the verifier checks

- `dbt run --select +fct_orders` exits 0, building all dependencies in DAG order.
- The table `fct_orders` exists in `dev.duckdb`.
- `select count(*) from fct_orders` equals `select count(*) from stg__orders` — proving no fan-out, no row loss.
- The schema has the columns: `order_id`, `customer_id`, `first_name`, `last_name`, `order_date`, `status`, `amount`, `payment_count`.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: Model 'fct_orders' depends on a node named 'int_order_payments' which was not found` | Previous exercise didn't ship — go back to `intermediate_model`. |
| `select count(*) from fct_orders` is 113 instead of 99 | You joined directly to `stg__payments`. Use the intermediate (`int_order_payments`) — that's why we built it. |
| `select count(*) from fct_orders` is less than 99 | Inner join filtered rows. Switch to `left join` for the customer / payments joins. |
| `Binder Error: Reference to column "customer_id" is ambiguous` | `using (customer_id)` requires the column to have the same name in both tables. If you wrote `o.user_id` instead of `o.customer_id`, switch to `on o.user_id = c.customer_id` or fix the staging rename. |

## After you pass

Press `n`. You've finished the model layer for Stage 2. The remaining two exercises are dbt CLI tooling: `dbt build` (the unified build command) and `dbt docs` (the lineage site).
