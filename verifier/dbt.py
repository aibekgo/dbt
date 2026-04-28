"""DbtVerifier — runs dbt commands against the learner's DuckDB project and checks results.

Each exercise declares its verification rules in curriculum.yaml under
`dbt_checks`. This verifier dispatches each rule by `type` to a `_check_*`
helper. Add new rule types by writing a new helper and registering it in
RULE_HANDLERS at the bottom of this file.

Currently implemented rule types:
  - dbt_installed: `dbt --version` runs and the duckdb adapter is loaded
  - dbt_debug_success: `dbt debug` exits 0
  - dbt_seed_success: `dbt seed` exits 0 (optional `select` to scope)
  - dbt_run_success: `dbt run --select <model>` exits 0
  - dbt_build_success: `dbt build` (optionally scoped) exits 0 and every
    node in target/run_results.json shows status=success
  - dbt_docs_generated: `dbt docs generate` exits 0 and target/manifest.json
    + target/catalog.json were regenerated this run
  - duckdb_table_exists: query dev.duckdb's information_schema for the table
  - duckdb_query: run a SQL query and assert `expected_rows` (the count) or
    `expected_value` (the first scalar). The SQL itself goes in the rule.
  - manifest_materialization: parse target/manifest.json, check node
    materialized=<expected>
  - manifest_source_declared: parse target/manifest.json, assert a source
    block named `<source>` declares each table in `<tables>`.

Planned (added per-stage as needed):
  - dbt_test_success, dbt_snapshot_success
  - manifest_node_exists, manifest_test_count, manifest_exposure_exists
  - run_results_node_status, incremental_row_growth
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

from .base import BaseVerifier, TestResult, VerifyResult

ROOT = Path(os.environ.get("COURSE_ROOT", Path(__file__).parent.parent))
CURRICULUM_PATH = ROOT / "curriculum.yaml"
DBT_PROJECT_DIR = ROOT / "dbt_project"
DUCKDB_PATH = ROOT / "database" / "dev.duckdb"
MANIFEST_PATH = DBT_PROJECT_DIR / "target" / "manifest.json"
CATALOG_PATH = DBT_PROJECT_DIR / "target" / "catalog.json"
RUN_RESULTS_PATH = DBT_PROJECT_DIR / "target" / "run_results.json"


def _project_missing_result(name: str) -> list[TestResult]:
    return [TestResult(
        name=name,
        passed=False,
        message=(
            f"`dbt_project/` doesn't exist yet — run `dbt init dbt_project` "
            "from the repo root first."
        ),
    )]


# ---------------------------------------------------------------------------
# Curriculum lookup
# ---------------------------------------------------------------------------

def _find_dbt_checks(item_path: str) -> dict | None:
    """Return the `dbt_checks` block for the curriculum item matching this path."""
    resolved = Path(item_path).resolve()
    with open(CURRICULUM_PATH) as f:
        curriculum = yaml.safe_load(f)
    for stage in curriculum.get("stages", []):
        for item in stage.get("items", []):
            candidate = item.get("exercise") or item.get("file")
            if not candidate:
                continue
            if (ROOT / candidate).resolve() == resolved:
                return item.get("dbt_checks")
    return None


# ---------------------------------------------------------------------------
# dbt subprocess runner
# ---------------------------------------------------------------------------

@dataclass
class DbtRun:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _run_dbt(*args: str) -> DbtRun:
    """Run `dbt <args>` inside dbt_project/ and capture its output."""
    cmd = ["dbt", *args]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(DBT_PROJECT_DIR),
        env={**os.environ, "DBT_PROFILES_DIR": str(DBT_PROJECT_DIR)},
    )
    return DbtRun(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def _run_dbt_anywhere(*args: str) -> DbtRun:
    """Run `dbt <args>` from the repo root — for checks that don't need a project (e.g. --version)."""
    cmd = ["dbt", *args]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    return DbtRun(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


# ---------------------------------------------------------------------------
# Rule handlers — each returns a list[TestResult]
# ---------------------------------------------------------------------------

def _check_dbt_installed(rule: dict) -> list[TestResult]:
    """`dbt --version` exits 0 and the duckdb adapter is loaded."""
    try:
        run = _run_dbt_anywhere("--version")
    except FileNotFoundError:
        return [TestResult(
            name="dbt installed",
            passed=False,
            message=(
                "`dbt` command not found. Activate your virtualenv with "
                "`source .venv/bin/activate` and try again."
            ),
        )]
    output = run.stdout + run.stderr
    if not run.ok:
        return [TestResult(
            name="dbt --version",
            passed=False,
            message=_tail(output, lines=15),
        )]
    has_duckdb = "duckdb" in output.lower()
    return [
        TestResult(
            name="dbt --version exits 0",
            passed=True,
            message=_tail(output, lines=8),
        ),
        TestResult(
            name="dbt-duckdb adapter loaded",
            passed=has_duckdb,
            message="" if has_duckdb else (
                "dbt is installed but the duckdb plugin isn't listed. "
                "Run `uv pip install -e .` from the repo root."
            ),
        ),
    ]


def _check_dbt_run_success(rule: dict) -> list[TestResult]:
    if not DBT_PROJECT_DIR.exists():
        return _project_missing_result("dbt_run_success")
    select = rule.get("select", "")
    if not select:
        return [TestResult(
            name="dbt_run_success",
            passed=False,
            message="rule is missing required `select` field",
        )]
    run = _run_dbt("run", "--select", select)
    return [TestResult(
        name=f"dbt run --select {select}",
        passed=run.ok,
        message="" if run.ok else _tail(run.stdout + run.stderr, lines=20),
    )]


def _check_dbt_debug_success(rule: dict) -> list[TestResult]:
    if not DBT_PROJECT_DIR.exists():
        return _project_missing_result("dbt_debug_success")
    run = _run_dbt("debug")
    return [TestResult(
        name="dbt debug",
        passed=run.ok,
        message="" if run.ok else _tail(run.stdout + run.stderr, lines=25),
    )]


def _check_dbt_seed_success(rule: dict) -> list[TestResult]:
    if not DBT_PROJECT_DIR.exists():
        return _project_missing_result("dbt_seed_success")
    args = ["seed"]
    select = rule.get("select")
    if select:
        args += ["--select", select]
    run = _run_dbt(*args)
    label = "dbt seed" + (f" --select {select}" if select else "")
    return [TestResult(
        name=label,
        passed=run.ok,
        message="" if run.ok else _tail(run.stdout + run.stderr, lines=20),
    )]


def _check_duckdb_table_exists(rule: dict) -> list[TestResult]:
    table = rule.get("table")
    if not table:
        return [TestResult(
            name="duckdb_table_exists",
            passed=False,
            message="rule is missing required `table` field",
        )]
    if not DUCKDB_PATH.exists():
        return [TestResult(
            name=f"duckdb_table_exists:{table}",
            passed=False,
            message=(
                f"DuckDB file not found at {DUCKDB_PATH.relative_to(ROOT)}. "
                "Did `dbt seed` / `dbt run` complete successfully?"
            ),
        )]
    try:
        import duckdb
    except ImportError:
        return [TestResult(
            name=f"duckdb_table_exists:{table}",
            passed=False,
            message="duckdb python package not installed",
        )]
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    try:
        rows = con.execute(
            "select table_schema from information_schema.tables where table_name = ?",
            [table],
        ).fetchall()
    finally:
        con.close()
    if rows:
        schemas = ", ".join(sorted({r[0] for r in rows}))
        return [TestResult(
            name=f"duckdb_table_exists:{table}",
            passed=True,
            message=f"found in schema(s): {schemas}",
        )]
    return [TestResult(
        name=f"duckdb_table_exists:{table}",
        passed=False,
        message=f"table '{table}' not found in any schema in dev.duckdb",
    )]


def _check_manifest_materialization(rule: dict) -> list[TestResult]:
    model = rule.get("model")
    expected = rule.get("expected")
    if not model or not expected:
        return [TestResult(
            name="manifest_materialization",
            passed=False,
            message="rule needs both `model` and `expected` fields",
        )]
    if not DBT_PROJECT_DIR.exists():
        return _project_missing_result("manifest_materialization")
    # Refresh the manifest so we read the current project state
    parse = _run_dbt("parse")
    if not parse.ok:
        return [TestResult(
            name="dbt parse",
            passed=False,
            message=_tail(parse.stdout + parse.stderr, lines=20),
        )]
    if not MANIFEST_PATH.exists():
        return [TestResult(
            name="manifest_materialization",
            passed=False,
            message=f"manifest.json not found at {MANIFEST_PATH.relative_to(ROOT)}",
        )]
    manifest = json.loads(MANIFEST_PATH.read_text())
    for node in manifest.get("nodes", {}).values():
        if node.get("name") == model and node.get("resource_type") == "model":
            actual = node.get("config", {}).get("materialized")
            return [TestResult(
                name=f"materialization:{model}",
                passed=actual == expected,
                message="" if actual == expected else f"expected '{expected}', got '{actual}'",
            )]
    return [TestResult(
        name=f"materialization:{model}",
        passed=False,
        message=f"model '{model}' not found in manifest.json",
    )]


def _check_manifest_source_declared(rule: dict) -> list[TestResult]:
    """`<source>` is declared in `_sources.yml` with each table in `<tables>`."""
    source_name = rule.get("source")
    tables = rule.get("tables", [])
    if not source_name or not tables:
        return [TestResult(
            name="manifest_source_declared",
            passed=False,
            message="rule needs both `source` (str) and `tables` (list[str]) fields",
        )]
    if not DBT_PROJECT_DIR.exists():
        return _project_missing_result("manifest_source_declared")
    parse = _run_dbt("parse")
    if not parse.ok:
        return [TestResult(
            name="dbt parse",
            passed=False,
            message=_tail(parse.stdout + parse.stderr, lines=20),
        )]
    if not MANIFEST_PATH.exists():
        return [TestResult(
            name="manifest_source_declared",
            passed=False,
            message=f"manifest.json not found at {MANIFEST_PATH.relative_to(ROOT)}",
        )]
    manifest = json.loads(MANIFEST_PATH.read_text())
    declared: set[str] = set()
    for node in manifest.get("sources", {}).values():
        if node.get("source_name") == source_name:
            declared.add(node.get("name"))
    if not declared:
        return [TestResult(
            name=f"source:{source_name}",
            passed=False,
            message=(
                f"Source `{source_name}` not found in target/manifest.json — "
                f"check the `name:` field in models/staging/_sources.yml."
            ),
        )]
    missing = [t for t in tables if t not in declared]
    if missing:
        return [TestResult(
            name=f"source:{source_name} tables",
            passed=False,
            message=(
                f"Source `{source_name}` is declared but missing tables: "
                f"{', '.join(missing)}. Found: {', '.join(sorted(declared))}."
            ),
        )]
    return [TestResult(
        name=f"source:{source_name}",
        passed=True,
        message=f"declares {len(tables)} table(s): {', '.join(tables)}",
    )]


def _check_duckdb_query(rule: dict) -> list[TestResult]:
    """Run `sql` against dev.duckdb; assert `expected_rows` or `expected_value`."""
    sql = rule.get("sql")
    if not sql:
        return [TestResult(
            name="duckdb_query",
            passed=False,
            message="rule is missing required `sql` field",
        )]
    label = rule.get("name") or _short_sql(sql)
    if not DUCKDB_PATH.exists():
        return [TestResult(
            name=f"duckdb_query:{label}",
            passed=False,
            message=(
                f"DuckDB file not found at {DUCKDB_PATH.relative_to(ROOT)}. "
                "Run `dbt run` first so the model exists."
            ),
        )]
    try:
        import duckdb
    except ImportError:
        return [TestResult(
            name=f"duckdb_query:{label}",
            passed=False,
            message="duckdb python package not installed",
        )]
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    try:
        try:
            rows = con.execute(sql).fetchall()
        except Exception as e:
            return [TestResult(
                name=f"duckdb_query:{label}",
                passed=False,
                message=f"query failed: {e}",
            )]
    finally:
        con.close()

    if "expected_rows" in rule:
        expected = rule["expected_rows"]
        actual = len(rows)
        return [TestResult(
            name=f"duckdb_query:{label} row count",
            passed=actual == expected,
            message="" if actual == expected else (
                f"expected {expected} row(s), got {actual}"
            ),
        )]
    if "expected_value" in rule:
        expected = rule["expected_value"]
        if not rows:
            return [TestResult(
                name=f"duckdb_query:{label} value",
                passed=False,
                message=f"expected value {expected!r} but query returned no rows",
            )]
        actual = rows[0][0]
        return [TestResult(
            name=f"duckdb_query:{label} value",
            passed=actual == expected,
            message="" if actual == expected else f"expected {expected!r}, got {actual!r}",
        )]
    return [TestResult(
        name=f"duckdb_query:{label}",
        passed=False,
        message="rule needs either `expected_rows` (int) or `expected_value` (any)",
    )]


def _check_dbt_build_success(rule: dict) -> list[TestResult]:
    """`dbt build` exits 0 and every node in run_results.json has status=success."""
    if not DBT_PROJECT_DIR.exists():
        return _project_missing_result("dbt_build_success")
    args = ["build"]
    select = rule.get("select")
    if select:
        args += ["--select", select]
    run = _run_dbt(*args)
    label = "dbt build" + (f" --select {select}" if select else "")
    results: list[TestResult] = [TestResult(
        name=label,
        passed=run.ok,
        message="" if run.ok else _tail(run.stdout + run.stderr, lines=25),
    )]
    if not run.ok:
        return results
    if not RUN_RESULTS_PATH.exists():
        results.append(TestResult(
            name="run_results.json present",
            passed=False,
            message=f"{RUN_RESULTS_PATH.relative_to(ROOT)} missing after `dbt build`",
        ))
        return results
    run_results = json.loads(RUN_RESULTS_PATH.read_text())
    failures = [
        r for r in run_results.get("results", [])
        if r.get("status") not in ("success", "pass")
    ]
    if failures:
        names = ", ".join(r.get("unique_id", "?") for r in failures[:5])
        results.append(TestResult(
            name="all nodes success",
            passed=False,
            message=f"{len(failures)} node(s) did not succeed: {names}",
        ))
    else:
        n = len(run_results.get("results", []))
        results.append(TestResult(
            name="all nodes success",
            passed=True,
            message=f"all {n} node(s) succeeded",
        ))
    return results


def _check_dbt_docs_generated(rule: dict) -> list[TestResult]:
    """`dbt docs generate` exits 0 and manifest.json + catalog.json were touched."""
    if not DBT_PROJECT_DIR.exists():
        return _project_missing_result("dbt_docs_generated")
    start = time.time()
    run = _run_dbt("docs", "generate")
    results: list[TestResult] = [TestResult(
        name="dbt docs generate",
        passed=run.ok,
        message="" if run.ok else _tail(run.stdout + run.stderr, lines=25),
    )]
    if not run.ok:
        return results
    for path in (MANIFEST_PATH, CATALOG_PATH):
        rel = path.relative_to(ROOT)
        if not path.exists():
            results.append(TestResult(
                name=f"{rel} present",
                passed=False,
                message=f"{rel} not found after `dbt docs generate`",
            ))
            continue
        # Allow a 2s grace window — file mtimes can lag the captured `start`.
        fresh = path.stat().st_mtime + 2 >= start
        results.append(TestResult(
            name=f"{rel} regenerated",
            passed=fresh,
            message="" if fresh else (
                f"{rel} exists but wasn't updated by this run "
                f"(its mtime predates the dbt command)."
            ),
        ))
    return results


def _short_sql(sql: str, limit: int = 40) -> str:
    one_line = " ".join(sql.split())
    return one_line if len(one_line) <= limit else one_line[: limit - 1] + "…"


def _tail(text: str, lines: int = 20) -> str:
    parts = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(parts[-lines:])


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

RuleHandler = Callable[[dict], list[TestResult]]

RULE_HANDLERS: dict[str, RuleHandler] = {
    "dbt_installed":             _check_dbt_installed,
    "dbt_debug_success":         _check_dbt_debug_success,
    "dbt_seed_success":          _check_dbt_seed_success,
    "dbt_run_success":           _check_dbt_run_success,
    "dbt_build_success":         _check_dbt_build_success,
    "dbt_docs_generated":        _check_dbt_docs_generated,
    "duckdb_table_exists":       _check_duckdb_table_exists,
    "duckdb_query":              _check_duckdb_query,
    "manifest_materialization":  _check_manifest_materialization,
    "manifest_source_declared":  _check_manifest_source_declared,
}


# ---------------------------------------------------------------------------
# Verifier
# ---------------------------------------------------------------------------

class DbtVerifier(BaseVerifier):
    """Run dbt against the bundled DuckDB project and dispatch curriculum rules."""

    def verify(self, exercise_path: str) -> VerifyResult:
        checks = _find_dbt_checks(exercise_path)
        if checks is None:
            return VerifyResult(
                exercise_path=exercise_path,
                syntax_ok=True,
                syntax_error="No dbt_checks defined for this exercise in curriculum.yaml",
            )

        tests: list[TestResult] = []
        for rule in checks.get("rules", []):
            rule_type = rule.get("type")
            handler = RULE_HANDLERS.get(rule_type)
            if handler is None:
                tests.append(TestResult(
                    name=f"unknown rule: {rule_type}",
                    passed=False,
                    message=f"No handler registered for rule type {rule_type!r}",
                ))
                continue
            tests.extend(handler(rule))

        return VerifyResult(exercise_path=exercise_path, syntax_ok=True, tests=tests)
