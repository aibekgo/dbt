# Exercise — Add an analysis

## Goal

Write `dbt_project/analyses/top_customers_by_revenue.sql` — a top-10 customers query joining `fct_orders` and `dim_customers`. Run `dbt compile` and confirm the rendered SQL lands in `target/compiled/`.

## Steps

**1.** From the repo root, create the analysis file:

```bash
mkdir -p dbt_project/analyses
touch dbt_project/analyses/top_customers_by_revenue.sql
```

The `analyses/` folder ships with the default `dbt init` scaffold but is empty by default — `mkdir -p` is harmless if it already exists.

**2.** Paste this into `top_customers_by_revenue.sql`:

```sql
-- Top 10 customers by lifetime order revenue.
-- Compiled-only — not materialized, but lives in target/compiled/ and is
-- versioned alongside the rest of the project.
select
    c.customer_id,
    c.first_name,
    c.last_name,
    count(o.order_id) as order_count,
    sum(o.amount)     as lifetime_revenue
from {{ ref('fct_orders') }} o
join {{ ref('dim_customers') }} c using (customer_id)
group by 1, 2, 3
order by lifetime_revenue desc
limit 10
```

Key things:

- **No `{{ config(...) }}`.** Analyses don't materialize; a config block here is a smell.
- **Two `ref()` calls.** Both `fct_orders` and `dim_customers` are existing models. The analysis depends on them at compile time — dbt knows it can only render after parsing those models.
- **`group by 1, 2, 3`** — positional grouping. Equivalent to `group by c.customer_id, c.first_name, c.last_name`. Either form works.

**3.** Compile the analysis:

```bash
cd dbt_project
dbt compile --select top_customers_by_revenue
```

You should see one log line confirming it compiled. Unlike `dbt run`, nothing changes in DuckDB — analyses are compile-only.

**4.** Inspect the rendered output:

```bash
cat target/compiled/dbt_project/analyses/top_customers_by_revenue.sql
```

The `{{ ref(...) }}` calls have been replaced with `"main"."fct_orders"` and `"main"."dim_customers"`. That's the file you'd paste into a BI tool or DuckDB shell.

**5.** (Optional, just to see it work end-to-end.) Pipe the rendered SQL into DuckDB:

```bash
duckdb ../database/dev.duckdb < target/compiled/dbt_project/analyses/top_customers_by_revenue.sql
```

Ten rows, sorted by `lifetime_revenue` descending.

**6.** Press `v` to verify.

## What the verifier checks

- `dbt compile --select top_customers_by_revenue` exits 0.
- The compiled artifact exists at `target/compiled/<project>/analyses/top_customers_by_revenue.sql`.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: 'fct_orders' is undefined` | The `ref()` argument doesn't match a model name. Run `dbt ls --resource-type model` to see valid names — should be `fct_orders` (single underscore). |
| `dbt compile --select top_customers_by_revenue` reports `Found 0 nodes` | The file is in the wrong folder. Confirm path is exactly `dbt_project/analyses/top_customers_by_revenue.sql` (plural `analyses`, not `analysis`). |
| `Compiled artifact 'analyses/top_customers_by_revenue.sql' not found under target/compiled/` | The compile may have errored silently. Re-run `dbt compile --select top_customers_by_revenue` and read the full log; or just `dbt compile` (no select) and grep the output. |
| `Catalog Error: Table with name fct_orders does not exist!` | Only happens if you try to *run* the compiled SQL against DuckDB before the upstream models exist. `dbt compile` itself just renders Jinja — it doesn't execute anything against the database. Run `dbt build` first if you want to actually query the result. |

## After you pass

That's the last exercise of Stage 3. Press `n` to take the stage quiz, then on to Stage 4 — materializations, incremental models, and snapshots.
