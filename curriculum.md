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

## Repo branding & renames

| File | Change |
|---|---|
| `pyproject.toml` | `name = "dbt-learn"`; entry point `dbt-learn = "cli.main:app"`; deps: `dbt-core>=1.8,<2.0`, `dbt-duckdb>=1.8,<2.0`, `duckdb`, `typer`, `rich`, `pyyaml`, `pytest`, `markdown` |
| `cli/main.py` | `COURSE_NAME = "dbt-learn"`, `COURSE_EMOJI = "🔧"`; remove `docker exec` plumbing from `LocalVerifier` (run pytest in-process); register `DbtVerifier` and `FileVerifier` |
| `README.md` | Rewrite per the template's README spec (one-liner, prereqs, `uv venv` + `uv pip install -e .` setup, key-commands table) — **no Docker** |

---

## Verifier architecture

Following the `learn_spark` pattern (one verifier class per *type*, all checks
declared in `curriculum.yaml`), three verifier classes register alongside the
existing `LocalVerifier`:

### 1. `LocalVerifier` (existing — reuse)

Pure Python/SQL logic exercises (e.g., a Jinja macro you call from pytest,
validating a YAML structure manually). Used sparingly — most dbt exercises need
real dbt execution.

### 2. `DbtVerifier` (new) — `verifier/dbt.py`

The workhorse. Runs dbt commands against the bundled DuckDB project and
validates results. Reads `dbt_checks` block from `curriculum.yaml` per
exercise.

Rule types (each maps to a `_check_*` helper):

