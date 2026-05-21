from pydantic import BaseModel
from typing import List


class FactCheckResult(BaseModel):

    chapter_number: int

    corrected_content: str

    flagged_claims: List[str]

    softened_claims: List[str]