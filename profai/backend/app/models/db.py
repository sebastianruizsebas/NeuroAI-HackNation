from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from ..core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Competency(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    topic: str
    sup: float
    unsup: float
    rl: float
    gen: float

class Topic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str
    title: str
    canonical_outline: str  # JSON string


def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)