## Hint 1

You don't need to write any code for this exercise. It's a single command from the repo root.

## Hint 2

The command is `dbt init dbt_project`. The argument after `init` becomes the directory name and the project name inside `dbt_project.yml` — keep it as `dbt_project` so the verifier can find it.

## Hint 3

Make sure your virtualenv is active before running `dbt init`. From the repo root:

```bash
source .venv/bin/activate
dbt init dbt_project
```

When prompted, pick `duckdb` as the database (or just press Enter for defaults). After it finishes, run `ls dbt_project/` to confirm `dbt_project.yml` is there, then press `v`.
