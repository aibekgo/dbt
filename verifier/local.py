"""LocalVerifier — syntax check + pytest, run in-process on the host.

For pure-Python exercises that don't need to call dbt. Most dbt exercises use
DbtVerifier instead.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import yaml

from .base import BaseVerifier, TestResult, VerifyResult

ROOT = Path(os.environ.get("COURSE_ROOT", Path(__file__).parent.parent))
CURRICULUM_PATH = ROOT / "curriculum.yaml"


def _find_test_relative(exercise_path: str) -> str | None:
    exercise = Path(exercise_path).resolve()
    with open(CURRICULUM_PATH) as f:
        curriculum = yaml.safe_load(f)
    for stage in curriculum.get("stages", []):
        for item in stage.get("items", []):
            if item.get("type") != "exercise":
                continue
            if (ROOT / item["exercise"]).resolve() == exercise:
                return item.get("test")
    return None


def _check_syntax(exercise_path: str) -> tuple[bool, str]:
    try:
        ast.parse(Path(exercise_path).read_text())
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError on line {e.lineno}: {e.msg}"


def _run_pytest(test_relative: str) -> tuple[list[TestResult], str | None]:
    test_path = str(ROOT / test_relative)
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path,
         "-v", "--tb=short", "--no-header", "--capture=no"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
    )
    return _parse_pytest_output(result.stdout + result.stderr)


def _parse_pytest_output(output: str) -> tuple[list[TestResult], str | None]:
    results = []
    output_lines = []
    last_test_name = None
    for line in output.splitlines():
        if "OUTPUT:" in line:
            output_lines.append(line[line.index("OUTPUT:") + len("OUTPUT:"):].strip())
        if "::" in line:
            name = line.split("::")[1].split(" ")[0]
            last_test_name = name
            if " PASSED" in line:
                results.append(TestResult(name=name, passed=True))
                last_test_name = None
            elif " FAILED" in line:
                results.append(TestResult(name=name, passed=False))
                last_test_name = None
            elif " ERROR" in line:
                results.append(TestResult(name=name, passed=False, message="collection error"))
                last_test_name = None
        elif line.strip() == "PASSED" and last_test_name:
            results.append(TestResult(name=last_test_name, passed=True))
            last_test_name = None
        elif line.strip() == "FAILED" and last_test_name:
            results.append(TestResult(name=last_test_name, passed=False))
            last_test_name = None
    extra = "\n".join(output_lines) if output_lines else None
    return results, extra


class LocalVerifier(BaseVerifier):
    """Syntax check + pytest run in-process."""

    def verify(self, exercise_path: str) -> VerifyResult:
        syntax_ok, syntax_error = _check_syntax(exercise_path)
        if not syntax_ok:
            return VerifyResult(exercise_path=exercise_path, syntax_ok=False, syntax_error=syntax_error)

        test_relative = _find_test_relative(exercise_path)
        if test_relative is None:
            return VerifyResult(
                exercise_path=exercise_path,
                syntax_ok=True,
                syntax_error="No test file found for this exercise in curriculum.yaml",
            )

        tests, extra = _run_pytest(test_relative)
        return VerifyResult(exercise_path=exercise_path, syntax_ok=True, tests=tests, extra=extra)
