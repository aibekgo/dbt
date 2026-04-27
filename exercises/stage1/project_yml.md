# Exercise 15 — Configuring `dbt_project.yml`

## Goal

Tell dbt that everything under `models/staging/` should default to the `view` materialization (instead of dbt's built-in default of `view` — which sounds like a no-op, but you'll set it explicitly so future stages can switch staging to ephemeral or something else without touching every model file).

You'll also see how `dbt_project.yml` is the place to set defaults that apply to whole folders.

## Background

Every model in dbt has a **materialization** — what dbt does with the SQL:

| Materialization | What dbt does |
|---|---|
| `view` | `CREATE OR REPLACE VIEW` (default) — recomputes on every read |
| `table` | `CREATE OR REPLACE TABLE` — physically materializes once per run |
| `incremental` | inserts/upserts new rows on each run |
| `ephemeral` | inlines the SQL as a CTE in downstream models — never lands in the warehouse |

You can set the materialization three ways, in increasing specificity:

1. Project-wide default in `dbt_project.yml` (this exercise)
2. Folder-level default in `dbt_project.yml`
3. Per-model with `{{ config(materialized='table') }}` at the top of the file

The folder-level config is the workhorse — it lets a 200-model project say "everything in `staging/` is a view, everything in `marts/` is a table" in five lines of YAML.

## Steps

**1.** Open `dbt_project/dbt_project.yml`. `dbt init` left you a `models:` block at the bottom. Replace it (or its contents) with:

```yaml
models:
  dbt_project:
    staging:
      +materialized: view
```

Indentation matters. Two-space indent throughout. The structure reads as:
- `models:` — top-level config block
- `dbt_project:` — name of your project (matches `name:` at the top of the file)
- `staging:` — folder under `models/`
- `+materialized: view` — the leading `+` marks this as a config to apply to every model in the folder

**2.** Press `v`.

## What the verifier checks

The verifier runs `dbt parse` to refresh `target/manifest.json`, then inspects the manifest entry for `stg_customers` and confirms its `config.materialized` is `view`.

## Why the leading `+` on `+materialized`

Without the `+`, dbt treats `materialized: view` as the *name of a sub-folder* called `materialized` containing a model called `view`. The `+` is dbt's way of saying "this is a configuration, not a path." You'll see `+enabled`, `+tags`, `+schema` etc. in real projects.

## After you pass

Press `n` for the Stage 1 quiz. After that, Stage 2 — sources, refs, and the staging→marts pattern.
