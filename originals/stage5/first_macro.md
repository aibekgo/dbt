# Exercise — Write `cents_to_dollars` and refactor `stg__payments`

## Goal

Create `dbt_project/macros/cents_to_dollars.sql` defining a macro that converts a cents-valued column to dollars with configurable rounding. Refactor `dbt_project/models/staging/stg__payments.sql` to call the macro instead of using the inline `amount / 100.0` expression. Downstream values stay the same.

## Steps

**1.** From the repo root, create the macro file:

```bash
mkdir -p dbt_project/macros
touch dbt_project/macros/cents_to_dollars.sql
```

**2.** Paste this into `cents_to_dollars.sql`:

```jinja
{% macro cents_to_dollars(column_name, decimal_places=2) -%}
round( 1.0 * {{ column_name }} / 100, {{ decimal_places }} )
{%- endmacro %}
```

The macro:
- Takes `column_name` (positional, required) and `decimal_places` (positional with default 2).
- Renders to a SQL expression: `round( 1.0 * <col> / 100, <decimal_places> )`.
- The leading `-%}` and trailing `{%-` strip whitespace so the expansion is one clean inline expression.

**3.** Open `dbt_project/models/staging/stg__payments.sql`. Replace the inline `amount / 100.0` with a macro call. The full file should read:

```sql
select
    id                                  as payment_id,
    order_id,
    payment_method,
    {{ cents_to_dollars('amount') }}    as amount
from {{ source('stripe', 'raw_payments') }}
```

The first argument is the column name as a **string**: `'amount'`, with quotes.

**4.** Re-run the staging model to materialize against the macro:

```bash
cd dbt_project
dbt run --select stg__payments
```

You should see one green line. Behind the scenes, dbt rendered the macro into `round( 1.0 * amount / 100, 2 )` and used that as the column expression.

**5.** Inspect the compiled SQL to confirm the macro expanded:

```bash
cat target/compiled/dbt_project/models/staging/stg__payments.sql
```

The `{{ cents_to_dollars('amount') }}` line is gone; in its place is `round( 1.0 * amount / 100, 2 )`.

**6.** Sanity-check the dollar values look right:

```bash
duckdb ../database/dev.duckdb -c "select payment_id, amount from stg__payments limit 5"
```

Five rows, `amount` values like `1.00`, `26.00`, `1.50` — dollars, not cents.

**7.** Press `v` to verify.

## What the verifier checks

- `dbt run --select stg__payments` exits 0.
- `target/manifest.json` registers a macro named `cents_to_dollars`.
- `select count(*) from stg__payments where amount > 0 and amount < 100` returns 113 — meaning all 113 payments are now in dollar units (not cents).

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: macro 'cents_to_dollars' is undefined` | The macro file isn't in `dbt_project/macros/` or its filename doesn't end in `.sql`. Confirm the path: `dbt_project/macros/cents_to_dollars.sql`. |
| `Macro `cents_to_dollars` not found in target/manifest.json` | The macro file exists but didn't parse — usually a syntax error in the Jinja. Common cause: missing `{% endmacro %}` or a typo like `{% macro %}` (no name). |
| `Compilation Error: '<class ...>' object has no attribute 'amount'` (or similar attribute error) | You wrote `{{ cents_to_dollars(amount) }}` without quotes. The argument must be a string: `'amount'`. |
| `count(*) where amount > 0 and amount < 100` returns 0 or wrong number | The cents → dollars conversion didn't happen. Check that the macro body has `/ 100` (not `* 100`) and that you replaced the original expression rather than adding another column. |
| Stage 3 tests fail (e.g. `not_null` on payment_id) | Unrelated — the refactor didn't touch the column shape. Check you didn't accidentally drop columns from the `select` list. |

## After you pass

Press `n`. Next exercise covers **state selection** — `dbt run --select state:modified+ --state ./prev_target` — the CI optimization that lets you rebuild only what changed.
