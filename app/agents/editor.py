from app.logging.trace_logger import log_trace
from app.utils.ai_tells import AI_TELLS


def run_editor(state):
    edited = []
    for chapter in state.get("chapters", []):
        content = chapter.get("content", "")
        for phrase in AI_TELLS:
            content = content.replace(phrase, "")
        edited.append({**chapter, "content": content.strip()})
    log_trace("editor", "SUCCESS")
    return {**state, "chapters": edited}
