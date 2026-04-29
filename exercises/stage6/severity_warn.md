# Exercise — Add `severity: warn` and `where:` to the status test

## Goal

Extend the `accepted_values` test on `stg__orders.status` (which you wrote in Stage 3's `accepted_values_relationships` exercise) with a `config:` block specifying `severity: warn` and a `where:` clause. The test still passes on the seed data; the new config controls *how* it would behave if the data ever violated the assertion.

## Steps

**1.** Open `dbt_project/models/staging/_models.yml`. Find the `status` column under `stg__orders`. Currently it looks like this:

```yaml
- name: status
  description: "Order lifecycle state."
  tests:
    - accepted_values:
        values: [placed, shipped, completed, return_pending, returned]
```

**2.** Replace it with the extended form including the config block:

```yaml
- name: status
  description: "Order lifecycle state."
  tests:
    - accepted_values:
        values: [placed, shipped, completed, return_pending, returned]
        config:
          severity: warn
          where: "order_date >= '2018-01-01'"
```

Two things to flag:

- `config:` is nested *under* `accepted_values:`, not at the test list level. Indent it to align with `values:`.
- `where:` value is a string. Quote it as YAML expects (single quotes around the date literal because it's nested inside a YAML string).

**3.** Run the staging tests to confirm the YAML parses and the test executes:

```bash
cd dbt_project
dbt test --select stg__orders
```

You should see the tests pass cleanly. The seed data has all statuses in the allowed set, so the test doesn't have anything to warn about — but the config is now in place.

**4.** (Optional, to *see* the warn behavior.) Temporarily modify the `values:` list to exclude `returned`:

```yaml
values: [placed, shipped, completed, return_pending]
```

Re-run `dbt test --select stg__orders`. Notice the output: dbt reports a `WARN` (not `FAIL`), the run still exits 0, and you'd see a "1 of 4 WARN" line. Revert the `values:` list before pressing `v`.

**5.** Press `v` to verify.

## What the verifier checks

- `dbt test --select stg__orders` exits 0 (proves the YAML is valid and the test runs).
- `dbt_project/models/staging/_models.yml` contains the literal string `severity: warn` (proves the config block is there).

## Common failure modes

| Symptom | Fix |
|---|---|
| `Compilation Error: ... unable to find configuration ... 'severity'` | The `severity:` key is at the wrong indent level. It must be inside a `config:` block, which is nested under `accepted_values:`. |
| `dbt test` errors with a YAML parse issue | Indentation. The structure is: `tests: → - accepted_values: → values: AND config:` (peers). If `config:` is at the same indent as `tests:`, YAML rejects it. |
| `file 'dbt_project/models/staging/_models.yml' does not contain 'severity: warn'` | The string didn't land in the file. Check you saved the file and the line reads exactly `severity: warn` (no extra characters, lowercase `warn`). |
| `Compilation Error: 'placed' is not in the accepted values list` (after step 4 experiment) | You forgot to revert the `values:` list. Add `returned` back. |

## After you pass

Press `n`. The next exercise covers **custom generic tests** — writing your own `{% test %}` blocks for assertions that the four built-ins don't quite fit.
