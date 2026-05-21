import argparse
import json

from app.orchestration.graph import build_graph


def build_initial_state(
    topic,
    tone,
    chapters,
    reader_profile="",
    length="short MVP",
    genre="Nonfiction",
    characters=None,
    output_slug="generated_book",
):
    return {
        "user_brief": {
            "topic": topic,
            "tone": tone,
            "chapters": chapters,
            "reader_profile": reader_profile,
            "length": length,
            "genre": genre,
            "characters": characters or [],
            "output_slug": output_slug,
        },
        "outline": {},
        "current_chapter": 0,
        "current_chapter_data": {},
        "chapter_text": "",
        "chapters": [],
        "facts": [],
        "references": [],
        "glossary": [],
        "callbacks": [],
        "tone_profile": {},
        "research_notes": [],
        "concept_bible": [],
        "callback_index": [],
        "decision_log": [],
        "memory_io": [],
        "logs": [],
        "generated_docx": "",
        "generated_pdf": "",
    }


def main():
    parser = argparse.ArgumentParser(description="Run AIuthor book generation.")
    parser.add_argument("--topic", default="Personal Finance")
    parser.add_argument("--tone", default="Conversational")
    parser.add_argument("--chapters", type=int, default=3)
    parser.add_argument("--reader-profile", default="Beginners")
    parser.add_argument("--length", default="short MVP")
    parser.add_argument("--genre", default="Nonfiction")
    parser.add_argument("--characters", default="")
    parser.add_argument("--output-slug", default="generated_book")
    args = parser.parse_args()

    state = build_initial_state(
        topic=args.topic,
        tone=args.tone,
        chapters=args.chapters,
        reader_profile=args.reader_profile,
        length=args.length,
        genre=args.genre,
        characters=[name.strip() for name in args.characters.split(",") if name.strip()],
        output_slug=args.output_slug,
    )
    result = build_graph().invoke(state)
    print(json.dumps({
        "title": result.get("outline", {}).get("book_title"),
        "chapters": len(result.get("chapters", [])),
        "docx": result.get("generated_docx", ""),
        "pdf": result.get("generated_pdf", ""),
        "logs": result.get("logs", []),
    }, indent=2))


if __name__ == "__main__":
    main()
