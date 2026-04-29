# Exercise — Make `int_order_payments` ephemeral

## Goal

Change `int_order_payments` from `table` (set in the previous exercise) to `ephemeral`. After this change, `int_order_payments` is no longer a queryable warehouse object — its SQL gets inlined as a CTE in `fct_orders` whenever the fact is rebuilt. `fct_orders` still has the same 99 rows.

## Steps

**1.** Open `dbt_project/models/intermediate/int_order_payments.sql`. Change the config block's value from `table` to `ephemeral`:

```sql
{{ config(materialized='ephemeral') }}

select
    order_id,
    sum(amount)              as total_amount,
    count(*)                 as payment_count
from {{ ref('stg__payments') }}
group by order_id
```

That's the only edit — one word change. The `select` stays as-is.

**2.** Rebuild the marts chain with `--full-refresh` so the leftover `int_order_payments` table gets dropped and `fct_orders` is rebuilt with the inlined CTE:

```bash
cd dbt_project
dbt run --select +fct_orders --full-refresh
```

The `+` selector means "this model and everything upstream"; `--full-refresh` forces dbt to drop and recreate. The output should show `int_order_payments` skipped (it's ephemeral, nothing to materialize) and `fct_orders` rebuilt as a table.

**3.** Confirm `fct_orders` still has 99 rows — proving the inlining works:

```bash
duckdb ../database/dev.duckdb -c "select count(*) from fct_orders"
```

Should print `99`.

**4.** (Optional, for the visual win.) Look at the compiled `fct_orders` SQL and find the inlined CTE:

```bash
cat target/compiled/dbt_project/models/marts/fct_orders.sql | head -25
```

You'll see a `with __dbt__cte__int_order_payments as (...)` block at the top — that's the ephemeral's query, inlined verbatim.

**5.** (Also optional but reinforcing.) Confirm `int_order_payments` is no longer a queryable table:

```bash
duckdb ../database/dev.duckdb -c "select * from int_order_payments limit 1"
```

Should error with *"Catalog Error: Table with name int_order_payments does not exist!"* — exactly the point of `ephemeral`.

**6.** Press `v` to verify.

## What the verifier checks

- `dbt run --select +fct_orders` exits 0.
- `target/manifest.json` reports `int_order_payments` as `materialized: ephemeral`.
- `select count(*) from fct_orders` returns `99` — proving the ephemeral inlining produced correct totals.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Model 'int_order_payments' is materialized as 'table', expected 'ephemeral'` | The config block still says `table`. Change it to `ephemeral`. |
| `Compilation Error: ephemeral model has tests attached` | If you added tests to `int_order_payments` somewhere (you didn't in this stage, but worth knowing), generic tests on ephemerals are forbidden. Move the model to `view` or remove the tests. |
| `fct_orders has 0 rows` | The full-refresh didn't run, or `fct_orders` never got rebuilt against the new ephemeral. Re-run `dbt run --select +fct_orders --full-refresh`. |
| `Catalog Error: Table with name int_order_payments does not exist!` (when running queries against it directly) | This is **expected** for an ephemeral — there's no warehouse object. Verifier doesn't assert the table doesn't exist (since the leftover may persist), but the *correct* state is that the table is gone. |

## After you pass

Press `n`. The next two exercises shift to **incremental** materializations — the most operationally important one for production dbt projects. You'll build `fct_order_events` from scratch.
