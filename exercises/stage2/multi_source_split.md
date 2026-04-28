# Exercise — Split `raw` into `jaffle_shop` and `stripe`

## Goal

Refactor `models/staging/_sources.yml` so it declares two sources — `jaffle_shop` (application data) and `stripe` (payment processor) — instead of the catch-all `raw` source from Stage 1. Update `stg__customers.sql` to point at the new source name.

## Steps

**1.** From the repo root, open `dbt_project/models/staging/_sources.yml` and replace its contents with:

```yaml
version: 2

sources:
  - name: jaffle_shop
    description: "Application data from the Jaffle Shop app database"
    schema: main
    tables:
      - name: raw_customers
      - name: raw_orders

  - name: stripe
    description: "Payment data landed from the Stripe payment processor"
    schema: main
    tables:
      - name: raw_payments
```

Notice what changed: two top-level source blocks, customers + orders under `jaffle_shop`, payments under `stripe`. The `schema:` field stays as `main` because that's where `scripts/ingest_raw.py` lands the CSVs.

**2.** Open `dbt_project/models/staging/stg__customers.sql`. Update the `from` line so it references the new source:

```sql
select
    id          as customer_id,
    first_name,
    last_name
from {{ source('jaffle_shop', 'raw_customers') }}
```

The first argument of `source()` must match the `name:` field of the source block. Keep everything else the same.

**3.** Sanity-check the project parses and runs:

```bash
cd dbt_project
dbt run --select stg__customers
```

You should see the same green success message as in Stage 1. The compiled SQL still resolves to `main.raw_customers` — only dbt's *understanding* of where that table came from has changed.

**4.** List the new sources to confirm both are on the DAG:

```bash
dbt ls --resource-type source
```

Three lines, grouped by source:

```
dbt_project.jaffle_shop.raw_customers
dbt_project.jaffle_shop.raw_orders
dbt_project.stripe.raw_payments
```

**5.** Press `v` to verify.

## What the verifier checks

- Source `jaffle_shop` is declared in `target/manifest.json` with both `raw_customers` and `raw_orders`.
- Source `stripe` is declared with `raw_payments`.
- `dbt run --select stg__customers` still exits 0 — proving the SQL edit kept the model parseable.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Found a source named 'raw' but there is no matching source declaration` | You updated the YAML but forgot the SQL — `stg__customers.sql` still references `source('raw', ...)`. Change the first argument to `'jaffle_shop'`. |
| `Source 'jaffle_shop' not found in target/manifest.json` | The YAML edit didn't land — confirm the file was saved at `dbt_project/models/staging/_sources.yml` and the top-level key is `sources:` (plural). |
| `Compilation Error: duplicate source name 'jaffle_shop'` | You have two `- name: jaffle_shop` blocks. Each `name:` must be unique. |
| YAML parse error | Indentation. YAML uses spaces (two per level), never tabs. |

## After you pass

Press `n`. The next exercise fans out the staging layer — building `stg__orders` and `stg__payments` against your new sources.
