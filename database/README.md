# Local DuckDB warehouse

The dbt project writes its DuckDB file (`dev.duckdb`) here. The actual file is gitignored — only this README is tracked, so the directory exists in fresh clones.

To inspect the warehouse from the repo root:

```bash
duckdb database/dev.duckdb -c "SHOW TABLES"
```

To wipe the warehouse without touching your dbt project files:

```bash
rm -f database/dev.duckdb
```
