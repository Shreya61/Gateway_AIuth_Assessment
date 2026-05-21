from app.utils.llm import get_fast_llm
from app.logging.prompt_logger import log_prompt
from app.logging.trace_logger import log_trace
from app.logging.cost_tracker import increment_calls
from app.utils.json_parser import clean_json_response


front_matter_prompt = """
You are the Front Matter Agent.

Create publication-ready front and back matter that matches the selected tone.

STRICT RULES:
- Cascade tonality through every section
- Mention no fabricated credentials
- Keep claims modest and grounded
- Return ONLY valid JSON

FORMAT:
{
  "dedication": "",
  "epigraph": "",
  "foreword": "",
  "preface": "",
  "acknowledgments": "",
  "introduction": "",
  "afterword": "",
  "about_author": "",
  "back_cover_copy": ""
}
"""


def run_front_matter(state):
    try:
        llm = get_fast_llm()
        increment_calls()
        final_prompt = (
            front_matter_prompt
            + f"\n\nUSER BRIEF:\n{state.get('user_brief', {})}"
            + f"\n\nOUTLINE:\n{state.get('outline', {})}"
            + f"\n\nMEMORY:\n{state.get('callback_index', [])}"
        )
        response = llm.invoke(final_prompt)
        raw_output = response.content
        log_prompt("front_matter", final_prompt, raw_output)
        parsed = clean_json_response(raw_output)
        log_trace("front_matter", "SUCCESS")
        return {**state, **parsed}
    except Exception as e:
        log_trace("front_matter", "FAILED", str(e))
        topic = state.get("user_brief", {}).get("topic", "the subject")
        return {
            **state,
            "dedication": "For readers building a sturdier next page.",
            "epigraph": "Small choices become a map when you keep returning to them.",
            "foreword": f"This book approaches {topic} with clarity, restraint, and care.",
            "preface": "This system writes through planning, memory, critique, and revision.",
            "acknowledgments": "Thanks to the reviewers and test runs that exposed weak drafts.",
            "introduction": f"This book begins with {topic} and keeps its promises through remembered callbacks.",
            "afterword": "The ending is a handoff into practice.",
            "about_author": "AIuthor is an auditable multi-agent book generation system.",
            "back_cover_copy": f"A grounded, reader-aware book about {topic}.",
        }
