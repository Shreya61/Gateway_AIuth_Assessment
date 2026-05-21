import json

from app.utils.llm import (
    get_fast_llm
)

from app.logging.trace_logger import (
    log_trace
)

from app.logging.prompt_logger import (
    log_prompt
)

from app.logging.cost_tracker import (
    increment_calls
)

from app.utils.json_parser import (
    clean_json_response
)


glossary_prompt = """
You are the Glossary Agent.

Your responsibility:
Extract meaningful concepts from the book
and generate publication-quality glossary entries.

STRICT RULES:
- Terms must appear in chapters
- Definitions must match book tone
- Definitions must feel human-written
- Avoid generic dictionary phrasing
- Vary definition rhythm and structure
- Some definitions should be concise
- Some definitions should use examples
- Preserve readability

STYLE RULES:
- Sound natural
- Avoid repetitive definition patterns
- Avoid textbook phrasing
- Make definitions accessible

BAD:
"Manipulation is the act of manipulating."

GOOD:
"Manipulation happens when someone quietly
pushes another person toward decisions
that primarily benefit the manipulator."

Return ONLY valid JSON.

FORMAT:
{
  "terms": [
    {
      "term": "",
      "definition": ""
    }
  ]
}
"""


def run_glossary(state):

    try:

        llm = get_fast_llm()

        increment_calls()

        chapters = state["chapters"]

        combined_text = ""

        for chapter in chapters:

            combined_text += (
                chapter["content"] + "\n\n"
            )

        final_prompt = (

            glossary_prompt

            + f"\n\nBOOK CONTENT:\n"
            + combined_text
        )

        response = llm.invoke(
            final_prompt
        )

        raw_output = response.content

        log_prompt(
            "glossary",
            final_prompt,
            raw_output
        )

        parsed = clean_json_response(
            raw_output
        )

        glossary = parsed.get(
            "terms",
            []
        )

        log_trace(
            "glossary",
            "SUCCESS"
        )

        return {

            **state,

            "glossary":
                glossary
        }

    except Exception as e:

        log_trace(
            "glossary",
            "FAILED",
            str(e)
        )

        return {

            **state,

            "logs":
                state["logs"] + [
                    {
                        "agent":
                            "glossary",

                        "error":
                            str(e)
                    }
                ]
        }