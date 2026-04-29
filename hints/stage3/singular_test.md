## Hint 1

One new file: `dbt_project/tests/assert_no_negative_payment_totals.sql`. The `tests/` folder is part of the default dbt scaffold so it should already exist.

The query selects from `{{ ref('int_order_payments') }}` (always use `ref()`, never the raw table name) where `total_amount < 0`. The test passes when 0 rows come back.

Then `dbt test --select test_type:singular` from inside `dbt_project/`.

## Hint 2

The file in its final form:

```sql
-- dbt_project/tests/assert_no_negative_payment_totals.sql
select order_id, total_amount
from {{ ref('int_order_payments') }}
where total_amount < 0
```

Two things to remember:

1. The `where` clause has to find the *violations*. `total_amount < 0` — bad rows — not `total_amount >= 0` — good rows.
2. The `ref()` is mandatory. Without it dbt doesn't know this test depends on `int_order_payments`, and `dbt build` may run them in the wrong order.

## Hint 3

If verification still fails:

1. Confirm the file path is exactly `dbt_project/tests/assert_no_negative_payment_totals.sql`. Filenames have to end in `.sql` for dbt to discover them.
2. `dbt ls --resource-type test --select test_type:singular` should print one line containing `assert_no_negative_payment_totals`. If it prints nothing, the file isn't being picked up — check the path.
3. `dbt test --select test_type:singular` should report `PASS=1`. If it reports `FAIL=1`, the predicate is probably inverted (using `>= 0` instead of `< 0`) — flip it.
4. If `dbt test` fails with `Catalog Error: Table with name int_order_payments does not exist`, the intermediate model isn't built in DuckDB. Run `dbt run --select int_order_payments` first, then re-run the test.
