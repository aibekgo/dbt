# Exercise — Build `int_order_payments`

## Goal

Create your first intermediate model. It rolls `stg__payments` (113 rows, one per payment) up to **one row per `order_id`** with two aggregates: `total_amount` and `payment_count`. The next exercise's fact table joins to it.

## Steps

**1.** From the repo root, create the intermediate folder (peer of `staging/` and `marts/`, not nested under either) and the new model file:

```bash
mkdir -p dbt_project/models/intermediate
touch dbt_project/models/intermediate/int_order_payments.sql
```

**2.** Paste this into `int_order_payments.sql`:

```sql
select
    order_id,
    sum(amount)              as total_amount,
    count(*)                 as payment_count
from {{ ref('stg__payments') }}
group by order_id
```

Three things to notice:

- **`{{ ref('stg__payments') }}`** — intermediates depend on staging via `ref()`, not on the source. The `amount / 100.0` cast you wrote in staging is already applied; you get dollars here, not cents.
- **`group by order_id`** — collapses 113 payment rows to 99 unique-order rows.
- **No `{{ config(...) }}` block at the top.** Without an explicit `intermediate:` entry in `dbt_project.yml`, the model defaults to `view` — which is the conventional choice for intermediates: cheap to recompute while you debug, no warehouse storage to babysit.

**3.** Build it:

```bash
cd dbt_project
dbt run --select int_order_payments
```

You should see one green line. dbt automatically rebuilds `stg__payments` first if it isn't fresh.

**4.** Sanity-check the result:

```bash
dbt show --select int_order_payments --limit 5
```

Five rows, three columns, totals look like dollar amounts (e.g. `26.00`, not `2600`).

```bash
duckdb ../database/dev.duckdb -c "select count(*) from int_order_payments"
```

Should print `99` — one row per distinct `order_id` from `raw_payments`.

**5.** Press `v`.

## What the verifier checks

- `dbt run --select int_order_payments` exits 0.
- The table `int_order_payments` exists in `dev.duckdb`.
- `select count(*) from int_order_payments` returns `99` — confirming the `group by` collapsed payments to the order grain.
- `select count(distinct order_id) from int_order_payments` also returns `99` — confirming `order_id` is unique per row.
- `payment_count` and `total_amount` columns are present.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: Model 'int_order_payments' depends on a node named 'stg__payments' which was not found` | Either you skipped the previous exercise (`stg__payments` doesn't exist) or you typed `ref('stg_payments')` (single underscore). Check the model name in `models/staging/`. |
| Row count is `113` instead of `99` | Missing `group by order_id`, or `count(*)` was applied at the wrong grain. |
| `total_amount` shows huge integer values | The cents → dollars cast didn't happen — check that `stg__payments` has `amount / 100.0`. The intermediate just sums what staging gives it. |
| `Binder Error: column "order_id" must appear in the GROUP BY clause` | The `select` list includes a column that isn't aggregated and isn't grouped on. Either group on it or wrap it in `min()` / `max()` / `sum()`. |

## After you pass

Press `n`. Time to land the fact table — `fct_orders` will join all three staging models plus this intermediate into the one denormalized table the analyst actually queries.
