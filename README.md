# ProfAI - Consolidated Backend Setup

## Quick Start

### 1. Backend (API Server)
```bash
cd backend
pip install -r requirements.txt
python api_server.py
```
Server will start on: http://localhost:5000

### 2. Frontend (React App)
```bash
cd frontend  
npm install
npm run dev
```
App will start on: http://localhost:5173

## Environment Setup

1. Ensure you have a `.env` file in the `backend/` directory with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

2. Install dependencies:
```bash
# Backend
cd backend
pip install openai python-dotenv rich flask flask-cors

# Frontend  
cd frontend
npm install
```

## Repository Structure

```
NeuroAI-HackNation/
├── backend/                  # Consolidated Python backend
│   ├── api_server.py        # Main API server
│   ├── profai_engine.py     # Core AI engine  
│   ├── config.py            # Configuration
│   ├── main.py              # CLI interface
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── data/                # Data storage
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   └── services/
│   └── package.json
└── environment.yml          # Conda environment
```

## What Changed in Phase 1 Consolidation

✅ **Removed redundancies:**
- Deleted V1/ directory (100% duplicate of V2)  
- Deleted V2/ directory (moved to backend/)
- Removed duplicate api_server.py from profai/
- Consolidated data storage

✅ **Moved to backend/:**
- Enhanced ProfAI engine with all V2 features
- Complete API server with all endpoints
- Configuration and requirements
- CLI interface

✅ **Updated imports:**
- Fixed relative import issues
- Updated DATA_DIR to use absolute paths
- Frontend API calls point to consolidated backend

## Next Steps

- **Phase 2:** Clean frontend (remove V2 React implementation) 
- **Phase 3:** Update documentation and test all functionality

---

**Space Saved:** ~60% reduction in duplicate code and files
