# Exercise — Add a reference seed

## Goal

Add a small reference CSV (`order_status_descriptions.csv`) under `dbt_project/seeds/`, run `dbt seed`, and confirm the table lands in DuckDB. This is the canonical use case for seeds: a slow-changing lookup table versioned alongside your dbt code.

## Steps

**1.** From the repo root, create the seed file at `dbt_project/seeds/order_status_descriptions.csv` with this content:

```csv
status,description
placed,Order has been placed but not yet shipped
shipped,Order has shipped to the customer
completed,Order delivered and confirmed received
return_pending,Customer has indicated a return; awaiting receipt
returned,Item has been returned to the warehouse
```

Five rows. The `status` column matches the values the `accepted_values` test from the previous exercise constrains `stg__orders.status` to.

**2.** Run the seed loader:

```bash
cd dbt_project
dbt seed --select order_status_descriptions
```

You should see one green line:

```
1 of 1 OK loaded seed file main.order_status_descriptions
```

The `--select` is optional — bare `dbt seed` would load every CSV in `seeds/`. Scoping is just faster while developing.

**3.** Confirm the table exists in DuckDB:

```bash
duckdb ../database/dev.duckdb -c "select count(*) from order_status_descriptions"
```

Should print `5`.

**4.** Peek at the data:

```bash
duckdb ../database/dev.duckdb -c "select * from order_status_descriptions"
```

Five rows with the descriptions you wrote. Notice DuckDB inferred `status` and `description` as `VARCHAR` automatically — `dbt seed` reads the CSV header for column names and the first batch of rows for types.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt seed --select order_status_descriptions` exits 0.
- Table `order_status_descriptions` exists in `dev.duckdb`.
- `select count(*) from order_status_descriptions` returns exactly `5`.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Encountered an error: Could not find any seeds named like 'order_status_descriptions'` | The CSV isn't where dbt expects. Confirm the path is exactly `dbt_project/seeds/order_status_descriptions.csv` (the filename minus `.csv` becomes the seed name). |
| Row count is `6` not `5` | One too many rows in the CSV — the header row counts as a row in the file but not in the table. Five status descriptions = 5 data rows + 1 header line = 6 lines total. |
| Row count is `4` | Missing one of the five statuses, or an extra blank line. CSVs with trailing whitespace lines silently drop the last data row in some parsers. |
| `column "status" mentioned in CHECK constraint does not exist` | The column header doesn't match. Confirm the first line of the CSV reads exactly `status,description` with no spaces around the comma. |

## After you pass

Press `n`. The last exercise of Stage 3 covers **analyses** — SQL files that compile but don't materialize, useful for one-off audits and training queries.
