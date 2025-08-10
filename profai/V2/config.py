import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# Simple settings
MAX_LESSON_CHUNKS = 4
ASSESSMENT_QUESTIONS = 5
DATA_DIR = "data"