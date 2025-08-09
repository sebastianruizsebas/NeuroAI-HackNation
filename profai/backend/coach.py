import os
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from .models import CoachIn

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

@router.post("/api/coach")
async def coach(inp: CoachIn):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="Missing OPENAI_API_KEY")

    sys = (
        "You are ProfAI, an empathetic Python tutor for micro-lessons. "
        "Keep replies under 80 words. If mode=confused: add a tiny analogy + 1 example. "
        "If mode=frustrated: propose a minimal patch and precise reason."
    )

    content = [
        {"role":"system","content":sys},
        {"role":"user","content": f"mode={inp.mode}; question={inp.transcript}; code={inp.code or ''}"}
    ]

    rsp = client.responses.create(model=MODEL, input=content)
    return {"reply": rsp.output_text}