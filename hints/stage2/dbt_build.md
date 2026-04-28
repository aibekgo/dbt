## Hint 1

Two commands, in this order:

```bash
cd dbt_project
dbt build
```

The verifier re-runs `dbt build` itself and checks `target/run_results.json` — you don't have to leave a side effect on disk. Just confirm the command succeeds end-to-end before pressing `v`.

## Hint 2

If `dbt build` fails with an error in one of your Stage 2 models, fix that file first — you can't move past `dbt_build` until every node is green. The error message names which model errored and on which line.

A quick way to scope the build while you debug:

```bash
dbt build --select +fct_orders
```

That rebuilds the fact and everything upstream, ignoring `dim_customers` from Stage 1. Once that subset is green, the unscoped `dbt build` should also pass.

## Hint 3

If the verifier is failing but `dbt build` succeeds when you run it manually:

1. The verifier runs the build itself — it doesn't read whatever you ran. So a stale success in your terminal doesn't matter; what matters is what happens when the verifier reaches in.
2. Make sure no exercise file has a typo / unsaved change. The verifier sees the latest disk state.
3. Look at the error message under each failed test. The verifier surfaces the relevant lines from `dbt build`'s stdout/stderr; the actual cause is usually in there.
