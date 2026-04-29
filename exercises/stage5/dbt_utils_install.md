# Exercise — Install `dbt_utils` and use `generate_surrogate_key`

## Goal

Install the `dbt_utils` package via `packages.yml` + `dbt deps`. Add an `order_key` column to `fct_orders` using `dbt_utils.generate_surrogate_key`.

## Steps

**1.** From the repo root, create `dbt_project/packages.yml`:

```bash
touch dbt_project/packages.yml
```

Paste this:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
```

The version range pins to the 1.x line — won't accidentally pull in 2.x breaking changes when they ship.

**2.** Install the package:

```bash
cd dbt_project
dbt deps
```

You should see one green line confirming the package was installed. After this, `dbt_project/dbt_packages/dbt_utils/` exists and contains the package's macros.

**3.** Open `dbt_project/models/marts/fct_orders.sql`. Add a new column at the end of the `select` list using the `generate_surrogate_key` macro. The full file should read:

```sql
select
    o.order_id,
    o.customer_id,
    c.first_name,
    c.last_name,
    o.order_date,
    o.status,
    coalesce(p.total_amount, 0)  as amount,
    coalesce(p.payment_count, 0) as payment_count,
    {{ dbt_utils.generate_surrogate_key(['o.order_id', 'o.customer_id']) }} as order_key
from {{ ref('stg__orders') }} o
left join {{ ref('stg__customers') }}     c using (customer_id)
left join {{ ref('int_order_payments') }} p using (order_id)
```

The macro takes a list of column references and returns an MD5-hashed surrogate key. Note the column names are passed as **strings inside a Python-style list** — `['o.order_id', 'o.customer_id']`. The strings can include table aliases.

**4.** Rebuild fct_orders:

```bash
dbt run --select fct_orders
```

You should see one green line.

**5.** Confirm the new column lands and is unique:

```bash
duckdb ../database/dev.duckdb -c "select count(distinct order_key) from fct_orders"
```

Should return `99`.

**6.** Peek at the actual values:

```bash
duckdb ../database/dev.duckdb -c "select order_id, order_key from fct_orders limit 3"
```

Three rows, each with `order_id` (an integer) and `order_key` (a 32-character MD5 hash like `c4ca4238a0b923820dcc509a6f75849b`).

**7.** Press `v` to verify.

## What the verifier checks

- `dbt_project/dbt_packages/dbt_utils/` exists (proves `dbt deps` ran).
- `dbt run --select fct_orders` exits 0 (proves the model parses and runs with the new macro call).
- `select count(distinct order_key) from fct_orders` returns `99` (proves the surrogate key is unique across all 99 orders).

## Common failure modes

| Symptom | Fix |
|---|---|
| `path 'dbt_project/dbt_packages/dbt_utils' does not exist` | You skipped `dbt deps`. Run `cd dbt_project && dbt deps`. |
| `Compilation Error: 'dbt_utils' is undefined` | The package didn't install correctly, or you're calling the macro without the prefix. Check `dbt_project/dbt_packages/dbt_utils/` exists and your call is `{{ dbt_utils.generate_surrogate_key(...) }}` with the prefix. |
| `count(distinct order_key)` returns less than 99 | Two rows hashed to the same key — usually means the column list is too narrow. `['o.order_id']` alone would still be unique here, but something like `['o.status']` would collide (since orders share statuses). Verify the column list is `['o.order_id', 'o.customer_id']`. |
| `Error: Module 'dbt-labs/dbt_utils' not found` | `packages.yml` syntax issue. The key is `package:` (singular under each list item), not `name:` or anything else. |
| Stage 4's `incremental_merge` exercise's verifier breaks | Unrelated — the new `order_key` column is on `fct_orders`, not `fct_order_events`. Should not interfere. |

## After you pass

That's the last exercise of Stage 5. Press `n` to take the stage quiz. Stage 6 (advanced testing, deployment, the dbt CLI surface) is the next planning session.
