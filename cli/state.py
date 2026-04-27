"""Progress state — persisted to a progress.txt file.

The state file location is resolved as follows:
  1. If /workspace exists (i.e. running inside Docker), use /workspace/.course/progress.txt
     so progress survives container restarts via a mounted volume.
  2. Otherwise fall back to the repo root (local dev).

Override the directory by setting the STATE_DIR env var.
"""

import os
from pathlib import Path

from cli.curriculum import CURRICULUM

_WORKSPACE = Path("/workspace")

if os.environ.get("STATE_DIR"):
    _STATE_DIR = Path(os.environ["STATE_DIR"])
elif _WORKSPACE.exists():
    _STATE_DIR = _WORKSPACE / ".course"
else:
    _STATE_DIR = Path(__file__).parent.parent

STATE_FILE = _STATE_DIR / "progress.txt"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"current": CURRICULUM[0].id, "done": [], "verified": []}

    lines = STATE_FILE.read_text().strip().splitlines()
    content = [l.strip() for l in lines if l.strip() and not l.startswith("DON'T")]

    if not content:
        return {"current": CURRICULUM[0].id, "done": [], "verified": []}

    current = content[0]

    done = []
    verified = []
    for entry in content[1:]:
        if entry.startswith("verified:"):
            verified.append(entry[len("verified:"):])
        else:
            done.append(entry)

    if not current or current == "COMPLETED":
        return {"current": "", "done": done, "verified": verified}

    return {"current": current, "done": done, "verified": verified}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = ["DON'T EDIT THIS FILE!\n", state["current"] or "COMPLETED"]
    lines.extend(state.get("done", []))
    lines.extend(f"verified:{v}" for v in state.get("verified", []))
    STATE_FILE.write_text("\n".join(lines) + "\n")


def mark_done(state: dict, item_id: str) -> dict:
    if item_id not in state["done"]:
        state["done"].append(item_id)
    return state


def is_done(state: dict, item_id: str) -> bool:
    return item_id in state["done"]


def mark_verified(state: dict, item_id: str) -> dict:
    if item_id not in state.get("verified", []):
        state.setdefault("verified", []).append(item_id)
    return state


def is_verified(state: dict, item_id: str) -> bool:
    return item_id in state.get("verified", [])


def unmark_verified(state: dict, item_id: str) -> dict:
    state["verified"] = [v for v in state.get("verified", []) if v != item_id]
    return state
