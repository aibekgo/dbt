#!/usr/bin/env python3
"""dbt-learn CLI — interactive learning environment for dbt + DuckDB."""

import os
import shutil
import subprocess
import typer
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from cli.curriculum import CURRICULUM, CurriculumItem, get_index, get_item, get_stage_items, is_last_in_stage, reset_exercise
from cli.state import is_done, is_verified, load_state, mark_done, mark_verified, save_state, unmark_verified

# ---------------------------------------------------------------------------
# Verifier registry — keys match the `verifier:` field in curriculum.yaml.
# ---------------------------------------------------------------------------
from verifier.local import LocalVerifier
from verifier.dbt import DbtVerifier
from verifier.file import FileVerifier

VERIFIER_REGISTRY: dict[str, type] = {
    "local": LocalVerifier,
    "dbt":   DbtVerifier,
    "file":  FileVerifier,
}

# Course branding — override via env vars if needed.
COURSE_NAME = os.environ.get("COURSE_NAME", "dbt-learn")
COURSE_EMOJI = os.environ.get("COURSE_EMOJI", "🔧")

# dbt project state we wipe on reset
ROOT = Path(__file__).resolve().parent.parent
DBT_PROJECT = ROOT / "dbt_project"


def _get_verifier(item: CurriculumItem):
    cls = VERIFIER_REGISTRY.get(item.verifier, LocalVerifier)
    return cls()


console = Console()
app = typer.Typer(
    name=COURSE_NAME,
    help=f"{COURSE_EMOJI} Interactive learning CLI.",
    add_completion=False,
    no_args_is_help=False,
)


# --- Display ---

def show_item(item: CurriculumItem, state: dict) -> None:
    total = len(CURRICULUM)
    idx = get_index(item.id)
    done_count = len(state["done"])

    bar_width = 50
    filled = int(bar_width * done_count / total) if total > 0 else 0
    bar = "[green]" + "#" * filled + "[/]" + "-" * (bar_width - filled)

    type_label = "📖 Lesson" if item.type == "lesson" else "💪 Exercise"
    file_hint = ""
    if item.type == "exercise" and item.exercise_path:
        file_hint = (
            f"\n📁 File: [green]{item.exercise}[/]"
            f"\n[dim]Read the comments in the file for instructions.[/]"
        )

    console.print()
    console.print(Panel(
        f"[cyan][{idx + 1}/{total}][/] [bold]{item.title}[/]  {type_label}"
        f"{file_hint}",
        title=f"{COURSE_EMOJI} {COURSE_NAME}  ·  {item.stage_title}",
        border_style="bright_blue",
    ))
    console.print(f"Progress: [{bar}]  {done_count}/{total}")


def show_prompt(item: CurriculumItem) -> None:
    console.print("\n[dim]💡 Press [bold]l[/] to read the lesson before starting.[/]")
    parts = ["[bold]l[/]:lesson"]
    if item.has_verifier:
        parts.append("[bold]h[/]:hint")
        parts.append("[bold]v[/]:verify")
    parts.append("[bold]n[/]:next")
    parts.append("[bold]r[/]:reset-progress")
    parts.append("[bold]q[/]:quit")
    console.print("\n" + "  ".join(parts) + " ? ", end="")


# --- Actions ---

def action_read(item: CurriculumItem) -> None:
    path = item.lesson_path
    if not path or not path.exists():
        console.print("\n[dim]No lesson found for this item.[/]")
        return
    console.print("\n[dim]Opening lesson in browser...[/]")
    subprocess.Popen(["open", str(path)])


def action_verify(item: CurriculumItem, state: dict) -> bool:
    path = item.exercise_path or item.lesson_path
    if not path:
        console.print("\n[dim]No file to verify for this item.[/]")
        return False

    console.print(f"\n⏳ Verifying [cyan]{item.id}[/]...")
    result = _get_verifier(item).verify(str(path))

    if not result.syntax_ok:
        console.print(f"\n[red]✘ Syntax error[/] — {result.syntax_error}\n")
        return False

    if not result.tests:
        console.print("\n[red]✘ No tests were collected.[/]\n")
        return False

    for t in result.tests:
        icon = "[green]✔[/]" if t.passed else "[red]✘[/]"
        suffix = f" — {t.message}" if t.message else ""
        console.print(f"  {icon} {t.name}{suffix}")

    if result.extra:
        console.print(result.extra)

    if result.passed:
        mark_verified(state, item.id)
        save_state(state)
        console.print("\n[green]Exercise passed ✓[/]")
        console.print("When done experimenting, press [bold]n[/] to advance.\n")
    else:
        failed = len(result.failed_tests)
        total = len(result.tests)
        console.print(f"\n[red]❌ {failed}/{total} test(s) failed.[/] Fix and press [bold]v[/] to retry.\n")

    return result.passed


