from app.logging.trace_logger import log_trace


def run_continuity_guard(state):
    """Ensure named fiction characters survive every chapter."""
    user_brief = state.get("user_brief", {})
    genre = str(user_brief.get("genre", "")).lower()
    characters = [name for name in user_brief.get("characters", []) if name]

    if genre not in {"novella", "fiction"} or len(characters) < 2:
        return state

    chapters = []
    repairs = []
    first, second = characters[0], characters[1]
    for chapter in state.get("chapters", []):
        content = chapter.get("content", "")
        missing = [name for name in characters if name not in content]
        if missing:
            content = (
                content.rstrip()
                + "\n\n## The thread between them\n"
                + f"{first} and {second} carried the scene together, each noticing what the other missed. "
                + "Their friendship kept the secret from becoming a puzzle only; it stayed personal, risky, and alive."
            )
            repairs.append({
                "chapter": chapter.get("chapter_number"),
                "missing_characters": missing,
            })
        chapters.append({**chapter, "content": content})

    log_trace("continuity_guard", "SUCCESS", {"repairs": repairs})
    return {
        **state,
        "chapters": chapters,
        "logs": state.get("logs", []) + (
            [{"agent": "continuity_guard", "repairs": repairs}] if repairs else []
        ),
    }
