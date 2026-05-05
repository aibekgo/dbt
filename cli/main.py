#!/usr/bin/env python3
"""dbt-learn CLI — interactive learning environment for dbt + DuckDB."""

import html
import os
import shutil
import tempfile
import webbrowser
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
DATABASE_DIR = ROOT / "database"


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
            f"\n[dim]Open the file for step-by-step instructions.[/]"
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
    parts.append("[bold]p[/]:previous")
    if item.type == "exercise":
        parts.append("[bold]x[/]:reset-exercise")
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
    webbrowser.open(path.resolve().as_uri())


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
    items_with_quiz = [it for it in stage_items if it.quiz_path]
    topics = load_topics_for_items(items_with_quiz)
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


def action_previous(item: CurriculumItem, state: dict) -> CurriculumItem:
    idx = get_index(item.id)
    if idx <= 0:
        console.print("\n[dim]Already at the first item.[/]")
        return item

    prev_item = CURRICULUM[idx - 1]
    state["current"] = prev_item.id
    save_state(state)
    show_item(prev_item, state)
    return prev_item


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
        return None


def show_completion_screen(state: dict) -> CurriculumItem | None:
    """Celebrate, then offer review / reset / quit. Returns the item to switch to, or None to exit."""
    console.print()
    console.print(Panel(
        "[bold green]🎉 You've completed all exercises![/]\n\n"
        "What's next?\n"
        "  [bold]p[/]  go back and review previous lessons\n"
        "  [bold]r[/]  reset progress and start over\n"
        "  [bold]q[/]  quit",
        title=f"{COURSE_EMOJI} {COURSE_NAME}  ·  Complete",
        border_style="green",
    ))
    while True:
        console.print("\n[bold]p[/]:review  [bold]r[/]:reset  [bold]q[/]:quit ? ", end="")
        try:
            cmd = input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print()
            return None
        if cmd in ("q", ""):
            console.print("👋 See you next time!")
            return None
        if cmd == "p":
            item = CURRICULUM[-1]
            state["current"] = item.id
            save_state(state)
            show_item(item, state)
            return item
        if cmd == "r":
            console.print("[yellow]Reset progress and start over?[/] [dim](y/N)[/] ", end="")
            try:
                confirm = input().strip().lower()
            except (KeyboardInterrupt, EOFError):
                confirm = ""
            if confirm == "y":
                state.clear()
                state.update({"current": CURRICULUM[0].id, "done": [], "verified": []})
                save_state(state)
                item = CURRICULUM[0]
                console.print("\n[green]✅ Progress reset.[/]")
                show_item(item, state)
                return item
            console.print("[dim]Cancelled.[/]")
            continue
        console.print(f"[dim]Unknown command: '{cmd}'[/]")


# --- Interactive session ---

def interactive_session() -> None:
    state = load_state()
    save_state(state)
    item = get_item(state["current"]) if state["current"] else None

    if not item:
        item = show_completion_screen(state)
        if item is None:
            return
    else:
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
                state = load_state()
                result = show_completion_screen(state)
                if result is None:
                    break
            item = result
        elif cmd == "p":
            state = load_state()
            item = action_previous(item, state)
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

def _resolve_target(target: str) -> CurriculumItem | None:
    """Look up a curriculum item by 1-based position (e.g. '49') or by id (e.g. 'welcome')."""
    if target.isdigit():
        idx = int(target) - 1
        if 0 <= idx < len(CURRICULUM):
            return CURRICULUM[idx]
        return None
    return get_item(target)


def _jump_to(target: str) -> None:
    """Update progress to start at the given lesson, then fall through to interactive_session."""
    item = _resolve_target(target)
    if item is None:
        console.print(
            f"\n[red]No lesson at '{target}'.[/] "
            f"Run [bold]{COURSE_NAME} list[/] to see valid positions and ids.\n"
        )
        raise typer.Exit(1)
    state = load_state()
    state["current"] = item.id
    save_state(state)
    idx = get_index(item.id)
    console.print(
        f"\n[green]→ Jumped to[/] [cyan]{idx + 1}. {item.title}[/] "
        f"[dim]({item.id})[/]\n"
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    go: str | None = typer.Option(
        None,
        "--go",
        "-g",
        help="Jump to a specific item by 1-based position or id (e.g. --go 49 or --go welcome).",
    ),
) -> None:
    if ctx.invoked_subcommand is None:
        if go is not None:
            _jump_to(go)
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

    if DATABASE_DIR.exists():
        for f in DATABASE_DIR.glob("*.duckdb*"):
            console.print(f"[dim]Wiping {f.relative_to(ROOT)}...[/]")
            f.unlink(missing_ok=True)

    console.print("[green]✅ Reset complete.[/]")


