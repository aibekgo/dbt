# Learn dbt

An interactive, rustlings-style CLI for learning dbt — hands-on exercises with instant feedback against an embedded DuckDB warehouse. No cloud account, no Docker.

## Before you start

dbt revolutionized the transformation layer of the modern data stack. It took
analytics out of the world of scattered, one-off SQL scripts and brought
software-engineering best practices to it: version control, branches and pull
requests, modular models, automated tests, lineage, and CI/CD. The course
assumes you're comfortable with the workflows dbt is built around — if any of
the points below feel shaky, brush up first or you'll spend more time fighting
the tooling than learning dbt itself.

- **Git** — you can clone a repo, create a branch, commit, push, and open a
  pull request without looking up the commands every time. dbt projects live
  in version control and every change is reviewed like application code.
- **SQL** — confident with `JOIN`s (inner / left / right / full),
  `GROUP BY` aggregations, CTEs, and window functions (`ROW_NUMBER`, `RANK`,
  `LAG`/`LEAD`, partitioned aggregates). This course teaches dbt mechanics,
  not SQL fundamentals.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [VSCode](https://code.visualstudio.com/) (recommended editor)
- Python 3.11+

## Setup

**1. Clone the repo, then `cd` into it and open it in VSCode:**

```bash
git clone <repo-url> learn_dbt
cd learn_dbt
code .
```

**2. Set up your Python environment from inside `learn_dbt/`:**

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

This installs `dbt-core`, `dbt-duckdb`, and the CLI itself in editable mode. After this completes, the `dbt-learn` command is available on your PATH (inside the venv).

**3. Point VSCode to the local interpreter:**

`Cmd+Shift+P` → "Python: Select Interpreter" → select `.venv`.

## Running

```bash
dbt-learn
```

The CLI runs everything locally. dbt commands execute on your host against the embedded DuckDB file at `database/dev.duckdb`. Progress is saved to `progress.txt` in your workspace.

## Interactive session

Once inside, navigate with single-key commands:

**Lessons:**

| Key | Action |
| --- | --- |
| `l` | Open the lesson in browser |
| `n` | Advance to next item |
| `p` | Go back to the previous item |
| `r` | Reset progress only (start over from item 1; keeps your `dbt_project/` and warehouse) |
| `q` | Quit |

**Exercises:**

| Key | Action |
| --- | --- |
| `l` | Open the associated lesson in browser |
| `v` | Verify your solution (output is shown inline) |
| `h` | Show hints |
| `n` | Advance (must pass verification first) |
| `p` | Go back to the previous item |
| `x` | Reset the current exercise file back to its scaffold |
| `r` | Reset progress only (start over from item 1; keeps your `dbt_project/` and warehouse) |
| `q` | Quit |

## CLI commands (non-interactive)

```bash
dbt-learn                  # launch interactive session
dbt-learn list             # list all curriculum items and their status
dbt-learn quiz             # run the full quiz across every stage
dbt-learn reset-progress   # reset progress only — keeps your dbt_project/ and DuckDB intact
dbt-learn reset            # ⚠️  DESTRUCTIVE: resets progress, restores all exercise files,
                           #    deletes dbt_project/ and database/*.duckdb*, and sends you back to stage 1.
                           #    The warehouse is empty afterwards — you'll re-run
                           #    `python scripts/ingest_raw.py` from the Stage 1 ingestion exercise.
```

## How exercises work

Each curriculum item is either a **lesson** or an **exercise**.

- **Lessons** — press `l` to open in browser, then `n` to advance.
- **Exercises** — press `l` to open the lesson first, edit the exercise file the CLI points you at, then press `v` to verify. The verifier runs `dbt` for real and inspects `target/manifest.json`, `run_results.json`, and the DuckDB warehouse to confirm correctness. Fix any failures and verify again — press `n` to advance once all checks pass.

The dbt project lives at `dbt_project/` — you'll create it yourself in Stage 1 with `dbt init`. The three `jaffle_shop` raw CSVs (`raw_customers`, `raw_orders`, `raw_payments`) live at `data/raw_*.csv` and are loaded into DuckDB by `scripts/ingest_raw.py`, which the Stage 1 ingestion exercise walks you through. We use a Python script (not `dbt seed`) on purpose — it mirrors how a real data team uses an ingestion tool like Fivetran or Airbyte for raw operational data, leaving `dbt seed` for what it's actually good at: small lookup tables (you'll meet that in Stage 3).
