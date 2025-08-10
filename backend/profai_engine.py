import json
import os
from datetime import datetime
from typing import Dict, List, Any
import openai

# Import from local config
from config import OPENAI_API_KEY, DATA_DIR

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

class ProfAIEngine:
    def __init__(self):
        self.users_file = f"{DATA_DIR}/users.json"
        self.lessons_file = f"{DATA_DIR}/lessons.json"
        self.sessions_file = f"{DATA_DIR}/sessions.json"
        self.progress_file = f"{DATA_DIR}/progress.json"
        self.curriculum_file = f"{DATA_DIR}/curriculum.json"
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Create data files if they don't exist"""
        os.makedirs(DATA_DIR, exist_ok=True)
        for file_path in [self.users_file, self.lessons_file, self.progress_file, self.curriculum_file]:
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
        """Create a new user with enhanced profile"""
        try:
            print(f"Creating user with name: {name}")
            print(f"Users file path: {self.users_file}")
            self._ensure_data_files()  # Make sure data files exist
            
            users = self.load_data(self.users_file)
            print(f"Current users: {len(users)}")
            
            user_id = f"user_{len(users) + 1}"
            users[user_id] = {
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
            
            self.save_data(self.users_file, users)
            print(f"Successfully created user: {user_id}")
            return user_id
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            print(f"DATA_DIR: {DATA_DIR}")
            print(f"Current directory: {os.getcwd()}")
            raise  # Re-raise the exception after logging
    
    def generate_lesson_content(self, topic: str, user_profile: Dict) -> Dict:
        """Generate personalized lesson content for a topic and user profile, using OpenAI and RAG from PDF chunks."""
        competency = user_profile.get('competency_scores', {}).get(topic, 0)
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
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=3)
            context = '\n\n'.join([f"From {fname}: {chunk}" for fname, chunk in relevant_chunks])
        except Exception as rag_e:
            print(f"RAG retrieval failed: {rag_e}")
            context = ""

        prompt = f"""You are an expert AI tutor. Use the following course material as context to create a lesson about {topic} for someone with competency level {competency}/10.

Course context (from real lecture notes):\n{context}\n
        ]
        """
        try:
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
            # Optionally cache the lesson
            return lesson
        except Exception as e:
            print(f"Lesson generation failed: {e}")
            return {}
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
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=3)
            context = '\n\n'.join([f"From {fname}: {chunk}" for fname, chunk in relevant_chunks])
        except Exception as rag_e:
            print(f"RAG retrieval failed (assessment): {rag_e}")
            context = ""

        prompt = f"""You are an expert AI tutor. Use the following course material as context to create exactly 5 multiple choice questions for an initial assessment on \"{topic}\".\n\nCourse context (from real lecture notes):\n{context}\n\nThese questions should:\n1. Cover different fundamental aspects of {topic}\n2. Range from basic to intermediate difficulty\n3. Help identify what areas the student knows vs doesn't know\n4. Be diagnostic rather than just testing\n\nReturn ONLY a JSON array with this exact format:\n[\n    {{\n        \"question\": \"Question text here\",\n        \"options\": [\"A) Option 1\", \"B) Option 2\", \"C) Option 3\", \"D) Option 4\"],\n        \"correct\": \"A\",\n        \"concept\": \"fundamental_concept_being_tested\",\n        \"difficulty\": 1\n    }}\n]\n"""

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
            # Ensure we have exactly 5 questions
            if len(questions) != 5:
                print(f"Warning: Expected 5 questions, got {len(questions)}")
            return questions
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw content: {content}")
            return []
        except Exception as e:
            print(f"Error generating initial assessment: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def generate_lesson_content(self, topic: str, user_profile: Dict) -> Dict:
        """Generate personalized lesson content for a topic and user profile, always using OpenAI."""
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