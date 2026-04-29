# Exercise — Add generic tests + descriptions to the staging models

## Goal

Create `dbt_project/models/staging/_models.yml` declaring `unique` and `not_null` on the primary keys of all three staging models, plus `not_null` on the foreign-key columns. Add descriptions on the way through — the YAML file is the natural home for both.

## Steps

**1.** From the repo root, create a new file at `dbt_project/models/staging/_models.yml` with this content:

```yaml
version: 2

models:
  - name: stg__customers
    description: "One row per customer from the Jaffle Shop application database."
    columns:
      - name: customer_id
        description: "Surrogate primary key from raw_customers.id."
        tests:
          - unique
          - not_null
      - name: first_name
      - name: last_name

  - name: stg__orders
    description: "One row per order placed in the Jaffle Shop app."
    columns:
      - name: order_id
        description: "Primary key, renamed from raw_orders.id in staging."
        tests:
          - unique
          - not_null
      - name: customer_id
        description: "Foreign key to stg__customers.customer_id."
        tests:
          - not_null
      - name: status
        description: "Order lifecycle state. Constrained to a known set in the next exercise."

  - name: stg__payments
    description: "One row per payment event from Stripe (cents converted to dollars in staging)."
    columns:
      - name: payment_id
        description: "Primary key, renamed from raw_payments.id in staging."
        tests:
          - unique
          - not_null
      - name: order_id
        description: "Foreign key to stg__orders.order_id."
        tests:
          - not_null
```

**2.** From inside `dbt_project/`, run the tests:

```bash
cd dbt_project
dbt test --select staging
```

You should see seven tests run and pass:

```
Completed successfully

Done. PASS=7 WARN=0 ERROR=0 SKIP=0 TOTAL=7
```

(Three `unique` tests on the three primary keys, plus four `not_null` tests on `customer_id`/`order_id`/`payment_id`/`stg__orders.customer_id`.)

**3.** Sanity-check that the manifest sees the tests:

```bash
dbt ls --resource-type test --select staging
```

You should see seven lines like `dbt_project.unique_stg__customers_customer_id`, etc.

**4.** Press `v` to verify.

## What the verifier checks

- `dbt test --select staging` exits 0 and every test passes.
- `target/manifest.json` shows at least 2 tests on `stg__customers` (specifically `unique` and `not_null`).
- At least 2 tests on `stg__orders`.
- At least 2 tests on `stg__payments`.

The verifier is checking the **tests are declared**, not just that the YAML file exists. If you put the tests at the wrong YAML level (e.g. directly under the model instead of under a column), the count check will fail with a clear message.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: Invalid version 'version' for `models.yml`` | Missing `version: 2` at the top. Required for every schema YAML. |
| `Model `stg__customers` has 0 test(s) — expected at least 2` | The YAML loaded but tests didn't attach. Check that `tests:` is nested under a `columns: - name: customer_id` block, not at the model level. |
| `Model `stg__customers` has tests but none of type `unique`` | You added `not_null` but forgot `unique` (or vice versa). Both go under the same column. |
| `dbt test` reports `FAIL N` on a test | The data actually violates the assertion. Run the failing test manually with `dbt show --select <test_name>` to see the bad rows. (Shouldn't happen here — staging is 1:1 with the deterministic seed CSVs.) |
| `relationships test failed` on `customer_id` | You added a `relationships` test in this exercise. That comes in the next one — only do `unique` and `not_null` here. |

## After you pass

Press `n`. Next exercise extends `_models.yml` with `accepted_values` for `status` and adds a `relationships` test on `fct_orders` — the two remaining built-in generic tests.
