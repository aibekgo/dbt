# Exercise — Write a singular test

## Goal

Add a custom singular test that asserts `int_order_payments.total_amount` is never negative. The file lives at `dbt_project/tests/assert_no_negative_payment_totals.sql`.

## Steps

**1.** From the repo root, create the test file:

```bash
mkdir -p dbt_project/tests
touch dbt_project/tests/assert_no_negative_payment_totals.sql
```

The `tests/` folder may already exist (it's part of the default `dbt init` scaffold) — `mkdir -p` is harmless either way.

**2.** Paste this into `assert_no_negative_payment_totals.sql`:

```sql
-- A singular test passes when this query returns 0 rows.
-- We're asserting that no order has a negative total_amount.
select order_id, total_amount
from {{ ref('int_order_payments') }}
where total_amount < 0
```

Three things to notice:

- **`select` finds the bad rows, not the good ones.** The query returns rows that *violate* the assertion. 0 rows = test passes.
- **`{{ ref('int_order_payments') }}` not raw table name.** This wires the test into the DAG so dbt builds the model before running the test in `dbt build`.
- **`where total_amount < 0`** — strict inequality. Zero is allowed (a refunded order can sum to 0); only *negative* amounts are violations.

**3.** Run just the singular tests:

```bash
cd dbt_project
dbt test --select test_type:singular
```

You should see one test execute and pass:

```
Completed successfully

Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

**4.** Confirm it shows up in the manifest:

```bash
dbt ls --resource-type test --select test_type:singular
```

One line: `dbt_project.assert_no_negative_payment_totals`.

**5.** (Optional, just to see the failure path.) Temporarily flip the predicate to `where total_amount > 0` and re-run `dbt test --select test_type:singular`. You should see a `FAIL` with the count of rows the test found. Flip it back to `< 0` before pressing `v`.

**6.** Press `v` to verify.

## What the verifier checks

- `dbt test --select test_type:singular` exits 0 with at least one test running and passing.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: dbt found 0 tests of type singular` | The file isn't in `tests/`, or it doesn't end in `.sql`. Confirm path is exactly `dbt_project/tests/assert_no_negative_payment_totals.sql`. |
| `Compilation Error: 'int_order_payments' is undefined` | You wrote `from int_order_payments` (raw name) instead of `from {{ ref('int_order_payments') }}`. The `ref()` is required. |
| Test reports `FAIL N` | Either the predicate is inverted (`> 0` instead of `< 0` — finds the *good* rows) or the upstream data legitimately has a negative total (shouldn't happen with the seed data). |
| `Database Error: Catalog Error: Table with name int_order_payments does not exist!` | The intermediate model isn't built yet. Run `dbt run --select int_order_payments` first, or use `dbt build --select int_order_payments+` to build the chain *and* run the test together. |

## After you pass

Press `n`. Next up: **seeds** — small reference CSVs committed to git, contrasted with Stage 1's Python ingestion of the raw CSVs.
