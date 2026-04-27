# Exercise — Confirm dbt is installed

## Goal

Make sure `dbt` is on your `PATH` and the DuckDB adapter is loaded, before you start building anything.

## Steps

**1.** Make sure your virtualenv is active. From the repo root:

```bash
source .venv/bin/activate
```

If you skipped the venv during setup, run `uv venv && source .venv/bin/activate && uv pip install -e .` first.

**2.** Run:

```bash
dbt --version
```

You should see something like:

```
Core:
  - installed: 1.8.x
  - latest:    1.8.x

Plugins:
  - duckdb: 1.8.x
```

The two things to look for:

- A `Core` section — proves `dbt-core` (the CLI) is installed.
- A `duckdb` line under `Plugins` — proves the `dbt-duckdb` adapter is installed and dbt knows how to talk to DuckDB.

**3.** Press `v` to verify.

## What the verifier checks

- `dbt --version` exits 0
- The output mentions `duckdb` (i.e., the adapter is loaded)

## If it fails

| Error | Fix |
|---|---|
| `dbt: command not found` | Your venv isn't active. Run `source .venv/bin/activate` from the repo root. |
| `Core` shows but `duckdb` is missing under `Plugins` | Run `uv pip install -e .` from the repo root to install all course dependencies. |
| `dbt-fusion` shows instead of `dbt-core` | You're hitting a system-installed `dbt-fusion` from your `PATH` instead of the venv binary. Activate the venv. |

## After you pass

Press `n` — next you'll actually scaffold the project with `dbt init`.
