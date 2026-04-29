## Hint 1

One file change: `dbt_project/models/staging/_models.yml`. Find the `status` column under `stg__orders` (you added it in Stage 3's `accepted_values_relationships` exercise). Add a `config:` block under the `accepted_values:` test with `severity: warn` and a `where:` clause.

Then `dbt test --select stg__orders` from inside `dbt_project/`.

## Hint 2

The relevant block in its final form:

```yaml
- name: status
  description: "Order lifecycle state."
  tests:
    - accepted_values:
        values: [placed, shipped, completed, return_pending, returned]
        config:
          severity: warn
          where: "order_date >= '2018-01-01'"
```

The `config:` key is at the same indent level as `values:` — both are children of `accepted_values:`. Inside `config:`, `severity:` and `where:` are at the next indent level.

## Hint 3

If verification still fails:

1. `dbt parse` from inside `dbt_project/` should exit 0. If it errors with a YAML structure issue, indentation is wrong — `config:` aligned with `values:`, both under `accepted_values:`.
2. `dbt test --select stg__orders` should print `Done. PASS=N WARN=0 ERROR=0 SKIP=0` (the seed data triggers no warnings). If it errors with `'severity' is not a valid config key`, the key is misspelled or at the wrong level.
3. `grep "severity: warn" dbt_project/models/staging/_models.yml` should print one line. If it prints nothing, the string isn't in the file — re-check your edit.
4. The `where:` expression must be a string. Quote it: `where: "order_date >= '2018-01-01'"`. Without the outer double quotes, YAML mis-parses the inner single-quoted date.
