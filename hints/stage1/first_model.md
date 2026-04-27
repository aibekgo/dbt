## Hint 1

The file path matters: `dbt_project/models/staging/stg_customers.sql`. Make the `staging/` subdir if it doesn't exist (`mkdir -p dbt_project/models/staging`).

## Hint 2

Inside the SQL file, do **not** write `from raw_customers` or `from main.raw_customers`. Use `{{ ref('raw_customers') }}` so dbt builds the dependency graph and inserts the fully qualified table name at compile time.

## Hint 3

The full minimum-viable file:

```sql
select
    id as customer_id,
    first_name,
    last_name
from {{ ref('raw_customers') }}
```

Then from `dbt_project/`, run `dbt run --select stg_customers`. If you forgot to mkdir the `staging/` subdir, dbt will silently not find the file — `dbt ls --select stg_customers` should show your model if it's wired up correctly.