| Rule type | What it checks |
|---|---|
| `dbt_run_success` | `dbt run --select <model>` exits 0, all nodes succeed |
| `dbt_test_success` | `dbt test --select <model>` exits 0, all tests pass |
| `dbt_seed_success` | `dbt seed --select <name>` exits 0 |
| `dbt_snapshot_success` | `dbt snapshot --select <name>` exits 0 |
| `dbt_build_success` | `dbt build --select <selector>` exits 0 |
| `manifest_node_exists` | parse `target/manifest.json`, assert node id present |
| `manifest_materialization` | node materialized as `view` / `table` / `incremental` / `ephemeral` |
| `manifest_test_count` | node has ≥ N tests attached |
| `manifest_source_declared` | source block exists in manifest |
| `manifest_exposure_exists` | exposure node exists |
| `duckdb_query` | run SQL against `dev.duckdb`, assert row count / value matches |
| `duckdb_table_exists` | table/view present in DuckDB catalog |
| `run_results_node_status` | `target/run_results.json` shows node status `success` |
| `incremental_row_growth` | run twice, assert row count grew (or didn't, depending) |

Checks run as plain subprocesses on the host (no container hop) — students
have already installed `dbt-core` and `dbt-duckdb` into their local venv via
`uv pip install -e .`.

### 3. `FileVerifier` (port from `learn_spark`) — `verifier/file.py`

Asserts a file exists with optional `min_bytes`. Used for "did you create
`dbt_project.yml`?"-style exercises.

### `VERIFIER_REGISTRY` in `cli/main.py`

```python
VERIFIER_REGISTRY = {
    "local": LocalVerifier,
    "dbt":   DbtVerifier,
    "file":  FileVerifier,
}
```

---

## Local setup (no Docker)

DuckDB is an embedded, in-process database — there's nothing to run as a
service, so the course skips Docker entirely and runs everything on the host.

**One-time setup** (documented in README, mirrors the `learn_spark` pattern):

```bash
uv venv
source .venv/bin/activate
uv pip install -e .   # installs dbt-core, dbt-duckdb, the CLI, and engine deps
```

After install, students run `dbt-learn` directly — `pyproject.toml` exposes
the `dbt-learn = "cli.main:app"` entry point, so the venv puts a real
`dbt-learn` binary on `PATH`. No `Dockerfile`, no `docker-compose.yml`, no
shell wrapper.

The course ships a pre-scaffolded dbt project at `<repo>/dbt_project/` with:

- `dbt_project.yml` (minimal)
- `profiles.yml` (DuckDB target → `<repo>/database/dev.duckdb`; uses
  `DBT_PROFILES_DIR` pointed at the project dir, or relies on dbt's default
  search path)
- `seeds/raw_*.csv` (jaffle_shop)
- `models/` (empty — students fill it in)
- `macros/`, `tests/`, `snapshots/`, `analyses/` (empty)

Each exercise's `original/` scaffold contains the SQL/YAML file the student
must complete; the `exercise/` copy is identical and is what the student
edits. Verification runs dbt commands as a plain subprocess against this
project (`subprocess.run(["dbt", "run", "--select", model], cwd=dbt_project)`).

Reset extension in `cli/main.py`:

- `shutil.rmtree(dbt_project/target)`
- `shutil.rmtree(dbt_project/dbt_packages)` (if present)
- delete `database/dev.duckdb`
- run `dbt seed` to repopulate raw tables

---

## Curriculum — 7 stages, ~42 items

Naming convention follows `learn_spark`: numeric ID prefix on lessons
(`welcome`), slug on exercises. Folder layout: `lessons/stage{N}/`,
`exercises/stage{N}/`, etc.

> **Legend:** L = pure lesson · X = exercise · each stage ends with a quiz

---

### Stage 0 — Foundations (concept-only, no dbt yet) · 6 items

Maps to `notion_dbt_series/01-dbt-100-foundations.md`. All lessons; quiz tests
conceptual understanding.

| # | id | type | what it teaches |
|---|---|---|---|
| 1 | `welcome` | L | What this course is, how the CLI works, prereqs |
| 2 | `etl_vs_elt` | L | ETL vs ELT, why the shift, cost / scalability / governance |
| 3 | `modern_data_team` | L | Data engineer / analytics engineer / data analyst roles |
| 4 | `cloud_data_warehouses` | L | Snowflake, BigQuery, Redshift, Databricks, DuckDB |
| 5 | `what_is_dbt` | L | Why dbt, the modern data stack, where dbt fits |
| 6 | `dbt_flavors` | L | dbt Core vs dbt Cloud vs dbt Fusion (Rust engine) — when to use which |

**Quiz `quiz/stage0.yaml`:** ETL vs ELT, role definitions, dbt's place in the
stack, when to pick Cloud vs Core vs Fusion.

---

### Stage 1 — Your First dbt Project · 6 items

Maps to `02-dbt-101-fundamental.md`. Student builds a real dbt project from
scratch — `dbt init` to first running model. **No bundled `dbt_project/`** —
the learner creates and configures every piece. The repo ships only the raw
CSVs in `data/`; everything under `dbt_project/` is learner-generated and
gitignored.

| # | id | type | verifier | what it teaches |
|---|---|---|---|---|
| 1 | `dbt_install` | L | — | What dbt-core + dbt-duckdb are, where they live in your venv, what `dbt --version` shows |
| 2 | `dbt_init` | X | file (`dbt_project/dbt_project.yml`) | Run `dbt init dbt_project` to scaffold a fresh project; understand the directory layout it generates |
| 3 | `profiles_yml` | X | dbt (`dbt_debug_success`) | Write `dbt_project/profiles.yml` pointing at a local DuckDB file; `dbt debug` connects |
| 4 | `dbt_seed` | X | dbt (`dbt_seed_success`, `duckdb_table_exists` × 3) | Copy the raw CSVs from `data/` into `dbt_project/seeds/`; run `dbt seed`; verify 3 raw tables exist in DuckDB |
| 5 | `first_model` | X | dbt (`dbt_run_success`, `duckdb_table_exists`) | Write `models/staging/stg_customers.sql` using `{{ ref('raw_customers') }}`; `dbt run --select stg_customers`; verify table |
| 6 | `project_yml` | X | dbt (`manifest_materialization`) | Configure `dbt_project.yml` so models in `staging/` materialize as views by default |

**Quiz `quiz/stage1.yaml`:** what `dbt init` creates, what `profiles.yml`
configures, `ref()` vs raw table names, `dbt seed` vs `dbt run`, where output
lands in DuckDB, view vs table materialization.

**Engine changes Stage 1 needs:**

- Add `dbt_project/` to `.gitignore` (learner-generated; reset wipes it)
- Extend `cli/main.py reset()` to `rm -rf dbt_project/` (so learner can start over cleanly); skip `dbt seed` when the project doesn't exist
- New `DbtVerifier` rule types: `dbt_debug_success`, `dbt_seed_success`, `duckdb_table_exists`, `manifest_materialization`
- `duckdb_table_exists` queries `database/dev.duckdb` directly via the `duckdb` Python package (already in `pyproject.toml`)
- Exercise scaffold pattern for "run-a-command" items: a `.md` instructions file in `exercises/stage1/<id>.md` that the learner reads (no edits); the verifier checks the resulting side effect, not the file

---

### Stage 2 — Sources, Refs & Project Structure · 6 items

Continues `02-dbt-101-fundamental.md` (sources, naming conventions,
`dbt build`, `dbt docs`).

| # | id | type | verifier | what it teaches |
|---|---|---|---|---|
| 1 | `20_naming_conventions` | L | — | `src_` / `stg_` / `int_` / `fct_` / `dim_` and the staging→marts pattern |
| 2 | `21_sources_yml` | X | dbt (`manifest_source_declared`) | Declare the three raw tables in `models/sources.yml` |
| 3 | `22_staging_models` | X | dbt | Build `stg_orders` and `stg_payments` using `source()` |
| 4 | `23_marts_layer` | X | dbt | Build `fct_orders` joining the three staging models |
| 5 | `24_dbt_build` | X | dbt (`dbt_build_success`) | One command runs seeds + models + tests |
| 6 | `25_dbt_docs` | X | dbt + file (`target/manifest.json`, `target/catalog.json`) | Generate docs, verify artifacts exist |

**Quiz `quiz/stage2.yaml`:** `ref()` vs `source()`, why staging vs marts, what
`dbt build` does that `dbt run` doesn't.

---

### Stage 3 — Tests, Seeds & Analyses · 5 items

Maps to `03-dbt-102-analyses-and-seeds.md` plus the testing chapter from
Fundamentals.

| # | id | type | verifier | what it teaches |
|---|---|---|---|---|
| 1 | `30_generic_tests` | X | dbt (`manifest_test_count`, `dbt_test_success`) | Add `not_null`, `unique` to `stg_customers.customer_id` |
| 2 | `31_relationships_test` | X | dbt | Add `relationships` test on `fct_orders.customer_id` → `stg_customers` |
| 3 | `32_singular_test` | X | dbt | Write a custom singular SQL test in `tests/` |
| 4 | `33_seed_config` | X | dbt | Configure `seeds:` in `dbt_project.yml` (column types, schema) |
| 5 | `34_analyses` | X | dbt + file | Add an analysis SQL file, verify `dbt compile` produces output |

**Quiz `quiz/stage3.yaml`:** generic vs singular tests, when to use seeds vs
sources, what `dbt compile` does without running.

---

### Stage 4 — Materializations · 6 items

Maps to `04-dbt-201-materialization.md`, `05-dbt-202-incremental-model.md`,
`06-dbt-203-snapshots.md`.

| # | id | type | verifier | what it teaches |
|---|---|---|---|---|
| 1 | `40_materialization_overview` | L | — | View / table / ephemeral / materialized_view / incremental — pros / cons table |
| 2 | `41_view_to_table` | X | dbt (`manifest_materialization=table`) | Switch `fct_orders` to a table |
| 3 | `42_ephemeral` | X | dbt (`manifest_materialization=ephemeral`) | Make `int_orders_pivoted` ephemeral; verify it inlines as a CTE |
| 4 | `43_incremental_basic` | X | dbt + `incremental_row_growth` | Build an incremental model with `is_incremental()` filter on `event_time` |
| 5 | `44_incremental_merge` | X | dbt | Add `unique_key` and `incremental_strategy='merge'`; assert no dupes after re-run |
| 6 | `45_snapshot_scd2` | X | dbt (`dbt_snapshot_success`, `duckdb_query`) | Snapshot `stg_customers` with `strategy='check'`; verify `dbt_valid_from` / `dbt_valid_to` columns |

**Quiz `quiz/stage4.yaml`:** when to use each materialization, what
`is_incremental()` returns on first run, SCD2 vs SCD1.

---

### Stage 5 — Jinja, Macros & State · 5 items

Maps to `08-dbt-302-jinja-and-macros.md`, `07-dbt-301-state.md`,
`09-dbt-303-exposure.md`.

| # | id | type | verifier | what it teaches |
|---|---|---|---|---|
| 1 | `50_jinja_basics` | L | — | `{% %}` vs `{{ }}` vs `{# #}`, control flow, whitespace |
| 2 | `51_first_macro` | X | dbt + `duckdb_query` | Write `cents_to_dollars(col)` macro, use in `fct_orders` |
| 3 | `52_dbt_utils` | X | dbt + file (`packages.yml`, `dbt_packages/`) | Install `dbt_utils`, use `dbt_utils.surrogate_key()` |
| 4 | `53_state_selection` | X | dbt | Modify a model, run `dbt run --select state:modified+ --state ./prev_target` and verify only the changed node + downstream ran |
| 5 | `54_exposures` | X | dbt (`manifest_exposure_exists`) | Declare a downstream BI dashboard exposure on `fct_orders` |

**Quiz `quiz/stage5.yaml`:** Jinja delimiters, macro reuse, what
`state:modified+` selects, why exposures matter.

---

### Stage 6 — Advanced Testing, Deployment, Tooling & Artifacts · 10 items

Combined stage covering everything past the core workflow: advanced tests,
deployment / refactoring, the dbt CLI surface, the `target/` directory, dbt
Fusion, and MetricFlow.

Maps to `10-dbt-401-advance-testing.md`, `11-dbt-402-advance-deployment.md`,
`12-dbt-403-clone.md`, `13-dbt-404-refactoring.md`,
`14-dbt-406-grants-and-retry.md`, `15-dbt-500-command.md`,
`16-dbt-501-target-directory.md`, `17-setup-dbt-mcp.md`,
`18-dbt-601-fusion-vscode.md`, `19-dbt-602-metricflow.md`.

| # | id | type | verifier | what it teaches |
|---|---|---|---|---|
| 1 | `60_advanced_tests` | X | dbt (`manifest_test_count`, store_failures audit) | `severity: warn`, `where:`, `limit:`, `--store-failures` |
| 2 | `61_dbt_expectations` | X | dbt | Install `dbt_expectations`, add `expect_column_values_to_be_between` |
| 3 | `62_refactoring` | X | dbt + `duckdb_query` | Refactor a legacy hardcoded SQL into staging + marts; final query results must match the legacy output |
| 4 | `63_dbt_clone` | X | dbt | Practice `dbt clone --select state:modified+` (simulated dev / prod targets in the same DuckDB file with different schemas) |
| 5 | `64_retry` | X | dbt | Introduce a deliberately failing test, run `dbt build`, then `dbt retry` after fix; assert retry skipped previously-successful nodes |
| 6 | `65_commands_tour` | L | — | `dbt parse`, `dbt ls`, `dbt show`, `dbt source freshness` — when to reach for each |
| 7 | `66_target_directory` | X | file | Inspect `target/` after a build; identify each artifact's role |
| 8 | `67_dbt_show` | X | dbt | Use `dbt show --select fct_orders --limit 5` to preview output |
| 9 | `68_fusion_intro` | L | — | dbt Fusion (Rust) vs Core, VS Code extension features, why it matters |
| 10 | `69_metricflow_basic` | X | dbt | Define a simple semantic model + metric on `fct_orders`, run `dbt sl query` |

**Quiz `quiz/stage6.yaml`:** severity vs error, when to use `dbt clone`, what
makes a refactor safe (audit_helper concept), what `dbt retry` resumes from,
what each `target/` artifact is for, Fusion vs Core differences, what a metric
defines.

---

## Lesson authoring workflow

Per the template's README rules:

- Author lesson source as `lessons/stage{N}/<id>.md` (gitignored).
- Run `python3 build_lessons.py` to produce `lessons/stage{N}/<id>.html` (committed).
- Lessons stay under ~300 lines; each ends with 1–2 common pitfalls.
- Cross-link to the user's existing `notion_dbt_series/` post in the lesson
  footer ("further reading").

---

## Critical files to create / modify

### Modify

- `pyproject.toml` — set `name = "dbt-learn"`, entry point `dbt-learn = "cli.main:app"`, dependencies (`dbt-core`, `dbt-duckdb`, `duckdb`, plus engine deps)
- `cli/main.py` — `COURSE_NAME`, `COURSE_EMOJI`, register `DbtVerifier` and `FileVerifier`, extend `reset()` to wipe `target/` and `dev.duckdb`; strip any `docker exec` plumbing from `LocalVerifier` (run pytest in-process via `subprocess.run([sys.executable, "-m", "pytest", ...])`)
- `curriculum.yaml` — replace skeleton with the 7-stage structure above
- `README.md` — rewrite per template spec
- `.gitignore` — add `lessons/**/*.md`, `dbt_project/`, `database/*.duckdb`, `database/*.duckdb.wal`

### Create

- `verifier/dbt.py` — `DbtVerifier` with all rule-type helpers
- `verifier/file.py` — port from `learn_spark/verifier/file.py`
- `dbt_project/dbt_project.yml`, `dbt_project/profiles.yml`
- `dbt_project/seeds/raw_customers.csv`, `raw_orders.csv`, `raw_payments.csv` (jaffle_shop)
- `lessons/stage{0..6}/*.html` (~30 lessons total)
- `exercises/stage{1..6}/*.{sql,yml,py}` + matching `originals/` scaffolds (~30 exercises)
- `tests/stage{1..6}/test_*.py` for any local-verified items
- `hints/stage{1..6}/*.md` (~30 hint files, 2–4 hints each)
- `quiz/stage{0..6}.yaml` (7 stage-end quizzes)
- `build_lessons.py` (dev-only script, gitignored)

### Delete

- `Dockerfile`, `docker-compose.yml` — not used; everything runs locally
- `lessons/Untitled` (orphan)
- `lessons/hello_pipeline.html`, `exercises/hello_pipeline.py`, `originals/hello_pipeline.py`, `tests/test_hello_pipeline.py`, `hints/hello_pipeline.md`, `quiz/hello_pipeline.yaml`

### Reuse from existing template

- `verifier/base.py` — interface unchanged
- `verifier/local.py` — reuse for any pure-Python exercises
- `cli/curriculum.py`, `cli/state.py` — generic, no changes
- `quiz/loader.py`, `quiz/runner.py` — generic, no changes

### Reuse from `learn_spark`

- `verifier/file.py` — port directly
- `build_lessons.py` — port directly
- Cluster verifier's "rule dispatch" pattern — model `DbtVerifier` on the same `_check_*` helper structure

---

## Phased build (for the follow-up implementation session)

Each phase ends with a working `dbt-learn` CLI so we never accumulate broken
state:

1. **Phase A — Plumbing** (no content): delete `Dockerfile` / `docker-compose.yml`, rewrite `pyproject.toml` for dbt-learn with the entry-point script, scaffold `dbt_project/` with jaffle_shop seeds, run `dbt seed` locally to confirm the connection, scaffold `DbtVerifier` skeleton with one rule (`dbt_run_success`).
2. **Phase B — Stage 1 end-to-end**: build all 6 Stage 1 items; the `dbt_seed` and `first_model` exercises must verify cleanly. This is the gate — if the verifier design is wrong, fix it now before writing more content.
3. **Phase C — Stage 0**: write the 6 concept lessons (no exercises, fastest stage to ship).
4. **Phase D — Stages 2 → 6**: one stage per session, in order. Add new `DbtVerifier` rule types as exercises demand them.
5. **Phase E — Quizzes**: write all 7 quiz YAMLs in one pass once content is stable.
6. **Phase F — Polish**: README rewrite, reset cleanup, run a fresh student walkthrough end-to-end.

**Out of scope for v1** (defer to v2 if requested):

- A separate Snowflake / BigQuery target option (DuckDB only)
- dbt Cloud-specific exercises (Cloud is taught conceptually in Stage 0, not hands-on)
- MetricFlow beyond a single trivial metric (Stage 6 has one exercise; deeper Semantic Layer is a future stage)

---

## Verification (how we'll know each phase works)

For every exercise we ship:

- Run `dbt-learn` from a clean checkout.
- Navigate to the exercise. Press `v` on the *unedited* scaffold — must fail with a clear, learner-friendly message naming what's missing.
- Implement the solution. Press `v` again — must pass.
- Press `n` — must advance.
- Run `dbt-learn reset` — must restore the scaffold and wipe DuckDB state so the next attempt is clean.

Stage-level smoke test:

- After each stage is built, run `dbt-learn list` to confirm all items appear.
- Walk a fresh student profile through the entire stage in one sitting (~20 min) and note any verifier message that's confusing.
