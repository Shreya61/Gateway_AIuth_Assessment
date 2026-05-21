import json
import os

from app.main import build_initial_state
from app.orchestration.graph import build_graph
from app.utils.ai_tells import AI_TELLS


REQUIRED_FRONT_BACK = [
    "dedication",
    "epigraph",
    "foreword",
    "preface",
    "acknowledgments",
    "introduction",
    "afterword",
    "about_author",
    "back_cover_copy",
]


def run_smoke_eval():
    os.environ.setdefault("AIUTHOR_OFFLINE", "1")
    state = build_initial_state("Personal Finance", "Conversational", 2, "Beginners")
    result = build_graph().invoke(state)
    all_text = "\n".join(ch.get("content", "") for ch in result.get("chapters", []))
    scores = {
        "chapters_generated": len(result.get("chapters", [])) == 2,
        "front_back_matter": all(result.get(field) for field in REQUIRED_FRONT_BACK),
        "callbacks_rebuilt": bool(result.get("callback_index")),
        "glossary_generated": bool(result.get("glossary")),
        "docx_generated": os.path.exists(result.get("generated_docx", "")),
        "pdf_generated": os.path.exists(result.get("generated_pdf", "")),
        "ai_tells_removed": not any(phrase in all_text.lower() for phrase in AI_TELLS),
        "trace_exists": os.path.exists("traces/agent_trace.jsonl"),
        "prompt_log_exists": os.path.exists("logs/prompt_logs.jsonl"),
    }
    print(json.dumps(scores, indent=2))
    return scores


if __name__ == "__main__":
    run_smoke_eval()
