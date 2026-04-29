## Hint 1

No file edits. Just run from inside `dbt_project/`:

```bash
dbt show --select fct_orders --limit 5
```

The verifier runs the same command. As long as it exits 0, you pass.

## Hint 2

If the command errors with `Catalog Error: Table with name fct_orders does not exist!`, the model isn't materialized yet. Run:

```bash
dbt run --select fct_orders
```

Then retry `dbt show`. (`dbt show` reads from the warehouse, so the table needs to exist.)

## Hint 3

If verification still fails:

1. `dbt show --select fct_orders --limit 5` (from inside `dbt_project/`) should print a 5-row table with no errors. If it errors, scroll up the output for the cause.
2. `dbt ls --resource-type model --select fct_orders` should print one line. If it prints zero, the model name is wrong (it's `fct_orders` with a single underscore).
3. If you see the table render fine but the verifier still complains, check that you're running the verifier from the repo root (not from inside `dbt_project/`).
