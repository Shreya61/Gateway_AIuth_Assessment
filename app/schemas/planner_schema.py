from pydantic import BaseModel
from typing import List


class ChapterSchema(BaseModel):

    chapter_number: int
    title: str
    summary: str
    callback_candidates: List[str]


class BookOutlineSchema(BaseModel):

    book_title: str
    chapters: List[ChapterSchema]