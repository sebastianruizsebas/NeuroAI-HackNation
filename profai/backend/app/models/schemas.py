from pydantic import BaseModel
from typing import List, Literal

Section = Literal["sup","unsup","rl","gen"]

class QItem(BaseModel):
    section: Section
    difficulty: int  # 1..5
    stem: str
    choices: list[str]
    answer: str
    explain: str

class PretestOut(BaseModel):
    questions: List[QItem]

class AnswersIn(BaseModel):
    answers: list[str]
    mapping: list[Section]

class CompetencyVector(BaseModel):
    sup: float; unsup: float; rl: float; gen: float