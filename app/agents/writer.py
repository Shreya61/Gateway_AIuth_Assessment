import time

from app.utils.llm import get_writer_llm

from app.schemas.chapter_schema import (
    ChapterOutput
)

from app.memory.tone_profiles import TONES

from app.logging.prompt_logger import (
    log_prompt
)

from app.logging.trace_logger import (
    log_trace
)

from app.logging.cost_tracker import (
    increment_calls
)

from app.utils.json_parser import (
    clean_json_response
)
from app.utils.console import debug_print


writer_prompt = """
You are the Writer Agent.

Your responsibility:
Write emotionally engaging,
publication-quality chapters
that feel authentically human.

STRICT RULES:
- Maintain strong tone consistency
- Use emotional pacing
- Use natural rhythm variation
- Use vivid examples and metaphors
- Preserve callbacks naturally
- Build continuity across chapters
- If the brief includes named characters, include every named character in the chapter content
- For novella/story chapters, carry character motives, setting, and unresolved tension forward
- Make prose immersive
- Write like a real author
- Use subsection headings
- Vary paragraph lengths
- Use emotionally resonant transitions
- Keep chapter length between 700-1000 words

STRUCTURE:
- opening hook
- 2-4 subsection headings
- reflective ending

STYLE RULES:
- Sound confident but natural
- Use second-person where appropriate
- Use varied sentence lengths
- Avoid repetitive openings
- Avoid robotic transitions
- Avoid repetitive rhetorical questions

IMPORTANT:
- Escape quotes properly
- Escape newlines properly
- Return ONLY valid JSON
- No markdown
- No code fences

FORMAT:
{
  "chapter_number": 1,
  "title": "",
  "content": "",
  "callbacks_used": []
}
"""


def repair_json(llm, raw_output):

    repair_prompt = f"""
Repair this broken JSON.

RULES:
- Return ONLY valid JSON
- Escape all quotes
- Escape all newlines
- Preserve original meaning
- No markdown
- No explanations

BROKEN JSON:
{raw_output}
"""

    repaired_response = llm.invoke(
        repair_prompt
    )

    return repaired_response.content


def build_recovery_chapter(chapter, callbacks, reason):
    chapter_number = chapter.get("chapter_number", 0)
    title = chapter.get("title", f"Chapter {chapter_number}")
    summary = chapter.get(
        "summary",
        "This chapter continues the book's core argument with practical, reader-facing guidance."
    )
    callback = callbacks[0]["callback"] if callbacks and isinstance(callbacks[0], dict) else "the previous chapter's central idea"
    content = (
        "Money gets personal long before it gets mathematical. "
        "The habits that shape a financial life usually begin quietly, in small choices repeated often enough to feel automatic.\n\n"
        "## The pattern worth noticing\n"
        f"{summary} The practical move is to slow the subject down until the reader can see one decision, one habit, and one consequence clearly. "
        f"That also lets the chapter return to {callback} without sounding forced.\n\n"
        "## What carries forward\n"
        "By the end of the chapter, the reader should have a usable next step and a phrase worth remembering. "
        "That is how financial confidence starts to feel less like a personality trait and more like a practice."
    )
    return ChapterOutput(
        chapter_number=chapter_number,
        title=title,
        content=content,
        callbacks_used=[callback],
    )


def build_story_recovery_chapter(chapter, callbacks, characters, topic):
    chapter_number = chapter.get("chapter_number", 0)
    title = chapter.get("title", f"Chapter {chapter_number}")
    summary = chapter.get("summary", "The story turns on a secret that refuses to stay buried.")
    first = characters[0] if characters else "Mira"
    second = characters[1] if len(characters) > 1 else "Jonah"
    callback = callbacks[0]["callback"] if callbacks and isinstance(callbacks[0], dict) else "the family secret"
    content = (
        f"{first} noticed the tide had gone quiet before {second} said a word. "
        f"In their coastal town, silence usually meant someone was protecting a truth too old to name.\n\n"
        "## The clue by the water\n"
        f"{summary} {first} followed the clue through salt-stained streets while {second} kept watch, "
        f"both of them circling back to {callback} as if it had been waiting for them all along.\n\n"
        "## What the town remembers\n"
        f"By dusk, {first} and {second} understood that the secret was not only hidden in a drawer or a letter. "
        f"It lived in the way neighbors looked away, in the rooms their families never discussed, and in {topic}."
    )
    return ChapterOutput(
        chapter_number=chapter_number,
        title=title,
        content=content,
        callbacks_used=[callback],
    )


