import copy
import re

from app.orchestration.graph import _write_single_chapter
from app.agents.editor import run_editor
from app.agents.memory_keeper import run_memory_keeper
from app.agents.references import run_references
from app.agents.glossary import run_glossary
from app.agents.assembler import run_assembler


def _strip_chapter_prefix(title):
    title = str(title or "").strip()
    title = re.sub(r"^chapter\s+\d+\s*:\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^chapter\s+\d+\s+", "", title, flags=re.IGNORECASE)
    return title


def _renumber_items(items):
    renumbered = []
    for idx, item in enumerate(items, start=1):
        updated = {**item, "chapter_number": idx}
        if "title" in updated:
            updated["title"] = _strip_chapter_prefix(updated["title"])
        renumbered.append(updated)
    return renumbered


def insert_chapter_and_repair(state, insert_after=4, chapter_plan=None):
    """Insert a chapter into an existing generated book and rebuild downstream state."""
    outline = copy.deepcopy(state.get("outline", {}))
    outline_chapters = outline.get("chapters", [])
    existing_chapters = copy.deepcopy(state.get("chapters", []))

    if not outline_chapters or not existing_chapters:
        raise ValueError("Insert repair requires an existing outline and generated chapters.")

    insert_index = max(0, min(insert_after, len(outline_chapters)))
    chapter_plan = chapter_plan or {
        "chapter_number": insert_index + 1,
        "title": "Money in Motion",
        "summary": (
            "A bridge chapter that shows how everyday financial habits change when income, "
            "expenses, goals, and emotions move at the same time."
        ),
        "callback_candidates": [
            "small choices compound",
            "money habits move with real life",
        ],
    }

    repaired_outline_chapters = (
        outline_chapters[:insert_index]
        + [chapter_plan]
        + outline_chapters[insert_index:]
    )
    repaired_outline_chapters = _renumber_items(repaired_outline_chapters)
    inserted_plan = repaired_outline_chapters[insert_index]

    base_state = {
        **state,
        "outline": {**outline, "chapters": repaired_outline_chapters},
        "callbacks": state.get("callback_index", state.get("callbacks", [])),
    }
    inserted_chapter = _write_single_chapter((inserted_plan, base_state))

    repaired_chapters = (
        existing_chapters[:insert_index]
        + [inserted_chapter]
        + existing_chapters[insert_index:]
    )
    repaired_chapters = _renumber_items(repaired_chapters)

    repaired_state = {
        **state,
        "outline": {**outline, "chapters": repaired_outline_chapters},
        "chapters": repaired_chapters,
        "glossary": [],
        "references": [],
        "callback_index": [],
        "callbacks": [],
        "logs": state.get("logs", []) + [{
            "agent": "repair",
            "action": "insert_chapter",
            "insert_after": insert_after,
            "inserted_chapter_number": insert_index + 1,
        }],
    }

    for step in (run_editor, run_memory_keeper, run_references, run_glossary, run_assembler):
        repaired_state = step(repaired_state)

    return repaired_state
