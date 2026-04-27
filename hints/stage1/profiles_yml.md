## Hint 1

The file goes at `dbt_project/profiles.yml` (inside the project dir, not in your home directory). The verifier sets `DBT_PROFILES_DIR=dbt_project/` so dbt looks there.

## Hint 2

Make sure the top-level key matches the `profile:` field inside `dbt_project/dbt_project.yml`. `dbt init dbt_project` defaults that field to `dbt_project`, so the top-level key in `profiles.yml` should also be `dbt_project`.

## Hint 3

If `dbt debug` fails with a connection error, double-check `type: duckdb` (not `duckdb_db` or `duck`) and that `path: ../database/dev.duckdb` has a colon and a single space after it. The path is relative to `dbt_project/`, which is why it walks up one directory. YAML is whitespace-sensitive — use **spaces**, never tabs, and indent each level by exactly 2 spaces.
