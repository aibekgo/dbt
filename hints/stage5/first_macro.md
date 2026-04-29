## Hint 1

Two file changes:

1. Create `dbt_project/macros/cents_to_dollars.sql` with a `{% macro cents_to_dollars(column_name, decimal_places=2) %} ... {% endmacro %}` block. The body renders `round( 1.0 * {{ column_name }} / 100, {{ decimal_places }} )`.
2. Edit `dbt_project/models/staging/stg__payments.sql` to replace `amount / 100.0` with `{{ cents_to_dollars('amount') }}`.

Then `dbt run --select stg__payments` from inside `dbt_project/`.

## Hint 2

Final shapes:

```jinja
{# dbt_project/macros/cents_to_dollars.sql #}
{% macro cents_to_dollars(column_name, decimal_places=2) -%}
round( 1.0 * {{ column_name }} / 100, {{ decimal_places }} )
{%- endmacro %}
```

```sql
-- dbt_project/models/staging/stg__payments.sql
select
    id                                  as payment_id,
    order_id,
    payment_method,
    {{ cents_to_dollars('amount') }}    as amount
from {{ source('stripe', 'raw_payments') }}
```

The leading `-%}` and trailing `{%-` strip whitespace — without them the macro expansion has extra newlines around it. The argument `'amount'` is a string in single quotes.

## Hint 3

If verification still fails:

1. `ls dbt_project/macros/` should list `cents_to_dollars.sql`. If it's missing or named differently, dbt won't find it.
2. `dbt parse` from inside `dbt_project/` should succeed silently. If it errors, the macro syntax is wrong — most often a missing `{% endmacro %}` or typo in `{% macro ... %}`.
3. `cat target/compiled/dbt_project/models/staging/stg__payments.sql` should show `round( 1.0 * amount / 100, 2 )` where the macro call used to be. If the line still says `{{ cents_to_dollars('amount') }}`, dbt didn't compile — check `dbt parse` again.
4. `duckdb database/dev.duckdb -c "select max(amount) from stg__payments"` (from repo root) should return a value < 100 (dollars). If it returns a value > 100, the conversion didn't happen — re-check the macro body has `/ 100` not `* 100`.
