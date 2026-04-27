# Exercise 12 — `profiles.yml` and `dbt debug`

## Goal

Tell dbt how to connect to your local DuckDB warehouse, then prove it works with `dbt debug`.

## Background

dbt separates the **project** (what to build) from the **connection** (where to build it). Connection lives in `profiles.yml`. By default dbt looks for it in `~/.dbt/profiles.yml`, but for this course we keep it inside `dbt_project/` so the whole project is self-contained.

The verifier sets `DBT_PROFILES_DIR=dbt_project/` when it runs dbt, so dbt will look there.

## Steps

**1.** Open (or create) the file `dbt_project/profiles.yml` and paste exactly this:

```yaml
dbt_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 4
```

A few things to notice:

- The top-level key `dbt_project` matches the `profile:` field in `dbt_project.yml` that `dbt init` generated. They have to match — that's how dbt links the project to a profile.
- `target: dev` picks which output below to use. Real teams often have `dev`, `ci`, `prod` outputs side by side; we only need one.
- `path: dev.duckdb` is **relative to the project dir**, so the file lives at `dbt_project/dev.duckdb`. dbt will create it on the first run.
- `threads: 4` is how many models dbt runs in parallel. 4 is fine for a laptop.

**2.** From the repo root, run:

```bash
dbt-learn  # if not already running
```

then press `v` on this exercise. The verifier runs `dbt debug` inside `dbt_project/`. You should see **all checks pass** (Connection test: OK).

If it fails, read the error — the most common cause is YAML indentation (use spaces, not tabs) or a typo in `path:` / `type:`.

## What success looks like

`dbt debug` prints something like:

```
All checks passed!
```

That means dbt found your project, parsed `profiles.yml`, opened a connection to DuckDB, and ran a smoke query.

## After you pass

Press `n` to advance — next exercise loads the raw CSVs into DuckDB.
