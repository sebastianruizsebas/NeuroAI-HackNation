import json
import os
from datetime import datetime
from typing import Dict, List, Any
import openai
from config import OPENAI_API_KEY, DATA_DIR

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

class ProfAIEngine:
    def __init__(self):
        self.users_file = f"{DATA_DIR}/users.json"
        self.lessons_file = f"{DATA_DIR}/lessons.json"
        self.sessions_file = f"{DATA_DIR}/sessions.json"
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Create data files if they don't exist"""
        os.makedirs(DATA_DIR, exist_ok=True)
        for file_path in [self.users_file, self.lessons_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump([], f)
    
    def load_data(self, file_path: str) -> Any:
        """Load JSON data from file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def save_data(self, file_path: str, data: Any):
        """Save JSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_user(self, name: str) -> str:
        """Create a new user"""
        users = self.load_data(self.users_file)
        user_id = f"user_{len(users) + 1}"
        users[user_id] = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "competency_scores": {},
            "total_lessons": 0
        }
        self.save_data(self.users_file, users)
        return user_id
    
    def get_user(self, user_id: str) -> Dict:
        """Get user data"""
        users = self.load_data(self.users_file)
        return users.get(user_id, {})
    
    def generate_assessment_questions(self, topic: str) -> List[Dict]:
        """Generate assessment questions for a topic"""
        prompt = f"""Create 5 multiple choice questions to assess knowledge about {topic}.
        Make them range from basic to intermediate difficulty.
        
        Return ONLY a JSON array with this format:
        [
            {{
                "question": "What is...",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct": "A",
                "difficulty": 1
            }}
        ]
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
    
    def generate_lesson_content(self, topic: str, user_profile: Dict) -> Dict:
        """Generate personalized lesson content"""
        competency = user_profile.get('competency_scores', {}).get(topic, 0)
        
        prompt = f"""Create a lesson about {topic} for someone with competency level {competency}/10.
        
        Structure the lesson with:
        1. Brief overview
        2. 4 main learning chunks (each should be digestible in 2-3 minutes)
        3. Key takeaways
        
        Return ONLY a JSON object with this format:
        {{
            "topic": "{topic}",
            "overview": "Brief overview...",
            "chunks": [
                {{
                    "title": "Chunk 1 Title",
                    "content": "Detailed explanation...",
                    "key_point": "Main takeaway"
                }}
            ],
            "key_takeaways": ["Point 1", "Point 2", "Point 3"]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            lesson = json.loads(content)
            
            # Save lesson to local storage
            lessons = self.load_data(self.lessons_file)
            lesson_id = f"lesson_{len(lessons) + 1}"
            lessons[lesson_id] = lesson
            self.save_data(self.lessons_file, lessons)
            
            return lesson
        except Exception as e:
            print(f"Error generating lesson: {e}")
            return {}
    
    def analyze_sentiment(self, user_response: str) -> Dict:
        """Analyze user response for confusion/frustration"""
        prompt = f"""Analyze this student response for emotional state and understanding level:
        "{user_response}"
        
        Return ONLY a JSON object:
        {{
            "confusion_level": 0.0,
            "frustration_level": 0.0,
            "confidence_level": 0.0,
            "understanding": "high/medium/low",
            "suggestion": "Brief teaching adjustment suggestion"
        }}
        
        Scale: 0.0 = none, 1.0 = maximum
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                "confusion_level": 0.0,
                "frustration_level": 0.0,
                "confidence_level": 0.5,
                "understanding": "medium",
                "suggestion": "Continue with current pace"
            }
    
    def update_user_competency(self, user_id: str, topic: str, score: float):
        """Update user's competency score for a topic"""
        users = self.load_data(self.users_file)
        if user_id in users:
            users[user_id]['competency_scores'][topic] = score
            users[user_id]['total_lessons'] += 1
            self.save_data(self.users_file, users)
    
    def save_session(self, user_id: str, session_data: Dict):
        """Save a complete learning session"""
        sessions = self.load_data(self.sessions_file)
        session_data['user_id'] = user_id
        session_data['timestamp'] = datetime.now().isoformat()
        sessions.append(session_data)
        self.save_data(self.sessions_file, sessions)