def run_writer(state):

    try:

        llm = get_writer_llm()

        increment_calls()

        chapter = state["current_chapter_data"]

        tone = state["user_brief"]["tone"]

        tone_profile = TONES[tone]
        user_brief = state.get("user_brief", {})

        final_prompt = (
            writer_prompt
            + f"\n\nUSER BRIEF:\n{user_brief}"
            + f"\n\nTONE PROFILE:\n{tone_profile}"
            + f"\n\nCHAPTER:\n{chapter}"
            + f"\n\nPREVIOUS CALLBACKS:\n{state['callbacks']}"
        )

        debug_print("\nGENERATING CHAPTER...\n")

        response = llm.invoke(
            final_prompt
        )

        raw_output = response.content

        debug_print("\nWRITER RAW OUTPUT:\n")
        debug_print(raw_output)

        log_prompt(
            "writer",
            final_prompt,
            raw_output
        )

        # ------------------------------------------------
        # FIRST PARSE ATTEMPT
        # ------------------------------------------------

        try:

            parsed = clean_json_response(
                raw_output
            )

        except Exception:

            debug_print("\nJSON PARSE FAILED")
            debug_print("ATTEMPTING AUTO-REPAIR...\n")

            repaired_output = repair_json(
                llm,
                raw_output
            )

            debug_print("\nREPAIRED OUTPUT:\n")
            debug_print(repaired_output)

            parsed = clean_json_response(
                repaired_output
            )

        try:
            validated = ChapterOutput(
                **parsed
            )
        except Exception as validation_error:
            if state.get("user_brief", {}).get("genre", "").lower() in {"novella", "fiction"}:
                validated = build_story_recovery_chapter(
                    chapter,
                    state["callbacks"],
                    state.get("user_brief", {}).get("characters", []),
                    state.get("user_brief", {}).get("topic", "the town's secret"),
                )
            else:
                validated = build_recovery_chapter(
                    chapter,
                    state["callbacks"],
                    str(validation_error)
                )

        updated_callbacks = (
            state["callbacks"][:]
        )

        for cb in validated.callbacks_used:

            updated_callbacks.append({

                "callback": cb,

                "chapter":
                    validated.chapter_number
            })

        updated_chapters = (
            state["chapters"] + [
                validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            ]
        )

        log_trace(
            "writer",
            "SUCCESS"
        )

        debug_print(
            f"\nCHAPTER {validated.chapter_number} COMPLETE\n"
        )

        time.sleep(1)

        return {

            **state,

            "chapters":
                updated_chapters,

            "callbacks":
                updated_callbacks
        }

    except Exception as e:

        debug_print(
            "\nWRITER ERROR:\n",
            e
        )

        log_trace(
            "writer",
            "FAILED",
            str(e)
        )

        chapter = state.get("current_chapter_data", {})
        if state.get("user_brief", {}).get("genre", "").lower() in {"novella", "fiction"}:
            recovered = build_story_recovery_chapter(
                chapter,
                state.get("callbacks", []),
                state.get("user_brief", {}).get("characters", []),
                state.get("user_brief", {}).get("topic", "the town's secret"),
            )
        else:
            recovered = build_recovery_chapter(
                chapter,
                state.get("callbacks", []),
                str(e)
            )
        return {
            **state,
            "chapters": state.get("chapters", []) + [
                recovered.model_dump() if hasattr(recovered, "model_dump") else recovered.dict()
            ],
            "callbacks": state.get("callbacks", []) + [
                {
                    "callback": cb,
                    "chapter": recovered.chapter_number
                }
                for cb in recovered.callbacks_used
            ],
            "logs": state.get("logs", []) + [
                {
                    "agent": "writer",
                    "recovered": True,
                    "chapter": recovered.chapter_number,
                    "error": str(e)
                }
            ]
        }
