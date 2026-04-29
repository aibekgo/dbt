# Exercise — Build an incremental model

## Goal

Create a new fact table, `fct_order_events`, that materializes incrementally. First run loads all 99 rows; subsequent runs load only rows with `order_date` newer than what's already in the table (zero rows on a static seed, but the structure is what matters).

## Steps

**1.** From the repo root, create the new model file:

```bash
touch dbt_project/models/marts/fct_order_events.sql
```

**2.** Paste this into `fct_order_events.sql`:

```sql
{{ config(materialized='incremental') }}

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

Key things:

- **`{{ config(materialized='incremental') }}`** at the top.
- **`{% if is_incremental() %}` ... `{% endif %}`** wraps the entire `where ...` clause. The `where` keyword stays *inside* the block — without that, the first-run compile would emit a dangling `where` and fail.
- **`{{ this }}`** is the model's own fully-qualified relation. Don't use `{{ ref('fct_order_events') }}` here — that creates a circular dependency.

**3.** First build — populates the table from scratch:

```bash
cd dbt_project
dbt build --select fct_order_events
```

The log says *"START sql incremental model"* and *"OK created incremental model"*. Behind the scenes dbt issued `create table ... as select ...` (the filter was skipped because `is_incremental()` returned `false`).

**4.** Confirm the table has 99 rows:

```bash
duckdb ../database/dev.duckdb -c "select count(*) from fct_order_events"
```

**5.** Second build — incremental insert path:

```bash
dbt build --select fct_order_events
```

The log still says *"OK created incremental model"* but this time dbt issued `insert into ... select ... where order_date > ...`. The filter eliminated everything (no new rows in the seed), so the table is unchanged — still 99 rows.

**6.** Sanity check it stayed at 99:

```bash
duckdb ../database/dev.duckdb -c "select count(*) from fct_order_events"
```

**7.** Press `v` to verify.

## What the verifier checks

- `dbt build --select fct_order_events` exits 0 and every node succeeds.
- `target/manifest.json` reports `fct_order_events` as `materialized: incremental`.
- `select count(*) from fct_order_events` returns `99`.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: ... near "where"` on the first run | The `where` keyword is outside the `{% if is_incremental() %}` block. Move it inside — the entire clause should be wrapped. |
| `Compilation Error: 'this' is undefined` | Typo on `{{ this }}` (extra space inside braces or capital `This`). Lowercase, exact name, double-curly braces. |
| `Catalog Error: Table with name fct_order_events does not exist!` on the second build | The first build didn't create the table. Re-run the first command and check the log for the `OK created` line. |
| Row count is 0 | The first run hit `is_incremental()` returning true somehow (rare — usually a stale state where the table existed before). Try `dbt build --select fct_order_events --full-refresh` to force a clean rebuild. |
| `Catalog Error: ... near "is_incremental"` | Spelling. The macro is `is_incremental()` exactly — including the parens. Without parens it's a reference, not a call. |

## After you pass

Press `n`. Next exercise extends this same model with a `unique_key` and the `merge` incremental strategy — the standard pattern for handling late-arriving updates.
