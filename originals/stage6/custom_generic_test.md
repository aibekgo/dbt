# Exercise — Write a `non_negative` custom generic test

## Goal

Create `dbt_project/tests/generic/non_negative.sql` defining a custom generic test that asserts a column's values are zero or positive (no negative values). Attach it to the numeric columns in `int_order_payments` via a new `_models.yml` schema file.

> **First, undo Stage 4's ephemeral switch.** In Stage 4 you set `int_order_payments` to `materialized='ephemeral'`. Ephemeral models don't have a warehouse object, so dbt can't attach generic tests to them — the test query needs a real relation to query. This exercise first switches the materialization back to `view` (the dbt default for the `intermediate/` folder).

## Steps

**1.** Open `dbt_project/models/intermediate/int_order_payments.sql` and remove the `{{ config(materialized='ephemeral') }}` line — leaving just the `select`. Without an explicit override, it falls back to the dbt default for the folder, which is `view`.

The file should now read:

```sql
select
    order_id,
    sum(amount)              as total_amount,
    count(*)                 as payment_count
from {{ ref('stg__payments') }}
group by order_id
```

Re-run it so the warehouse rebuilds it as a view:

```bash
cd dbt_project
dbt run --select int_order_payments
```

**2.** From the repo root, create the `tests/generic/` folder and the test file:

```bash
mkdir -p dbt_project/tests/generic
touch dbt_project/tests/generic/non_negative.sql
```

**3.** Paste this into `non_negative.sql`:

```jinja
{% test non_negative(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
```

The structure:
- `{% test non_negative(model, column_name) %}` opens the test definition.
- The body is a `select` returning the **bad rows** — values where the assertion fails (i.e., `< 0`).
- `{% endtest %}` closes the block.

(Note: `< 0` not `<= 0` — zero is a legitimate value for a refunded order with `total_amount = 0`.)

**4.** Create `dbt_project/models/intermediate/_models.yml` (this folder didn't have a schema YAML before):

```yaml
version: 2

models:
  - name: int_order_payments
    description: "Per-order rollup of payment events from stg__payments."
    columns:
      - name: order_id
        description: "Primary key."
        tests:
          - unique
          - not_null
      - name: total_amount
        description: "Sum of all payment amounts (in dollars) for the order. Refunds can sum to 0."
        tests:
          - non_negative
      - name: payment_count
        description: "Number of payment events that rolled up into this order."
        tests:
          - non_negative
```

Three tests on `int_order_payments`: `unique`+`not_null` on `order_id`, plus the new `non_negative` test on both numeric columns.

**5.** Run the tests:

```bash
dbt test --select int_order_payments
```

You should see four tests run and pass:

```
Done. PASS=4 WARN=0 ERROR=0 SKIP=0 TOTAL=4
```

(`unique`, `not_null`, plus two `non_negative` calls.)

**6.** Confirm the new tests show up in the manifest:

```bash
dbt ls --resource-type test --select int_order_payments
```

You should see lines like:

```
dbt_project.unique_int_order_payments_order_id
dbt_project.not_null_int_order_payments_order_id
dbt_project.non_negative_int_order_payments_total_amount
dbt_project.non_negative_int_order_payments_payment_count
```

The naming pattern matches the built-ins.

**7.** Press `v` to verify.

## What the verifier checks

- `dbt_project/tests/generic/non_negative.sql` exists.
- The file contains the literal string `{% test non_negative`.
- `dbt test --select int_order_payments` exits 0 with all tests passing.

## Common failure modes

| Symptom | Fix |
|---|---|
| `path 'dbt_project/tests/generic/non_negative.sql' does not exist` | The file is in the wrong folder. It must be under `tests/generic/`, not `tests/`. |
| `Compilation Error: 'non_negative' is undefined` | Two possibilities: (a) the file is in `tests/` instead of `tests/generic/` — dbt parses singular tests differently; (b) the `{% test ... %}` block has a syntax error and didn't register. Run `dbt parse` to see the exact error. |
| `dbt test` errors with *"compiled SQL is not a valid select"* | The body of the test isn't a `select` statement. The body must be a query returning rows; nothing else. |
| `Compilation Error: macro 'non_negative' is undefined` (in YAML) | Means dbt couldn't find the test. Check the file path again, and confirm `dbt parse` succeeds. |
| Test reports `FAIL` | The data violates the assertion. Run `select * from int_order_payments where total_amount <= 0` to see what's actually there — shouldn't happen on the seed data, but if it does, the test is doing its job. |

## After you pass

Press `n`. The next exercise installs the `dbt_expectations` package — bringing in tests like `expect_column_values_to_be_between` for richer statistical assertions.
