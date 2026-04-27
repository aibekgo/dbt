# Exercise — `profiles.yml` and `dbt debug`

## Goal

Tell dbt how to connect to your local DuckDB warehouse, then prove it works with `dbt debug`.

## Background

dbt separates the **project** (what to build) from the **connection** (where to build it). The connection lives in `profiles.yml`. By default dbt looks for it in `~/.dbt/profiles.yml`, but for this course we keep it inside `dbt_project/` so the whole project is self-contained.

The verifier sets `DBT_PROFILES_DIR=dbt_project/` when it runs dbt, so dbt will look there.

## Steps

**1.** Open a new terminal at the repo root (the directory that holds `dbt_project/`, `database/`, and `curriculum.yaml`).

**2.** Step into the project directory:

```bash
cd dbt_project
```

**3.** Create an empty `profiles.yml` file in the project directory:

```bash
touch profiles.yml
```

You should now have `dbt_project/profiles.yml` (empty). Confirm with `ls profiles.yml`.

**4.** Open `dbt_project/profiles.yml` in your editor and paste **exactly** this:

```yaml
dbt_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../database/dev.duckdb
      threads: 4
```

Save the file. A few things to notice:

- **Top-level key `dbt_project`** matches the `profile:` field in `dbt_project.yml` that `dbt init` generated. They have to match — that's how dbt links the project to a profile.
- **`target: dev`** picks which output below to use. Real teams often have `dev`, `ci`, `prod` outputs side by side; we only need one.
- **`type: duckdb`** tells dbt which adapter to load. It must match the package you have installed (`dbt-duckdb`).
- **`path: ../database/dev.duckdb`** is the location of the DuckDB file, relative to `dbt_project/`. The `..` walks up one level to the repo root, then into `database/`, where dbt creates `dev.duckdb` on its first run. Keeping the warehouse outside `dbt_project/` means `dbt-learn reset` can wipe the project without losing raw data.
- **`threads: 4`** is how many models dbt runs in parallel. 4 is fine for a laptop.

**5.** Confirm dbt can read the file by running `dbt debug` from inside `dbt_project/`:

```bash
dbt debug
```

You should see a series of OK lines ending with **`All checks passed!`**. If you see anything else, scroll up and read the first failing line — that's the one that matters.

**6.** Switch back to the dbt-learn CLI and press `v` to verify. The verifier runs the same `dbt debug` for you and reports the result.

## What the verifier checks

Just one rule: `dbt debug` exits 0. That single check covers parsing `dbt_project.yml`, parsing `profiles.yml`, matching the project to a profile, opening a connection to DuckDB, and running a `SELECT 1` smoke query.

## What success looks like

```
All checks passed!
```

## Common failure modes

| Symptom | What to check |
|---|---|
| `Could not find profile named 'dbt_project'` | The top-level key in `profiles.yml` must match the `profile:` field in `dbt_project.yml`. |
| `Credentials in profile 'dbt_project', target 'dev' invalid` | Probably a missing or misspelled field — `type:` and `path:` are required. |
| `mapping values are not allowed in this context` | YAML indentation. Use spaces, never tabs. Two-space indent per level. |
| `IO Error: Cannot open file ".../database/dev.duckdb"` | Make sure the `database/` directory exists at the repo root (`ls database/` from the root). |

## After you pass

Press `n` to advance — next exercise loads the raw CSVs into DuckDB.
