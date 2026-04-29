## Hint 1

One new file: `dbt_project/models/_exposures.yml` (any `.yml` under `models/` works, but the leading underscore is convention).

The file declares one exposure named `orders_dashboard` of type `dashboard`, with `depends_on: [ref('fct_orders'), ref('dim_customers')]` and an `owner.name` set.

Then `dbt docs generate` from inside `dbt_project/` to refresh the manifest with the new exposure.

## Hint 2

The file in its final form:

```yaml
version: 2

exposures:
  - name: orders_dashboard
    label: "Orders Operational Dashboard"
    type: dashboard
    maturity: high
    url: https://example.com/dashboards/orders
    description: "Daily order volume, revenue, and status breakdown for the operations team."
    depends_on:
      - ref('fct_orders')
      - ref('dim_customers')
    owner:
      name: Data Team
      email: data@example.com
```

The `depends_on:` entries are `ref()` calls (Jinja), not bare strings. `ref('fct_orders')` is what makes dbt register the lineage edge.

## Hint 3

If verification still fails:

1. `ls dbt_project/models/_exposures.yml` should list the file. If you put it elsewhere (e.g. project root or `dbt_project/exposures.yml`), dbt won't see it — only `.yml` files under `model-paths:` (default `models/`) are scanned.
2. `dbt parse` from inside `dbt_project/` should exit 0. If not, the YAML has a syntax error — usually missing `version: 2` or wrong indentation under `depends_on:` / `owner:`.
3. `dbt ls --resource-type exposure` should print one line containing `orders_dashboard`. If it prints nothing, the exposure didn't register.
4. The verifier runs `dbt docs generate` and checks both `manifest.json` and `catalog.json` exist + were updated. If `dbt docs generate` errors, look at the error message — usually a `type:` typo or missing `owner.name`.
