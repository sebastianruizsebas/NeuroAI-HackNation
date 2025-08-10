import json
import os
import traceback
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import openai
from progress_utils import (
    calculate_lesson_deadlines,
    update_lesson_progress,
    get_lesson_deadlines,
    update_topic_progress,
    get_topic_complete_data
)

# Import from local config
from config import OPENAI_API_KEY, DATA_DIR

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

class ProfAIEngine:
    def generate_initial_assessment(self, topic: str) -> List[Dict]:
        """Generate 5 very beginner-friendly questions for pre-competency test."""
        try:
            from rag_utils import load_all_chunks, find_relevant_chunks
            base_dir = os.path.dirname(__file__)
            chunk_files = [
                os.path.join(base_dir, 'math_ml_chunks.json'),
                os.path.join(base_dir, 'mit_ocw_chunks.json'),
            ]
            chunks = load_all_chunks(chunk_files)
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=5)
            if relevant_chunks:
                context = '\n\n'.join([f"EDUCATIONAL CONTENT FROM {fname}:\n{chunk}" for fname, chunk in relevant_chunks])
            else:
                context = "No specific course material found. Use general machine learning principles."
        except Exception as rag_e:
            print(f"RAG retrieval failed (assessment): {rag_e}")
            context = "No specific course material found. Use general machine learning principles."

        prompt = f"""You are a world-class AI tutor. Create exactly 5 multiple-choice questions for a PRE-TEST on the topic '{topic}'.\n\nREQUIREMENTS:\n1. All questions must be suitable for ABSOLUTE BEGINNERS with no prior experience.\n2. Focus on basic definitions, simple concepts, and fundamental understanding.\n3. Avoid technical jargon, advanced math, or code.\n4. Each question should have 4 options (A-D), only one correct.\n5. Use clear, simple language and real-world analogies if possible.\n6. Base questions on the following course material if available:\n{context}\n\nReturn ONLY a JSON array with this format:\n[\n    {{\n        \"question\": \"...\",\n        \"options\": [\"A) ...\", \"B) ...\", \"C) ...\", \"D) ...\"],\n        \"correct\": \"A\",\n        \"concept\": \"...\",\n        \"difficulty\": 1,\n        \"explanation\": \"...\"\n    }}\n]\n"""
        try:
            print(f"Calling OpenAI API for initial beginner assessment on topic: {topic}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                timeout=30
            )
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            questions = json.loads(content)
            return questions
        except Exception as e:
            print(f"Error generating initial assessment: {e}")
            # Fallback: return 5 basic template questions
            return [
                {
                    "question": f"What is the main idea of {topic}?",
                    "options": ["A) A basic explanation", "B) An unrelated concept", "C) A technical detail", "D) None of the above"],
                    "correct": "A",
                    "concept": topic,
                    "difficulty": 1,
                    "explanation": f"{topic} is best understood as..."
                }
            ] * 5

    def generate_adaptive_assessment(self, topic: str, previous_answers: list) -> List[Dict]:
        """Generate 5 more questions, adaptively increasing difficulty if user did well on the first 5."""
        # Count correct answers (assume previous_answers is a list of bools or 0/1)
        correct = sum(1 for a in previous_answers if a)
        if correct >= 4:
            difficulty = "intermediate to advanced"
            prompt_level = "Increase the difficulty for each question. Include some intermediate and advanced concepts, simple math, or real-world scenarios."
        elif correct >= 2:
            difficulty = "intermediate"
            prompt_level = "Make the questions a mix of basic and intermediate. Introduce some practical scenarios or slightly more technical terms."
        else:
            difficulty = "basic"
            prompt_level = "Keep all questions beginner-friendly, but introduce a few slightly more detailed concepts."
        try:
            from rag_utils import load_all_chunks, find_relevant_chunks
            base_dir = os.path.dirname(__file__)
            chunk_files = [
                os.path.join(base_dir, 'math_ml_chunks.json'),
                os.path.join(base_dir, 'mit_ocw_chunks.json'),
            ]
            chunks = load_all_chunks(chunk_files)
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=5)
            if relevant_chunks:
                context = '\n\n'.join([f"EDUCATIONAL CONTENT FROM {fname}:\n{chunk}" for fname, chunk in relevant_chunks])
            else:
                context = "No specific course material found. Use general machine learning principles."
        except Exception as rag_e:
            print(f"RAG retrieval failed (adaptive assessment): {rag_e}")
            context = "No specific course material found. Use general machine learning principles."

        prompt = f"""You are a world-class AI tutor. Create exactly 5 multiple-choice questions for a COMPETENCY TEST on the topic '{topic}'.\n\nREQUIREMENTS:\n1. Each question should be {difficulty}. {prompt_level}\n2. Each question should have 4 options (A-D), only one correct.\n3. Use clear, academic language, but keep it accessible.\n4. Base questions on the following course material if available:\n{context}\n\nReturn ONLY a JSON array with this format:\n[\n    {{\n        \"question\": \"...\",\n        \"options\": [\"A) ...\", \"B) ...\", \"C) ...\", \"D) ...\"],\n        \"correct\": \"A\",\n        \"concept\": \"...\",\n        \"difficulty\": 2,\n        \"explanation\": \"...\"\n    }}\n]\n"""
        try:
            print(f"Calling OpenAI API for adaptive assessment on topic: {topic}, difficulty: {difficulty}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                timeout=30
            )
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            questions = json.loads(content)
            return questions
        except Exception as e:
            print(f"Error generating adaptive assessment: {e}")
            # Fallback: return 5 template questions
            return [
                {
                    "question": f"(Adaptive) What is a key concept in {topic}?",
                    "options": ["A) Correct concept", "B) Wrong", "C) Wrong", "D) Wrong"],
                    "correct": "A",
                    "concept": topic,
                    "difficulty": 2,
                    "explanation": f"This is a key concept in {topic}."
                }
            ] * 5
    def __init__(self):
        print("[__init__] Initializing ProfAIEngine")
        self.users_file = os.path.join(DATA_DIR, "users.json")  # Use os.path.join for cross-platform compatibility
        self.lessons_file = os.path.join(DATA_DIR, "lessons.json")
        self.sessions_file = os.path.join(DATA_DIR, "sessions.json")
        self.progress_file = os.path.join(DATA_DIR, "progress.json")
        self.curriculum_file = os.path.join(DATA_DIR, "curriculum.json")
        print(f"[__init__] Data directory: {DATA_DIR}")
        print(f"[__init__] Users file path: {self.users_file}")
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Create data files if they don't exist"""
        try:
            print(f"[_ensure_data_files] Creating data directory: {DATA_DIR}")
            os.makedirs(DATA_DIR, exist_ok=True)
            for file_path in [self.users_file, self.lessons_file, self.progress_file, self.curriculum_file]:
                print(f"[_ensure_data_files] Checking file: {file_path}")
                if not os.path.exists(file_path):
                    print(f"[_ensure_data_files] Creating new file: {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({}, f, indent=2)
                else:
                    print(f"[_ensure_data_files] File exists: {file_path}")
            if not os.path.exists(self.sessions_file):
                print(f"[_ensure_data_files] Creating sessions file: {self.sessions_file}")
                with open(self.sessions_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
            else:
                print(f"[_ensure_data_files] Sessions file exists: {self.sessions_file}")
        except Exception as e:
            print(f"[_ensure_data_files] Error: {str(e)}")
            print(f"[_ensure_data_files] Stack trace: {traceback.format_exc()}")
    
    def load_data(self, file_path: str) -> Any:
        """Load JSON data from file, with self-healing for missing/corrupt files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:  # Empty file
                    print(f"[load_data] {file_path} is empty, resetting to default.")
                    self.save_data(file_path, {} if file_path != self.sessions_file else [])
                    return {} if file_path != self.sessions_file else []
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    print(f"[load_data] Invalid JSON in {file_path}, resetting to default.")
                    self.save_data(file_path, {} if file_path != self.sessions_file else [])
                    return {} if file_path != self.sessions_file else []
        except FileNotFoundError:
            print(f"[load_data] {file_path} not found, creating new file.")
            self.save_data(file_path, {} if file_path != self.sessions_file else [])
            return {} if file_path != self.sessions_file else []
        except Exception as e:
            print(f"[load_data] Error reading {file_path}: {str(e)}")
            self.save_data(file_path, {} if file_path != self.sessions_file else [])
            return {} if file_path != self.sessions_file else []
    
    def save_data(self, file_path: str, data: Any):
        """Save JSON data to file safely using atomic write"""
        print(f"[save_data] Saving data to {file_path}")
        temp_file = file_path + '.tmp'
        try:
            # First verify the data can be serialized
            try:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
            except Exception as json_error:
                print(f"[save_data] Error serializing data: {str(json_error)}")
                return False

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write to temp file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            
            # Verify the temp file was written correctly
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    _ = json.load(f)
            except Exception as verify_error:
                print(f"[save_data] Error verifying temp file: {str(verify_error)}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return False
            
            # If successful, rename temp file to actual file
            try:
                if os.path.exists(file_path):
                    os.replace(temp_file, file_path)  # atomic on most platforms
                else:
                    os.rename(temp_file, file_path)
                print(f"[save_data] Successfully saved data to {file_path}")
                return True
            except Exception as rename_error:
                print(f"[save_data] Error during file rename: {str(rename_error)}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return False
                
        except Exception as e:
            print(f"[save_data] Error saving to {file_path}: {str(e)}")
            print(f"[save_data] Stack trace: {traceback.format_exc()}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False
    
    def create_user(self, name: str) -> str:
        """Create a new user with enhanced profile"""
        try:
            print(f"[create_user] Starting user creation with name: {name}")
            print(f"[create_user] Users file path: {self.users_file}")
            
            # Ensure data directory exists
            data_dir = os.path.dirname(self.users_file)
            os.makedirs(data_dir, exist_ok=True)
            print(f"[create_user] Ensured data directory exists: {data_dir}")
            
            # Initialize users dict
            users = {}
            
            # Carefully read existing users file
            if os.path.exists(self.users_file):
                try:
                    print(f"[create_user] Reading existing users file")
                    with open(self.users_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if file_content.strip():  # Only try to parse if file is not empty
                            users = json.loads(file_content)
                            if not isinstance(users, dict):
                                print(f"[create_user] Warning: users.json contained invalid data, resetting to empty dict")
                                users = {}
                except Exception as e:
                    print(f"[create_user] Error reading users file: {str(e)}")
                    users = {}
            
            print(f"Current users: {len(users)}")
            
            print(f"[create_user] Current number of users: {len(users)}")
            
            # Generate new user ID
            next_id = 1
            while f"user_{next_id}" in users:
                next_id += 1
            user_id = f"user_{next_id}"
            print(f"[create_user] Generated new user ID: {user_id}")
            
            # Create user data
            user_data = {
                "name": name,
                "created_at": datetime.now().isoformat(),
                "competency_scores": {},
                "knowledge_gaps": {},
                "strong_areas": {},
                "learning_path": [],
                "completed_lessons": [],
                "total_lessons": 0,
                "current_curriculum": None
            }
            
            # Add user to users dict
            users[user_id] = user_data
            print(f"[create_user] Created user data structure")
            
            # Validate user data before saving
            if not isinstance(users, dict):
                print("[create_user] Error: users data is not a dictionary")
                return None
                
            if not user_id or not isinstance(user_data, dict):
                print("[create_user] Error: invalid user data structure")
                return None
                
            # Use the improved save_data method
            if self.save_data(self.users_file, users):
                print(f"[create_user] Successfully saved user data for {user_id}")
                # Verify the save was successful by reading back the file
                try:
                    saved_users = self.load_data(self.users_file)
                    if user_id in saved_users:
                        print(f"[create_user] Verified user {user_id} was saved successfully")
                        return user_id
                    else:
                        print(f"[create_user] Error: User {user_id} not found in saved data")
                        return None
                except Exception as verify_error:
                    print(f"[create_user] Error verifying saved data: {str(verify_error)}")
                    return None
            else:
                print("[create_user] Failed to save user data")
                return None
            
        except Exception as e:
            print(f"[create_user] Error creating user: {str(e)}")
            print(f"[create_user] DATA_DIR: {DATA_DIR}")
            print(f"[create_user] Current directory: {os.getcwd()}")
            import traceback
            print(f"[create_user] Stack trace: {traceback.format_exc()}")
            return None
    
    # Duplicate generate_lesson_outline removed (see robust version at end of file)
        try:
            prompt = f"""Create a detailed, topic-specific lesson outline for {topic} at {difficulty} level.

Assessment Results: {json.dumps(assessment_results) if assessment_results else 'No prior assessment'}

OUTLINE REQUIREMENTS:
1. Topic-Specific Structure:
   - Organize modules in a logical sequence for {topic}
   - Each module should build upon previous knowledge
   - Include specific tools, frameworks, and technologies relevant to {topic}

2. Detailed Learning Path:
   - Break down complex concepts into manageable steps
   - Specify exact technologies and methods to be covered
   - Include practical exercises with real-world applications

3. Technical Depth:
   - List specific algorithms, formulas, or methods to be covered
   - Include implementation details and best practices
   - Reference specific libraries or tools where applicable

Return a JSON object with detailed, topic-specific outline information."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating lesson outline: {e}")
            return {
                "topic": topic,
                "difficulty": difficulty,
                "modules": [
                    {
                        "title": "Introduction to " + topic,
                        "description": "Basic concepts and fundamentals",
                        "estimatedTime": "30 minutes"
                    }
                ]
            }

    # Duplicate generate_lesson_content removed (see robust version at end of file)
        competency = user_profile.get('competency_scores', {}).get(topic, 0)
        knowledge_gaps = user_profile.get('knowledge_gaps', {}).get(topic, [])
        learning_path = user_profile.get('learning_path', [])
        completed_lessons = user_profile.get('completed_lessons', [])
        # Extract actionable components from the topic title
        title_analysis = self._analyze_topic_title(topic)
        # --- RAG: Retrieve relevant chunks from course materials ---
        try:
            from rag_utils import load_all_chunks, find_relevant_chunks
            import os
            base_dir = os.path.dirname(__file__)
            chunk_files = [
                os.path.join(base_dir, 'math_ml_chunks.json'),
                os.path.join(base_dir, 'mit_ocw_chunks.json'),
            ]
            chunks = load_all_chunks(chunk_files)
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=5)  # Get more chunks for better coverage
            if relevant_chunks:
                context = '\n\n'.join([f"EDUCATIONAL CONTENT FROM {fname}:\n{chunk}" for fname, chunk in relevant_chunks])
                print(f"Successfully retrieved {len(relevant_chunks)} relevant chunks for topic: {topic}")
            else:
                print(f"No relevant chunks found for topic: {topic}")
                context = ""
        except Exception as rag_e:
            print(f"RAG retrieval failed: {rag_e}")
            context = ""
        # Determine the next topic in the learning path
        current_topic_index = learning_path.index(topic) if topic in learning_path else -1
        is_sequential = current_topic_index >= 0 and len(completed_lessons) > 0
        try:
            prompt = f"""You are a world-class AI educator creating a lesson that MUST deliver on the specific learning outcomes promised in the title: \"{topic}\".\n\nTitle Analysis:\n- Action words: {title_analysis['actions']}\n- Technical components: {title_analysis['technologies']}\n- Application domain: {title_analysis['domain']}\n- Expected deliverables: {title_analysis['deliverables']}\n\nEDUCATIONAL FOUNDATION - YOU MUST BASE YOUR LESSON ON THIS MATERIAL:\n{context}\n"""
            print(f"Calling OpenAI for lesson generation with RAG context...")
            print(f"Topic: {topic}, Competency: {competency}")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )
            print(f"OpenAI response received")
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            lesson = json.loads(content)
            print(f"Lesson parsed successfully")
            
            # Validate lesson alignment with source material and title
            if relevant_chunks:
                validation_report = self.validate_lesson_alignment(lesson, topic, relevant_chunks)
                print(f"Lesson validation score: {validation_report['overall_score']:.2f}")
                
                if not validation_report['validation_passed']:
                    print("Lesson validation failed. Issues found:")
                    for issue in validation_report['issues']:
                        print(f"  - {issue}")
                    print("Recommendations:")
                    for rec in validation_report['recommendations']:
                        print(f"  - {rec}")
                
                # Add validation metadata to lesson
                lesson['validation_report'] = validation_report
            
            # Cache the lesson
            try:
                lessons = self.load_data(self.lessons_file)
                lesson_id = f"lesson_{len(lessons) + 1}"
                lessons[lesson_id] = lesson
                self.save_data(self.lessons_file, lessons)
                print(f"Lesson saved with ID: {lesson_id}")
            except Exception as cache_e:
                print(f"Warning: Could not cache lesson: {cache_e}")
            return lesson
        except Exception as e:
            print(f"Error in generate_lesson_content: {e}")
            print(f"Error type: {type(e).__name__}")
            # Try to load a cached lesson for this topic
            try:
                lessons = self.load_data(self.lessons_file)
                for lesson in lessons.values():
                    if lesson.get("topic") == topic:
                        print("Returning cached lesson for topic.")
                        return lesson
            except Exception as cache_e:
                print(f"No cached lesson found: {cache_e}")
            # Return a fallback lesson so the user isn't stuck
            print("Returning fallback lesson...")
            return {
                "topic": topic,
                "overview": f"Introduction to {topic} - exploring the fundamentals and key concepts you need to understand.",
                "chunks": [
                    {
                        "title": "Understanding the Basics",
                        "content": f"Let's start by understanding what {topic} means and why it's important in the field of artificial intelligence. We'll break down the core concepts and build your foundation knowledge step by step.",
                        "key_point": f"Understanding {topic} is fundamental to AI knowledge and practical applications."
                    },
                    {
                        "title": "Key Concepts and Components",
                        "content": f"There are several important concepts within {topic} that form the foundation of this area. Each concept builds on the previous ones, creating a comprehensive understanding of how these systems work.",
                        "key_point": "Each concept builds on the previous ones to create comprehensive understanding."
                    },
                    {
                        "title": "Real-World Applications",
                        "content": f"Now let's explore how {topic} is used in real-world scenarios and applications. Understanding practical applications helps bridge the gap between theory and practice.",
                        "key_point": "Theory becomes powerful when applied to solve real-world problems."
                    },
                    {
                        "title": "Summary and Next Steps",
                        "content": f"We've covered the fundamentals of {topic}. Let's summarize what we've learned and discuss how you can continue building on this knowledge in your AI learning journey.",
                        "key_point": "Continuous learning and practice are key to mastering AI concepts."
                    }
                ],
                "key_takeaways": [
                    f"Learned the fundamentals of {topic} and its importance in AI",
                    "Understood key concepts and their relationships to each other",
                    "Explored real-world applications and practical use cases",
                    "Ready to continue learning more advanced topics and applications"
                ]
            }
            print(f"Error generating adaptive assessment: {e}")
            return []
    
    def analyze_full_assessment(self, user_id: str, topic: str, initial_answers: Dict, 
                               adaptive_answers: Dict, all_questions: List[Dict]) -> Dict:
        """Analyze complete 10-question assessment and create learning plan"""
        
        total_correct = 0
        total_questions = len(all_questions)
        knowledge_gaps = []
        strong_areas = []
        concept_performance = {}
        
        # Analyze initial 5 questions
        for i in range(min(5, len(all_questions))):
            question = all_questions[i]
            user_answer = initial_answers.get(str(i))
            correct = user_answer == question.get('correct')
            
            if correct:
                total_correct += 1
                strong_areas.append(question.get('concept', 'unknown'))
            else:
                knowledge_gaps.append(question.get('concept', 'unknown'))
            
            concept_performance[question.get('concept', 'unknown')] = {
                'attempted': concept_performance.get(question.get('concept', 'unknown'), {}).get('attempted', 0) + 1,
                'correct': concept_performance.get(question.get('concept', 'unknown'), {}).get('correct', 0) + (1 if correct else 0)
            }
        
        # Analyze adaptive 5 questions
        for i in range(5, min(10, len(all_questions))):
            question = all_questions[i]
            user_answer = adaptive_answers.get(str(i-5))
            correct = user_answer == question.get('correct')
            
            if correct:
                total_correct += 1
                if question.get('concept') not in strong_areas:
                    strong_areas.append(question.get('concept', 'unknown'))
            else:
                if question.get('concept') not in knowledge_gaps:
                    knowledge_gaps.append(question.get('concept', 'unknown'))
            
            concept = question.get('concept', 'unknown')
            if concept not in concept_performance:
                concept_performance[concept] = {'attempted': 0, 'correct': 0}
            concept_performance[concept]['attempted'] += 1
            concept_performance[concept]['correct'] += (1 if correct else 0)
        
        overall_score = (total_correct / total_questions) * 10
        
        # Generate learning path based on performance
        learning_path = self._generate_learning_path(knowledge_gaps, strong_areas, concept_performance)
        
        return {
            'overall_score': overall_score,
            'knowledge_gaps': knowledge_gaps,
            'strong_areas': strong_areas,
            'concept_performance': concept_performance,
            'learning_path': learning_path,
            'recommended_lessons': self._recommend_lessons(knowledge_gaps, overall_score)
        }
    
    def _generate_learning_path(self, gaps: List[str], strengths: List[str], performance: Dict) -> List[str]:
        """Generate optimal learning sequence"""
        # Sort gaps by performance (worst first)
        sorted_gaps = sorted(gaps, key=lambda x: performance.get(x, {}).get('correct', 0) / max(performance.get(x, {}).get('attempted', 1), 1))
        
        # Create learning path: start with fundamentals, build up complexity
        learning_path = []
        if 'fundamentals' in [gap.lower() for gap in sorted_gaps]:
            learning_path.extend([gap for gap in sorted_gaps if 'fundamental' in gap.lower()])
        
        learning_path.extend([gap for gap in sorted_gaps if gap not in learning_path])
        
        return learning_path
    
    def _recommend_lessons(self, gaps: List[str], score: float) -> List[str]:
        """Recommend specific lessons based on gaps and score"""
        lessons = []
        
        if score < 3:
            lessons.append("Fundamentals Review")
        
        for gap in gaps:
            lessons.append(f"Deep Dive: {gap}")
        
        if score > 7:
            lessons.append("Advanced Applications")
        
        return lessons
    
    def update_user_competency_detailed(self, user_id: str, topic: str, analysis: Dict):
        """Update user profile with detailed competency analysis"""
        users = self.load_data(self.users_file)
        if user_id in users:
            users[user_id]['competency_scores'][topic] = analysis['overall_score']
            users[user_id]['knowledge_gaps'][topic] = analysis['knowledge_gaps']
            users[user_id]['strong_areas'][topic] = analysis['strong_areas']
            users[user_id]['learning_path'] = analysis['learning_path']
            self.save_data(self.users_file, users)
    
    def generate_personalized_curriculum(self, user_id: str, topic: str, knowledge_gaps: List[str]) -> Dict:
        """Generate a complete curriculum based on assessment"""
        
        prompt = f"""Create a personalized curriculum for learning "{topic}" based on these knowledge gaps: {knowledge_gaps}
        
        Create a structured learning plan with:
        1. 3-5 lessons that address the gaps systematically
        2. Each lesson should build on the previous one
        3. Include estimated time and difficulty
        4. Provide clear learning objectives for each lesson
        
        Return ONLY a JSON object with this format:
        {{
            "curriculum_id": "unique_id",
            "topic": "{topic}",
            "total_lessons": 4,
            "estimated_duration": "2-3 hours",
            "lessons": [
                {{
                    "lesson_id": "lesson_1",
                    "title": "Lesson Title",
                    "description": "What this lesson covers",
                    "learning_objectives": ["Objective 1", "Objective 2"],
                    "estimated_time": "30 minutes",
                    "difficulty": "beginner",
                    "prerequisites": [],
                    "targets_gaps": ["gap1", "gap2"]
                }}
            ]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            curriculum = json.loads(content)
            
            # Save curriculum
            curriculums = self.load_data(self.curriculum_file)
            curriculum_id = curriculum.get('curriculum_id', f"curr_{len(curriculums) + 1}")
            curriculums[curriculum_id] = curriculum
            self.save_data(self.curriculum_file, curriculums)
            
            # Update user's current curriculum
            users = self.load_data(self.users_file)
            if user_id in users:
                users[user_id]['current_curriculum'] = curriculum_id
                self.save_data(self.users_file, users)
            
            return curriculum
        except Exception as e:
            print(f"Error generating curriculum: {e}")
            return {}
    
    def get_lesson_content(self, lesson_id: str) -> Dict:
        """Generate detailed lesson content"""
        prompt = f"""Create detailed lesson content for lesson_id: {lesson_id}
        
        Include:
        1. Comprehensive explanation of the topic
        2. Real-world examples
        3. Step-by-step breakdowns
        4. Key takeaways
        5. Interactive elements
        
        Return as JSON with detailed content structure."""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )
            
            return {
                "lesson_id": lesson_id,
                "content": response.choices[0].message.content,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error generating lesson content: {e}")
            return {}
    
    def generate_lesson_quiz(self, lesson_id: str, lesson_content: Dict) -> Dict:
        """Generate quiz questions for a specific lesson"""
        prompt = f"""Based on this lesson content, create 3-5 quiz questions to test understanding:
        
        Lesson: {lesson_content.get('content', '')[:500]}...
        
        Questions should:
        1. Test key concepts from the lesson
        2. Be directly related to what was taught
        3. Have clear correct answers
        4. Include some application-based questions
        
        Return as JSON array of questions."""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return {
                "lesson_id": lesson_id,
                "questions": json.loads(content),
                "total_questions": len(json.loads(content))
            }
        except Exception as e:
            print(f"Error generating lesson quiz: {e}")
            return {"lesson_id": lesson_id, "questions": [], "total_questions": 0}
    
    def evaluate_lesson_quiz(self, user_id: str, lesson_id: str, answers: Dict, questions: List[Dict]) -> Dict:
        """Evaluate lesson quiz answers and return results"""
        total_correct = 0
        total_questions = len(questions)
        
        for i, question in enumerate(questions):
            user_answer = answers.get(str(i))
            if user_answer == question.get('correct'):
                total_correct += 1
        
        score = (total_correct / total_questions) * 10 if total_questions > 0 else 0
        
        # Update user progress
        progress_data = self.load_data(self.progress_file)
        if user_id not in progress_data:
            progress_data[user_id] = {
                "lessons_completed": 0,
                "total_lessons": 0,
                "average_quiz_score": 0,
                "quiz_scores": []
            }
        
        progress_data[user_id]['quiz_scores'].append(score)
        progress_data[user_id]['average_quiz_score'] = sum(progress_data[user_id]['quiz_scores']) / len(progress_data[user_id]['quiz_scores'])
        self.save_data(self.progress_file, progress_data)
        
        return {
            'score': score,
            'correct_answers': total_correct,
            'total_questions': total_questions,
            'percentage': (total_correct / total_questions) * 100 if total_questions > 0 else 0,
            'passed': score >= 7.0,
            'feedback': self._generate_quiz_feedback(score, total_correct, total_questions)
        }
    
    def _generate_quiz_feedback(self, score: float, correct: int, total: int) -> str:
        """Generate feedback based on quiz performance"""
        percentage = (correct / total) * 100 if total > 0 else 0
        
        if percentage >= 90:
            return "Excellent! You have mastered this material."
        elif percentage >= 80:
            return "Great job! You have a strong understanding of the concepts."
        elif percentage >= 70:
            return "Good work! You understand most of the material, but review the areas you missed."
        elif percentage >= 60:
            return "You're getting there! Review the lesson material and try again."
        else:
            return "Consider reviewing the lesson material more thoroughly before continuing."
    
    def get_user(self, user_id: str) -> Dict:
        """Get user data by ID"""
        users = self.load_data(self.users_file)
        return users.get(user_id, {})

    def get_user_progress(self, user_id: str) -> Dict:
        """Get comprehensive user progress data"""
        user = self.get_user(user_id)
        
        progress_data = self.load_data(self.progress_file)
        user_progress = progress_data.get(user_id, {
            "lessons_completed": 0,
            "total_lessons": 0,
            "average_quiz_score": 0,
            "learning_velocity": 0,
            "knowledge_improvement": {},
            "session_history": []
        })
        
        return {
            "user_id": user_id,
            "name": user.get('name', 'Unknown'),
            "overall_progress": user_progress,
            "current_competencies": user.get('competency_scores', {}),
            "knowledge_gaps": user.get('knowledge_gaps', {}),
            "strong_areas": user.get('strong_areas', {}),
            "learning_path": user.get('learning_path', []),
            "recommendations": self._generate_recommendations(user, user_progress)
        }
    
    def _generate_recommendations(self, user: Dict, progress: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if progress.get('lessons_completed', 0) == 0:
            recommendations.append("Start with your first lesson!")
        elif progress.get('average_quiz_score', 0) < 7:
            recommendations.append("Review previous lessons to strengthen understanding")
        elif progress.get('lessons_completed', 0) / progress.get('total_lessons', 1) > 0.8:
            recommendations.append("You're almost done! Complete the final lessons")
        
        return recommendations
    
    def generate_final_assessment(self, user_id: str, topic: str, completed_lessons: List[str]) -> Dict:
        """Generate final wrap-up assessment"""
        prompt = f"""Create a final assessment for "{topic}" based on completed lessons: {completed_lessons}
        
        Create 5 comprehensive questions that:
        1. Test understanding across all completed lessons
        2. Include both theoretical and practical application questions
        3. Measure learning improvement since initial assessment
        4. Cover the most important concepts
        
        Return ONLY a JSON array with this format:
        [
            {{
                "question": "Question text here",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct": "A",
                "concept": "concept_being_tested",
                "difficulty": 3,
                "lesson_reference": "lesson_id"
            }}
        ]
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            questions = json.loads(content)
            
            return {
                'questions': questions,
                'type': 'final',
                'total_questions': len(questions),
                'description': 'Final assessment to measure your overall learning progress'
            }
        except Exception as e:
            print(f"Error generating final assessment: {e}")
            return {'questions': [], 'type': 'final', 'total_questions': 0}
    
    def analyze_sentiment_enhanced(self, user_response: str, lesson_context: str = '') -> Dict:
        """Enhanced sentiment analysis with lesson context"""
        prompt = f"""Analyze this student response for emotional state and understanding:
        
        Student Response: "{user_response}"
        Lesson Context: "{lesson_context}"
        
        Provide analysis for:
        1. Confusion level (0-1)
        2. Confidence level (0-1) 
        3. Engagement level (0-1)
        4. Understanding quality (poor/fair/good/excellent)
        5. Specific suggestions for improvement
        6. Whether to proceed or review
        
        Return as JSON with these exact keys."""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                timeout=30
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
                "confidence_level": 0.5,
                "engagement_level": 0.5,
                "understanding": "fair",
                "suggestion": "Continue with current pace",
                "should_proceed": True
            }
    
    def save_detailed_session(self, user_id: str, session_data: Dict):
        """Save comprehensive session data"""
        sessions = self.load_data(self.sessions_file)
        session_data['user_id'] = user_id
        session_data['timestamp'] = datetime.now().isoformat()
        session_data['session_id'] = f"session_{len(sessions) + 1}"
        sessions.append(session_data)
        self.save_data(self.sessions_file, sessions)
        
        # Update progress tracking
        progress_data = self.load_data(self.progress_file)
        if user_id not in progress_data:
            progress_data[user_id] = {
                "lessons_completed": 0,
                "total_lessons": 0,
                "average_quiz_score": 0,
                "session_history": []
            }
        
        progress_data[user_id]['session_history'].append(session_data['session_id'])
        self.save_data(self.progress_file, progress_data)

    # BACKWARD COMPATIBILITY METHODS (for old CLI and legacy endpoints to work)

    def generate_assessment_questions(self, topic: str) -> List[Dict]:
        """Legacy method for backward compatibility"""
        return self.generate_initial_assessment(topic)

    def validate_question_quality(self, question_data: Dict, topic: str) -> Dict:
        """Validate the quality and coherence of a generated question"""
        validation_results = {
            "is_valid": True,
            "quality_score": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        try:
            question = question_data.get("question", "")
            options = question_data.get("options", [])
            correct_answer = question_data.get("correct", "")
            concept = question_data.get("concept", "")
            
            # 1. Check basic structure - more rigorous standards
            if not question or len(question.strip()) < 30:
                validation_results["issues"].append("Question text is too short (minimum 30 characters)")
                validation_results["is_valid"] = False
            
            # Check for academic rigor
            if len(question.split()) < 8:
                validation_results["issues"].append("Question lacks depth (minimum 8 words)")
                validation_results["quality_score"] -= 0.2
            
            if len(options) != 4:
                validation_results["issues"].append(f"Expected 4 options, got {len(options)}")
                validation_results["is_valid"] = False
            
            if not correct_answer:
                validation_results["issues"].append("No correct answer specified")
                validation_results["is_valid"] = False
            
            # 2. Check topic relevance
            topic_keywords = topic.lower().split()
            question_text = question.lower()
            relevance_score = sum(1 for keyword in topic_keywords if keyword in question_text) / len(topic_keywords)
            
            if relevance_score < 0.2:
                validation_results["issues"].append("Question seems unrelated to the topic")
                validation_results["quality_score"] -= 0.3
            else:
                validation_results["quality_score"] += relevance_score * 0.3
            
            # 3. Check option quality
            if validation_results["is_valid"]:
                # Clean options (remove A), B), etc. prefixes)
                clean_options = []
                for opt in options:
                    clean_opt = opt.strip()
                    if clean_opt.startswith(('A)', 'B)', 'C)', 'D)')):
                        clean_opt = clean_opt[2:].strip()
                    clean_options.append(clean_opt)
                
                option_lengths = [len(opt) for opt in clean_options]
                
                # Check for very short options - more strict
                if any(length < 8 for length in option_lengths):
                    validation_results["issues"].append("Some options are too short (minimum 8 characters)")
                    validation_results["quality_score"] -= 0.2
                
                # Check for academic depth in options
                option_word_counts = [len(opt.split()) for opt in clean_options]
                if any(count < 3 for count in option_word_counts):
                    validation_results["issues"].append("Options lack substance (minimum 3 words per option)")
                    validation_results["quality_score"] -= 0.15
                
                # Check for similar options (potential duplicates)
                unique_options = set(opt.lower().strip() for opt in clean_options)
                if len(unique_options) < len(clean_options):
                    validation_results["issues"].append("Options contain duplicates or very similar text")
                    validation_results["quality_score"] -= 0.2
                
                # Check if correct answer exists in options
                correct_found = False
                for opt in options:
                    if opt.startswith(correct_answer):
                        correct_found = True
                        break
                
                if not correct_found:
                    validation_results["issues"].append("Correct answer not found in options")
                    validation_results["is_valid"] = False
                else:
                    validation_results["quality_score"] += 0.2
            
            # 4. Check concept specificity
            if concept and len(concept.strip()) > 3:
                validation_results["quality_score"] += 0.1
            else:
                validation_results["suggestions"].append("Consider specifying the concept being tested")
            
            # 5. Use AI to validate coherence if API is available
            try:
                coherence_score = self._assess_question_coherence(question_data, topic)
                validation_results["quality_score"] += coherence_score * 0.4
            except Exception as e:
                print(f"Coherence assessment failed: {e}")
                # Give neutral score if AI assessment fails
                validation_results["quality_score"] += 0.2
            
            # Normalize quality score to 0-1 range
            validation_results["quality_score"] = max(0.0, min(1.0, validation_results["quality_score"]))
            
            # Final validation
            if validation_results["quality_score"] < 0.4:
                validation_results["is_valid"] = False
                validation_results["issues"].append("Overall quality score too low")
            
        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["issues"].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def _assess_question_coherence(self, question_data: Dict, topic: str) -> float:
        """Use AI to assess question coherence and educational value"""
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            question_text = json.dumps(question_data, indent=2)
            
            prompt = f"""As an expert educator, rigorously evaluate this multiple choice question for the topic "{topic}":

{question_text}

EVALUATION CRITERIA (rate 0.0-1.0):
1. ACADEMIC RIGOR: Does it test deep understanding vs. surface knowledge?
2. CLARITY: Is the question unambiguous and professionally written?
3. TECHNICAL ACCURACY: Are all facts and concepts correct?
4. FAIRNESS: Are distractors plausible but clearly wrong to experts?
5. APPROPRIATENESS: Is complexity suitable for the topic level?
6. REAL-WORLD RELEVANCE: Does it connect to practical applications?
7. COGNITIVE DEMAND: Does it require analysis/synthesis vs. mere recall?

QUALITY THRESHOLDS:
- 0.9-1.0: Excellent, publication-ready question
- 0.7-0.8: Good, minor improvements needed  
- 0.5-0.6: Adequate but needs significant improvement
- 0.3-0.4: Poor, major issues present
- 0.0-0.2: Unacceptable quality

Consider: Does this question distinguish between students who truly understand {topic} versus those who've just memorized facts?

Return only a single decimal number between 0.0 and 1.0."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1,
                timeout=15
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            print(f"AI coherence assessment failed: {e}")
            return 0.5  # Neutral score if assessment fails
    
    def _regenerate_single_question(self, topic: str, concept: str, difficulty: str = "Beginner") -> Dict:
        """Regenerate a single question for a specific concept with higher quality standards"""
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            prompt = f"""Create ONE high-quality, academically rigorous multiple choice question about "{concept}" in the context of "{topic}" at {difficulty} level.

STRICT REQUIREMENTS:
- Question must be at least 30 words and present a realistic scenario
- Test deep understanding, not memorization
- Include quantitative elements where appropriate
- Each option must be substantive (minimum 10 words)
- Distractors should reflect actual misconceptions experts encounter
- Use precise, technical language appropriate for university level

QUALITY STANDARDS:
- The correct answer must be unambiguous and defensible
- Wrong answers should be plausible to novices but clearly wrong to experts
- Include real-world context or applications
- Test analytical thinking, not just recall

EXAMPLE STRUCTURE:
"In a neural network optimization scenario where [specific context], which approach would yield the most effective results considering [specific constraints]?"

Return JSON format:
{{
    "question": "Comprehensive question with specific scenario and technical details (minimum 30 words)",
    "options": [
        "A) Detailed technical option with specific reasoning and implications (minimum 10 words)",
        "B) Alternative approach with different technical rationale and trade-offs", 
        "C) Common misconception with plausible but flawed reasoning",
        "D) Another misconception or oversimplified approach with specific technical errors"
    ],
    "correct": "A",
    "concept": "{concept}",
    "difficulty": 3,
    "explanation": "Detailed explanation of why the correct answer is right and why each distractor is wrong, including technical reasoning"
}}"""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            question = json.loads(content)
            
            # Validate the regenerated question
            validation = self.validate_question_quality(question, topic)
            if validation["quality_score"] < 0.6:
                print(f"Regenerated question still low quality: {validation['quality_score']}")
                return None
                
            return question
            
        except Exception as e:
            print(f"Failed to regenerate question: {e}")
            return None
    
    def _generate_fallback_question(self, topic: str, question_num: int) -> Dict:
        """Generate a rigorous fallback question when AI generation fails"""
        fallback_questions = {
            1: {
                "question": f"In the context of {topic}, which mathematical foundation is most critical for understanding the underlying computational processes and optimization techniques used in modern implementations?",
                "options": [
                    "A) Linear algebra and calculus, as they provide the mathematical framework for gradient-based optimization and matrix operations essential to most algorithms",
                    "B) Basic arithmetic and simple statistics, which are sufficient for most practical applications", 
                    "C) Only probability theory, since all AI systems are fundamentally probabilistic",
                    "D) Discrete mathematics alone, as AI systems only work with digital discrete values"
                ],
                "correct": "A",
                "concept": "Mathematical Foundations",
                "difficulty": 2,
                "explanation": "Linear algebra and calculus are fundamental because most AI algorithms rely on matrix operations and gradient-based optimization methods."
            },
            2: {
                "question": f"When implementing {topic} in a production environment, which consideration is most critical for ensuring both computational efficiency and model performance?",
                "options": [
                    "A) Balancing model complexity with computational resources while maintaining accuracy requirements for the specific use case",
                    "B) Always choosing the most complex model available regardless of computational cost",
                    "C) Focusing solely on speed without considering accuracy metrics",
                    "D) Using only pre-trained models without any customization or fine-tuning"
                ],
                "correct": "A", 
                "concept": "Implementation Trade-offs",
                "difficulty": 3,
                "explanation": "Production environments require careful balance between computational efficiency and performance, considering real-world constraints."
            },
            3: {
                "question": f"Which approach best demonstrates understanding of the theoretical principles underlying {topic} when faced with a novel problem domain?",
                "options": [
                    "A) Analyzing the problem structure to identify relevant mathematical properties and selecting appropriate algorithmic approaches based on theoretical guarantees",
                    "B) Randomly trying different popular algorithms until one produces reasonable results",
                    "C) Always using the same algorithm regardless of problem characteristics",
                    "D) Relying entirely on automated machine learning tools without understanding the underlying methods"
                ],
                "correct": "A",
                "concept": "Problem Analysis and Algorithm Selection",
                "difficulty": 4,
                "explanation": "Deep understanding requires analyzing problem structure and applying theoretical knowledge to select appropriate methods."
            }
        }
        
        return fallback_questions.get(question_num, fallback_questions[1])

    def get_question_quality_report(self, questions: List[Dict], topic: str) -> Dict:
        """Generate a comprehensive quality report for a set of questions"""
        if not questions:
            return {"error": "No questions to evaluate"}
        
        total_score = 0
        individual_reports = []
        issues_summary = {}
        
        for i, question in enumerate(questions):
            validation = self.validate_question_quality(question, topic)
            individual_reports.append({
                "question_number": i + 1,
                "question_text": question.get("question", "")[:50] + "...",
                "quality_score": validation["quality_score"],
                "is_valid": validation["is_valid"],
                "issues": validation["issues"],
                "suggestions": validation["suggestions"]
            })
            
            total_score += validation["quality_score"]
            
            # Aggregate issues
            for issue in validation["issues"]:
                issues_summary[issue] = issues_summary.get(issue, 0) + 1
        
        avg_score = total_score / len(questions)
        
        return {
            "summary": {
                "total_questions": len(questions),
                "average_quality_score": round(avg_score, 2),
                "passed_validation": sum(1 for r in individual_reports if r["is_valid"]),
                "overall_grade": "Excellent" if avg_score >= 0.8 else "Good" if avg_score >= 0.6 else "Needs Improvement"
            },
            "individual_reports": individual_reports,
            "common_issues": issues_summary,
            "recommendations": self._generate_quality_recommendations(avg_score, issues_summary)
        }
    
    def validate_lesson_alignment(self, lesson: Dict, topic: str, source_chunks: List[Tuple[str, str]]) -> Dict:
        """Validate that the generated lesson properly incorporates the source chunks and aligns with the title."""
        validation_report = {
            "title_alignment_score": 0.0,
            "source_material_usage_score": 0.0,
            "content_depth_score": 0.0,
            "overall_score": 0.0,
            "issues": [],
            "recommendations": [],
            "validation_passed": False
        }
        
        try:
            # Extract lesson content for analysis
            lesson_text = lesson.get('overview', '') + ' '
            for chunk in lesson.get('chunks', []):
                lesson_text += chunk.get('content', '') + ' ' + chunk.get('key_point', '') + ' '
            lesson_text = lesson_text.lower()
            
            # 1. Title Alignment Analysis
            title_analysis = self._analyze_topic_title(topic)
            title_keywords = []
            for action_list in title_analysis.values():
                if isinstance(action_list, list):
                    title_keywords.extend(action_list)
                elif isinstance(action_list, str):
                    title_keywords.append(action_list)
            
            title_matches = sum(1 for keyword in title_keywords if keyword.lower() in lesson_text)
            validation_report["title_alignment_score"] = min(1.0, title_matches / max(len(title_keywords), 1))
            
            if validation_report["title_alignment_score"] < 0.5:
                validation_report["issues"].append("Lesson content does not adequately address the specific promises made in the title")
                validation_report["recommendations"].append("Ensure lesson content directly enables students to achieve what the title promises")
            
            # 2. Source Material Usage Analysis
            if source_chunks:
                source_concepts = set()
                source_text = ""
                for fname, chunk_content in source_chunks:
                    source_text += chunk_content.lower() + " "
                    # Extract key concepts from source material
                    import re
                    concepts = re.findall(r'\b(?:theorem|definition|algorithm|method|approach|model|technique|principle)\b', chunk_content.lower())
                    source_concepts.update(concepts)
                
                # Check if lesson incorporates source concepts
                source_matches = sum(1 for concept in source_concepts if concept in lesson_text)
                validation_report["source_material_usage_score"] = min(1.0, source_matches / max(len(source_concepts), 1))
                
                # Check for direct quotes or references
                has_references = any(ref in lesson.get('source_material_references', []) for ref in ['MIT OCW', 'lecture', 'course material'])
                if has_references:
                    validation_report["source_material_usage_score"] += 0.2
                    validation_report["source_material_usage_score"] = min(1.0, validation_report["source_material_usage_score"])
                
                if validation_report["source_material_usage_score"] < 0.4:
                    validation_report["issues"].append("Lesson does not adequately incorporate the provided source material")
                    validation_report["recommendations"].append("Include more direct references to concepts, theorems, and examples from the course material")
            else:
                validation_report["source_material_usage_score"] = 0.5  # Neutral if no source material available
            
            # 3. Content Depth Analysis
            total_content_length = sum(len(chunk.get('content', '')) for chunk in lesson.get('chunks', []))
            avg_chunk_length = total_content_length / max(len(lesson.get('chunks', [])), 1)
            
            # Check for mathematical content
            math_indicators = ['equation', 'formula', 'theorem', 'proof', 'algorithm', 'optimization', 'gradient', 'matrix']
            math_score = sum(1 for indicator in math_indicators if indicator in lesson_text) / len(math_indicators)
            
            # Check for practical content
            practical_indicators = ['implementation', 'example', 'application', 'step-by-step', 'code', 'practice', 'exercise']
            practical_score = sum(1 for indicator in practical_indicators if indicator in lesson_text) / len(practical_indicators)
            
            depth_score = (avg_chunk_length / 200.0 + math_score + practical_score) / 3
            validation_report["content_depth_score"] = min(1.0, depth_score)
            
            if validation_report["content_depth_score"] < 0.5:
                validation_report["issues"].append("Lesson content lacks sufficient depth and substance")
                validation_report["recommendations"].append("Include more detailed explanations, mathematical formulations, and practical examples")
            
            # 4. Overall Assessment
            validation_report["overall_score"] = (
                validation_report["title_alignment_score"] * 0.4 +
                validation_report["source_material_usage_score"] * 0.4 +
                validation_report["content_depth_score"] * 0.2
            )
            
            # Determine if validation passed
            validation_report["validation_passed"] = (
                validation_report["overall_score"] >= 0.6 and
                validation_report["title_alignment_score"] >= 0.4 and
                validation_report["source_material_usage_score"] >= 0.3
            )
            
            if validation_report["validation_passed"]:
                validation_report["recommendations"].append("Lesson meets quality standards for content alignment and source material usage")
            else:
                validation_report["issues"].append(f"Overall lesson quality score {validation_report['overall_score']:.2f} below minimum threshold of 0.6")
                
        except Exception as e:
            validation_report["issues"].append(f"Validation error: {str(e)}")
            print(f"Error in lesson validation: {e}")
        
        return validation_report

    def _generate_quality_recommendations(self, avg_score: float, issues_summary: Dict) -> List[str]:
        """Generate recommendations based on quality analysis"""
        recommendations = []
        
        if avg_score < 0.5:
            recommendations.append("Consider regenerating questions with more specific prompts")
        
        if "Question seems unrelated to the topic" in issues_summary:
            recommendations.append("Improve topic relevance by including more specific keywords")
        
        if "Options contain duplicates or very similar text" in issues_summary:
            recommendations.append("Ensure all answer options are distinct and clearly different")
        
        if "Some options are too short" in issues_summary:
            recommendations.append("Provide more detailed and comprehensive answer options")
        
        if avg_score >= 0.8:
            recommendations.append("Questions meet high quality standards!")
        
        return recommendations

    def generate_initial_assessment(self, topic: str) -> List[Dict]:
        """Generate initial 5 questions to identify broad knowledge areas, using RAG from PDF chunks."""
        # --- RAG: Retrieve relevant chunks ---
        try:
            from rag_utils import load_all_chunks, find_relevant_chunks
            import os
            base_dir = os.path.dirname(__file__)
            chunk_files = [
                os.path.join(base_dir, 'math_ml_chunks.json'),
                os.path.join(base_dir, 'mit_ocw_chunks.json'),
            ]
            chunks = load_all_chunks(chunk_files)
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=5)
            
            if relevant_chunks:
                context = '\n\n'.join([f"EDUCATIONAL CONTENT FROM {fname}:\n{chunk}" for fname, chunk in relevant_chunks])
                print(f"Successfully retrieved {len(relevant_chunks)} relevant chunks for assessment: {topic}")
            else:
                print(f"No relevant chunks found for assessment topic: {topic}")
                context = "No specific course material found. Use general machine learning principles."
        except Exception as rag_e:
            print(f"RAG retrieval failed (assessment): {rag_e}")
            context = "No specific course material found. Use general machine learning principles."

        prompt = f"""You are a world-class AI tutor. Create exactly 5 multiple-choice questions for a PRE-TEST on the topic '{topic}'.\n\nREQUIREMENTS:\n1. All questions must be suitable for BEGINNERS with no prior experience.\n2. Focus on basic definitions, simple concepts, and fundamental understanding.\n3. Avoid technical jargon, advanced math, or code unless absolutely necessary.\n4. Each question should have 4 options (A-D), only one correct.\n5. Use clear, simple language and real-world analogies if possible.\n6. Base questions on the following course material if available:\n{context}\n\nReturn ONLY a JSON array with this format:\n[\n    {{\n        \"question\": \"...\",\n        \"options\": [\"A) ...\", \"B) ...\", \"C) ...\", \"D) ...\"],\n        \"correct\": \"A\",\n        \"concept\": \"...\",\n        \"difficulty\": 1,\n        \"explanation\": \"...\"\n    }}\n]\n"""

        try:
            print(f"Calling OpenAI API for initial assessment on topic: {topic}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )
            content = response.choices[0].message.content.strip()
            print(f"OpenAI response received, length: {len(content)}")
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            questions = json.loads(content)
            print(f"Successfully parsed {len(questions)} questions")
            
            # === QUALITY VETTING LAYER ===
            print("Starting quality vetting process...")
            vetted_questions = []
            quality_reports = []
            
            for i, question in enumerate(questions):
                print(f"Validating question {i+1}...")
                validation_result = self.validate_question_quality(question, topic)
                quality_reports.append(validation_result)
                
                if validation_result["is_valid"] and validation_result["quality_score"] >= 0.5:
                    vetted_questions.append(question)
                    print(f"Question {i+1}: PASSED (score: {validation_result['quality_score']:.2f})")
                else:
                    print(f"Question {i+1}: FAILED (score: {validation_result['quality_score']:.2f})")
                    print(f"Issues: {', '.join(validation_result['issues'])}")
                    
                    # Try to regenerate this specific question
                    concept = question.get("concept", f"concept_{i+1}")
                    print(f"Attempting to regenerate question for concept: {concept}")
                    regenerated = self._regenerate_single_question(topic, concept)
                    if regenerated:
                        regen_validation = self.validate_question_quality(regenerated, topic)
                        if regen_validation["is_valid"] and regen_validation["quality_score"] >= 0.4:
                            vetted_questions.append(regenerated)
                            print(f"Question {i+1}: REGENERATED and PASSED (score: {regen_validation['quality_score']:.2f})")
                        else:
                            print(f"Regenerated question also failed validation")
            
            # If we don't have enough quality questions, add fallback ones
            while len(vetted_questions) < 3:
                fallback = self._generate_fallback_question(topic, len(vetted_questions) + 1)
                vetted_questions.append(fallback)
                print(f"Added fallback question {len(vetted_questions)}")
            
            # Ensure we don't exceed 5 questions
            if len(vetted_questions) > 5:
                vetted_questions = vetted_questions[:5]
            
            print(f"Quality vetting complete: {len(vetted_questions)} questions passed")
            if quality_reports:
                avg_score = sum(r["quality_score"] for r in quality_reports) / len(quality_reports)
                print(f"Average quality score: {avg_score:.2f}")
            
            return vetted_questions
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw content: {content}")
            return []
        except Exception as e:
            print(f"Error generating initial assessment: {e}")
            import traceback
            traceback.print_exc()
            
            # Return vetted fallback questions
            print("Generating fallback questions with quality validation...")
            fallback_questions = []
            for i in range(3):
                fallback = self._generate_fallback_question(topic, i + 1)
                validation = self.validate_question_quality(fallback, topic)
                print(f"Fallback question {i+1} quality score: {validation['quality_score']:.2f}")
                fallback_questions.append(fallback)
            
            return fallback_questions

    def generate_lesson_content(self, topic: str, user_profile: Dict) -> Dict:
        """Generate personalized lesson content for a topic and user profile, always using OpenAI."""
        competency = user_profile.get('competency_scores', {}).get(topic, 0)
        prompt = f"""Create a comprehensive, university-level lesson on {topic} for someone with competency level {competency}/10.

LESSON REQUIREMENTS:
- Academic rigor appropriate for advanced learners
- Include mathematical formulations where relevant  
- Provide concrete examples and case studies
- Connect theory to practical applications
- Include potential pitfalls and common misconceptions
- Reference current research and developments

STRUCTURE GUIDELINES:
1. Overview should establish context and importance (2-3 paragraphs)
2. Each chunk should be substantial (150-200 words minimum)
3. Include quantitative examples and equations where applicable
4. Connect concepts to real-world problems and solutions
5. Progressive complexity building from fundamentals

DEPTH REQUIREMENTS:
- For competency 0-3: Focus on clear explanations with simple examples
- For competency 4-6: Include intermediate mathematical concepts and applications  
- For competency 7-10: Advanced theory, cutting-edge research, complex scenarios

Return ONLY a JSON object with this format:
{{
    "topic": "{topic}",
    "overview": "Comprehensive overview establishing context, importance, and learning objectives. Should connect to broader field and practical applications.",
    "chunks": [
        {{
            "title": "Descriptive, Academic Title",
            "content": "Detailed, rigorous explanation with examples, mathematical concepts where relevant, and connections to applications. Minimum 150 words.",
            "key_point": "Specific, actionable takeaway that demonstrates mastery",
            "mathematical_concepts": ["concept1", "concept2"] or null,
            "examples": ["example1", "example2"],
            "applications": ["application1", "application2"]
        }}
    ],
    "key_takeaways": [
        "Specific technical knowledge gained",
        "Practical skills developed", 
        "Conceptual understanding achieved",
        "Applications mastered"
    ],
    "prerequisites": ["prerequisite1", "prerequisite2"],
    "further_reading": ["resource1", "resource2"],
    "assessment_criteria": ["criteria1", "criteria2"]
}}
}}
"""
        try:
            print(f"Calling OpenAI for lesson generation...")
            print(f"Topic: {topic}, Competency: {competency}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=30
            )
            print(f"OpenAI response received")
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            lesson = json.loads(content)
            print(f"Lesson parsed successfully")
            # Optionally cache the lesson
            try:
                lessons = self.load_data(self.lessons_file)
            except Exception:
                lessons = {}
            lesson_id = f"lesson_{len(lessons) + 1}"
            lessons[lesson_id] = lesson
            self.save_data(self.lessons_file, lessons)
            print(f"Lesson saved with ID: {lesson_id}")
            return lesson
        except Exception as e:
            print(f"Error in generate_lesson_content: {e}")
            print(f"Error type: {type(e).__name__}")
            # Try to load a cached lesson for this topic
            try:
                lessons = self.load_data(self.lessons_file)
                for lesson in lessons.values():
                    if lesson.get("topic") == topic:
                        print("Returning cached lesson for topic.")
                        return lesson
            except Exception as cache_e:
                print(f"No cached lesson found: {cache_e}")
            # Return a fallback lesson so the user isn't stuck
            print("Returning fallback lesson...")
            return {
                "topic": topic,
                "overview": f"Introduction to {topic} - exploring the fundamentals and key concepts you need to understand.",
                "chunks": [
                    {
                        "title": "Understanding the Basics",
                        "content": f"Let's start by understanding what {topic} means and why it's important in the field of artificial intelligence. We'll break down the core concepts and build your foundation knowledge step by step.",
                        "key_point": f"Understanding {topic} is fundamental to AI knowledge and practical applications."
                    },
                    {
                        "title": "Key Concepts and Components",
                        "content": f"There are several important concepts within {topic} that form the foundation of this area. Each concept builds on the previous ones, creating a comprehensive understanding of how these systems work.",
                        "key_point": "Each concept builds on the previous ones to create comprehensive understanding."
                    },
                    {
                        "title": "Real-World Applications",
                        "content": f"Now let's explore how {topic} is used in real-world scenarios and applications. Understanding practical applications helps bridge the gap between theory and practice.",
                        "key_point": "Theory becomes powerful when applied to solve real-world problems."
                    },
                    {
                        "title": "Summary and Next Steps",
                        "content": f"We've covered the fundamentals of {topic}. Let's summarize what we've learned and discuss how you can continue building on this knowledge in your AI learning journey.",
                        "key_point": "Continuous learning and practice are key to mastering AI concepts."
                    }
                ],
                "key_takeaways": [
                    f"Learned the fundamentals of {topic} and its importance in AI",
                    "Understood key concepts and their relationships to each other",
                    "Explored real-world applications and practical use cases",
                    "Ready to continue learning more advanced topics and applications"
                ]
            }
    
    def analyze_sentiment(self, user_response: str) -> Dict:
        """Legacy method for backward compatibility"""
        return self.analyze_sentiment_enhanced(user_response)
    
    def update_user_competency(self, user_id: str, topic: str, score: float):
        """Legacy method for backward compatibility"""
        users = self.load_data(self.users_file)
        if user_id in users:
            users[user_id]['competency_scores'][topic] = score
            users[user_id]['total_lessons'] += 1
            self.save_data(self.users_file, users)
    
    def save_session(self, user_id: str, session_data: Dict):
        """Legacy method for backward compatibility"""
        return self.save_detailed_session(user_id, session_data)
    
    # New methods for custom topics and learning sessions
    
    def generate_custom_topics(self, user_id: str, user_input: str) -> List[Dict]:
        """Generate custom learning topics based on user input"""
        try:
            # Get user data for personalization
            users = self.load_data(self.users_file)
            user_data = users.get(user_id, {})
            
            prompt = f"""
            Based on the user's request: "{user_input}"
            
            User background:
            - Competency scores: {user_data.get('competency_scores', {})}
            - Completed lessons: {user_data.get('completed_lessons', [])}
            - Knowledge gaps: {user_data.get('knowledge_gaps', {})}
            
            Generate 3 personalized learning topics that match their interests and current skill level.
            
            IMPORTANT: Create descriptive titles that reflect what the student will actually learn, not just generic introductions.
            
            For each topic:
            1. First outline the key learning objectives and main concepts that will be covered
            2. Create a specific, descriptive title that captures the core learning outcome (e.g., "Building Convolutional Neural Networks for Image Classification" instead of "Introduction to Neural Networks")
            3. Write a detailed description that explains what specific skills and knowledge the student will gain
            4. Select appropriate difficulty, timing, and intensity based on the content depth
            
            Title Guidelines:
            - Be specific about what will be learned or built
            - Include the main technique, tool, or outcome
            - Avoid generic words like "Introduction to" or "Basics of"
            - Focus on practical applications and concrete skills
            
            Examples of good titles:
            - "Implementing Gradient Descent Optimization in Python"
            - "Designing Computer Vision Systems for Medical Imaging"
            - "Building Natural Language Processing Pipelines with Transformers"
            - "Applying Reinforcement Learning to Game AI Development"
            
            Return as JSON array with this exact structure:
            [
                {{
                    "id": "custom_topic_1",
                    "title": "Specific, Descriptive Title About What Will Be Learned",
                    "description": "Detailed description explaining the specific skills, techniques, and knowledge the student will gain...",
                    "userInput": "{user_input}",
                    "baseTopic": "machine_learning",
                    "difficulty": "beginner",
                    "estimatedHours": 8,
                    "createdAt": "{datetime.now().isoformat()}",
                    "deadline": "2025-08-17",
                    "intensity": "moderate"
                }}
            ]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI education expert who creates personalized learning experiences. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            import re
            content = response.choices[0].message.content
            json_match = re.search(r'\\[.*\\]', content, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group())
                
                # Add unique IDs
                for i, topic in enumerate(suggestions):
                    topic['id'] = f"{user_id}_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                
                return suggestions
            else:
                # Fallback topics
                return self._generate_fallback_topics(user_input, user_id)
                
        except Exception as e:
            print(f"Error generating custom topics: {e}")
            return self._generate_fallback_topics(user_input, user_id)
    
    def _generate_fallback_topics(self, user_input: str, user_id: str) -> List[Dict]:
        """Generate fallback topics when AI generation fails"""
        base_date = datetime.now()
        
        # Create a more descriptive title based on the user input
        def create_descriptive_title(input_text: str) -> str:
            input_lower = input_text.lower()
            
            # Map common topics to specific learning outcomes
            if "neural network" in input_lower or "neural net" in input_lower:
                return "Building and Training Neural Networks from Scratch"
            elif "machine learning" in input_lower or "ml" in input_lower:
                return "Implementing Core Machine Learning Algorithms"
            elif "deep learning" in input_lower or "dl" in input_lower:
                return "Developing Deep Learning Models with PyTorch"
            elif "computer vision" in input_lower or "cv" in input_lower:
                return "Creating Computer Vision Systems for Image Analysis"
            elif "nlp" in input_lower or "natural language" in input_lower:
                return "Building Natural Language Processing Applications"
            elif "reinforcement learning" in input_lower or "rl" in input_lower:
                return "Designing Reinforcement Learning Agents for Decision Making"
            elif "ai" in input_lower or "artificial intelligence" in input_lower:
                return "Applying Artificial Intelligence Techniques to Real-World Problems"
            elif "data science" in input_lower:
                return "Mastering Data Science Workflows and Analytics"
            elif "algorithm" in input_lower:
                return "Implementing and Optimizing Core Algorithms"
            elif "python" in input_lower:
                return "Advanced Python Programming for Data Science and AI"
            else:
                # For other topics, create a more specific title
                clean_input = input_text.replace("I'm interested in", "").replace("learning about", "").strip()
                return f"Mastering {clean_input}: From Theory to Implementation"
        
        title = create_descriptive_title(user_input)
        
        return [
            {
                "id": f"{user_id}_custom_{base_date.strftime('%Y%m%d_%H%M%S')}_0",
                "title": title,
                "description": f"Develop practical skills and deep understanding in {user_input}. This comprehensive course covers essential concepts, hands-on implementation, and real-world applications to build your expertise from the ground up.",
                "userInput": user_input,
                "baseTopic": "machine_learning",
                "difficulty": "beginner",
                "estimatedHours": 6,
                "createdAt": base_date.isoformat(),
                "deadline": (base_date.replace(day=base_date.day + 14)).strftime('%Y-%m-%d'),
                "intensity": "moderate"
            }
        ]
    
    def generate_descriptive_title_from_content(self, user_input: str, lesson_outline: Dict = None) -> str:
        """Generate a descriptive title based on lesson content and learning objectives"""
        try:
            if lesson_outline and 'learningObjectives' in lesson_outline:
                objectives = lesson_outline.get('learningObjectives', [])
                modules = lesson_outline.get('modules', [])
                
                # Extract key skills and concepts from objectives and modules
                key_concepts = []
                for obj in objectives:
                    # Extract action verbs and key concepts
                    if 'implement' in obj.lower() or 'build' in obj.lower():
                        key_concepts.append('implementation')
                    elif 'design' in obj.lower() or 'create' in obj.lower():
                        key_concepts.append('design')
                    elif 'analyze' in obj.lower() or 'evaluate' in obj.lower():
                        key_concepts.append('analysis')
                    elif 'optimize' in obj.lower():
                        key_concepts.append('optimization')
                
                module_topics = [module.get('title', '') for module in modules]
                
                # Generate title based on content
                prompt = f"""
                Based on the following lesson content, create a specific, descriptive title that captures what students will actually learn and be able to do:
                
                User Interest: {user_input}
                Learning Objectives: {objectives}
                Module Topics: {module_topics}
                Key Concepts: {key_concepts}
                
                Create a title that:
                1. Focuses on practical skills and outcomes
                2. Includes specific techniques or applications
                3. Avoids generic terms like "Introduction" or "Basics"
                4. Reflects the depth and scope of learning
                
                Examples of good titles:
                - "Building Convolutional Neural Networks for Medical Image Analysis"
                - "Implementing Natural Language Processing with Transformer Models"
                - "Developing Reinforcement Learning Agents for Strategic Games"
                - "Creating Computer Vision Systems for Autonomous Vehicles"
                
                Return only the title, nothing else.
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an educational content specialist who creates descriptive, outcome-focused course titles."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=0.7,
                    timeout=15
                )
                
                title = response.choices[0].message.content.strip()
                return title if title else self._generate_fallback_title(user_input)
                
            else:
                return self._generate_fallback_title(user_input)
                
        except Exception as e:
            print(f"Error generating descriptive title: {e}")
            return self._generate_fallback_title(user_input)
    
    def _generate_fallback_title(self, user_input: str) -> str:
        """Generate a fallback descriptive title when AI generation fails"""
        input_lower = user_input.lower()
        
        # Map common topics to specific learning outcomes
        if "neural network" in input_lower:
            return "Building and Training Neural Networks from Scratch"
        elif "machine learning" in input_lower:
            return "Implementing Core Machine Learning Algorithms"
        elif "deep learning" in input_lower:
            return "Developing Deep Learning Models with PyTorch"
        elif "computer vision" in input_lower:
            return "Creating Computer Vision Systems for Image Analysis"
        elif "nlp" in input_lower or "natural language" in input_lower:
            return "Building Natural Language Processing Applications"
        elif "reinforcement learning" in input_lower:
            return "Designing Reinforcement Learning Agents for Decision Making"
        elif "ai" in input_lower or "artificial intelligence" in input_lower:
            return "Applying Artificial Intelligence Techniques to Real-World Problems"
        elif "data science" in input_lower:
            return "Mastering Data Science Workflows and Analytics"
        elif "algorithm" in input_lower:
            return "Implementing and Optimizing Core Algorithms"
        elif "python" in input_lower:
            return "Advanced Python Programming for Data Science and AI"
        else:
            # For other topics, create a more specific title
            clean_input = user_input.replace("I'm interested in", "").replace("learning about", "").strip()
            return f"Mastering {clean_input}: From Theory to Implementation"
    
    def _analyze_topic_title(self, topic_title: str) -> Dict:
        """Analyze a topic title to extract actionable components and learning outcomes"""
        title_lower = topic_title.lower()
        
        # Extract action verbs that indicate what students will do
        actions = []
        action_words = ['building', 'creating', 'implementing', 'developing', 'designing', 'applying', 'mastering', 'optimizing', 'analyzing', 'training', 'deploying']
        for action in action_words:
            if action in title_lower:
                actions.append(action)
        
        # Extract technical components/technologies
        technologies = []
        tech_keywords = [
            'neural networks', 'machine learning', 'deep learning', 'computer vision', 
            'nlp', 'natural language processing', 'reinforcement learning', 'algorithms',
            'models', 'systems', 'pipelines', 'agents', 'networks', 'transformers',
            'convolutional', 'recurrent', 'lstm', 'gru', 'pytorch', 'tensorflow',
            'python', 'pandas', 'numpy', 'scikit-learn'
        ]
        for tech in tech_keywords:
            if tech in title_lower:
                technologies.append(tech)
        
        # Extract application domains
        domain = "general application"
        domain_keywords = {
            'medical': ['medical', 'healthcare', 'diagnosis', 'imaging'],
            'autonomous vehicles': ['autonomous', 'vehicle', 'driving', 'transportation'],
            'games': ['game', 'gaming', 'strategic', 'ai'],
            'finance': ['financial', 'trading', 'market', 'investment'],
            'robotics': ['robot', 'robotic', 'automation', 'control'],
            'image analysis': ['image', 'vision', 'visual', 'recognition'],
            'text analysis': ['text', 'language', 'linguistic', 'sentiment'],
            'data science': ['data', 'analytics', 'prediction', 'analysis']
        }
        
        for domain_name, keywords in domain_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                domain = domain_name
                break
        
        # Extract expected deliverables
        deliverables = []
        if 'system' in title_lower:
            deliverables.append('functional system')
        if 'model' in title_lower:
            deliverables.append('trained model')
        if 'application' in title_lower:
            deliverables.append('working application')
        if 'pipeline' in title_lower:
            deliverables.append('data pipeline')
        if 'agent' in title_lower:
            deliverables.append('intelligent agent')
        
        if not deliverables:
            deliverables = ['practical implementation']
        
        # Generate a non-verbatim, academic course title
        base = technologies[0] if technologies else "AI Topic"
        if actions:
            course_title = f"Introduction to {base}" if any(a in actions for a in ['learn', 'understand']) else f"{actions[0].capitalize()} {base}"
        else:
            course_title = f"{base} Fundamentals"
        if domain and domain != "general application":
            course_title += f" for {domain.title()}"
        return {
            'actions': actions if actions else ['learn', 'understand'],
            'technologies': technologies if technologies else ['core concepts'],
            'domain': domain,
            'deliverables': deliverables,
            'course_title': course_title
        }
    
    def save_custom_topic(self, user_id: str, topic: Dict):
        """Save a custom topic to user's library"""
        # Create custom topics file if it doesn't exist
        custom_topics_file = f"{DATA_DIR}/custom_topics.json"
        if not os.path.exists(custom_topics_file):
            with open(custom_topics_file, 'w') as f:
                json.dump({}, f)
        
        custom_topics = self.load_data(custom_topics_file)
        
        if user_id not in custom_topics:
            custom_topics[user_id] = []
        
        # Always use a non-verbatim, academic course title
        if 'title' not in topic or not topic['title'] or topic['title'].strip().lower() == topic.get('userInput', '').strip().lower():
            # Generate a descriptive title from the topic or userInput
            analysis = self._analyze_topic_title(topic.get('userInput', topic.get('title', '')))
            topic['title'] = analysis.get('course_title', topic.get('title', ''))
        # Add progress tracking fields and library metadata
        topic.update({
            'progress': 0,
            'timeSpent': 0,
            'lastAccessed': None,
            'createdDate': datetime.now().isoformat(),
            'status': 'not_started',
            'completionDate': None,
            'totalSessions': 0,
            'averageSessionTime': 0,
            'competencyScore': None,
            'tags': topic.get('baseTopic', '').split('_'),
            'isLibraryItem': True
        })
        
        custom_topics[user_id].append(topic)
        self.save_data(custom_topics_file, custom_topics)
        
        # Also save to topics library for better organization
        self._add_to_topics_library(user_id, topic)
    
    def get_user_custom_topics(self, user_id: str) -> List[Dict]:
        """Get user's custom topics library"""
        custom_topics_file = f"{DATA_DIR}/custom_topics.json"
        if not os.path.exists(custom_topics_file):
            return []
        
        custom_topics = self.load_data(custom_topics_file)
        return custom_topics.get(user_id, [])
    
    def update_topic_progress(self, user_id: str, topic_id: str, progress: int, time_spent: int = None):
        """Update progress for a custom topic"""
        custom_topics_file = f"{DATA_DIR}/custom_topics.json"
        if not os.path.exists(custom_topics_file):
            return
        
        custom_topics = self.load_data(custom_topics_file)
        user_topics = custom_topics.get(user_id, [])
        
        for topic in user_topics:
            if topic['id'] == topic_id:
                topic['progress'] = progress
                topic['lastAccessed'] = datetime.now().isoformat()
                if time_spent is not None:
                    topic['timeSpent'] = topic.get('timeSpent', 0) + time_spent
                break
        
        custom_topics[user_id] = user_topics
        self.save_data(custom_topics_file, custom_topics)
    
    def _add_to_topics_library(self, user_id: str, topic: Dict):
        """Add topic to organized library structure"""
        library_file = f"{DATA_DIR}/topics_library.json"
        if not os.path.exists(library_file):
            with open(library_file, 'w') as f:
                json.dump({}, f)
        
        library = self.load_data(library_file)
        if user_id not in library:
            library[user_id] = {
                'by_category': {},
                'by_difficulty': {},
                'recent': [],
                'favorites': [],
                'completed': []
            }
        # Categorize by base topic
        category = topic.get('baseTopic', 'general')
        if category not in library[user_id]['by_category']:
            library[user_id]['by_category'][category] = []
        library[user_id]['by_category'][category].append(topic['id'])
        
        # Categorize by difficulty
        difficulty = topic.get('difficulty', 'beginner')
        if difficulty not in library[user_id]['by_difficulty']:
            library[user_id]['by_difficulty'][difficulty] = []
        library[user_id]['by_difficulty'][difficulty].append(topic['id'])
        
        # Add to recent (keep last 10)
        library[user_id]['recent'].insert(0, topic['id'])
        if len(library[user_id]['recent']) > 10:
            library[user_id]['recent'] = library[user_id]['recent'][:10]
        
        self.save_data(library_file, library)
    
    def get_topics_library(self, user_id: str) -> Dict:
        """Get organized topics library for user"""
        library_file = f"{DATA_DIR}/topics_library.json"
        custom_topics = self.get_user_custom_topics(user_id)
        
        if not os.path.exists(library_file):
            return {'by_category': {}, 'by_difficulty': {}, 'recent': [], 'favorites': [], 'completed': []}
        
        library = self.load_data(library_file)
        user_library = library.get(user_id, {'by_category': {}, 'by_difficulty': {}, 'recent': [], 'favorites': [], 'completed': []})
        
        # Populate with full topic data
        topics_by_id = {topic['id']: topic for topic in custom_topics}
        
        result = {
            'by_category': {},
            'by_difficulty': {},
            'recent': [],
            'favorites': [],
            'completed': [],
            'stats': {
                'total_topics': len(custom_topics),
                'completed_topics': len([t for t in custom_topics if t.get('progress', 0) == 100]),
                'in_progress': len([t for t in custom_topics if 0 < t.get('progress', 0) < 100]),
                'total_time_spent': sum(t.get('timeSpent', 0) for t in custom_topics)
            }
        }
        
        # Populate categories
        for category, topic_ids in user_library['by_category'].items():
            result['by_category'][category] = [topics_by_id.get(tid) for tid in topic_ids if tid in topics_by_id]
            result['by_category'][category] = [t for t in result['by_category'][category] if t is not None]
        
        # Populate recent
        result['recent'] = [topics_by_id.get(tid) for tid in user_library['recent'][:5] if tid in topics_by_id]
        result['recent'] = [t for t in result['recent'] if t is not None]
        
        return result
    
    def search_topics_library(self, user_id: str, query: str, filters: Dict = None) -> List[Dict]:
        """Search user's topics library"""
        custom_topics = self.get_user_custom_topics(user_id)
        
        query_lower = query.lower()
        results = []
        
        for topic in custom_topics:
            # Search in title, description, tags
            searchable_text = f"{topic.get('title', '')} {topic.get('description', '')} {' '.join(topic.get('tags', []))}"
            if query_lower in searchable_text.lower():
                results.append(topic)
        
        # Apply filters
        if filters:
            if filters.get('difficulty'):
                results = [t for t in results if t.get('difficulty') == filters['difficulty']]
            if filters.get('status'):
                results = [t for t in results if t.get('status') == filters['status']]
            if filters.get('category'):
                results = [t for t in results if t.get('baseTopic') == filters['category']]
        
        # Sort by relevance and recency
        results.sort(key=lambda x: (
            query_lower in x.get('title', '').lower(),
            x.get('lastAccessed', '2000-01-01')
        ), reverse=True)
        
        return results
    
    def start_learning_session(self, user_id: str, topic_id: str) -> str:
        """Start a learning session and return session ID"""
        learning_sessions_file = f"{DATA_DIR}/learning_sessions.json"
        if not os.path.exists(learning_sessions_file):
            with open(learning_sessions_file, 'w') as f:
                json.dump([], f)
        
        sessions = self.load_data(learning_sessions_file)
        
        session_id = f"{user_id}_{topic_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = {
            'id': session_id,
            'userId': user_id,
            'topicId': topic_id,
            'startTime': datetime.now().isoformat(),
            'endTime': None,
            'duration': None,
            'active': True
        }
        
        sessions.append(session)
        self.save_data(learning_sessions_file, sessions)
        
        return session_id
    
    def end_learning_session(self, session_id: str) -> int:
        """End a learning session and return duration in minutes"""
        learning_sessions_file = f"{DATA_DIR}/learning_sessions.json"
        if not os.path.exists(learning_sessions_file):
            return 0
        
        sessions = self.load_data(learning_sessions_file)
        
        for session in sessions:
            if session['id'] == session_id and session['active']:
                end_time = datetime.now()
                start_time = datetime.fromisoformat(session['startTime'])
                duration = int((end_time - start_time).total_seconds() / 60)
                
                session['endTime'] = end_time.isoformat()
                session['duration'] = duration
                session['active'] = False
                
                self.save_data(learning_sessions_file, sessions)
                return duration
        
        return 0
    
    def get_active_sessions(self, user_id: str) -> List[Dict]:
        """Get active learning sessions for a user"""
        learning_sessions_file = f"{DATA_DIR}/learning_sessions.json"
        if not os.path.exists(learning_sessions_file):
            return []
        
        sessions = self.load_data(learning_sessions_file)
        return [s for s in sessions if s['userId'] == user_id and s['active']]
    
    def generate_lesson_outline(self, topic: str, difficulty: str = "beginner", user_assessment: Dict = None) -> Dict:
        """Generate a comprehensive, pedagogically progressive lesson outline with numbered modules, model-specific titles, and deepening content."""
        try:
            analysis = self._analyze_topic_title(topic)
            course_title = analysis.get('course_title') or topic
            # Make course title more specific if needed
            if course_title.strip().lower() == topic.strip().lower() or 'i wanna' in course_title.lower() or 'learn' in course_title.lower():
                course_title = self._generate_fallback_title(topic)
            knowledge_gaps = user_assessment.get('knowledge_gaps', []) if user_assessment else []
            strong_areas = user_assessment.get('strong_areas', []) if user_assessment else []
            prompt = f"""You are an expert AI curriculum designer. Create a comprehensive, implementation-focused lesson outline for the course titled: '{course_title}'.\n\nREQUIREMENTS:\n- Number each module sequentially (e.g., Module 1, Module 2, ...).\n- Each module must deepen in complexity and build on the previous.\n- Make the course title specific to the type of model or topic.\n- For each module, elaborate on mathematical concepts, provide concrete examples, and include practical applications.\n- Add a variety of content types: math boxes, code boxes, real-world case studies, visual explanations, and summary tables.\n- Each module must have: title, estimated time, description, key concepts, activities, assessment type, and which gaps it addresses.\n- The outline must show clear pedagogical progression from fundamentals to advanced applications.\n- Include a final project/deliverable that is concrete and measurable.\n- List prerequisites and resources.\n- Use the following user knowledge profile:\n  - Knowledge gaps: {knowledge_gaps}\n  - Strong areas: {strong_areas}\n  - Difficulty: {difficulty}\n- Return ONLY a JSON object with this format:\n{{\n    \"course_title\": \"{course_title}\",\n    \"topic\": \"{topic}\",\n    \"difficulty\": \"{difficulty}\",\n    \"title_promises\": {analysis},\n    \"estimatedDuration\": \"4-6 hours for hands-on implementation\",\n    \"learningObjectives\": [\"...\"],\n    \"prerequisites\": [\"...\"],\n    \"modules\": [{{\n        \"id\": \"module_1\",\n        \"title\": \"...\",\n        \"estimatedTime\": \"...\",\n        \"description\": \"...\",\n        \"keyConcepts\": [\"...\"],\n        \"activities\": [\"...\"],\n        \"assessmentType\": \"...\",\n        \"addressesGaps\": [\"...\"],\n        \"mathBox\": \"...\",\n        \"codeBox\": \"...\",\n        \"caseStudy\": \"...\",\n        \"visualExplanation\": \"...\",\n        \"summaryTable\": \"...\"\n    }}],\n    \"resources\": [\"...\"],\n    \"expectedOutcomes\": [\"...\"]\n}}"""
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.7,
                timeout=40
            )
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            outline = json.loads(content)
            outline['generated_at'] = datetime.now().isoformat()
            return outline
        except Exception as e:
            print(f"Error generating lesson outline: {e}")
            return self._generate_fallback_outline(topic, difficulty)
    
    def _generate_fallback_outline(self, topic: str, difficulty: str) -> Dict:
        """Generate a robust fallback lesson outline with numbered, deepening modules and rich content types."""
        title_analysis = self._analyze_topic_title(topic)
        action_verb = title_analysis['actions'][0] if title_analysis['actions'] else "implement"
        main_tech = title_analysis['technologies'][0] if title_analysis['technologies'] else "core concepts"
        domain = title_analysis['domain']
        deliverable = title_analysis['deliverables'][0] if title_analysis['deliverables'] else "practical solution"
        modules = []
        for i in range(1, 5):
            modules.append({
                "id": f"module_{i}",
                "title": f"Module {i}: {'Foundations' if i==1 else 'Advanced Concepts' if i==4 else 'Deepening Skills'} in {main_tech}",
                "estimatedTime": f"{30 + i*15} minutes",
                "description": f"{'Establish theoretical foundation and setup.' if i==1 else 'Apply and extend concepts.' if i==2 else 'Real-world application.' if i==3 else 'Integration and mastery.'}",
                "keyConcepts": [f"Key concept {i}A", f"Key concept {i}B"],
                "activities": [f"Activity {i}A", f"Activity {i}B"],
                "assessmentType": "quiz" if i < 4 else "project",
                "addressesGaps": [f"Gap {i}"],
                "mathBox": f"Math concept explanation for module {i}.",
                "codeBox": f"Code example for module {i}.",
                "caseStudy": f"Case study for module {i}.",
                "visualExplanation": f"Visual explanation for module {i}.",
                "summaryTable": f"Summary table for module {i}."
            })
        return {
            "course_title": f"{action_verb.title()} {main_tech} for {domain.title() if domain else 'AI'}: From Fundamentals to {deliverable.title()}",
            "topic": topic,
            "difficulty": difficulty,
            "title_promises": title_analysis,
            "estimatedDuration": "4-6 hours for hands-on implementation",
            "learningObjectives": [
                f"Students will {action_verb} a {deliverable} using {main_tech}",
                f"Apply {main_tech} techniques to {domain} problems",
                f"Demonstrate mastery through a working implementation",
                f"Understand the theoretical and mathematical foundations behind {main_tech}"
            ],
            "prerequisites": ["Basic programming knowledge", "Familiarity with Python", "Mathematical fundamentals"],
            "modules": modules,
            "resources": [f"Documentation for {main_tech}", "Code examples and templates", "Domain-specific datasets"],
            "expectedOutcomes": [
                f"Fully functional {deliverable}",
                f"Understanding of {main_tech} principles through implementation",
                f"Ability to apply techniques to new {domain} problems",
                "Confidence in building similar systems independently"
            ],
            "generated_at": datetime.now().isoformat()
        }

# --- Flask API server entry point for frontend integration ---
if __name__ == "__main__":
    try:
        from api_server import app
        print("[profai_engine] Running Flask API server for frontend integration...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"[profai_engine] Error running Flask API server: {e}")