## Hint 1

Three steps in order:

1. From `dbt_project/`, run `dbt build` to populate `target/` with the current state.
2. From `dbt_project/`, run `cp -R target ../state_initial` — this places `state_initial/` at the repo root, peer of `dbt_project/`.
3. Add a line containing the string `state-selection-marker` to `dbt_project/models/marts/dim_customers.sql` (a comment line works: `-- state-selection-marker`).

Then `dbt run --select state:modified+ --state ../state_initial` from inside `dbt_project/` — dbt detects only `dim_customers` changed and rebuilds just it.

## Hint 2

The exact commands, copy-pasteable from the repo root:

```bash
cd dbt_project
dbt build
cp -R target ../state_initial
echo "-- state-selection-marker" >> models/marts/dim_customers.sql
dbt run --select state:modified+ --state ../state_initial
```

After this, the verifier will:
- Find `state_initial/manifest.json` ✓
- See the marker in `dim_customers.sql` ✓
- Run the state-aware command itself and confirm it exits 0 ✓

## Hint 3

If verification still fails:

1. `ls -la state_initial/manifest.json` (from repo root) — must exist. If it's not there, the `cp -R target ../state_initial` step didn't run from inside `dbt_project/`, or the path resolved differently.
2. `grep state-selection-marker dbt_project/models/marts/dim_customers.sql` should print one line. If it prints nothing, the marker isn't in the file.
3. `dbt run --select state:modified+ --state ../state_initial` (from inside dbt_project) — should print `1 of 1 START sql table model main.dim_customers` and `Done. PASS=1`. If it prints `Found 0 models`, dbt's state diff thinks nothing changed — re-do the snapshot *before* modifying.
4. The order matters: build → copy target → modify file → run with state selector. Reversing any of those breaks the diff.
