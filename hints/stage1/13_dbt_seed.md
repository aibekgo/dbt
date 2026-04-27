## Hint 1

dbt only loads CSVs that live inside the project's `seeds/` directory. From the repo root, run `cp data/raw_*.csv dbt_project/seeds/` first, then `dbt seed`.

## Hint 2

`dbt seed` must be run from inside `dbt_project/` (or with `--project-dir dbt_project`), not from the repo root. The simplest way:

```bash
cd dbt_project
dbt seed
cd ..
```

## Hint 3

If `dbt seed` fails with a "profile not found" error, you skipped exercise 12 — go back and create `dbt_project/profiles.yml`. If it fails with "no seeds were selected", check that the CSVs really are in `dbt_project/seeds/` (run `ls dbt_project/seeds/`).
