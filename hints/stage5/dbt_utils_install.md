## Hint 1

Two file changes:

1. Create `dbt_project/packages.yml` listing `dbt-labs/dbt_utils` as a package with a version range.
2. Edit `dbt_project/models/marts/fct_orders.sql` to add an `order_key` column at the end of the `select` list using `{{ dbt_utils.generate_surrogate_key(['o.order_id', 'o.customer_id']) }}`.

Between the two: run `dbt deps` from inside `dbt_project/` to install the package. Then `dbt run --select fct_orders`.

## Hint 2

Final shapes:

```yaml
# dbt_project/packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
```

The relevant added line in `fct_orders.sql`:

```sql
{{ dbt_utils.generate_surrogate_key(['o.order_id', 'o.customer_id']) }} as order_key
```

Three things to double-check:
- Note the dot prefix: `dbt_utils.generate_surrogate_key`, not just `generate_surrogate_key`.
- The argument is a Python-style list of strings: `['o.order_id', 'o.customer_id']`.
- It goes inside the `select` block, with a comma separating it from the previous column.

## Hint 3

If verification still fails:

1. `ls dbt_project/dbt_packages/dbt_utils/` should list files. If the directory doesn't exist, `dbt deps` didn't run — `cd dbt_project && dbt deps`.
2. `dbt run --select fct_orders` should exit 0. If it errors with *"'dbt_utils' is undefined"*, the package didn't install. If it errors with a SQL syntax issue near `as order_key`, the macro call has a typo — check that `[` and `]` are around the column list.
3. `duckdb database/dev.duckdb -c "select count(distinct order_key) from fct_orders"` (from repo root) should return `99`. If it returns less, two rows are hashing to the same key — verify the column list is `['o.order_id', 'o.customer_id']` (both columns).
4. The verifier doesn't check the macro call's exact form, just that `dbt_packages/dbt_utils/` exists, `fct_orders` builds, and `order_key` is unique. So if all three are true, you pass.
