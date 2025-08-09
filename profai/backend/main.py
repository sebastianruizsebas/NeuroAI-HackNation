import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .generate import router as gen_router
from .coach import router as coach_router

load_dotenv()

app = FastAPI()

# CORS for local vite dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gen_router)
app.include_router(coach_router)

@app.get("/api/health")
def health():
    return {"ok": True, "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")}