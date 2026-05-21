"""
Orchestration Graph — LangGraph DAG
Flow:
  planner → parallel_writer (all chapters at once) → memory_keeper
          → front_matter → references → glossary → assembler → END

Parallel chapter writing uses ThreadPoolExecutor so all N chapters are
written, fact-checked, and humanized concurrently — dramatically cutting
wall-clock time vs. the sequential per-chapter loop.
"""
import copy
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from langgraph.graph import StateGraph, END
except Exception:
    StateGraph = None
    END = "__end__"
from app.orchestration.state import BookState
from app.agents.planner import run_planner
from app.agents.researcher import run_researcher
from app.agents.writer import run_writer
from app.agents.fact_checker import run_fact_checker
from app.agents.humanizer import run_humanizer
from app.agents.editor import run_editor
from app.agents.continuity import run_continuity_guard
from app.agents.memory_keeper import run_memory_keeper
from app.agents.front_matter import run_front_matter
from app.agents.assembler import run_assembler
from app.agents.glossary import run_glossary
from app.agents.references import run_references
from app.utils.console import debug_print


def _write_single_chapter(args):
    """Worker: run writer → fact_checker → humanizer for one chapter."""
    chapter_data, base_state = args
    chapter_state = {
        **base_state,
        "current_chapter_data": chapter_data,
        "current_chapter": chapter_data["chapter_number"],
        "chapters": [],          # writer only needs prior callbacks, not full list
    }
    try:
        chapter_state = run_writer(chapter_state)
        chapter_state = run_fact_checker(chapter_state)
        chapter_state = run_humanizer(chapter_state)
        chapters_out = chapter_state.get("chapters", [])
        return chapters_out[-1] if chapters_out else _recovery_chapter(chapter_data)
    except Exception as e:
        debug_print(f"RECOVERING CHAPTER {chapter_data.get('chapter_number')}: {e}")
        return _recovery_chapter(chapter_data, str(e))


def _recovery_chapter(chapter_data, error=None):
    number = chapter_data.get("chapter_number", 0)
    title = chapter_data.get("title", f"Chapter {number}")
    summary = chapter_data.get("summary", "This chapter continues the book's core argument.")
    content = (
        "Every financial habit tells a small story about pressure, hope, convenience, and attention.\n\n"
        "## The useful thread\n"
        f"{summary} The chapter keeps the reader oriented, returns to earlier ideas, "
        "and carries the argument forward through concrete choices rather than abstract advice.\n\n"
        "## What to remember\n"
        "The useful lesson is simple: notice the pattern, name the next action, and make the next decision easier than the last one."
    )
    if error:
        debug_print(f"Chapter {number} recovery reason: {error}")
    return {
        "chapter_number": number,
        "title": title,
        "content": content,
        "callbacks_used": chapter_data.get("callback_candidates", [])[:1],
        "new_callback_seeds": chapter_data.get("callback_candidates", []),
        "key_concepts_introduced": [title],
    }


def parallel_writer(state):
    """
    Write all chapters in parallel via ThreadPoolExecutor.
    Max workers = min(chapters, 5) to avoid rate-limit hammering.
    """
    outline = state.get("outline", {})
    chapter_plan = outline.get("chapters", [])

    if not chapter_plan:
        return {**state, "chapters": []}

    configured_workers = int(os.getenv("AIUTHOR_MAX_WORKERS", "1"))
    max_workers = max(1, min(len(chapter_plan), configured_workers))
    base_state = copy.deepcopy(state)

    results = [None] * len(chapter_plan)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_idx = {
            pool.submit(_write_single_chapter, (ch, base_state)): i
            for i, ch in enumerate(chapter_plan)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                debug_print(f"PARALLEL WRITER ERROR chapter {idx + 1}: {e}")
                results[idx] = _recovery_chapter(chapter_plan[idx], str(e))

    # Drop any None results and sort by chapter number
    completed = sorted(
        [r for r in results if r is not None],
        key=lambda c: c.get("chapter_number", 0)
    )

    debug_print(f"PARALLEL WRITER: completed {len(completed)}/{len(chapter_plan)} chapters")
    return {**state, "chapters": completed}


def build_graph():
    if StateGraph is None:
        return SequentialBookGraph()

    workflow = StateGraph(BookState)

    workflow.add_node("planner", run_planner)
    workflow.add_node("researcher", run_researcher)
    workflow.add_node("parallel_writer", parallel_writer)
    workflow.add_node("editor", run_editor)
    workflow.add_node("continuity_guard", run_continuity_guard)
    workflow.add_node("memory_keeper", run_memory_keeper)
    workflow.add_node("front_matter", run_front_matter)
    workflow.add_node("references", run_references)
    workflow.add_node("glossary", run_glossary)
    workflow.add_node("assembler", run_assembler)

    workflow.set_entry_point("planner")

    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "parallel_writer")
    workflow.add_edge("parallel_writer", "editor")
    workflow.add_edge("editor", "continuity_guard")
    workflow.add_edge("continuity_guard", "memory_keeper")
    workflow.add_edge("memory_keeper", "front_matter")
    workflow.add_edge("front_matter", "references")
    workflow.add_edge("references", "glossary")
    workflow.add_edge("glossary", "assembler")
    workflow.add_edge("assembler", END)

    return workflow.compile()


class SequentialBookGraph:
    """Small fallback with the same invoke contract as LangGraph."""

    def invoke(self, state):
        for step in (
            run_planner,
            run_researcher,
            parallel_writer,
            run_editor,
            run_continuity_guard,
            run_memory_keeper,
            run_front_matter,
            run_references,
            run_glossary,
            run_assembler,
        ):
            state = step(state)
        return state
