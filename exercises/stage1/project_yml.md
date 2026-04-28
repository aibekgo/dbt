# Exercise — Configure `dbt_project.yml`

## Goal

Use folder-level config in `dbt_project.yml` to materialize **staging models as views** (cheap, recompute-on-read) and **marts as tables** (paid once, fast forever) — without touching any SQL file.

To prove it works you'll add a second model — `dim_customers` under `models/marts/` — and watch dbt build it as a *table* even though the SQL has no `{{ config() }}` block.

## Steps

**1.** Make sure you're inside `dbt_project/`:

```bash
cd dbt_project   # if you're not already here
```

**2.** Create the marts folder and a new model called `dim_customers`:

```bash
mkdir -p models/marts
touch models/marts/dim_customers.sql
```

**3.** Paste this into `models/marts/dim_customers.sql`:

```sql
select
    customer_id,
    first_name,
    last_name
from {{ ref('stg__customers') }}
```

Two things to notice:
- **No `{{ config(materialized='table') }}` at the top.** The materialization will come entirely from `dbt_project.yml` in the next step.
- `{{ ref('stg__customers') }}` — marts depend on staging models via `ref()`, the same way staging depends on raw via `source()`. dbt will build `stg__customers` first, then `dim_customers`.

**4.** Open `dbt_project/dbt_project.yml`. Scroll to the bottom — `dbt init` left you a `models:` block that points at the demo `example/` folder:

```yaml
models:
  dbt_project:
    example:
      +materialized: view
```

Replace it with two folder configs — one for the `staging/` folder, one for the new `marts/` folder. **The key change is `+materialized: table` on the marts block — that's what flips `dim_customers` from a view (the default) to a table.**

```yaml
models:
  dbt_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

What this YAML says:
- `models:` — top-level config block
- `dbt_project:` — your project name (must match the `name:` field at the top of the same file)
- `staging:` and `marts:` — folders under `models/` that the configs apply to
- `+materialized: <view|table>` — the leading `+` marks the line as a config, not a sub-folder. Without `+`, dbt looks for a folder called `materialized/` containing `view.sql` and silently no-ops.

**5.** Build everything:

```bash
dbt run
```

You should see two green nodes — `stg__customers` (view) and `dim_customers` (table). Look closely at the log:

```
1 of 2 OK created sql view  model main.stg__customers ...
2 of 2 OK created sql table model main.dim_customers ...
```

The words `view` and `table` come from the folder-level config you just set.

**6.** Sanity check the materializations actually differ in the warehouse:

```bash
duckdb ../database/dev.duckdb -c "
  select table_name, table_type
  from information_schema.tables
  where table_schema = 'main_main'
  order by table_name;
"
```

Expected:

```
┌────────────────┬────────────┐
│   table_name   │ table_type │
├────────────────┼────────────┤
│ dim_customers  │ BASE TABLE │
│ stg__customers │ VIEW       │
└────────────────┴────────────┘
```

**7.** Press `v`.

## What the verifier checks

- `dbt run --select +dim_customers` exits 0 (the `+` prefix means "this and all upstream").
- `target/manifest.json` reports `dim_customers` resolved to `materialized: table`.
- `target/manifest.json` reports `stg__customers` is still `materialized: view`.

If both materializations come out right, your folder-level config is wired correctly.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: Model 'dim_customers' depends on a node named 'stg__customers' which was not found` | The staging model wasn't built yet. Run `dbt run` (no select) — `+dim_customers` covers it but full `dbt run` is foolproof. |
| `dim_customers` shows up as `VIEW` in DuckDB | Either your `marts:` block is missing the `+` on `materialized`, or it's nested under the wrong project name. Re-check the YAML against step 4. |
| YAML parse error / `Could not run dbt` | Indentation. Two spaces per level, no tabs. |

## After you pass

Press `n` for the Stage 1 quiz. After that — Stage 2.
