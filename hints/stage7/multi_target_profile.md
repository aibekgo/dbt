## Hint 1

Three changes:

1. Edit `dbt_project/profiles.yml`. Add a `prod:` block under `outputs:`, at the same indent as the existing `dev:` block. Inside it: `type: duckdb`, `path: ../database/prod.duckdb`, `threads: 4`.
2. From the repo root, run `python scripts/ingest_raw.py prod` to populate `database/prod.duckdb` with the raw_* tables. (Ingestion has to run against prod separately; dbt won't do it for you.)
3. From inside `dbt_project/`, run `dbt build --target prod`.

## Hint 2

Final shape of `profiles.yml`:

```yaml
dbt_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../database/dev.duckdb
      threads: 4
    prod:
      type: duckdb
      path: ../database/prod.duckdb
      threads: 4
```

Don't change the `target: dev` line — that just sets the default. The `--target prod` flag overrides it for one command.

The two-step nature of step 2 (ingest) and step 3 (build) is real — in production, your data engineering team runs ingestion (Fivetran, Airbyte, custom jobs) against the prod warehouse, and then dbt runs against whatever ingestion landed.

## Hint 3

If verification still fails:

1. `cat dbt_project/profiles.yml | grep -E 'dev:|prod:'` — should print both target names. If only `dev:` shows, the file wasn't saved.
2. `cd dbt_project && dbt debug --target prod` — should print `All checks passed`. If it errors, the `prod:` block is malformed (usually wrong indent).
3. If `dbt build --target prod` errors with `Catalog Error: Table "raw_customers" does not exist`, you skipped the ingestion step. Run `python scripts/ingest_raw.py prod` from the repo root.
4. `ls database/prod.duckdb` — should print the file. If "no such file," step 3 didn't complete: run `dbt build --target prod` from inside `dbt_project/`.
