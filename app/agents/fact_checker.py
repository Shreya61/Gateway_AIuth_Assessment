import time

from app.utils.llm import get_fast_llm

from app.schemas.fact_checker_schema import (
    FactCheckResult
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


fact_checker_prompt = """
You are the Fact Checker Agent.

Your responsibilities:
- identify unsupported claims
- soften unverifiable certainty
- preserve readability
- preserve emotional tone

STRICT RULES:
- NEVER invent sources
- NEVER fabricate studies
- NEVER fabricate statistics
- NEVER fabricate percentages
- NEVER fabricate experts

IMPORTANT:
- flagged_claims MUST be list of strings
- softened_claims MUST be list of strings
- Return ONLY valid JSON
- No markdown
- No explanations

FORMAT:
{
  "chapter_number": 1,
  "corrected_content": "",
  "flagged_claims": [],
  "softened_claims": []
}
"""


def repair_json(llm, raw_output):

    repair_prompt = f"""
Repair this broken JSON.

RULES:
- Return ONLY valid JSON
- No markdown
- Preserve meaning

BROKEN JSON:
{raw_output}
"""

    repaired_response = llm.invoke(
        repair_prompt
    )

    return repaired_response.content


def run_fact_checker(state):

    try:

        llm = get_fast_llm()

        increment_calls()

        latest_chapter = (
            state["chapters"][-1]
        )

        final_prompt = (
            fact_checker_prompt
            + f"\n\nCHAPTER:\n{latest_chapter}"
        )

        debug_print("\nRUNNING FACT CHECKER...\n")

        response = llm.invoke(
            final_prompt
        )

        raw_output = response.content

        debug_print("\nFACT CHECKER RAW OUTPUT:\n")
        debug_print(raw_output)

        log_prompt(
            "fact_checker",
            final_prompt,
            raw_output
        )

        # --------------------------------------------
        # FIRST PARSE ATTEMPT
        # --------------------------------------------

        try:

            parsed = clean_json_response(
                raw_output
            )

        except Exception:

            debug_print("\nFACT CHECKER JSON FAILED")
            debug_print("ATTEMPTING REPAIR...\n")

            repaired_output = repair_json(
                llm,
                raw_output
            )

            debug_print("\nREPAIRED FACT CHECKER OUTPUT:\n")
            debug_print(repaired_output)

            parsed = clean_json_response(
                repaired_output
            )

        # --------------------------------------------
        # FORCE SAFE TYPES
        # --------------------------------------------

        if not isinstance(
            parsed.get(
                "flagged_claims",
                []
            ),
            list
        ):

            parsed["flagged_claims"] = []

        if not isinstance(
            parsed.get(
                "softened_claims",
                []
            ),
            list
        ):

            parsed["softened_claims"] = []

        parsed["flagged_claims"] = [

            str(item)

            for item in parsed[
                "flagged_claims"
            ]
        ]

        parsed["softened_claims"] = [

            str(item)

            for item in parsed[
                "softened_claims"
            ]
        ]

        validated = FactCheckResult(
            **parsed
        )

        updated_chapters = (
            state["chapters"][:]
        )

        updated_chapters[-1]["content"] = (
            validated.corrected_content
        )

        log_trace(
            "fact_checker",
            "SUCCESS"
        )

        debug_print("\nFACT CHECK COMPLETE\n")

        time.sleep(1)

        return {

            **state,

            "chapters":
                updated_chapters,

            "logs":
                state["logs"] + [
                    {
                        "agent":
                            "fact_checker",

                        "flagged_claims":
                            validated.flagged_claims,

                        "softened_claims":
                            validated.softened_claims
                    }
                ]
        }

    except Exception as e:

        debug_print(
            "\nFACT CHECKER ERROR:\n",
            e
        )

        log_trace(
            "fact_checker",
            "FAILED",
            str(e)
        )

        raise Exception(
            f"FACT CHECKER FAILED: {str(e)}"
        )
