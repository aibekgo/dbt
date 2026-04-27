from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""


@dataclass
class VerifyResult:
    exercise_path: str
    syntax_ok: bool
    syntax_error: str = ""
    tests: list[TestResult] = field(default_factory=list)
    extra: str | None = None  # optional display text shown after test results

    @property
    def passed(self) -> bool:
        return self.syntax_ok and all(t.passed for t in self.tests)

    @property
    def failed_tests(self) -> list[TestResult]:
        return [t for t in self.tests if not t.passed]


class BaseVerifier(ABC):
    @abstractmethod
    def verify(self, exercise_path: str) -> VerifyResult:
        """Run all checks for the given exercise file and return a VerifyResult."""
        ...
