import json
import os

from app.main import build_initial_state
from app.orchestration.graph import build_graph


def run_test_a_eval():
    os.environ.setdefault("AIUTHOR_OFFLINE", "1")
    os.environ.setdefault("AIUTHOR_MAX_WORKERS", "1")

    state = build_initial_state(
        topic="Personal Finance",
        tone="Conversational",
        chapters=10,
        reader_profile="Beginners",
        length="2500 words per chapter target for live run",
        genre="Beginner nonfiction guide",
        output_slug="test_a_personal_finance",
    )
    result = build_graph().invoke(state)
    chapters = result.get("chapters", [])

    scores = {
        "ten_chapters": len(chapters) == 10,
        "conversational_tone": result.get("user_brief", {}).get("tone") == "Conversational",
        "beginner_profile": "Beginner" in result.get("user_brief", {}).get("reader_profile", ""),
        "callback_index_built": bool(result.get("callback_index")),
        "glossary_generated": bool(result.get("glossary")),
        "docx_generated": os.path.exists(result.get("generated_docx", "")),
        "pdf_generated": os.path.exists(result.get("generated_pdf", "")),
        "no_failure_artifacts": not any(
            "failed" in chapter.get("content", "").lower()
            or "json parse" in chapter.get("content", "").lower()
            for chapter in chapters
        ),
    }
    print(json.dumps(scores, indent=2))
    return scores


if __name__ == "__main__":
    run_test_a_eval()
