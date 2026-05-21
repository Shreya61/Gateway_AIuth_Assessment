import json
import os

from app.main import build_initial_state
from app.orchestration.graph import build_graph
from app.orchestration.regenerate import regenerate_chapter_variant


def run_test_c_eval():
    os.environ.setdefault("AIUTHOR_OFFLINE", "1")
    os.environ.setdefault("AIUTHOR_MAX_WORKERS", "1")

    state = build_initial_state(
        topic="Personal Finance",
        tone="Conversational",
        chapters=10,
        reader_profile="Beginners",
        length="2500 words per chapter target for live run",
        genre="Beginner nonfiction guide",
        output_slug="test_c_base",
    )
    base = build_graph().invoke(state)
    variants = {}
    for tone in ("Academic", "Motivational", "Witty"):
        variant_seed = {
            **base,
            "user_brief": {
                **base.get("user_brief", {}),
                "output_slug": f"test_c_chapter_3_{tone.lower()}",
            },
        }
        variants[tone] = regenerate_chapter_variant(variant_seed, chapter_number=3, tone=tone)

    scores = {
        "base_outline_has_10_chapters": len(base.get("outline", {}).get("chapters", [])) == 10,
        "three_variants_created": set(variants.keys()) == {"Academic", "Motivational", "Witty"},
        "all_variants_keep_10_chapters": all(len(v.get("chapters", [])) == 10 for v in variants.values()),
        "all_variants_have_chapter_3": all(
            any(ch.get("chapter_number") == 3 for ch in v.get("chapters", []))
            for v in variants.values()
        ),
        "tones_recorded": all(v.get("user_brief", {}).get("tone") == tone for tone, v in variants.items()),
        "glossary_rebuilt_each_time": all(bool(v.get("glossary")) for v in variants.values()),
        "docx_generated_each_time": all(os.path.exists(v.get("generated_docx", "")) for v in variants.values()),
    }
    print(json.dumps(scores, indent=2))
    return scores


if __name__ == "__main__":
    run_test_c_eval()
