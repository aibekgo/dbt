## Hint 1

Two file changes:

1. Extend `dbt_project/packages.yml` (already exists from Stage 5) to add `calogica/dbt_expectations`. Then run `dbt deps` from inside `dbt_project/`.
2. Edit `dbt_project/models/marts/_models.yml`. Add a new `amount` column entry under `fct_orders` with a `dbt_expectations.expect_column_values_to_be_between` test (`min_value: 0`, `max_value: 100`).

Then `dbt test --select fct_orders` to confirm the new test runs.

## Hint 2

Final shapes:

```yaml
# packages.yml — both packages
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
```

```yaml
# fct_orders columns block in models/marts/_models.yml
- name: amount
  description: "Total dollar amount paid across all payments for this order."
  tests:
    - dbt_expectations.expect_column_values_to_be_between:
        min_value: 0
        max_value: 100
```

The org for `dbt_expectations` is `calogica`, not `dbt-labs`. Easy mistake.

## Hint 3

If verification still fails:

1. `ls dbt_project/dbt_packages/` — should list both `dbt_utils` and `dbt_expectations`. If only `dbt_utils` is there, run `dbt deps` again.
2. `dbt parse` from inside `dbt_project/` — exits 0? If it errors with "macro not found," the test name has a typo or the prefix is missing. Use `dbt_expectations.expect_column_values_to_be_between` exactly.
3. `dbt ls --resource-type test --select fct_orders` should print 4 lines. If you see 3, the new test didn't attach — check the YAML indentation. `min_value:` and `max_value:` are nested *under* the test name.
4. `dbt test --select fct_orders` exits 0? If `FAIL`, the data is outside the bounds you set. The seed has amounts in `[0, ~50]` so `[0, 100]` should comfortably pass.
