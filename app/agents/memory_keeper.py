from app.logging.trace_logger import log_trace


def run_memory_keeper(state):
    """Build durable book memory after chapter generation."""
    chapters = state.get("chapters", [])
    facts = []
    concepts = []
    callbacks = []

    for chapter in chapters:
        number = chapter.get("chapter_number")
        title = chapter.get("title", "")
        for callback in chapter.get("callbacks_used", []):
            callbacks.append({"chapter": number, "callback": callback, "source": title})
        concepts.append({
            "id": f"chapter-{number}",
            "name": title,
            "introduced_in": number,
            "notes": chapter.get("content", "")[:240],
        })

    decision_log = state.get("decision_log", [])
    decision_log.append({
        "decision": "Chapter memory rebuilt after generation",
        "reason": "Keeps callback index, concept bible, and downstream glossary assembly repairable.",
    })

    log_trace("memory_keeper", "SUCCESS")
    return {
        **state,
        "facts": facts,
        "concept_bible": concepts,
        "callback_index": callbacks,
        "callbacks": callbacks,
        "decision_log": decision_log,
        "memory_io": state.get("memory_io", []) + [{
            "agent": "memory_keeper",
            "reads": ["chapters"],
            "writes": ["facts", "concept_bible", "callback_index", "decision_log"],
        }],
    }
