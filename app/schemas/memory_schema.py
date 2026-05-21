from pydantic import BaseModel
from typing import List


class CallbackMemory(BaseModel):

    callback_phrase: str
    introduced_in_chapter: int
    reused_in: List[int] = []


class FactMemory(BaseModel):

    fact: str
    source: str
    used_in_chapters: List[int] = []


class ToneMemory(BaseModel):

    tone_name: str
    writing_style: str
    sentence_rhythm: str
    humor_level: float