## Hint 1

Two file changes:

1. Create `dbt_project/models/marts/mart_customer_revenue.sql` with imports → logic → final CTE structure, materialized as a table. References `dim_customers` and `fct_orders`.
2. Edit `dbt_project/models/marts/_models.yml` — add a new entry for `mart_customer_revenue` with `description`, a `config:` block containing `meta:` (with `owner` and `pii`) and `tags:` (with `revenue` and `finance`), plus column-level tests on `customer_id` (`unique` + `not_null`).

Then `cd dbt_project && dbt run --select mart_customer_revenue && dbt test --select mart_customer_revenue` to confirm.

## Hint 2

Final shapes:

```sql
-- dbt_project/models/marts/mart_customer_revenue.sql
{{ config(materialized='table') }}

with

customers as (
    select * from {{ ref('dim_customers') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
),

customer_revenue as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        sum(o.amount) as lifetime_revenue,
        count(o.order_id) as lifetime_orders
    from customers c
    left join orders o on c.customer_id = o.customer_id
    group by c.customer_id, c.first_name, c.last_name
),

final as (
    select * from customer_revenue
    order by lifetime_revenue desc
)

select * from final
```

```yaml
# dbt_project/models/marts/_models.yml — add as a sibling of fct_orders
  - name: mart_customer_revenue
    description: "Customer-grain lifetime revenue and order count, derived from fct_orders + dim_customers."
    config:
      meta:
        owner: data_eng
        pii: false
      tags:
        - revenue
        - finance
    columns:
      - name: customer_id
        description: "Stable customer identifier."
        tests:
          - unique
          - not_null
      - name: lifetime_revenue
        description: "Sum of fct_orders.amount across all orders for this customer."
```

The `config:` block is nested under the model name (same indent as `description:`). The `meta:` and `tags:` keys are nested under `config:`. Don't put `meta:` at the top level of the model entry — dbt accepts that historically but it's deprecated; `config: { meta: ... }` is the current shape.

## Hint 3

If verification still fails:

1. `ls dbt_project/models/marts/mart_customer_revenue.sql` should print the file. If "no such file," the path is wrong.
2. `cd dbt_project && dbt parse` should exit 0. If it errors with a YAML problem, the indent on the new `_models.yml` entry is off — its leading `- name:` should align with the existing `- name: fct_orders`.
3. `cd dbt_project && dbt ls --resource-type test --select mart_customer_revenue` should print 2 lines (`unique_mart_customer_revenue_customer_id`, `not_null_mart_customer_revenue_customer_id`). If you see 0, the `tests:` block didn't attach — check that `tests:` is under the column's entry, not the model's.
4. `grep -E 'meta:|tags:' dbt_project/models/marts/_models.yml` should show both keys. If only one shows, the YAML entry is missing the other.
5. `cd dbt_project && dbt run --select mart_customer_revenue` should print `1 of 1 OK created sql table model`. If it errors with "relation does not exist," `dim_customers` or `fct_orders` isn't built — run `dbt build` once with no flags to refresh `dev.duckdb`.
