# Exercise — Use `state:modified+` to rebuild only what changed

## Goal

Simulate the production CI pattern: snapshot the current `target/` as a "previous state," modify a model, then run `dbt run --select state:modified+ --state ../state_initial` so dbt rebuilds *only* the changed model and its downstream.

## Steps

**1.** First, build the project so `target/` reflects the current state:

```bash
cd dbt_project
dbt build
```

You should see all models, the snapshot, the seed, and tests run cleanly.

**2.** Snapshot `target/` to `state_initial/` at the repo root (peer of `dbt_project/`, not inside it):

```bash
cp -R target ../state_initial
```

After this, `state_initial/manifest.json` exists at the repo root and captures the current state of every node.

**3.** Modify `dim_customers.sql` by adding a marker comment — this is the change dbt's state diff will detect:

```bash
echo "-- state-selection-marker" >> models/marts/dim_customers.sql
```

(Or open `dbt_project/models/marts/dim_customers.sql` in your editor and add a line containing the string `state-selection-marker` at the bottom. Either approach works.)

**4.** Run dbt's state-aware selector. dbt will detect that `dim_customers.sql` differs from the snapshot and rebuild only it:

```bash
dbt run --select state:modified+ --state ../state_initial
```

Expected output:

```
... 1 of 1 START sql table model main.dim_customers
... 1 of 1 OK created sql table model main.dim_customers
Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

One model. Not all 7. That's the whole point.

**5.** (Optional, to compare.) Try running with no state selector — `dbt run` from inside `dbt_project/` will rebuild every model (5 of them at least). This is the wasteful pattern state selection avoids.

**6.** Press `v` to verify.

## What the verifier checks

- `state_initial/manifest.json` exists (proves you took the snapshot).
- `models/marts/dim_customers.sql` contains the string `state-selection-marker` (proves you modified the file).
- `dbt run --select state:modified+ --state ../state_initial` runs cleanly — at minimum exits 0 (the verifier itself runs this command).

## Common failure modes

| Symptom | Fix |
|---|---|
| `path 'state_initial/manifest.json' does not exist` | You skipped step 2, or the snapshot landed in the wrong place. From inside `dbt_project/`, `cp -R target ../state_initial` puts it at the repo root, peer of dbt_project. |
| `file 'dbt_project/models/marts/dim_customers.sql' does not contain 'state-selection-marker'` | The marker comment didn't land in the file. Check the file content with `cat dbt_project/models/marts/dim_customers.sql` — last line should contain `state-selection-marker`. |
| `state:modified+` selects 0 models | dbt thinks nothing changed. Two common causes: (a) you snapshotted *after* modifying, so the snapshot already has the marker — re-snapshot before modifying, or (b) the marker line you added is identical to something already in the snapshot. |
| `Compilation Error: Could not find state path` | The `--state` value is wrong. From inside `dbt_project/`, the path to `state_initial/` is `../state_initial`. |
| `Encountered an error: state-related selector specified, but no `--state` flag was passed` | You ran `dbt run --select state:modified+` without `--state ../state_initial`. State selectors need both pieces. |

## After you pass

Press `n`. The next exercise covers **exposures** — the lineage extension that documents which BI dashboards or notebooks depend on your fct/dim models.
