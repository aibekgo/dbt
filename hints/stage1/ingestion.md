## Hint 1

This isn't a dbt step. The script is a plain Python file that uses `duckdb` to write rows into `database/dev.duckdb`. From the repo root with the venv active:

```bash
python scripts/ingest_raw.py
```

That's it — no `cd dbt_project`, no `dbt` command.

## Hint 2

If you get `ModuleNotFoundError: No module named 'duckdb'`, your venv isn't active. From the repo root:

```bash
source .venv/bin/activate
which python  # should print a path inside .venv/bin
python scripts/ingest_raw.py
```

If `which python` prints a system path (e.g. `/usr/bin/python` or a `pyenv` shim), the venv didn't activate cleanly — re-run `source .venv/bin/activate`.

## Hint 3

If you see `IO Error: Could not set lock on file`, another process has `database/dev.duckdb` open. Common culprits:

- A `duckdb database/dev.duckdb` shell you opened to peek at the data — type `.exit` in it.
- A previous `dbt run`/`dbt debug` that crashed and left the file locked — close any leftover terminal and retry.

You can sanity-check with `lsof database/dev.duckdb` (macOS/Linux) to find the holder.
