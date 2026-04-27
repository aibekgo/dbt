## Hint 1

If `dbt --version` says "command not found", the issue is your shell. The `dbt` binary lives inside `.venv/bin/`, which your shell only sees once the venv is activated.

## Hint 2

From the repo root:

```bash
source .venv/bin/activate
which dbt
```

`which dbt` should print a path that ends in `.../learn_dbt/.venv/bin/dbt`. If it prints something else (like `/usr/local/bin/dbt` or a `pyenv` shim), the wrong dbt is on your `PATH` — the venv isn't first. Re-run `source .venv/bin/activate`.

## Hint 3

Still stuck? Re-install course dependencies into the venv:

```bash
source .venv/bin/activate
uv pip install -e .
dbt --version
```

You should see the `Core` and `Plugins` blocks, with `duckdb` listed.
