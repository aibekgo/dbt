## Hint 1

Two file changes:

1. `dbt_project/models/staging/_models.yml` — extend the existing `status` column under `stg__orders` with an `accepted_values` test.
2. `dbt_project/models/marts/_models.yml` — **new file** declaring `fct_orders` and adding `unique`, `not_null`, and `relationships` tests.

Watch for the `relationships` syntax: `to: ref('dim_customers')` (a Jinja expression with quotes only inside `ref(...)`), not `to: 'dim_customers'` (a bare string).

Then `dbt test --select fct_orders` from inside `dbt_project/`.

## Hint 2

Final shapes:

```yaml
# dbt_project/models/staging/_models.yml — only the status column changes
- name: status
  description: "Order lifecycle state."
  tests:
    - accepted_values:
        values: [placed, shipped, completed, return_pending, returned]
```

```yaml
# dbt_project/models/marts/_models.yml — new file
version: 2

models:
  - name: fct_orders
    description: "One row per order, denormalized with customer attributes and payment totals."
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

The list of accepted values is the five jaffle_shop order statuses — those are the only ones the seed CSVs produce.

## Hint 3

If verification still fails:

1. `dbt parse` — does it exit 0? If `Could not find a model named 'dim_customers'`, you wrote `to: 'dim_customers'` instead of `to: ref('dim_customers')`. The Jinja `ref()` wrapper is mandatory.
2. `dbt ls --resource-type test --select fct_orders` should print at least 3 tests including one whose name starts with `relationships_`.
3. `dbt test --select fct_orders` should report `PASS=3 WARN=0 ERROR=0 SKIP=0`. If `accepted_values` fails with `FAIL`, run `select distinct status from stg__orders` to check what statuses are actually in the data.
4. `dbt test --select stg__orders` should now show 4 tests (the original `unique`/`not_null` on `order_id`, the `not_null` on `customer_id`, plus the new `accepted_values` on `status`).
