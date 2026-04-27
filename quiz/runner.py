"""Interactive quiz runner — prompts user, checks answers, tallies scores."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from cli.curriculum import get_item
from quiz.loader import Question, Topic


@dataclass
class AnswerOutcome:
    question_id: str
    topic: str
    correct: bool
    skipped: bool = False


@dataclass
class TopicResult:
    topic: Topic
    outcomes: list[AnswerOutcome] = field(default_factory=list)
    quit: bool = False

    @property
    def correct(self) -> int:
        return sum(1 for o in self.outcomes if o.correct)

    @property
    def total(self) -> int:
        return sum(1 for o in self.outcomes if not o.skipped)

    @property
    def failed_ids(self) -> list[str]:
        return [o.question_id for o in self.outcomes if not o.correct and not o.skipped]

    @property
    def score_pct(self) -> float:
        return (self.correct / self.total * 100.0) if self.total else 0.0


def check_answer(q: Question, user_input: str) -> bool:
    return user_input.strip().lower() == str(q.answer).strip().lower()


def _format_answer(q: Question) -> str:
    key = q.answer
    return f"{key}) {q.options.get(key, '')}"


def _prompt_for(q: Question) -> str:
    keys = "/".join(q.options.keys())
    return f"Answer ({keys}) · [bold]s[/]:skip  [bold]q[/]:quit ? "


def _render_question(console: Console, q: Question, idx: int, total: int, topic_title: str) -> None:
    header = f"[cyan][{idx}/{total}][/] [dim]{topic_title}[/]  ·  [dim]{q.difficulty}[/]"
    opts = "\n".join(f"  [bold]{k}[/]) {v}" for k, v in q.options.items())
    body = f"{q.prompt}\n\n{opts}"
    console.print()
    console.print(Panel(f"{header}\n\n{body}", border_style="bright_blue"))


def _render_feedback(console: Console, q: Question, correct: bool) -> None:
    if correct:
        console.print("\n[green]✔ Correct.[/]")
    else:
        console.print(f"\n[red]✘ Incorrect.[/] Answer: [bold]{_format_answer(q)}[/]")
    console.print(Markdown(q.explanation))
    item = get_item(q.related_item)
    if item and item.lesson_path:
        console.print(f"[dim]Related lesson:[/] [cyan]{item.lesson_path}[/]")


def run_topic(
    topic: Topic,
    *,
    shuffle: bool = True,
    limit: int | None = None,
    rng: random.Random | None = None,
    console: Console | None = None,
    input_fn=input,
) -> TopicResult:
    console = console or Console()
    rng = rng or random.Random()

    questions = list(topic.questions)
    if shuffle:
        rng.shuffle(questions)
    if limit is not None:
        questions = questions[:limit]

    console.print(Panel(
        f"[bold]{topic.title}[/]\n{len(questions)} question(s)",
        title="📝 Quiz",
        border_style="magenta",
    ))

    result = TopicResult(topic=topic)
    total = len(questions)

    for i, q in enumerate(questions, 1):
        _render_question(console, q, i, total, topic.title)
        console.print(_prompt_for(q), end="")
        try:
            raw = input_fn()
        except (EOFError, KeyboardInterrupt):
            result.quit = True
            break

        raw = raw.strip()
        if raw.lower() == "q":
            result.quit = True
            break
        if raw.lower() in {"s", ""}:
            result.outcomes.append(AnswerOutcome(q.id, topic.key, correct=False, skipped=True))
            console.print("[yellow]↷ Skipped.[/]")
            continue

        correct = check_answer(q, raw)
        _render_feedback(console, q, correct)
        result.outcomes.append(AnswerOutcome(q.id, topic.key, correct=correct, skipped=False))

    console.print()
    console.print(
        f"[bold]{topic.title}[/]: "
        f"[green]{result.correct}[/]/[bold]{result.total}[/]  "
        f"([cyan]{result.score_pct:.0f}%[/])"
    )
    return result


def run_all(
    topics: list[Topic],
    *,
    shuffle: bool = True,
    limit: int | None = None,
    rng: random.Random | None = None,
    console: Console | None = None,
    input_fn=input,
) -> list[TopicResult]:
    results: list[TopicResult] = []
    for topic in topics:
        if not topic.questions:
            continue
        result = run_topic(topic, shuffle=shuffle, limit=limit, rng=rng, console=console, input_fn=input_fn)
        results.append(result)
        if result.quit:
            break
    return results


def render_summary(console: Console, results: list[TopicResult]) -> None:
    if not results:
        console.print("[dim]No results to summarize.[/]")
        return

    table = Table(title="Quiz Summary", border_style="bright_blue")
    table.add_column("Topic", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Pct", justify="right")

    total_correct = 0
    total_asked = 0
    for r in results:
        table.add_row(r.topic.title, f"{r.correct}/{r.total}", f"{r.score_pct:.0f}%")
        total_correct += r.correct
        total_asked += r.total

    overall = (total_correct / total_asked * 100.0) if total_asked else 0.0
    table.add_section()
    table.add_row("[bold]Overall[/]", f"{total_correct}/{total_asked}", f"{overall:.0f}%")
    console.print()
    console.print(table)

    failed = [(r, qid) for r in results for qid in r.failed_ids]
    if failed:
        console.print("\n[dim]Review these lessons:[/]")
        for r, qid in failed:
            q = next((q for q in r.topic.questions if q.id == qid), None)
            if not q:
                continue
            item = get_item(q.related_item)
            path = item.lesson_path if item else None
            console.print(f"  [red]•[/] {qid}  →  [cyan]{path or q.related_item}[/]")
