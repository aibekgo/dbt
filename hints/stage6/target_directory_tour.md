## Hint 1

No file edits. From inside `dbt_project/`, run:

```bash
dbt build
```

Then verify with `ls target/` that the four critical artifacts (`manifest.json`, `run_results.json`, `compiled/`, `run/`) all exist.

## Hint 2

The verifier just checks four path-exists conditions. To populate them all, you need a full `dbt build` (or at least `dbt run` + `dbt test`). `dbt parse` alone doesn't create `compiled/` or `run/`.

If a previous Stage 6 exercise left state where one of the build steps fails, fix that first — the verifier needs `dbt build` to actually succeed.

## Hint 3

If verification still fails:

1. `ls dbt_project/target/manifest.json dbt_project/target/run_results.json dbt_project/target/compiled dbt_project/target/run` — all four should exist.
2. If `target/` itself is missing, you ran `dbt clean` or never ran a dbt command. Run `dbt build` from inside `dbt_project/`.
3. If `dbt build` errors out, an earlier exercise's state is broken. Read the error message — usually a YAML problem in `_models.yml` or a missing column reference in a SQL file.
4. If only `compiled/` or `run/` is missing, the build only got partway. Check the dbt log output — first failed node is usually the cause.
