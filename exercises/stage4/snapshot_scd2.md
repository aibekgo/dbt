# Exercise — Snapshot `stg__orders` with SCD2

## Goal

Create `snapshots/orders_snapshot.sql` that snapshots `{{ ref('stg__orders') }}` with `strategy='check'` on the `status` column. Run `dbt snapshot`. The result is a new table `snapshots.orders_snapshot` with all 99 orders plus four SCD2 metadata columns.

## Steps

**1.** From the repo root, create the snapshot file:

```bash
mkdir -p dbt_project/snapshots
touch dbt_project/snapshots/orders_snapshot.sql
```

The `snapshots/` folder ships with the default `dbt init` scaffold, so it should already exist.

**2.** Paste this into `orders_snapshot.sql`:

```sql
{% snapshot orders_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='order_id',
        strategy='check',
        check_cols=['status']
    )
}}

select * from {{ ref('stg__orders') }}

{% endsnapshot %}
```

Three things to flag:

- **`{% snapshot orders_snapshot %}` ... `{% endsnapshot %}`** — these tags are mandatory for snapshot files. Different from regular models. The name inside the tag becomes the snapshot's name.
- **`target_schema='snapshots'`** — the snapshot lands in a `snapshots` schema (DuckDB will auto-create it on first run). Keeps snapshots out of `main`.
- **`check_cols=['status']`** — only `status` is watched for changes. If `customer_id` were updated for an existing order (which would never happen in real life), the snapshot wouldn't append a new row.

**3.** Run the snapshot:

```bash
cd dbt_project
dbt snapshot --select orders_snapshot
```

You should see one green line. dbt issued `create table snapshots.orders_snapshot as select ..., dbt_scd_id, dbt_updated_at, dbt_valid_from, dbt_valid_to from ...`.

**4.** Confirm the table is in the `snapshots` schema with the SCD2 columns:

```bash
duckdb ../database/dev.duckdb -c "select table_schema, count(*) from information_schema.tables where table_name='orders_snapshot' group by 1"
```

Should show `snapshots | 1`.

```bash
duckdb ../database/dev.duckdb -c "select count(*) from information_schema.columns where table_name='orders_snapshot' and column_name in ('dbt_scd_id','dbt_updated_at','dbt_valid_from','dbt_valid_to')"
```

Should print `4` — all four metadata columns present.

**5.** Confirm 99 rows are active:

```bash
duckdb ../database/dev.duckdb -c "select count(*) from snapshots.orders_snapshot where dbt_valid_to is null"
```

Should print `99`. All orders are currently in their first-ever snapshot version, so all 99 rows have `dbt_valid_to IS NULL`.

**6.** (Optional, to see the SCD2 columns at work.) Peek at the data:

```bash
duckdb ../database/dev.duckdb -c "select order_id, status, dbt_valid_from, dbt_valid_to from snapshots.orders_snapshot order by order_id limit 5"
```

Five rows, each with a `dbt_valid_from` timestamp (when this snapshot ran) and `dbt_valid_to` of `NULL` (still active).

**7.** (Even more optional.) Run `dbt snapshot` a second time:

```bash
dbt snapshot --select orders_snapshot
```

The output reports 0 rows changed. The seed is static, so no `status` differences between runs — the snapshot is unchanged.

**8.** Press `v` to verify.

## What the verifier checks

- `dbt snapshot --select orders_snapshot` exits 0.
- 99 rows in `snapshots.orders_snapshot` with `dbt_valid_to IS NULL`.
- All 4 SCD2 metadata columns (`dbt_scd_id`, `dbt_updated_at`, `dbt_valid_from`, `dbt_valid_to`) are present in the table.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: Snapshot 'orders_snapshot' must contain a {% snapshot %} ... {% endsnapshot %} block` | Missing the tag wrapper. The whole content (config block + select) goes inside `{% snapshot orders_snapshot %} ... {% endsnapshot %}`. |
| `Compilation Error: Snapshots require either a 'check' or 'timestamp' strategy` | Missing or misspelled `strategy='check'`. |
| `Compilation Error: 'check' strategy requires 'check_cols' to be configured` | Add `check_cols=['status']` to the config block. |
| `Catalog Error: Table with name orders_snapshot does not exist!` (when querying without schema) | The snapshot is in `snapshots.orders_snapshot`, not `main.orders_snapshot`. Either use the full `snapshots.orders_snapshot` qualifier or `set search_path = 'snapshots';` first. |
| 0 rows in the snapshot | Something failed silently — check the `dbt snapshot` output. Could be a bad `ref()` (e.g. `ref('stg_orders')` single underscore) or a permissions issue creating the schema. |

## After you pass

That's the last exercise of Stage 4. Press `n` to take the stage quiz, then on to Stage 5 — Jinja, macros, state selection, and exposures.
