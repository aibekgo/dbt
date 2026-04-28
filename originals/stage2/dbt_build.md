# Exercise — Run `dbt build`

## Goal

Use `dbt build` to refresh the entire project in one command. Confirm every node succeeds and `target/run_results.json` reports `PASS` for each one. No new files — this is muscle memory for a command you'll use thousands of times.

## Steps

**1.** From the repo root, change into the project:

```bash
cd dbt_project
```

**2.** Run the build:

```bash
dbt build
```

You should see six green lines — three staging views, two intermediate / mart tables, plus `dim_customers` from Stage 1. Final summary:

```
Done. PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6
```

**3.** Inspect what dbt just recorded:

```bash
cat target/run_results.json | python3 -m json.tool | head -30
```

Look for the top-level `"results"` array — one entry per node, each with a `"status"` field. They should all read `"success"`.

```bash
ls -la target/manifest.json target/run_results.json
```

Both files should have an `mtime` of the last few seconds — proof that this build refreshed them.

**4.** (Optional sanity check) Try a scoped build, just the path to the fact:

```bash
dbt build --select +fct_orders
```

Same green output, different selector. The `+` prefix means "this and everything upstream"; `dbt build --select fct_orders` (no plus) would only rebuild the fact and leave staging alone. Useful when you're iterating on one part of the DAG.

**5.** Press `v`.

## What the verifier checks

- `dbt build` (run by the verifier itself) exits 0.
- Every entry in `target/run_results.json` shows `status=success`. Any single failed node fails the exercise — and the failure message names which one.

## Common failure modes

| Symptom | Fix |
|---|---|
| `dbt: command not found` | Activate the venv: `source .venv/bin/activate`. Then `dbt --version` should show the duckdb plugin. |
| `Could not find profile named 'dbt_project'` | You're not running from inside `dbt_project/`. dbt looks for `profiles.yml` in the current directory by default. |
| One model errored — `Compilation Error` somewhere | A previous Stage 2 exercise's file isn't in place. The error message names the missing dependency; go back and finish that exercise. |
| `PASS=0 WARN=0 ERROR=0 SKIP=0 TOTAL=0` | dbt didn't find anything to build. Check that `models/` has files in it and `dbt_project.yml` lists `model-paths: ["models"]`. |

## After you pass

Press `n`. Last exercise of Stage 2 — generate the `dbt docs` site and skim the lineage view of everything you've built.
