"""FileVerifier — assert files / directories exist and meet a min-size threshold.

Reads `file_checks` from the matching curriculum.yaml item:

    - id: my_exercise
      type: exercise
      verifier: file
      file_checks:
        - path: dbt_project/target/manifest.json
          min_bytes: 100
"""

import os
from pathlib import Path

import yaml

from .base import BaseVerifier, TestResult, VerifyResult

ROOT = Path(os.environ.get("COURSE_ROOT", Path(__file__).parent.parent))
CURRICULUM_PATH = ROOT / "curriculum.yaml"


def _find_file_checks(item_path: str) -> list[dict] | None:
    resolved = Path(item_path).resolve()
    with open(CURRICULUM_PATH) as f:
        curriculum = yaml.safe_load(f)
    for stage in curriculum.get("stages", []):
        for item in stage.get("items", []):
            candidate = item.get("exercise") or item.get("file")
            if not candidate:
                continue
            if (ROOT / candidate).resolve() == resolved:
                return item.get("file_checks")
    return None


class FileVerifier(BaseVerifier):
    """Assert that required files / directories exist with optional minimum sizes."""

    def verify(self, exercise_path: str) -> VerifyResult:
        checks = _find_file_checks(exercise_path)
        if checks is None:
            return VerifyResult(
                exercise_path=exercise_path,
                syntax_ok=True,
                syntax_error="No file_checks defined for this exercise in curriculum.yaml",
            )

        tests: list[TestResult] = []
        for entry in checks:
            path = ROOT / entry["path"]
            min_bytes = entry.get("min_bytes", 0)

            if not path.exists():
                tests.append(TestResult(
                    name=f"exists:{path}",
                    passed=False,
                    message=f"Expected path does not exist: {path}",
                ))
                continue

            if path.is_dir():
                total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            else:
                total = path.stat().st_size

            size_ok = total >= min_bytes
            tests.append(TestResult(
                name=f"size:{path}",
                passed=size_ok,
                message="" if size_ok else (
                    f"{path}: {total:,} bytes found, need at least {min_bytes:,} bytes"
                ),
            ))

        return VerifyResult(exercise_path=exercise_path, syntax_ok=True, tests=tests)
