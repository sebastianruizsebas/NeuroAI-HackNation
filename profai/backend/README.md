## Run
```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


---

## Frontend (Vite + React)

### `frontend/package.json`
```json
{
  "name": "profai-front",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {"dev":"vite","build":"vite build","preview":"vite preview"},
  "dependencies": {"react":"^18.3.1","react-dom":"^18.3.1","@monaco-editor/react":"^4.6.0"},
  "devDependencies": {"@types/react":"^18.3.3","@types/react-dom":"^18.3.0","@vitejs/plugin-react":"^4.3.1","typescript":"^5.5.4","vite":"^5.4.1"}
}