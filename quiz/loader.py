"""Load quiz questions from quiz/{item_id}.yaml files."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(os.environ.get("COURSE_ROOT", Path(__file__).parent.parent))
QUIZ_DIR = ROOT / "quiz"


@dataclass
class Question:
    id: str
    type: str           # multiple_choice | true_false | short_answer
    difficulty: str
    prompt: str
    answer: Any
    explanation: str
    related_item: str
    options: dict[str, str] = field(default_factory=dict)  # mc only


@dataclass
class Topic:
    key: str
    title: str
    questions: list[Question] = field(default_factory=list)

    @property
    def user_tldr_path(self) -> Path:
        return ROOT / "quiz" / "notes" / f"{self.key}.md"


def _parse_question(raw: dict) -> Question:
    return Question(
        id=raw["id"],
        type=raw["type"],
        difficulty=raw.get("difficulty", "medium"),
        prompt=raw["prompt"],
        answer=raw["answer"],
        explanation=raw.get("explanation", ""),
        related_item=raw.get("related_item", ""),
        options=raw.get("options", {}),
    )


def _load_topic_at(path: Path, key: str) -> Topic | None:
    if not path.exists():
        return None
    with open(path) as f:
        data = yaml.safe_load(f)
    title = data.get("topic", key).replace("_", " ").title()
    questions = [_parse_question(q) for q in data.get("questions", [])]
    return Topic(key=key, title=title, questions=questions)


def load_topic(item_id: str) -> Topic | None:
    return _load_topic_at(QUIZ_DIR / f"{item_id}.yaml", item_id)


def load_topics_for_items(items: list) -> list[Topic]:
    """Load quiz topics for a list of CurriculumItem objects (or item id strings)."""
    topics = []
    seen: set[str] = set()
    for item in items:
        if isinstance(item, str):
            key = item
            if key in seen:
                continue
            seen.add(key)
            topic = load_topic(key)
        else:
            key = item.id
            if key in seen or not getattr(item, "quiz_file", ""):
                continue
            seen.add(key)
            topic = _load_topic_at(ROOT / item.quiz_file, key)
        if topic:
            topics.append(topic)
    return topics