def action_hint(item: CurriculumItem) -> None:
    hints = item.hints
    if not hints:
        console.print("\n[dim]No hints available for this exercise.[/]")
        return
    console.print(f"\n💡 [bold]Hints for {item.id}:[/]\n")
    for i, h in enumerate(hints, 1):
        console.print(f"[bold yellow]── Hint {i} ──[/]")
        console.print(Markdown(h))
        console.print()


def _run_stage_quiz(stage_id: str) -> None:
    from quiz.loader import load_topics_for_items
    from quiz.runner import render_summary, run_all

    stage_items = get_stage_items(stage_id)
    item_ids = [it.id for it in stage_items if it.quiz_path]
    topics = load_topics_for_items(item_ids)
    if not topics:
        return

    stage_title = stage_items[0].stage_title if stage_items else stage_id
    console.print()
    console.print(Panel(
        f"You've finished [bold]{stage_title}[/]!\n"
        f"[dim]Time for a quick quiz on what you've learned.[/]",
        border_style="magenta",
    ))
    results = run_all(topics, console=console)
    render_summary(console, results)
    console.print()


def action_list(state: dict) -> None:
    console.print(f"\n{COURSE_EMOJI} [bold]{COURSE_NAME} — Curriculum[/]\n")
    current_stage = None
    for i, item in enumerate(CURRICULUM):
        if item.stage_id != current_stage:
            current_stage = item.stage_id
            console.print(f"  [bold]{item.stage_title}[/]")
        if is_done(state, item.id):
            status = "[green]✅[/]"
        elif item.id == state["current"]:
            status = "[yellow]▶ [/]"
        else:
            status = "  "
        type_tag = "[dim]lesson  [/]" if item.type == "lesson" else "[dim]exercise[/]"
        console.print(f"    {status} {i + 1:>2}. {type_tag}  {item.title}")
    console.print()


def action_next(item: CurriculumItem, state: dict) -> CurriculumItem | None:
    if item.has_verifier and not is_verified(state, item.id):
        console.print(
            "\n[yellow]⚠️  Finish the current exercise first.[/] "
            "Press [bold]v[/] to verify.\n"
        )
        return item

    state = mark_done(state, item.id)

    if is_last_in_stage(item.id):
        _run_stage_quiz(item.stage_id)

    idx = get_index(item.id)

    if idx + 1 < len(CURRICULUM):
        next_item = CURRICULUM[idx + 1]
        state["current"] = next_item.id
        save_state(state)
        show_item(next_item, state)
        return next_item
    else:
        state["current"] = ""
        save_state(state)
        console.print("\n[green]🎉 You've completed the curriculum![/]\n")
        return None


# --- Interactive session ---