@app.command(name="reset-progress")
def reset_progress() -> None:
    """Reset progress only — start from step 1 without touching exercise files or the warehouse."""
    save_state({"current": CURRICULUM[0].id, "done": [], "verified": []})
    console.print(f"[green]✅ Progress reset.[/] Next run will start at [cyan]{CURRICULUM[0].id}[/].")


@app.command()
def curriculum() -> None:
    """Build a one-page HTML index of every lesson and open it in the browser."""
    stages: dict[str, dict] = {}
    for i, item in enumerate(CURRICULUM):
        stage = stages.setdefault(item.stage_id, {"title": item.stage_title, "rows": []})
        stage["rows"].append((i + 1, item))

    rows_html: list[str] = []
    for stage in stages.values():
        rows_html.append(f'<h2>{html.escape(stage["title"])}</h2>')
        rows_html.append("<ul>")
        for pos, item in stage["rows"]:
            badge = "lesson" if item.type == "lesson" else "exercise"
            path = item.lesson_path
            title = html.escape(item.title)
            id_ = html.escape(item.id)
            if path and path.exists():
                href = path.resolve().as_uri()
                rows_html.append(
                    f'<li><span class="pos">{pos:>2}.</span>'
                    f'<span class="badge {badge}">{badge}</span>'
                    f'<a href="{href}" target="_blank">{title}</a>'
                    f'<span class="id">{id_}</span></li>'
                )
            else:
                rows_html.append(
                    f'<li><span class="pos">{pos:>2}.</span>'
                    f'<span class="badge {badge}">{badge}</span>'
                    f'<span class="missing">{title}</span>'
                    f'<span class="id">{id_}</span></li>'
                )
        rows_html.append("</ul>")

    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{COURSE_NAME} — curriculum</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       max-width: 900px; margin: 40px auto; padding: 0 24px; color: #1a1a1a; line-height: 1.5; }}
h1 {{ margin-bottom: 4px; }} .sub {{ color: #666; margin-bottom: 32px; }}
h2 {{ margin-top: 36px; padding-bottom: 6px; border-bottom: 1px solid #eee; }}
ul {{ list-style: none; padding-left: 0; }}
li {{ display: flex; align-items: baseline; gap: 10px; padding: 4px 0; }}
.pos {{ color: #999; font-variant-numeric: tabular-nums; min-width: 28px; text-align: right; }}
.badge {{ font-size: 0.72em; padding: 2px 8px; border-radius: 10px; text-transform: uppercase;
         letter-spacing: 0.04em; min-width: 60px; text-align: center; }}
.badge.lesson {{ background: #eaf3ff; color: #1f5fbf; }}
.badge.exercise {{ background: #fff1e0; color: #b56b00; }}
a {{ color: #1f5fbf; text-decoration: none; }} a:hover {{ text-decoration: underline; }}
.id {{ color: #aaa; font-size: 0.85em; font-family: ui-monospace, monospace; }}
.missing {{ color: #c00; }}
</style></head><body>
<h1>{COURSE_EMOJI} {COURSE_NAME} — curriculum</h1>
<div class="sub">{len(CURRICULUM)} items across {len(stages)} stages. Click any title to open the lesson.</div>
{chr(10).join(rows_html)}
</body></html>
"""
    fd, tmp_path = tempfile.mkstemp(suffix="_curriculum.html", prefix=f"{COURSE_NAME}_")
    with os.fdopen(fd, "w") as f:
        f.write(page)
    console.print(f"[dim]Opening curriculum index ({len(CURRICULUM)} items)...[/]")
    webbrowser.open(Path(tmp_path).as_uri())


@app.command()
def quiz() -> None:
    """Run a quiz on all exercises."""
    from quiz.loader import load_topics_for_items
    from quiz.runner import render_summary, run_all

    items_with_quiz = [it for it in CURRICULUM if it.quiz_path]
    topics = load_topics_for_items(items_with_quiz)
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
