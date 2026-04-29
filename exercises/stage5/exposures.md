# Exercise — Declare a downstream `orders_dashboard` exposure

## Goal

Create `dbt_project/models/_exposures.yml` declaring an `orders_dashboard` exposure that depends on `fct_orders` and `dim_customers`. Re-run `dbt docs generate` so the manifest + docs catalog include it.

## Steps

**1.** From the repo root, create the new YAML file:

```bash
touch dbt_project/models/_exposures.yml
```

**2.** Paste this into `_exposures.yml`:

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

Notice the `depends_on:` list uses `ref(...)` calls (Jinja expressions evaluated at parse time), *not* string literals. That's how dbt establishes the lineage edge from the upstream models to the exposure.

**3.** Refresh the manifest + catalog so the docs site picks up the new exposure:

```bash
cd dbt_project
dbt docs generate
```

You should see the regular generate output, plus the manifest now contains the exposure node.

**4.** Confirm the exposure landed:

```bash
dbt ls --resource-type exposure
```

Should print one line: `dbt_project.orders_dashboard`.

**5.** (Optional, to see it in the docs UI.) Run `dbt docs serve` and open the lineage view — `fct_orders` and `dim_customers` should now have an arrow pointing to a new `orders_dashboard` node colored differently from the model nodes.

**6.** Press `v` to verify.

## What the verifier checks

- `dbt docs generate` exits 0 and refreshes both `manifest.json` and `catalog.json`.
- `target/manifest.json` contains an exposure named `orders_dashboard`.
- That exposure's `depends_on.nodes` lists both `fct_orders` and `dim_customers`.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Exposure 'orders_dashboard' not found in target/manifest.json` | The YAML file isn't in the right place or didn't parse. The path must be exactly `dbt_project/models/_exposures.yml` (any `.yml` under `models/` works, but `_exposures.yml` is the convention). |
| `Compilation Error: Invalid version 'version' for ...` | Missing `version: 2` at the top of the YAML. |
| `Exposure 'orders_dashboard' does not depend on model 'fct_orders'` | The `depends_on:` entries are strings instead of `ref()` calls. Change `'fct_orders'` to `ref('fct_orders')`. |
| `Compilation Error: 'dashboard' must be one of ...` | The `type:` value is misspelled. Allowed: `dashboard`, `notebook`, `analysis`, `ml`, `application`. |
| `Compilation Error: 'owner' must contain a 'name'` | The `owner:` block is missing the `name:` key. `email:` is optional but `name:` is required. |

## After you pass

Press `n`. The last Stage 5 exercise covers `dbt_utils` — installing the community package and using one of its macros.
