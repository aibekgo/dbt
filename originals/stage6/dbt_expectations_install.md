# Exercise — Install `dbt_expectations` and add a range test

## Goal

Extend the existing `packages.yml` (from Stage 5) with `calogica/dbt_expectations`. Run `dbt deps`. Add `dbt_expectations.expect_column_values_to_be_between` on `fct_orders.amount` to assert all values fall in `[0, 100]`.

## Steps

**1.** Open `dbt_project/packages.yml`. Add the new package as a second entry. The full file should read:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
```

Note: the org is `calogica`, not `dbt-labs`.

**2.** Install the new package:

```bash
cd dbt_project
dbt deps
```

You should see two packages installed (or "up to date" for `dbt_utils`, "installed" for `dbt_expectations`). After this, `dbt_packages/dbt_expectations/` exists.

**3.** Open `dbt_project/models/marts/_models.yml`. Find the `fct_orders` block. Replace it with this version that adds an `amount` column entry with the new test:

```yaml
version: 2

models:
  - name: fct_orders
    description: "One row per order, denormalized with customer attributes and payment totals."
    columns:
      - name: order_id
        description: "Primary key. Inherited from stg__orders."
        tests:
          - unique
          - not_null
      - name: customer_id
        description: "Foreign key to dim_customers."
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: amount
        description: "Total dollar amount paid across all payments for this order."
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100
```

The new column entry has `dbt_expectations.expect_column_values_to_be_between` as its test, with `min_value` and `max_value` arguments.

**4.** Run the tests:

```bash
dbt test --select fct_orders
```

You should see all four tests pass: `unique`, `not_null`, `relationships`, and the new `expect_column_values_to_be_between`.

```
Done. PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4
```

**5.** Confirm the new test count in the manifest:

```bash
dbt ls --resource-type test --select fct_orders
```

Four lines, including one starting with `dbt_expectations_expect_column_values_to_be_between_fct_orders_amount`.

**6.** Press `v` to verify.

## What the verifier checks

- `dbt_project/dbt_packages/dbt_expectations/` exists (proves `dbt deps` ran successfully).
- `dbt test --select fct_orders` exits 0 with all tests passing.
- `target/manifest.json` shows `fct_orders` has at least 4 tests.

## Common failure modes

| Symptom | Fix |
|---|---|
| `path 'dbt_project/dbt_packages/dbt_expectations' does not exist` | You skipped `dbt deps`. Run it from inside `dbt_project/`. |
| `Encountered an error: package_name 'dbt-labs/dbt_expectations' not found` | The package is published under `calogica/dbt_expectations`, not `dbt-labs/`. Fix the org prefix. |
| `Compilation Error: macro 'expect_column_values_to_be_between' is undefined` | You forgot the `dbt_expectations.` prefix. Tests in packages need the package name as a prefix. |
| Test reports `FAIL` | The data violates the bounds. Run `select max(amount), min(amount) from fct_orders` to see the actual range — adjust `min_value` / `max_value` if needed. With the seed data, max should be under $100 and min should be 0. |
| `Model 'fct_orders' has 3 test(s) — expected at least 4` | The new test didn't attach. Check the YAML indent — `dbt_expectations.expect_column_values_to_be_between:` is under `tests: -`, with `min_value:` and `max_value:` nested under that. |

## After you pass

Press `n`. Next is the **dbt CLI tour** — `dbt show`, `dbt parse`, `dbt ls`, and the rest of the day-to-day commands you'll use as a senior dbt practitioner.
