# Exercise — Add a `prod` target to `profiles.yml`

## Goal

Extend `dbt_project/profiles.yml` to declare a second target — `prod` — alongside the existing `dev` target. Re-run ingestion against the prod warehouse, then run `dbt build --target prod` to materialize the whole DAG into a separate `prod.duckdb` file. The point: see the multi-target mechanic concretely. Same SQL, different destination, separate ingestion.

## Steps

**1.** Open `dbt_project/profiles.yml`. It currently looks like this:

```yaml
dbt_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../database/dev.duckdb
      threads: 4
```

**2.** Add a `prod:` block as a sibling of `dev:`. Both targets are DuckDB; they differ only in the `path:`. The final shape:

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

Things to watch:

- `prod:` is at the same indent level as `dev:` (both are children of `outputs:`).
- The `target: dev` line at the top doesn't change. It's the *default* target; `--target prod` overrides it.

**3.** Re-run ingestion against the prod warehouse. The `scripts/ingest_raw.py` script accepts a target name and routes the raw CSVs to `database/<target>.duckdb`:

```bash
python scripts/ingest_raw.py prod
```

This is the production reality you'd never bypass: dbt only sees data the ingestion layer landed in the warehouse. For the prod warehouse to have raw tables, ingestion has to run *against prod*. Same script you ran in Stage 1, different destination.

**4.** From inside `dbt_project/`, build the project against the prod target:

```bash
cd dbt_project
dbt build --target prod
```

This re-runs every seed, model, test, and snapshot in the project, but the output lands at `database/prod.duckdb` instead of `database/dev.duckdb`. Expect the build to take ~30s (the same as a normal `dbt build`).

**5.** Confirm the file landed:

```bash
ls ../database/
# should show: dev.duckdb  prod.duckdb  README.md
```

**6.** Press `v` to verify.

## What the verifier checks

- `dbt_project/profiles.yml` contains the literal string `prod:` (proves you added the target).
- `database/prod.duckdb` exists (proves you ran `dbt build --target prod` to populate it).

## Common failure modes

| Symptom | Fix |
|---|---|
| `Credentials in profile "dbt_project", target "prod" invalid: ...` | The `prod:` block is malformed. Check indentation — it must be a child of `outputs:`, not `dbt_project:`. |
| `dbt build --target prod` errors with "target not found" | The target name is misspelled or the indent is wrong. The block name `prod:` should appear directly under `outputs:`. |
| `dbt build --target prod` errors with `Catalog Error: Table "raw_customers" does not exist` | You skipped step 3. The prod warehouse needs raw tables before dbt can build models. Run `python scripts/ingest_raw.py prod` first. |
| `path 'database/prod.duckdb' does not exist` | You added `prod:` to profiles.yml but didn't run `dbt build --target prod`. Run it from inside `dbt_project/`. |
| `dbt build` (without `--target`) is using prod | You changed the top-level `target:` line. Leave it as `target: dev` so the default stays unchanged. |

## After you pass

Press `n`. The next exercise is `analysis_to_model` — promoting your Stage 3 analysis (`top_customers_by_revenue.sql`) to a real, tested mart with description, meta, and tags.
