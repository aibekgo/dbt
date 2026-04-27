"""DbtVerifier — runs dbt commands against the bundled DuckDB project and checks results.

Each exercise declares its verification rules in curriculum.yaml under
`dbt_checks`. This verifier dispatches each rule by `type` to a `_check_*`
helper. Add new rule types by writing a new helper and registering it in
RULE_HANDLERS at the bottom of this file.

Currently implemented rule types:
  - dbt_run_success: `dbt run --select <model>` exits 0

Planned rule types (added per-stage as needed):
  - dbt_test_success, dbt_seed_success, dbt_snapshot_success, dbt_build_success
  - manifest_node_exists, manifest_materialization, manifest_test_count,
    manifest_source_declared, manifest_exposure_exists
  - duckdb_query, duckdb_table_exists
  - run_results_node_status, incremental_row_growth
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

from .base import BaseVerifier, TestResult, VerifyResult

ROOT = Path(os.environ.get("COURSE_ROOT", Path(__file__).parent.parent))
CURRICULUM_PATH = ROOT / "curriculum.yaml"
DBT_PROJECT_DIR = ROOT / "dbt_project"


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


# ---------------------------------------------------------------------------
# Rule handlers — each returns a list[TestResult]
# ---------------------------------------------------------------------------

def _check_dbt_run_success(rule: dict) -> list[TestResult]:
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


def _tail(text: str, lines: int = 20) -> str:
    parts = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(parts[-lines:])


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

RuleHandler = Callable[[dict], list[TestResult]]

RULE_HANDLERS: dict[str, RuleHandler] = {
    "dbt_run_success": _check_dbt_run_success,
    # add more rule types here as exercises start needing them
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