def interactive_session() -> None:
    state = load_state()
    save_state(state)
    item = get_item(state["current"]) if state["current"] else None

    if not item:
        console.print(f"[green]🎉 You've completed all exercises![/]")
        console.print(f"[dim]Run [bold]{COURSE_NAME} reset[/] to start over.[/]")
        return

    show_item(item, state)

    while item:
        show_prompt(item)
        try:
            cmd = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n\n👋 See you next time!")
            break

        if cmd == "q":
            console.print("\n👋 See you next time!")
            break
        elif cmd == "l":
            action_read(item)
        elif cmd == "v":
            if not item.has_verifier:
                console.print("\n[dim]No verifier for this item — press [bold]n[/] to advance.[/]")
            else:
                state = load_state()
                action_verify(item, state)
        elif cmd == "h":
            if not item.has_verifier:
                console.print("\n[dim]No hints for this item.[/]")
            else:
                action_hint(item)
        elif cmd == "n":
            state = load_state()
            result = action_next(item, state)
            if result is None:
                break
            item = result
        elif cmd == "x":
            if item.type == "lesson":
                console.print("\n[dim]Nothing to reset for a lesson.[/]")
            else:
                ok, msg = reset_exercise(item)
                if ok:
                    state = load_state()
                    unmark_verified(state, item.id)
                    save_state(state)
                icon = "[green]✔[/]" if ok else "[red]✘[/]"
                console.print(f"\n{icon} {msg}\n")
        elif cmd == "r":
            console.print("\n[yellow]Reset progress and jump back to step 1?[/] [dim](y/N)[/] ", end="")
            try:
                confirm = input().strip().lower()
            except (KeyboardInterrupt, EOFError):
                confirm = ""
            if confirm == "y":
                state = {"current": CURRICULUM[0].id, "done": [], "verified": []}
                save_state(state)
                item = CURRICULUM[0]
                console.print(f"\n[green]✅ Progress reset.[/]\n")
                show_item(item, state)
            else:
                console.print("[dim]Cancelled.[/]")
        else:
            console.print(f"\n[dim]Unknown command: '{cmd}'[/]")


# --- Typer commands ---

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        interactive_session()


@app.command(hidden=True)
def verify() -> None:
    """Verify the current exercise."""
    state = load_state()
    item = get_item(state["current"])
    if not item:
        console.print("[green]🎉 All done![/]")
        return
    if item.type == "lesson":
        console.print("[dim]Current item is a lesson. Use next to advance.[/]")
        return
    action_verify(item, state)


@app.command(name="next", hidden=True)
def next_cmd() -> None:
    """Advance to the next item."""
    state = load_state()
    item = get_item(state["current"])
    if not item:
        console.print("[green]🎉 All done![/]")
        return
    action_next(item, state)


@app.command(hidden=True)
def hint() -> None:
    """Show hints for the current exercise."""
    state = load_state()
    item = get_item(state["current"])
    if not item or item.type == "lesson":
        console.print("[dim]No hints available.[/]")
        return
    action_hint(item)


@app.command(name="list")
def list_cmd() -> None:
    """List all curriculum items and their status."""
    action_list(load_state())


@app.command()
def reset() -> None:
    """Reset all progress, restore exercise scaffolds, and wipe the DuckDB warehouse."""
    console.print("[dim]Resetting progress...[/]")
    save_state({"current": CURRICULUM[0].id, "done": [], "verified": []})

    console.print("[dim]Restoring exercise files...[/]")
    for item in CURRICULUM:
        if item.type == "exercise" and item.original:
            reset_exercise(item)

    if DBT_PROJECT.exists():
        console.print(f"[dim]Wiping learner-created dbt project at {DBT_PROJECT.name}/...[/]")
        shutil.rmtree(DBT_PROJECT, ignore_errors=True)

    console.print("[green]✅ Reset complete.[/]")


@app.command(name="reset-progress")
def reset_progress() -> None:
    """Reset progress only — start from step 1 without touching exercise files or the warehouse."""
    save_state({"current": CURRICULUM[0].id, "done": [], "verified": []})
    console.print(f"[green]✅ Progress reset.[/] Next run will start at [cyan]{CURRICULUM[0].id}[/].")


@app.command()
def quiz() -> None:
    """Run a quiz on all exercises."""
    from quiz.loader import load_topics_for_items
    from quiz.runner import render_summary, run_all

    item_ids = [it.id for it in CURRICULUM if it.quiz_path]
    topics = load_topics_for_items(item_ids)
    if not topics:
        console.print("[dim]No quiz questions available yet.[/]")
        return

    results = run_all(topics, console=console)
    render_summary(console, results)


@app.command(name="reset-exercise", hidden=True)
def reset_exercise_cmd() -> None:
    """Restore the current exercise to its original scaffold."""
    state = load_state()
    item = get_item(state["current"])
    if not item:
        console.print("[dim]No current exercise.[/]")
        return
    ok, msg = reset_exercise(item)
    icon = "[green]✔[/]" if ok else "[red]✘[/]"
    console.print(f"{icon} {msg}")


if __name__ == "__main__":
    app()
