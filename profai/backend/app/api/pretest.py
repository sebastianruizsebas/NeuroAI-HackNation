from fastapi import APIRouter, HTTPException
from ..core.openai_client import client, MODEL
from ..models.schemas import PretestOut, QItem, AnswersIn, CompetencyVector, Section
import json

router = APIRouter(prefix="/api/pretest", tags=["pretest"])

GEN_SCHEMA = PretestOut.model_json_schema()

@router.post("/init", response_model=PretestOut)
async def pretest_init():
    sys = "Generate 5 beginner MCQs covering 4 sections: sup, unsup, rl, gen. Each must have {section, difficulty (1..5), stem, choices[4], answer, explain}. Keep stems concise."
    user = {"sections":["sup","unsup","rl","gen"], "count":5}
    rsp = client.responses.create(
        model=MODEL,
        input=[{"role":"system","content":sys},{"role":"user","content":json.dumps(user)}],
        response_format={"type":"json_schema","json_schema":{"name":"PretestOut","schema":GEN_SCHEMA}}
    )
    data = rsp.output[0].content[0].text
    payload = json.loads(data)
    return PretestOut(**payload)

@router.post("/adaptive", response_model=PretestOut)
async def pretest_adaptive(base: PretestOut, base_answers: AnswersIn):
    # Build difficulty hints per section from first 5 answers
    correct = 0
    by_sec: dict[Section, int] = {"sup":0,"unsup":0,"rl":0,"gen":0}
    for ans, sec, q in zip(base_answers.answers, base_answers.mapping, base.questions):
        if ans.strip() == q.answer.strip():
            correct += 1
            by_sec[sec] += 1
    hints = {k: ("hard" if v>=1 else "easy") for k,v in by_sec.items()}

    schema = GEN_SCHEMA
    sys = "Generate 5 adaptive MCQs. Use provided difficulty hints per section. Keep same JSON schema."
    user = {"hints":hints, "avoid_stems":[q.stem for q in base.questions]}
    rsp = client.responses.create(
        model=MODEL,
        input=[{"role":"system","content":sys},{"role":"user","content":json.dumps(user)}],
        response_format={"type":"json_schema","json_schema":{"name":"PretestOut","schema":schema}}
    )
    data = rsp.output[0].content[0].text
    payload = json.loads(data)
    return PretestOut(**payload)

@router.post("/score", response_model=CompetencyVector)
async def pretest_score(all_qs: list[QItem], all_answers: list[str]):
    by = {"sup":[0,0],"unsup":[0,0],"rl":[0,0],"gen":[0,0]}  # [correct,total]
    for q,a in zip(all_qs, all_answers):
        by[q.section][1]+=1
        if a.strip()==q.answer.strip():
            by[q.section][0]+=1
    def norm(c,t):
        return round((c/t if t else 0.0), 3)
    return CompetencyVector(
        sup=norm(*by["sup"]), unsup=norm(*by["unsup"]), rl=norm(*by["rl"]), gen=norm(*by["gen"]) )