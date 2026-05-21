import json

from app.utils.llm import get_writer_llm

from app.schemas.planner_schema import (
    BookOutlineSchema
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


planner_prompt = """
You are the Planner Agent.

Your responsibility:
Create publication-quality book outlines
with strong narrative progression,
logical chapter sequencing,
callback opportunities,
and thematic continuity.

STRICT RULES:
- Create emotionally compelling titles
- Ensure progressive knowledge flow
- Each chapter must naturally connect
  to previous and future chapters
- Generate meaningful callback candidates
- Maintain consistency with tone
- If genre is fiction or novella, preserve named characters across all chapter summaries
- If the brief includes characters, every chapter plan must mention those characters by name
- Avoid generic chapter naming
- Avoid repetitive structures

STYLE RULES:
- Titles should feel publishable
- Summaries should feel human-written
- Chapters should escalate naturally
- Avoid robotic educational phrasing

BANNED PHRASES:
- comprehensive guide
- ultimate guide
- deep dive
- overview of
- understanding the basics
- in this chapter we will

Return ONLY valid JSON.

FORMAT:
{
  "book_title": "",
  "chapters": [
    {
      "chapter_number": 1,
      "title": "",
      "summary": "",
      "callback_candidates": []
    }
  ]
}
"""


def run_planner(state):

    try:

        llm = get_writer_llm()

        increment_calls()

        final_prompt = (
            planner_prompt
            + f"\n\nUSER BRIEF:\n{state['user_brief']}"
        )

        response = llm.invoke(final_prompt)

        raw_output = response.content
        debug_print("\nPLANNER RAW OUTPUT:\n")
        debug_print(raw_output)
        debug_print("\n")

        log_prompt(
            "planner",
            final_prompt,
            raw_output
        )

        parsed = clean_json_response(raw_output)
        validated = BookOutlineSchema(**parsed)


        # cleaned_output = raw_output.strip()

        # # Remove markdown fences
        # cleaned_output = cleaned_output.replace(
        #     "```json",
        #     ""
        # )

        # cleaned_output = cleaned_output.replace(
        #     "```",
        #     ""
        # )

        # cleaned_output = cleaned_output.strip()

        # parsed = json.loads(cleaned_output)

        # validated = BookOutlineSchema(**parsed)

        log_trace(
            "planner",
            "SUCCESS"
        )

        return {
            **state,
            "outline": validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
        }

    except Exception as e:

        log_trace(
            "planner",
            "FAILED",
            str(e)
        )
        debug_print("PLANNER ERROR:", e)

        return {
            **state,
            "logs": state["logs"] + [
                {
                    "agent": "planner",
                    "error": str(e)
                }
            ]
        }
