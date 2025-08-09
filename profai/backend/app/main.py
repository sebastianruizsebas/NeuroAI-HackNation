from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import logger
from .models.db import init_db
from .api.router import api

app = FastAPI(title="ProfAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
app.include_router(api)

@app.get("/api/health")
def health():
    logger.info("health")
    return {"ok": True}