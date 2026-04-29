# Exercise — Promote an analysis to a tested mart

## Goal

Take the existing `analyses/top_customers_by_revenue.sql` (one-off SQL that compiles but doesn't materialize) and promote it to a real mart at `models/marts/mart_customer_revenue.sql`. The new model uses the imports → logic → final CTE pattern, materializes as a table, and gets a `_models.yml` entry with `description`, `meta`, `tags`, and tests on the primary key.

The original analysis stays in place — it's the audit trail showing what the mart is meant to compute.

## Steps

**1.** Create `dbt_project/models/marts/mart_customer_revenue.sql` with the CTE-structured SQL:

```sql
{{ config(materialized='table') }}

with

customers as (
    select * from {{ ref('dim_customers') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
),

customer_revenue as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        sum(o.amount) as lifetime_revenue,
        count(o.order_id) as lifetime_orders
    from customers c
    left join orders o on c.customer_id = o.customer_id
    group by c.customer_id, c.first_name, c.last_name
),

final as (
    select * from customer_revenue
    order by lifetime_revenue desc
)

select * from final
```

Three things to flag:

- The `with` keyword starts the CTE block.
- `customers` and `orders` are pure import CTEs — they pass-through `dim_customers` and `fct_orders` unchanged.
- The `final` CTE wraps the result. The bottom is always `select * from final`, never the logic CTE directly. The verifier checks for `final as (` to confirm you used the imports → logic → final pattern.

**2.** Open `dbt_project/models/marts/_models.yml` and add a new entry under `models:` for `mart_customer_revenue`:

```yaml
- name: mart_customer_revenue
  description: "Customer-grain lifetime revenue and order count, derived from fct_orders + dim_customers."
  config:
    meta:
      owner: data_eng
      pii: false
    tags:
      - revenue
      - finance
  columns:
    - name: customer_id
      description: "Stable customer identifier."
      tests:
        - unique
        - not_null
    - name: lifetime_revenue
      description: "Sum of fct_orders.amount across all orders for this customer."
```

Things to watch:

- The new entry is a sibling of the existing `fct_orders` block (same indent under `models:`).
- `config:` is nested under the model name. Inside it: `meta:` (a dict of key/value pairs) and `tags:` (a list of strings).
- Two tests on `customer_id`: `unique` and `not_null`. These prove the model is correctly grain-keyed.

**3.** From inside `dbt_project/`, build and test the new model:

```bash
cd dbt_project
dbt run --select mart_customer_revenue
dbt test --select mart_customer_revenue
```

Both should exit cleanly. The model materializes as a table; the tests confirm `customer_id` is unique and not null.

**4.** (Optional, to *use* the new tags.) Try `dbt build --select tag:finance` from inside `dbt_project/`. It should rebuild your new mart (and any other models tagged `finance`) — your first taste of tag-based selection.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt_project/models/marts/mart_customer_revenue.sql` exists.
- That file contains `final as (` (proves you used the imports → logic → final CTE pattern, not a flat select).
- `dbt run --select mart_customer_revenue` exits 0.
- The manifest shows ≥2 tests on `mart_customer_revenue` (the `unique` + `not_null` on `customer_id`).
- `dbt_project/models/marts/_models.yml` contains both `meta:` and `tags:` markers.

## Common failure modes

| Symptom | Fix |
|---|---|
| `path 'dbt_project/models/marts/mart_customer_revenue.sql' does not exist` | The file isn't where the verifier expects. Path is `models/marts/`, not `models/`. |
| `file 'dbt_project/models/marts/mart_customer_revenue.sql' does not contain 'final as ('` | The model is a flat `select` without the imports→logic→final pattern. Wrap the result in a `final` CTE and end with `select * from final`. |
| `dbt run --select mart_customer_revenue` errors with `relation "dim_customers" does not exist` | A previous exercise's `--target prod` build doesn't matter — `dbt run` defaults to `--target dev`. If `dev.duckdb` is missing, run `dbt build` (no flags) first. |
| `manifest_test_count: model 'mart_customer_revenue' has 0 tests, expected ≥2` | The YAML entry didn't attach. Check that `name: mart_customer_revenue` matches the model file name exactly, and that `tests:` is nested under `customer_id`'s entry (not the model's). |
| `file ... does not contain 'meta:'` or `'tags:'` | Your `_models.yml` entry skipped the `config:` block. Both `meta:` and `tags:` must be under a `config:` key in the model entry. |

## After you pass

Press `n`. The next item is `tooling_landscape` — a concept tour of the dbt ecosystem (MCP, Fusion, MetricFlow, audit_helper, dbt Mesh) before you graduate.
