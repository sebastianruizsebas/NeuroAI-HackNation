from fastapi import APIRouter
from .pretest import router as pretest

api = APIRouter()
api.include_router(pretest)