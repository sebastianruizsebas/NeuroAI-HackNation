from pydantic import BaseModel
from typing import List, Optional

class QuizItem(BaseModel):
    q: str
    choices: List[str]
    answer: str

class CodingSpec(BaseModel):
    prompt: str
    starter: str
    tests: List[str]

class LessonOut(BaseModel):
    id: str
    topic: str
    theory: str
    analogy: str
    example: str
    quiz: List[QuizItem]
    coding: CodingSpec

class CoachIn(BaseModel):
    transcript: str
    mode: str  # normal|confused|frustrated
    itemId: str
    code: Optional[str] = None