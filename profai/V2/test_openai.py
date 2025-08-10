# Create a test file: test_openai.py
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    print("OpenAI API is working!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"OpenAI API Error: {e}")