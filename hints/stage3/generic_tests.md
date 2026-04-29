## Hint 1

One new file: `dbt_project/models/staging/_models.yml`. The folder already exists (it has `_sources.yml` and your three `stg__*.sql` files). Use a leading underscore so it sorts to the top.

The shape: `version: 2` at the top, then `models:` (plural, list), one entry per model. Each entry has `name:`, `description:`, and `columns:`. Tests attach to columns, not to models — they go under `columns: - name: <col>: tests: -`.

The seven tests you need:
- `stg__customers.customer_id`: unique + not_null
- `stg__orders.order_id`: unique + not_null
- `stg__orders.customer_id`: not_null only
- `stg__payments.payment_id`: unique + not_null
- `stg__payments.order_id`: not_null only

Then `dbt test --select staging` from inside `dbt_project/`.

## Hint 2

The minimum-viable file (descriptions optional for the verifier, but write them anyway — the lesson explains why):

```yaml
version: 2

models:
  - name: stg__customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null

  - name: stg__orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null

  - name: stg__payments
    columns:
      - name: payment_id
        tests:
          - unique
          - not_null
      - name: order_id
        tests:
          - not_null
```

Indentation is two spaces per level. YAML hates tabs.

## Hint 3

If verification still fails:

1. `dbt parse` from inside `dbt_project/` — does it exit 0? If not, the error message names the YAML file and line. Most often it's a missing `version: 2` line or wrong indentation under `tests:`.
2. `dbt ls --resource-type test --select staging` should print 7 lines like `dbt_project.unique_stg__customers_customer_id`. If it prints 0, the tests aren't attached — check the YAML structure. If it prints 7 but they're attached to the wrong models, double-check the `name:` under each `models:` entry matches the SQL filename exactly (with the double underscore).
3. `dbt test --select staging` should exit 0 with `PASS=7 WARN=0 ERROR=0 SKIP=0 TOTAL=7`. If a test fails (`FAIL=1`), the data violates the assertion — `dbt show --select <test_unique_id> --limit 5` shows the offending rows.
4. The verifier doesn't care about descriptions, ordering, or extra columns listed without tests. Only the test count per model matters.
