import json
import os

from app.main import build_initial_state
from app.orchestration.graph import build_graph


def run_test_b_eval():
    os.environ.setdefault("AIUTHOR_OFFLINE", "1")
    os.environ.setdefault("AIUTHOR_MAX_WORKERS", "1")

    characters = ["Mira", "Jonah"]
    state = build_initial_state(
        topic="A quiet coastal town where two friends uncover a family secret",
        tone="Storyteller",
        chapters=5,
        reader_profile="Adult fiction readers",
        length="5 chapters",
        genre="Novella",
        characters=characters,
        output_slug="test_b_novella",
    )
    result = build_graph().invoke(state)
    chapters = result.get("chapters", [])
    chapter_text = "\n".join(ch.get("content", "") for ch in chapters)

    scores = {
        "five_chapters": len(chapters) == 5,
        "storyteller_tone": result.get("user_brief", {}).get("tone") == "Storyteller",
        "novella_genre": result.get("user_brief", {}).get("genre") == "Novella",
        "both_characters_all_chapters": all(
            all(name in ch.get("content", "") for name in characters)
            for ch in chapters
        ),
        "character_names_in_outline": all(
            all(name in ch.get("summary", "") for name in characters)
            for ch in result.get("outline", {}).get("chapters", [])
        ),
        "callback_index_built": bool(result.get("callback_index")),
        "docx_generated": os.path.exists(result.get("generated_docx", "")),
        "no_finance_recovery_bleed": "Money gets personal" not in chapter_text,
    }
    print(json.dumps(scores, indent=2))
    return scores


if __name__ == "__main__":
    run_test_b_eval()
