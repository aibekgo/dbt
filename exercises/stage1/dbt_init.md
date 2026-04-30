# Exercise 11 — `dbt init`

## Goal

Scaffold a fresh dbt project at `<repo>/dbt_project/` using the dbt CLI's project generator.

## Steps

From the repo root (where this file lives), run:

```bash
dbt init dbt_project
```

dbt will prompt you with a couple of questions. Use these answers:

| Prompt | Answer |
|---|---|
| `Which database would you like to use?` | `1` (or whichever number is next to **duckdb**) |
| Profile-related prompts (path, threads, etc.) | press Enter to accept defaults — we'll overwrite `profiles.yml` properly in the next exercise anyway |

If `dbt init` doesn't prompt for a database (some versions skip it when only one adapter is installed), that's fine — it'll just scaffold the project.

If dbt asks whether to overwrite an existing `~/.dbt/profiles.yml`, answer `n` (we won't use that one — this course keeps `profiles.yml` inside the project).

## What success looks like

After it finishes you should have a new directory tree:

```
dbt_project/
├── dbt_project.yml
├── analyses/
├── macros/
├── models/
│   └── example/        ← sample models dbt drops in — delete in the next step
├── seeds/
├── snapshots/
└── tests/
```

The CLI may also create or update `~/.dbt/profiles.yml` in your home directory. Ignore it — we won't use that one. The next exercise has you write `dbt_project/profiles.yml` instead.

## Remove the example models

`dbt init` ships sample models at `dbt_project/models/example/` (`my_first_dbt_model.sql`, `my_second_dbt_model.sql`, plus `schema.yml`). One of them returns a NULL row that fails a `not_null` test, which will break the Stage 2 `dbt build` exercise. Delete the folder now:

```bash
rm -rf dbt_project/models/example
```

You'll write your own models under `models/staging/` (Stage 1) and `models/marts/` / `models/intermediate/` (Stage 2).

## How verification works

Press `v` and the verifier will check that `dbt_project/dbt_project.yml` exists and is non-empty. It does **not** care about the contents yet; it just confirms `dbt init` ran.

## If you mess up

Run `dbt-learn reset` to delete `dbt_project/` entirely and start over.

## After you pass

Press `n` to advance to the next exercise where you'll configure the DuckDB connection.
