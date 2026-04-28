# Exercise — Declare sources, refactor the model

## Goal

The model you just built works, but dbt has no idea where its raw data came from. It treats `main.raw_customers` as a black box — not on the DAG, no lineage, no build-order safety. This exercise fixes that with a **source declaration** and the `{{ source(...) }}` macro.

You'll add one new file (`_sources.yml`), edit one existing file (`stg__customers.sql`), and run `dbt run` again.

## Steps

**1.** Make sure you're inside `dbt_project/`:

```bash
cd dbt_project   # if you're not already here
```

**2.** Create `dbt_project/models/staging/_sources.yml` and paste:

```yaml
version: 2

sources:
  - name: raw
    description: "Jaffle shop raw tables landed by scripts/ingest_raw.py"
    schema: main
    tables:
      - name: raw_customers
      - name: raw_orders
      - name: raw_payments
```

What this YAML does:

- Tells dbt: "there's a logical source called `raw` living in DuckDB schema `main`."
- Lists the three tables you ingested.
- Lets you reference them as `{{ source('raw', 'raw_customers') }}` from any model.

> The leading underscore in `_sources.yml` is convention — files starting with `_` sort to the top of the folder so configs are easy to find. dbt doesn't care about the name.

**3.** Open `dbt_project/models/staging/stg__customers.sql` and **replace** the hardcoded `from` line with a `source()` call:

```sql
select
    id          as customer_id,
    first_name,
    last_name
from {{ source('raw', 'raw_customers') }}
```

The rest of the file stays exactly the same.

**4.** Run it:

```bash
dbt run --select stg__customers
```

You'll see the same green success line as before — but the underlying compiled SQL has changed, and dbt now knows the dependency.

**5.** Confirm the source is on the DAG:

```bash
dbt ls --resource-type source
```

You should see three entries:

```
dbt_project.raw.raw_customers
dbt_project.raw.raw_orders
dbt_project.raw.raw_payments
```

These are first-class DAG nodes now. Lineage, selectors (`--select source:raw+`), and `dbt source freshness` all work against them.

**6.** Press `v` to verify.

## What the verifier checks

- `dbt_project/models/staging/_sources.yml` exists and is non-trivially populated.

The verifier doesn't re-run dbt — `first_model` already covered that. This exercise just confirms you've added the source declaration. (You should also still see green from `dbt run --select stg__customers`, which proves the model parses with the macro.)

## Common failure modes

| Symptom | Fix |
|---|---|
| `Found a source ... but no matching source declaration` | Either `_sources.yml` is missing, the `name:` doesn't match `source('raw', ...)`, or `raw_customers` isn't listed under `tables:`. |
| `Relation "dev"."raw"."raw_customers" does not exist` | Wrong `schema:` in `_sources.yml`. Should be `main` (DuckDB's default — that's where `ingest_raw.py` writes). |
| YAML parse error (`mapping values are not allowed in this context`) | YAML indentation. Use spaces, never tabs. Two-space indent per level. |

## After you pass

Press `n`. The last exercise of Stage 1 sets a default materialization for everything in `staging/`.
