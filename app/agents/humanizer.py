from app.utils.llm import (
    get_fast_llm
)

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

humanizer_prompt = """
You are the Humanizer Agent.

Transform robotic AI prose into
natural emotionally human writing.

STRICT RULES:
- preserve meaning
- preserve tone
- improve rhythm
- reduce repetition
- remove AI phrasing

Return ONLY valid JSON.

FORMAT:
{
  "chapter_number": 1,
  "humanized_content": ""
}
"""


def run_humanizer(state):

    try:

        llm = get_fast_llm()

        increment_calls()

        latest_chapter = (
            state["chapters"][-1]
        )

        final_prompt = (
            humanizer_prompt
            + f"\n\nCONTENT:\n"
            + latest_chapter["content"]
        )

        response = llm.invoke(
            final_prompt
        )

        raw_output = response.content

        debug_print("\nHUMANIZER RAW OUTPUT:\n")
        debug_print(raw_output)

        log_prompt(
            "humanizer",
            final_prompt,
            raw_output
        )

        parsed = clean_json_response(
            raw_output
        )

        updated_chapters = (
            state["chapters"][:]
        )

        updated_chapters[-1]["content"] = (
            parsed["humanized_content"]
        )

        log_trace(
            "humanizer",
            "SUCCESS"
        )

        return {

            **state,

            "chapters":
                updated_chapters
        }

    except Exception as e:

        debug_print(
            "HUMANIZER ERROR:",
            e
        )

        log_trace(
            "humanizer",
            "FAILED",
            str(e)
        )

        raise Exception(
            f"HUMANIZER FAILED: {str(e)}"
        )
