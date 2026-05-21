from pydantic import BaseModel


class HumanizedChapter(BaseModel):

    chapter_number: int
    title: str
    content: str