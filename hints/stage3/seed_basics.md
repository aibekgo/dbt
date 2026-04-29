## Hint 1

One new file: `dbt_project/seeds/order_status_descriptions.csv`. The `seeds/` folder is part of the default dbt scaffold so it should already exist (it's empty after Stage 2).

The CSV needs:
- A header line: `status,description`
- 5 data rows: one per order status (placed, shipped, completed, return_pending, returned), each with a short description.

Then `dbt seed --select order_status_descriptions` from inside `dbt_project/`.

## Hint 2

The CSV in its final form (six lines total — header + 5 rows):

```csv
status,description
placed,Order has been placed but not yet shipped
shipped,Order has shipped to the customer
completed,Order delivered and confirmed received
return_pending,Customer has indicated a return; awaiting receipt
returned,Item has been returned to the warehouse
```

The status values must match the five accepted values from the previous exercise. Descriptions can be whatever sentence you like (the verifier doesn't check the text), but they should be plain ASCII without commas — commas in the value would be parsed as field separators and break the load.

## Hint 3

If verification still fails:

1. `ls dbt_project/seeds/` — should list `order_status_descriptions.csv`. If it lists `order_status_descriptions.csv.csv` (double extension) or `order_status_descriptions` (no extension), `dbt seed` won't pick it up.
2. `dbt seed --select order_status_descriptions` from inside `dbt_project/` should print *"1 of 1 OK loaded seed file main.order_status_descriptions"*.
3. `duckdb database/dev.duckdb -c "select count(*) from order_status_descriptions"` (run from repo root) should return `5`. If it returns `4` or `6`, the CSV either has an extra blank line or a header miscount.
4. If the seed loads but the table can't be found, check the seed schema. Default is `main` (matching the rest of the project) — if `dbt_project.yml` has a `seeds: schema: foo` config, the table lands in a different schema and `from order_status_descriptions` fails to resolve.
