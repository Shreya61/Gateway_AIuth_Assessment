import os

import streamlit as st

from app.main import build_initial_state
from app.orchestration.graph import build_graph
from app.logging.cost_tracker import get_cost_summary


st.set_page_config(page_title="AIuthor", layout="wide")

st.title("AIuthor")
st.subheader("Agentic Book Generation System")

st.sidebar.header("Book Configuration")

topic = st.sidebar.text_area("Topic", "Personal Finance", height=80)
reader_profile = st.sidebar.text_input("Reader profile", "Beginners")
length = st.sidebar.text_input("Length target", "short MVP")
genre = st.sidebar.selectbox(
    "Genre",
    ["Beginner nonfiction guide", "Novella", "Fiction", "Nonfiction"],
)
tone = st.sidebar.selectbox(
    "Tone",
    ["Conversational", "Academic", "Storyteller", "Motivational", "Witty"],
)
chapter_count = st.sidebar.slider("Chapters", 1, 10, 5)
characters_text = st.sidebar.text_input(
    "Named characters",
    "Mira, Jonah" if genre in {"Novella", "Fiction"} else "",
)
output_slug = st.sidebar.text_input("Output filename", "generated_book")

st.sidebar.header("Run Controls")
offline_mode = st.sidebar.checkbox(
    "Offline smoke mode",
    value=os.getenv("AIUTHOR_OFFLINE", "1").lower() in {"1", "true", "yes"},
)
max_workers = st.sidebar.number_input(
    "Max workers",
    min_value=1,
    max_value=5,
    value=int(os.getenv("AIUTHOR_MAX_WORKERS", "1")),
)

generate = st.sidebar.button("Generate Book", type="primary")


if generate:
    os.environ["AIUTHOR_OFFLINE"] = "1" if offline_mode else "0"
    os.environ["AIUTHOR_MAX_WORKERS"] = str(max_workers)

    characters = [name.strip() for name in characters_text.split(",") if name.strip()]
    initial_state = build_initial_state(
        topic=topic,
        tone=tone,
        chapters=chapter_count,
        reader_profile=reader_profile,
        length=length,
        genre=genre,
        characters=characters,
        output_slug=output_slug,
    )

    with st.spinner("Generating book..."):
        result = build_graph().invoke(initial_state)

    outline = result.get("outline", {})
    chapters = result.get("chapters", [])

    tab_chapters, tab_outline, tab_memory, tab_logs = st.tabs(
        ["Chapters", "Outline", "Memory", "Logs"]
    )

    with tab_chapters:
        st.title(outline.get("book_title", "Untitled Book"))
        if not chapters:
            st.warning("No chapters generated.")
        for chapter in chapters:
            st.markdown(
                f"## Chapter {chapter.get('chapter_number')}: {chapter.get('title')}"
            )
            st.write(chapter.get("content", ""))
            st.divider()

    with tab_outline:
        st.json(outline)

    with tab_memory:
        st.subheader("Callback Index")
        st.json(result.get("callback_index", []))
        st.subheader("Concept Bible")
        st.json(result.get("concept_bible", []))
        st.subheader("Glossary")
        st.json(result.get("glossary", []))
        st.subheader("Memory I/O")
        st.json(result.get("memory_io", []))

    with tab_logs:
        st.json(result.get("logs", []))

    st.subheader("System Metrics")
    cost_summary = get_cost_summary()
    col1, col2, col3 = st.columns(3)
    col1.metric("LLM Calls", cost_summary["total_llm_calls"])
    col2.metric("Callbacks Stored", len(result.get("callbacks", [])))
    col3.metric("Chapters", len(chapters))

    col_docx, col_pdf = st.columns(2)
    if result.get("generated_docx"):
        with open(result["generated_docx"], "rb") as file:
            col_docx.download_button(
                label="Download DOCX",
                data=file,
                file_name="generated_book.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

    if result.get("generated_pdf"):
        with open(result["generated_pdf"], "rb") as file:
            col_pdf.download_button(
                label="Download PDF",
                data=file,
                file_name="generated_book.pdf",
                mime="application/pdf",
            )
else:
    st.info("Configure a brief in the sidebar, then generate a book.")
