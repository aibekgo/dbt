# Exercise — Add `unique_key` and `merge` strategy

## Goal

Extend the `fct_order_events` model with two new config keys: `unique_key='order_id'` and `incremental_strategy='merge'`. After this change, dbt knows how to *update* an existing order's row when an updated version arrives — instead of blindly inserting a duplicate.

## Steps

**1.** Open `dbt_project/models/marts/fct_order_events.sql`. Replace the single-arg config block with the multi-arg version:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

select
    order_id,
    customer_id,
    order_date,
    status
from {{ ref('stg__orders') }}

{% if is_incremental() %}
where order_date > (select max(order_date) from {{ this }})
{% endif %}
```

The `select` and `is_incremental()` block stay identical. Only the config grows.

Note the syntax: `config(...)` takes keyword arguments separated by commas. Multi-line is idiomatic for readability but functionally equivalent to a single line.

**2.** Rebuild:

```bash
cd dbt_project
dbt build --select fct_order_events
```

Behind the scenes dbt is now issuing `MERGE INTO ... USING ... WHEN MATCHED THEN UPDATE ...` instead of plain `INSERT INTO`. The seed didn't change, so no rows match the watermark filter — but the SQL pattern dbt emits is now upsert-shaped.

**3.** Confirm the row count is unchanged at 99 and `order_id` is still unique:

```bash
duckdb ../database/dev.duckdb -c "select count(*) from fct_order_events"
duckdb ../database/dev.duckdb -c "select count(distinct order_id) from fct_order_events"
```

Both should return `99`.

**4.** (Optional, to see the merge SQL.) Look at `target/run/dbt_project/models/marts/fct_order_events.sql` after the build:

```bash
cat target/run/dbt_project/models/marts/fct_order_events.sql | head -30
```

You'll see the rendered `merge into ...` statement that dbt generated. The `WHEN MATCHED THEN UPDATE` and `WHEN NOT MATCHED THEN INSERT` clauses make the upsert behavior explicit.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt build --select fct_order_events` exits 0 with all nodes succeeding.
- Row count is 99.
- Distinct `order_id` count is 99 — i.e., no duplicates.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: ... unexpected ','` inside the config block | The multi-arg syntax has bad commas — usually trailing or missing. Each kwarg is `key=value`, separated by `,`, no trailing comma needed. |
| `Catalog Error: MERGE statement not supported by this database` | Some dbt-adapter+warehouse combos don't support `merge`. dbt-duckdb 1.10.x does — if you see this, check `dbt --version` to confirm you're on the project's pinned versions. |
| Duplicates appear (`count != count(distinct)`) | Either the model was rebuilt with `append` (forgot the `incremental_strategy='merge'` line) or `unique_key` is wrong. Confirm the config block is the multi-arg form. |
| Row count is `0` after the rebuild | The merge probably matched-and-updated existing rows but dbt dropped the table first by accident. Try `dbt build --select fct_order_events --full-refresh` to force a clean rebuild from scratch. |

## After you pass

Press `n`. The final Stage 4 exercise covers **snapshots** — the SCD Type 2 mechanism for tracking how a column's value changes over time. It's a different beast than incremental: snapshots *preserve* history rather than overwriting it.
