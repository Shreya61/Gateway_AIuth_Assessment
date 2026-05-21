from pydantic import BaseModel
from typing import List


class ChapterOutput(BaseModel):

    chapter_number: int
    title: str
    content: str
    callbacks_used: List[str]