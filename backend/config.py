import os
from dotenv import load_dotenv

load_dotenv()

# Set up paths and configuration
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, 'data').replace('/', os.sep)

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Rachel")

# Simple settings
MAX_LESSON_CHUNKS = 4
ASSESSMENT_QUESTIONS = 5