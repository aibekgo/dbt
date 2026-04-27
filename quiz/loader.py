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


def load_topic(item_id: str) -> Topic | None:
    path = QUIZ_DIR / f"{item_id}.yaml"
    if not path.exists():
        return None
    with open(path) as f:
        data = yaml.safe_load(f)
    title = data.get("topic", item_id).replace("_", " ").title()
    questions = [_parse_question(q) for q in data.get("questions", [])]
    return Topic(key=item_id, title=title, questions=questions)


def load_topics_for_items(item_ids: list[str]) -> list[Topic]:
    topics = []
    seen: set[str] = set()
    for item_id in item_ids:
        if item_id in seen:
            continue
        seen.add(item_id)
        topic = load_topic(item_id)
        if topic:
            topics.append(topic)
    return topics
