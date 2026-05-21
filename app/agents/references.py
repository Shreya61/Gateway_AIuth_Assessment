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


reference_prompt = """
You are the References Agent.

Your responsibilities:
- identify major concepts discussed
- generate topical reference categories
- support hallucination-safe publishing
- avoid fabricated authority

STRICT RULES:
- NEVER invent citations
- NEVER invent authors
- NEVER invent books
- NEVER invent studies
- NEVER invent journals
- NEVER fabricate research papers

ONLY generate:
- topical domains
- broad research areas
- educational categories

GOOD:
- Behavioral Psychology Literature
- Emotional Intelligence Research
- Cognitive Bias Studies

BAD:
- Smith et al. 2022
- Journal of Dark Manipulation

STYLE RULES:
- references should feel credible
- references should remain broad
- avoid redundancy
- avoid excessive specificity

Return ONLY valid JSON.

FORMAT:
{
  "references": [
    ""
  ]
}
"""


def run_references(state):

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

            reference_prompt

            + f"\n\nBOOK CONTENT:\n"
            + combined_text
        )

        response = llm.invoke(
            final_prompt
        )

        raw_output = response.content

        log_prompt(
            "references",
            final_prompt,
            raw_output
        )

        parsed = clean_json_response(
            raw_output
        )

        references = parsed.get(
            "references",
            []
        )

        log_trace(
            "references",
            "SUCCESS"
        )

        return {

            **state,

            "references":
                references
        }

    except Exception as e:

        log_trace(
            "references",
            "FAILED",
            str(e)
        )

        return {

            **state,

            "logs":
                state["logs"] + [
                    {
                        "agent":
                            "references",

                        "error":
                            str(e)
                    }
                ]
        }