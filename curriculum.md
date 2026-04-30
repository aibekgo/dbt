# `learn_dbt` — Curriculum Plan (dbt + DuckDB)

An interactive, rustlings-style CLI course for learning dbt, built on the
`learn-de-template` engine and modeled after `learn_spark`. The warehouse is
embedded **DuckDB** so students can run every exercise locally with no cloud
account.

The curriculum is paced "slowly" — small, single-concept exercises with a
verifier that runs `dbt` for real and checks the result. It tracks the user's
existing `notion_dbt_series/` blog series (dbt 100 → 602) and aligns with the
official [dbt Fundamentals](https://learn.getdbt.com/courses/dbt-fundamentals)
ordering.

---

## Sample dataset: `jaffle_shop`

All exercises operate on the dbt-standard `jaffle_shop` seed CSVs
(`raw_customers.csv`, `raw_orders.csv`, `raw_payments.csv`). Matches the
official Fundamentals course so students can cross-reference external material;
small enough that DuckDB handles it instantly.

Seeds live at `dbt_project/seeds/raw_*.csv` and are loaded with `dbt seed`
early in Stage 1.

---

## Curriculum

Item ids are short, descriptive, and **never numerically prefixed** — ordering
lives in `curriculum.yaml`, so reordering or deleting an item is a one-line
shuffle in the YAML, no file rename required. Folder layout:
`lessons/stage{N}/`, `exercises/stage{N}/`, etc.

> **Legend:** L = pure lesson · X = exercise · stages end with a quiz when one is configured

---

### Stage 0 — Foundations (concept-only, no dbt yet)

Maps to `notion_dbt_series/01-dbt-100-foundations.md`. All lessons; quiz tests
conceptual understanding.

| id | type | what it teaches |
|---|---|---|
| `welcome` | L | What this course is, how the CLI works, prereqs |
| `etl_vs_elt` | L | ETL vs ELT, why the shift, cost / scalability / governance |
| `modern_data_team` | L | Data engineer / analytics engineer / data analyst roles |
| `cloud_data_warehouses` | L | Snowflake, BigQuery, Redshift, Databricks, DuckDB |
| `what_is_dbt` | L | Why dbt, the modern data stack, where dbt fits |
| `dbt_flavors` | L | dbt Core vs dbt Cloud vs dbt Fusion (Rust engine) — when to use which |

**Stage quiz:** ETL vs ELT, role definitions, dbt's place in the stack, when to pick Cloud vs Core vs Fusion.

---

### Stage 1 — Your First dbt Project

Maps to `02-dbt-101-fundamental.md`. Student builds a real dbt project from
scratch — `dbt init` to first running model. **No bundled `dbt_project/`** —
the learner creates and configures every piece. The repo ships only the raw
CSVs in `data/`; everything under `dbt_project/` is learner-generated and
gitignored.

| id | type | verifier | what it teaches |
|---|---|---|---|
| `dbt_install` | X | dbt (`dbt_installed`) | What dbt-core + dbt-duckdb are, where they live in your venv |
| `dbt_init` | X | file (`dbt_project/dbt_project.yml`) | Run `dbt init dbt_project` to scaffold a fresh project |
| `profiles_yml` | X | dbt (`dbt_debug_success`) | Write `dbt_project/profiles.yml` pointing at a local DuckDB file; `dbt debug` connects |
| `ingestion` | X | dbt (`duckdb_table_exists` × 3) | Copy raw CSVs from `data/` into `dbt_project/seeds/`; verify the raw tables exist in DuckDB |
| `first_model` | X | dbt (`dbt_run_success`, `duckdb_table_exists`) | Write `models/staging/stg__customers.sql` using `{{ ref('raw_customers') }}` |
| `add_sources` | X | file (`models/staging/_sources.yml`) | Declare the raw seed tables as a source so models can use `source()` |
| `project_yml` | X | dbt (`manifest_materialization`) | Configure `dbt_project.yml` so staging defaults to view, marts to table |

**Stage quiz:** what `dbt init` creates, what `profiles.yml` configures, `ref()` vs raw table names, `dbt seed` vs `dbt run`, view vs table materialization.

---

### Stage 2 — Sources, Refs & Project Structure

Continues `02-dbt-101-fundamental.md` (sources, naming conventions,
`dbt build`, `dbt docs`).

| id | type | verifier | what it teaches |
|---|---|---|---|
| `naming_conventions` | L | — | `src_` / `stg_` / `int_` / `fct_` / `dim_` and the staging→marts pattern |
| `multi_source_split` | X | dbt (`manifest_source_declared` × 2) | Split raw tables into two sources (`jaffle_shop`, `stripe`) and refactor staging |
| `more_staging` | X | dbt (`dbt_run_success`, `duckdb_table_exists`, `duckdb_query`) | Build `stg__orders` and `stg__payments` |
| `intermediate_model` | X | dbt (`dbt_run_success`, `duckdb_query`) | Build `int_order_payments` aggregating payments per order |
| `fact_model` | X | dbt (`dbt_run_success`, `duckdb_query`) | Build `fct_orders` joining staging + intermediate |
| `dbt_build` | X | dbt (`dbt_build_success`) | One command runs seeds + models + tests |
| `dbt_docs` | X | dbt (`dbt_docs_generated`) | Generate docs, verify `manifest.json` + `catalog.json` |

**Stage quiz:** `ref()` vs `source()`, why staging vs marts, what `dbt build` does that `dbt run` doesn't.

---

### Stage 3 — Data Quality: Tests, Seeds & Analyses

Maps to `03-dbt-102-analyses-and-seeds.md` plus the testing chapter from
Fundamentals.

| id | type | verifier | what it teaches |
|---|---|---|---|
| `tests_intro` | L | — | Generic vs singular tests, why testing matters, what `dbt test` runs |
| `generic_tests` | X | dbt (`dbt_test_success`, `manifest_test_count`) | Add `not_null`, `unique` across staging models |
| `accepted_values_relationships` | X | dbt (`manifest_test_count`) | Add `accepted_values` on `stg__orders.status` and `relationships` on `fct_orders` |
| `singular_test` | X | dbt (`dbt_test_success`) | Write a custom singular SQL test in `tests/` |
| `seed_basics` | X | dbt (`dbt_seed_success`, `duckdb_query`) | Add a lookup seed CSV and run `dbt seed` |
| `analyses_intro` | X | dbt (`dbt_compile_success`) | Add an analysis SQL file, verify `dbt compile` produces a compiled artifact |

**Stage quiz:** generic vs singular tests, when to use seeds vs sources, what `dbt compile` does without running.

---

### Stage 4 — Materializations, Incremental & Snapshots

Maps to `04-dbt-201-materialization.md`, `05-dbt-202-incremental-model.md`,
`06-dbt-203-snapshots.md`.

| id | type | verifier | what it teaches |
|---|---|---|---|
| `materialization_overview` | L | — | View / table / ephemeral / incremental — pros / cons table |
| `view_to_table` | X | dbt (`manifest_materialization=table`) | Switch a model to materialize as a table |
| `ephemeral_model` | X | dbt (`manifest_materialization=ephemeral`) | Make `int_order_payments` ephemeral; verify it inlines as a CTE |
| `incremental_basic` | X | dbt | Build an incremental model with `is_incremental()` filter |
| `incremental_merge` | X | dbt | Add `unique_key` and `incremental_strategy='merge'`; assert no dupes after re-run |
| `snapshot_scd2` | X | dbt (`dbt_snapshot_success`, `duckdb_query`) | Snapshot `stg__customers`; verify `dbt_valid_from` / `dbt_valid_to` columns |

**Stage quiz:** when to use each materialization, what `is_incremental()` returns on first run, SCD2 vs SCD1.

---

### Stage 5 — Jinja, Macros, State & Exposures

Maps to `08-dbt-302-jinja-and-macros.md`, `07-dbt-301-state.md`,
`09-dbt-303-exposure.md`.

| id | type | verifier | what it teaches |
|---|---|---|---|
| `jinja_basics` | L | — | `{% %}` vs `{{ }}` vs `{# #}`, control flow, whitespace |
| `first_macro` | X | dbt (`manifest_macro_exists`, `duckdb_query`) | Write a `cents_to_dollars(col)` macro and use it in `stg__payments` |
| `state_selection` | X | dbt | Modify a model, run `dbt run --select state:modified+ --state ./state_initial` and verify only the changed node + downstream ran |
| `exposures` | X | dbt (`manifest_exposure_exists`) | Declare a downstream BI dashboard exposure on `fct_orders` + `dim_customers` |
| `dbt_utils_install` | X | dbt + path | Install `dbt_utils`, use `dbt_utils.surrogate_key()` |

**Stage quiz:** Jinja delimiters, macro reuse, what `state:modified+` selects, why exposures matter.

---

### Stage 6 — Advanced Testing & the dbt CLI Tour

Maps to `10-dbt-401-advance-testing.md`, `15-dbt-500-command.md`,
`16-dbt-501-target-directory.md`.

| id | type | verifier | what it teaches |
|---|---|---|---|
| `advanced_testing_overview` | L | — | severity, where, limit, store_failures, custom generic tests |
| `severity_warn` | X | dbt (`file_contains`) | Add `severity: warn` so a test surfaces but doesn't fail the build |
| `custom_generic_test` | X | dbt (`path_exists`, `file_contains`, `dbt_test_success`) | Write a `non_negative` custom generic test in `tests/generic/` |
| `dbt_expectations_install` | X | dbt (`path_exists`, `manifest_test_count`) | Install `dbt_expectations`, add `expect_column_values_to_be_between` |
| `dbt_show_command` | X | dbt (`dbt_show_success`) | Use `dbt show --select fct_orders --limit 5` to preview output |
| `commands_tour` | L | — | `dbt parse`, `dbt ls`, `dbt show`, `dbt source freshness` — when to reach for each |
| `target_directory_tour` | X | dbt (`path_exists`) | Inspect `target/` after a build; identify each artifact's role |

**Stage quiz:** severity vs error, what each `target/` artifact is for, what `dbt show` does without writing.

---

### Stage 7 — Production Patterns & Tooling

Maps to `11-dbt-402-advance-deployment.md`, `13-dbt-404-refactoring.md`,
`17-setup-dbt-mcp.md`, `18-dbt-601-fusion-vscode.md`,
`19-dbt-602-metricflow.md`.

| id | type | verifier | what it teaches |
|---|---|---|---|
| `deployment_patterns` | L | — | dev / prod targets, CI patterns, why isolating environments matters |
| `multi_target_profile` | X | dbt (`file_contains`, `path_exists`) | Add a `prod:` block to `profiles.yml`, point at `database/prod.duckdb` |
| `analysis_to_model` | X | dbt (`dbt_run_success`, `manifest_test_count`, `file_contains`) | Promote a Stage 3 analysis into a `mart_customer_revenue` model with tests, meta, tags |
| `tooling_landscape` | L | — | dbt MCP server, dbt Fusion + VS Code, MetricFlow / Semantic Layer — what to learn next |
| `course_complete` | L | — | Recap, next steps, resources |

**Stage quiz:** dev vs prod target separation, when to promote an analysis to a model, what each tool in the broader ecosystem solves.
