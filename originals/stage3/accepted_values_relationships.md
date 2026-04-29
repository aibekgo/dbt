# Exercise — Add `accepted_values` and `relationships` tests

## Goal

Extend the testing coverage with the other two built-in generic tests:

- `accepted_values` on `stg__orders.status` (constrains it to the five known order states)
- `relationships` on `fct_orders.customer_id` → `dim_customers.customer_id` (foreign-key integrity)

You're touching two YAML files: extending the existing `models/staging/_models.yml` and creating a new `models/marts/_models.yml`.

## Steps

**1.** Open `dbt_project/models/staging/_models.yml`. Find the `status` column under `stg__orders` and replace it with this version:

```yaml
- name: status
  description: "Order lifecycle state."
  tests:
    - accepted_values:
        values: [placed, shipped, completed, return_pending, returned]
```

The rest of the file stays as-is. Only the `status` column gets the new test attached.

**2.** Create a new file at `dbt_project/models/marts/_models.yml` with this content:

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
```

Two things to notice:

- **`to: ref('dim_customers')`** — that's a Jinja expression evaluated by dbt at parse time, not a string literal `'dim_customers'`. Quotes go around the model name *inside* `ref()`.
- **The new file is a peer of `_sources.yml`, not nested under it.** The marts folder gets its own schema YAML.

**3.** From inside `dbt_project/`, run the tests scoped to the fact table:

```bash
cd dbt_project
dbt test --select fct_orders
```

You should see three tests run on `fct_orders` (its own `unique`, `not_null`, and `relationships`) plus the upstream `stg__orders.status` `accepted_values` test if you used `+fct_orders` instead. With just `--select fct_orders`, expect 3 tests.

**4.** Then test everything end-to-end:

```bash
dbt test
```

That runs all tests across the project — Stage 2's data plus the seven from `generic_tests` plus your two new ones. All pass.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt test --select fct_orders` exits 0 and every selected test passes.
- `target/manifest.json` shows at least 3 tests on `stg__orders` (the existing `unique`/`not_null` plus the new `accepted_values`).
- At least 3 tests on `fct_orders` (`unique`, `not_null`, `relationships`).

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: 'dim_customers' is undefined` | You wrote `to: 'dim_customers'` (string) instead of `to: ref('dim_customers')` (Jinja). Add the `ref()` wrapper. |
| `accepted_values` test fails with `FAIL N` | An order has a status outside the five values. Run `select distinct status from stg__orders` to see what's actually there — the seed data in this project should produce exactly the five listed values, so a failure usually means a typo in the YAML list. |
| `Model `fct_orders` has 2 test(s) — expected at least 3` | The `relationships` test didn't attach. Double-check the YAML indentation — `relationships:` is one of the children of `tests: -`, at the same indent as `not_null`. |
| `Compilation Error: Could not find a model named 'dim_customers'` | The `ref()` argument doesn't match a model name. Run `dbt ls --resource-type model` to see the valid names — should be `dim_customers` (single underscore). |

## After you pass

Press `n`. The next exercise covers **singular tests** — the kind you write by hand when no built-in fits.
