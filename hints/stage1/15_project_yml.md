## Hint 1

The change goes inside `dbt_project/dbt_project.yml` (the file `dbt init` generated). Look near the bottom for the existing `models:` block.

## Hint 2

The config has to be nested under `models:` → your project name → folder name. The project name must match the `name:` field at the top of the same file (for a fresh `dbt init dbt_project`, both are `dbt_project`).

## Hint 3

Full block to add:

```yaml
models:
  dbt_project:
    staging:
      +materialized: view
```

The leading `+` on `+materialized` is required — it tells dbt this is a config key, not a folder name. Without it, dbt looks for a subdirectory called `materialized/` containing a model named `view.sql` and quietly does nothing.
