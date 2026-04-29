# Exercise — Preview `fct_orders` with `dbt show`

## Goal

Use `dbt show` to preview the first 5 rows of `fct_orders`. No file edits — this exercise is about getting the muscle memory for the command.

## Steps

**1.** From inside `dbt_project/`, run:

```bash
cd dbt_project
dbt show --select fct_orders --limit 5
```

Output should show 5 rows of `fct_orders`, formatted as a table. Columns include `order_id`, `customer_id`, `first_name`, `last_name`, `order_date`, `status`, `amount`, `payment_count`, plus the `order_key` you added in Stage 5.

**2.** (Optional, to try the inline mode.) Run a one-off aggregation without writing a file:

```bash
dbt show --inline "select status, count(*) as n from {{ ref('fct_orders') }} group by 1 order by n desc"
```

Five rows, one per status, with the count. Notice how `{{ ref('fct_orders') }}` works inside `--inline` just like inside a model file.

**3.** (Also optional, to see the limit knob.) Compare the same query with different limits:

```bash
dbt show --select fct_orders --limit 1
dbt show --select fct_orders --limit 20
```

The first prints one row, the second prints 20. The model isn't re-run between them — `--limit` is a presentation-time cap, not a query-time filter.

**4.** Press `v` to verify.

## What the verifier checks

- `dbt show --select fct_orders --limit 5` exits 0.

The verifier itself runs the same command and confirms it succeeds. Your output isn't compared — only the exit code. So as long as `fct_orders` is queryable, this passes.

## Common failure modes

| Symptom | Fix |
|---|---|
| `Catalog Error: Table with name fct_orders does not exist!` | The model isn't built. Run `dbt run --select fct_orders` first, then retry. |
| `Compilation Error: 'fct_orders' is undefined` | Typo in the `--select` value, or the model name has changed. Run `dbt ls --resource-type model` to confirm. |
| Output is garbled / truncated | Terminal width is too narrow. Resize the terminal wider, or scope columns with `--inline "select order_id, status, amount from ... limit 5"`. |
| Verifier itself is slow | `dbt show` runs the model's full SQL query. For our 99-row seed, this is instant. On big tables, it can take a while — that's normal. |

## After you pass

Press `n`. Next is `commands_tour` — a lesson covering the full dbt CLI surface (`dbt parse`, `dbt ls`, `dbt source freshness`, `dbt retry`, `dbt clean`, etc.) so you know what's available beyond the workhorse `run`/`build`/`test`.
