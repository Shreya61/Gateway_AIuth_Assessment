from typing import (
    TypedDict,
    Dict,
    List,
    Any
)


class BookState(TypedDict):

    user_brief: Dict[str, Any]

    outline: Dict[str, Any]

    current_chapter: int

    current_chapter_data: Dict[str, Any]

    chapter_text: str

    chapters: List[Dict[str, Any]]

    facts: List[Dict[str, Any]]

    glossary: List[Dict[str, Any]]
    
    references: List[str]

    callbacks: List[Dict[str, Any]]

    tone_profile: Dict[str, Any]

    research_notes: List[Dict[str, Any]]

    concept_bible: List[Dict[str, Any]]

    callback_index: List[Dict[str, Any]]

    decision_log: List[Dict[str, Any]]

    memory_io: List[Dict[str, Any]]

    logs: List[Dict[str, Any]]

    generated_docx: str
