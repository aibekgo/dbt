# Learn dbt

An interactive, rustlings-style CLI for learning dbt — hands-on exercises with instant feedback against an embedded DuckDB warehouse. No cloud account, no Docker.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [VSCode](https://code.visualstudio.com/) (recommended editor)
- Python 3.11+

## Setup

**1. Clone the repo and open it in VSCode.**

**2. Set up your Python environment:**

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

The CLI runs everything locally. dbt commands execute on your host against the embedded DuckDB file at `dbt_project/dev.duckdb`. Progress is saved to `progress.txt` in your workspace.

## Interactive session

Once inside, navigate with single-key commands:

**Lessons:**

| Key | Action |
|-----|--------|
| `l` | Open the lesson in browser |
| `n` | Advance to next item |
| `q` | Quit |

**Exercises:**

| Key | Action |
|-----|--------|
| `l` | Open the associated lesson in browser |
| `v` | Verify your solution (output is shown inline) |
| `h` | Show hints |
| `n` | Advance (must pass verification first) |
| `x` | Reset the current exercise back to its scaffold |
| `q` | Quit |

## CLI commands (non-interactive)

```bash
dbt-learn          # launch interactive session
dbt-learn list     # list all curriculum items and their status
dbt-learn reset    # reset progress, restore exercise scaffolds, wipe DuckDB and re-seed
```

## How exercises work

Each curriculum item is either a **lesson** or an **exercise**.

- **Lessons** — press `l` to open in browser, then `n` to advance.
- **Exercises** — press `l` to open the lesson first, edit the exercise file the CLI points you at, then press `v` to verify. The verifier runs `dbt` for real and inspects `target/manifest.json`, `run_results.json`, and the DuckDB warehouse to confirm correctness. Fix any failures and verify again — press `n` to advance once all checks pass.

The dbt project lives at `dbt_project/`. The `jaffle_shop` raw CSVs (`raw_customers`, `raw_orders`, `raw_payments`) ship in `dbt_project/seeds/` and load into DuckDB on first run.
