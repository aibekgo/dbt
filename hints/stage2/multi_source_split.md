## Hint 1

Two files change:

1. `dbt_project/models/staging/_sources.yml` — replace the single `raw` source with two: `jaffle_shop` (`raw_customers`, `raw_orders`) and `stripe` (`raw_payments`).
2. `dbt_project/models/staging/stg__customers.sql` — update the `source()` call so its first argument is `'jaffle_shop'` instead of `'raw'`.

Then run `dbt run --select stg__customers` from inside `dbt_project/` to confirm both files line up.

## Hint 2

The two files in their final form:

```yaml
# dbt_project/models/staging/_sources.yml
version: 2

sources:
  - name: jaffle_shop
    schema: main
    tables:
      - name: raw_customers
      - name: raw_orders

  - name: stripe
    schema: main
    tables:
      - name: raw_payments
```

```sql
-- dbt_project/models/staging/stg__customers.sql
select
    id          as customer_id,
    first_name,
    last_name
from {{ source('jaffle_shop', 'raw_customers') }}
```

The verifier reads `target/manifest.json` after a `dbt parse`, so any YAML syntax error or missing source name will be caught.

## Hint 3

If verification still fails, walk through these checks in order:

1. `dbt parse` from inside `dbt_project/` — does it exit 0? If not, the error message tells you exactly what's wrong with the YAML.
2. `dbt ls --resource-type source` should print three lines: two prefixed `dbt_project.jaffle_shop.…` and one `dbt_project.stripe.raw_payments`.
3. `dbt run --select stg__customers` should still exit green. If it errors with *"Found a source named 'raw'…"*, your `stg__customers.sql` still references the old source name — change the first arg of `source(...)` to `'jaffle_shop'`.
4. The verifier doesn't care about descriptions, ordering, or extra whitespace — only the source `name:` and the list of tables. Don't over-think the YAML.
