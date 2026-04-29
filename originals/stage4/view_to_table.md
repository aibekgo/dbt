# Exercise — Override `int_order_payments` to materialize as a table

## Goal

Add a `{{ config(materialized='table') }}` block to the top of `int_order_payments.sql`. The model is currently a view (per dbt's built-in default — the folder has no project-yml override). After this exercise, `int_order_payments` is a table in DuckDB.

## Steps

**1.** Open `dbt_project/models/intermediate/int_order_payments.sql`. Add a config block as the very first thing in the file:

```sql
{{ config(materialized='table') }}

select
    order_id,
    sum(amount)              as total_amount,
    count(*)                 as payment_count
from {{ ref('stg__payments') }}
group by order_id
```

The `select` stays exactly as it was. Only the config block at the top is new.

**2.** Re-run the model so the warehouse catches up:

```bash
cd dbt_project
dbt run --select int_order_payments
```

You should see one green line. dbt issued `create or replace table main.int_order_payments as select ...` instead of `create or replace view`.

**3.** Confirm the warehouse object changed shape:

```bash
duckdb ../database/dev.duckdb -c "select table_type from information_schema.tables where table_name='int_order_payments'"
```

Should print `BASE TABLE`. Before this exercise it printed `VIEW`.

**4.** (Optional but useful.) Inspect the manifest:

```bash
duckdb -c "select * from read_json('target/manifest.json')" | grep -i int_order_payments
```

Or open `target/manifest.json` and search for the `int_order_payments` node — `config.materialized` is now `"table"`.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt run --select int_order_payments` exits 0.
- `target/manifest.json` shows `int_order_payments` materialized as `table`.
- `information_schema.tables` reports `table_type = 'BASE TABLE'`.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Model 'int_order_payments' is materialized as 'view', expected 'table'` | The `{{ config(...) }}` block isn't being picked up. Two common causes: (a) you put it below the `select` instead of at the top of the file, or (b) the syntax has a typo (`materialized='table'` — single quotes around `table`, the `=` has no spaces in idiomatic dbt code, but spaces don't actually break it). |
| `Compilation Error: 'config' is not callable` | Spelling. Must be `{{ config(materialized='table') }}` exactly — `config`, lowercase, with parentheses. |
| `int_order_payments.table_type` is still `VIEW` | dbt builds against the warehouse, but you ran the verifier without re-running the model. Run `dbt run --select int_order_payments` first, then `v`. |
| `Catalog Error: Table with name int_order_payments already exists!` (rare) | Stale state — usually fixed by `dbt run --select int_order_payments --full-refresh` which forces a drop-and-recreate. |

## After you pass

Press `n`. The next exercise demonstrates the *opposite* tradeoff — switching the same model to `ephemeral`, where it disappears from DuckDB entirely and gets inlined as a CTE in `fct_orders`.
