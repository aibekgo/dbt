"""Load and expose curriculum items from curriculum.yaml."""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# COURSE_ROOT can be overridden via env var — useful inside Docker containers
# where the repo is mounted at a different path (e.g. /workspace).
ROOT = Path(os.environ.get("COURSE_ROOT", Path(__file__).parent.parent))
CURRICULUM_FILE = ROOT / "curriculum.yaml"


@dataclass
class CurriculumItem:
    id: str
    type: str           # "lesson" | "exercise"
    stage_id: str
    stage_title: str
    # lesson items
    file: str = ""
    # exercise items
    lesson: str = ""
    exercise: str = ""
    test: str = ""
    hints_file: str = ""
    original: str = ""
    verifier: str = ""
    quiz_file: str = ""

    @property
    def has_verifier(self) -> bool:
        return bool(self.verifier)

    @property
    def title(self) -> str:
        return self.id.replace("_", " ").title()

    @property
    def lesson_path(self) -> Path | None:
        src = self.file if self.type == "lesson" else self.lesson
        return (ROOT / src) if src else None

    @property
    def exercise_path(self) -> Path | None:
        return (ROOT / self.exercise) if self.exercise else None

    @property
    def test_path(self) -> Path | None:
        return (ROOT / self.test) if self.test else None

    @property
    def quiz_path(self) -> Path | None:
        if not self.quiz_file:
            return None
        p = ROOT / self.quiz_file
        return p if p.exists() else None

    @property
    def hints(self) -> list[str]:
        if not self.hints_file:
            return []
        path = ROOT / self.hints_file
        if not path.exists():
            return []
        text = path.read_text()
        hints = []
        for section in text.split("## Hint ")[1:]:
            lines = section.strip().splitlines()
            body = "\n".join(lines[1:]).strip()  # skip "N" header line
            hints.append(body)
        return hints


def load_curriculum() -> list[CurriculumItem]:
    with open(CURRICULUM_FILE) as f:
        data = yaml.safe_load(f)

    items = []
    for stage in data.get("stages", []):
        for item in stage.get("items", []):
            items.append(CurriculumItem(
                id=item["id"],
                type=item["type"],
                stage_id=stage["id"],
                stage_title=stage["title"],
                file=item.get("file", ""),
                lesson=item.get("lesson", ""),
                exercise=item.get("exercise", ""),
                test=item.get("test", ""),
                hints_file=item.get("hints", ""),
                original=item.get("original", ""),
                verifier=item.get("verifier", ""),
                quiz_file=item.get("quiz", ""),
            ))
    return items


# Module-level curriculum — loaded once at import time.
CURRICULUM: list[CurriculumItem] = load_curriculum()


def get_item(item_id: str) -> CurriculumItem | None:
    for item in CURRICULUM:
        if item.id == item_id:
            return item
    return None


def get_stage_items(stage_id: str) -> list[CurriculumItem]:
    return [item for item in CURRICULUM if item.stage_id == stage_id]


def is_last_in_stage(item_id: str) -> bool:
    item = get_item(item_id)
    if not item:
        return False
    stage_items = get_stage_items(item.stage_id)
    return stage_items and stage_items[-1].id == item_id


def get_index(item_id: str) -> int:
    for i, item in enumerate(CURRICULUM):
        if item.id == item_id:
            return i
    return -1


def reset_exercise(item: CurriculumItem) -> tuple[bool, str]:
    """Restore an exercise file from its original scaffold."""
    if item.type != "exercise":
        return False, f"'{item.id}' is a lesson, nothing to reset."
    if not item.original:
        return False, f"No original defined for '{item.id}' in curriculum.yaml."

    src = ROOT / item.original
    dst = ROOT / item.exercise

    if not src.exists():
        return False, f"Original file not found: {src}"

    shutil.copy2(src, dst)
    return True, f"'{item.id}' restored to original scaffold."
