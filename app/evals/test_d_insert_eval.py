import json
import os

from app.main import build_initial_state
from app.orchestration.graph import build_graph
from app.orchestration.repair import insert_chapter_and_repair


def run_test_d_eval():
    os.environ.setdefault("AIUTHOR_OFFLINE", "1")
    os.environ.setdefault("AIUTHOR_MAX_WORKERS", "1")

    state = build_initial_state(
        topic="Personal Finance",
        tone="Conversational",
        chapters=10,
        reader_profile="Beginners",
        length="short assessment smoke",
        output_slug="test_d_before_insert",
    )
    original = build_graph().invoke(state)
    original = {
        **original,
        "user_brief": {**original.get("user_brief", {}), "output_slug": "test_d_after_insert"},
    }
    repaired = insert_chapter_and_repair(original, insert_after=4)

    chapter_numbers = [chapter.get("chapter_number") for chapter in repaired.get("chapters", [])]
    outline_numbers = [chapter.get("chapter_number") for chapter in repaired.get("outline", {}).get("chapters", [])]
    inserted = repaired.get("chapters", [])[4]
    toc_titles = [f"Chapter {ch.get('chapter_number')}: {ch.get('title')}" for ch in repaired.get("chapters", [])]

    scores = {
        "started_with_10_chapters": len(original.get("chapters", [])) == 10,
        "ends_with_11_chapters": len(repaired.get("chapters", [])) == 11,
        "chapter_numbers_repaired": chapter_numbers == list(range(1, 12)),
        "outline_numbers_repaired": outline_numbers == list(range(1, 12)),
        "inserted_between_4_and_5": inserted.get("chapter_number") == 5,
        "callbacks_rebuilt": bool(repaired.get("callback_index")),
        "glossary_rebuilt": bool(repaired.get("glossary")),
        "docx_generated": os.path.exists(repaired.get("generated_docx", "")),
        "toc_uses_repaired_chapters": len(toc_titles) == 11 and "Chapter 5" in toc_titles[4],
    }
    print(json.dumps(scores, indent=2))
    return scores


if __name__ == "__main__":
    run_test_d_eval()
