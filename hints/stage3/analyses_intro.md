## Hint 1

One new file: `dbt_project/analyses/top_customers_by_revenue.sql`. The `analyses/` folder is part of the default dbt scaffold — should already exist but be empty.

The query joins `fct_orders` and `dim_customers` via `customer_id`, aggregates by customer, and orders by total revenue. Both joined tables come from `ref()`. No `{{ config(...) }}` block — analyses don't materialize.

Then `dbt compile --select top_customers_by_revenue` from inside `dbt_project/`.

## Hint 2

The file in its final form:

```sql
-- dbt_project/analyses/top_customers_by_revenue.sql
select
    c.customer_id,
    c.first_name,
    c.last_name,
    count(o.order_id) as order_count,
    sum(o.amount)     as lifetime_revenue
from {{ ref('fct_orders') }} o
join {{ ref('dim_customers') }} c using (customer_id)
group by 1, 2, 3
order by lifetime_revenue desc
limit 10
```

After compile, the rendered SQL lands at `target/compiled/dbt_project/analyses/top_customers_by_revenue.sql` with `{{ ref(...) }}` replaced by fully-qualified table names.

## Hint 3

If verification still fails:

1. `ls dbt_project/analyses/` — should list `top_customers_by_revenue.sql`. The folder name is plural (`analyses`), not singular.
2. `dbt compile --select top_customers_by_revenue` should report a non-zero count of nodes compiled. If it says *"Found 0 nodes"*, the file isn't being discovered — check the path again.
3. After compile, `ls target/compiled/dbt_project/analyses/` should include `top_customers_by_revenue.sql`. If the file's there but the verifier still complains, you might be running the verifier from a working dir where `target/compiled/` paths don't resolve — re-run from the repo root.
4. If `dbt compile` errors with `'fct_orders' is undefined`, the `ref()` argument is wrong. Run `dbt ls --resource-type model` to see the list — it should include `fct_orders` and `dim_customers` (single underscores on marts).
