import os, json
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from .models import LessonOut

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

@router.post("/api/generate", response_model=LessonOut)
async def generate(topic: str):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="Missing OPENAI_API_KEY")

    schema = LessonOut.model_json_schema()

    sys = (
        "You are ProfAI, a concise Python instructor. "
        "Return a strictly valid JSON object for a micro-lesson with fields: "
        "id, topic, theory (≈200 words), analogy (1-2 sentences), example (short Python), "
        "quiz (3 items with q, choices[], answer), coding {prompt, starter, tests[2] of Python asserts}."
    )
    user = f"Topic: {topic}. Level: beginner. Keep code Python-only and simple."

    rsp = client.responses.create(
        model=MODEL,
        reasoning={"effort":"medium"},
        input=[
            {"role":"system","content":sys},
            {"role":"user","content":user}
        ],
        response_format={
            "type":"json_schema",
            "json_schema": {"name":"LessonOut","schema": schema}
        }
    )

    try:
        data = rsp.output[0].content[0].text
        payload = json.loads(data)
        payload.setdefault("id", topic.lower().replace(" ", "-"))
        return LessonOut(**payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation parse failed: {e}")