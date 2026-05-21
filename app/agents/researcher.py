from app.logging.trace_logger import log_trace


def run_researcher(state):
    """Quota-safe research scaffold for grounded claims and future RAG/web tools."""
    topic = state.get("user_brief", {}).get("topic", "the topic")
    research_notes = [
        {
            "claim": f"Chapters about {topic} should distinguish general guidance from factual claims.",
            "source_type": "system_note",
            "confidence": "medium",
            "citation": "No external citation used in offline mode",
        }
    ]
    log_trace("researcher", "SUCCESS")
    return {
        **state,
        "research_notes": research_notes,
        "memory_io": state.get("memory_io", []) + [{
            "agent": "researcher",
            "reads": ["user_brief", "outline"],
            "writes": ["research_notes"],
        }],
    }
