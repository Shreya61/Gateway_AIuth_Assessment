import copy

from app.orchestration.graph import _write_single_chapter
from app.agents.editor import run_editor
from app.agents.continuity import run_continuity_guard
from app.agents.memory_keeper import run_memory_keeper
from app.agents.references import run_references
from app.agents.glossary import run_glossary
from app.agents.assembler import run_assembler


def regenerate_chapter_variant(state, chapter_number, tone):
    """Regenerate one chapter from an existing outline with a new tone."""
    outline = copy.deepcopy(state.get("outline", {}))
    chapter_plan = None
    for item in outline.get("chapters", []):
        if item.get("chapter_number") == chapter_number:
            chapter_plan = item
            break

    if chapter_plan is None:
        raise ValueError(f"Chapter {chapter_number} not found in outline.")

    variant_state = {
        **copy.deepcopy(state),
        "user_brief": {**state.get("user_brief", {}), "tone": tone},
        "chapters": [],
        "callbacks": state.get("callback_index", state.get("callbacks", [])),
    }
    regenerated = _write_single_chapter((chapter_plan, variant_state))

    chapters = []
    replaced = False
    for chapter in state.get("chapters", []):
        if chapter.get("chapter_number") == chapter_number:
            chapters.append(regenerated)
            replaced = True
        else:
            chapters.append(copy.deepcopy(chapter))

    if not replaced:
        chapters.append(regenerated)
        chapters = sorted(chapters, key=lambda ch: ch.get("chapter_number", 0))

    repaired_state = {
        **variant_state,
        "chapters": chapters,
        "glossary": [],
        "references": [],
        "callback_index": [],
        "callbacks": [],
        "logs": state.get("logs", []) + [{
            "agent": "regenerate",
            "chapter": chapter_number,
            "tone": tone,
        }],
    }

    for step in (
        run_editor,
        run_continuity_guard,
        run_memory_keeper,
        run_references,
        run_glossary,
        run_assembler,
    ):
        repaired_state = step(repaired_state)

    return repaired_state
