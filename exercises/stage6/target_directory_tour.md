# Exercise — Inspect `target/` after a fresh build

## Goal

Run `dbt build` to populate `target/`, then verify the four critical artifacts are present: `manifest.json`, `run_results.json`, `compiled/`, `run/`. No file edits — this is a tour of what dbt produces.

## Steps

**1.** From inside `dbt_project/`, run a fresh build:

```bash
cd dbt_project
dbt build
```

This refreshes everything: seeds, models, snapshots, tests. After it completes, `target/` is fully populated.

**2.** List the top-level contents of `target/`:

```bash
ls target/
```

You should see entries like:

```
catalog.json
compiled
graph.gpickle
graph_summary.json
manifest.json
partial_parse.msgpack
perf_info.json
run
run_results.json
semantic_manifest.json
```

(Exact list varies by dbt version. The four highlighted in the lesson are the important ones.)

**3.** Peek at `manifest.json` to find one of your models. It's a big JSON blob, so use `jq` (or `python -m json.tool | grep`) to scope:

```bash
duckdb -c "select unique_id, resource_type, depends_on::varchar from read_json('target/manifest.json', records=true)" 2>/dev/null | head -20
```

(Or simpler — open `target/manifest.json` in your editor and search for `fct_orders`.)

**4.** Inspect the compiled SQL for a model with `ref()` calls:

```bash
cat target/compiled/dbt_project/models/marts/fct_orders.sql
```

Notice how `{{ ref('stg__orders') }}` got replaced with `"main"."stg__orders"`. That's Jinja resolution.

**5.** Compare to the run-time SQL (with the `create or replace` wrapper):

```bash
cat target/run/dbt_project/models/marts/fct_orders.sql
```

This file has the full DDL dbt issued — `create or replace table ... as (select ...)`. The compiled version has only the inner select.

**6.** Check `run_results.json` for the latest build's results:

```bash
duckdb -c "select unique_id, status, execution_time from read_json('target/run_results.json', records=true).results" 2>/dev/null | head -10
```

(Or just open the file.) You'll see one entry per node, with status `success` or `pass`.

**7.** Press `v` to verify.

## What the verifier checks

Four `path_exists` checks:
- `dbt_project/target/manifest.json` (the parsed project metadata)
- `dbt_project/target/run_results.json` (latest command's results)
- `dbt_project/target/compiled` (compiled SQL directory)
- `dbt_project/target/run` (run-time SQL directory)

If `dbt build` completed successfully, all four exist.

## Common failure modes

| Symptom | Fix |
|---|---|
| `path 'dbt_project/target/manifest.json' does not exist` | dbt hasn't been run since the last `dbt clean`. Run `dbt build` (or just `dbt parse`, which produces `manifest.json` without running models). |
| `path 'dbt_project/target/run' does not exist` | The `run/` directory only appears after at least one model has been *run* (not just parsed). `dbt parse` alone doesn't create it; `dbt run` or `dbt build` does. |
| `path 'dbt_project/target/compiled' does not exist` | Same as above — needs at least one compile step. `dbt compile` alone is enough; so is `dbt run` / `dbt build`. |
| Files exist but `dbt build` errored on a model | One of the Stage 4 / Stage 5 / Stage 6 changes broke a downstream. Run `dbt build` and read the errors carefully — the verifier won't pass until the build is green. |

## After you pass

That's the last exercise of Stage 6. Press `n` to take the stage quiz. The final `progress.txt` line covers Stage 6's quiz, and you've completed all six stages of the course.
