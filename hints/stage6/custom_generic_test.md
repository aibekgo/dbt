## Hint 1

Two file changes:

1. Create `dbt_project/tests/generic/non_negative.sql` with a `{% test non_negative(model, column_name) %} ... {% endtest %}` block. The body is `select * from {{ model }} where {{ column_name }} <= 0`.
2. Create `dbt_project/models/intermediate/_models.yml` declaring `int_order_payments` with `unique`+`not_null` on `order_id` and `non_negative` on `total_amount` and `payment_count`.

Then `dbt test --select int_order_payments` from inside `dbt_project/`.

## Hint 2

The two files in their final form:

```jinja
{# dbt_project/tests/generic/non_negative.sql #}
{% test non_negative(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
```

```yaml
# dbt_project/models/intermediate/_models.yml
version: 2

models:
  - name: int_order_payments
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: total_amount
        tests:
          - non_negative
      - name: payment_count
        tests:
          - non_negative
```

The folder `tests/generic/` (not `tests/`) is where dbt looks for custom generic test definitions. Singular tests live in `tests/` directly.

## Hint 3

If verification still fails:

1. `ls dbt_project/tests/generic/non_negative.sql` should print the file. If it shows the file at `tests/non_negative.sql` (one level up), dbt would parse it as a singular test and error.
2. `dbt parse` from inside `dbt_project/` should exit 0. If it errors, the `{% test ... %}` syntax has a typo — most often a missing `{% endtest %}` or wrong arg list.
3. `dbt ls --resource-type test --select int_order_payments` should print 4 lines including two whose names start with `non_negative_`. If you see fewer, the YAML didn't pick up the `- non_negative` tests — check the indentation in `_models.yml`.
4. `dbt test --select int_order_payments` should report `PASS=4`. If a `non_negative` test fails, the data has a non-non_negative value — the seed is consistent so this shouldn't happen unless something else broke `int_order_payments` upstream.
