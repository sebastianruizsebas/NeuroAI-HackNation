# ProfAI — Python Micro‑Learning with OpenAI

## Prereqs
- Python 3.10+
- Node 18+

## Run backend
```bash
cd backend
cp .env.example .env   # paste your OPENAI_API_KEY
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000