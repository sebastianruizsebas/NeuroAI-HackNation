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
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
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

        prompt = f"""You are a world-class AI educator with expertise in {topic}. Use the following authentic course material to create a comprehensive, university-level lesson for someone with competency level {competency}/10.

Course context (from real lecture notes):
{context}

LESSON REQUIREMENTS:
- Build directly on the provided course material
- Academic rigor appropriate for university-level study
- Include mathematical formulations and equations from the context
- Provide concrete examples and real-world case studies
- Connect theory to cutting-edge applications
- Address common misconceptions and potential pitfalls
- Reference current research and industry developments

DEPTH CALIBRATION:
- Competency 0-3: Clear explanations with step-by-step derivations
- Competency 4-6: Intermediate mathematical concepts and implementation details
- Competency 7-10: Advanced theory, research frontier, complex optimization problems

ACADEMIC STANDARDS:
- Each section should be substantial (200+ words)
- Include quantitative examples with actual numbers
- Reference equations and proofs from the source material
- Connect to broader field and interdisciplinary applications
- Provide multiple perspectives on complex topics

Return ONLY a JSON object with this enhanced format:
{{
    "topic": "{topic}",
    "competency_level": {competency},
    "overview": "Comprehensive overview establishing context, importance, and learning objectives. Should connect to broader field and reference the source material.",
    "chunks": [
        {{
            "title": "Descriptive Academic Title",
            "content": "Detailed, rigorous explanation with mathematical derivations, concrete examples, and connections to applications. Minimum 200 words.",
            "key_point": "Specific, actionable takeaway demonstrating mastery",
            "mathematical_concepts": ["concept1", "concept2"],
            "examples": ["example1", "example2"],
            "applications": ["application1", "application2"],
            "source_references": ["reference to course material"],
            "difficulty_level": "1-5 scale",
            "estimated_time": "15-20 minutes"
        }}
    ],
    "key_takeaways": [
        "Specific technical knowledge with quantitative understanding",
        "Practical implementation skills developed",
        "Conceptual frameworks mastered",
        "Real-world applications identified"
    ],
    "prerequisites": ["specific prerequisite topics"],
    "mathematical_foundations": ["foundational math concepts"],
    "further_reading": ["academic papers", "textbook chapters"],
    "assessment_criteria": ["measurable learning outcomes"],
    "industry_connections": ["how this applies in practice"],
    "common_misconceptions": ["typical student errors to avoid"]
}}"""
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
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=3)
            context = '\n\n'.join([f"From {fname}: {chunk}" for fname, chunk in relevant_chunks])
        except Exception as rag_e:
            print(f"RAG retrieval failed (assessment): {rag_e}")
            context = ""

        prompt = f"""You are a world-class AI educator with expertise in {topic}. Create exactly 5 diagnostic multiple choice questions for an initial assessment.

Course context from lecture notes:
{context}

REQUIREMENTS for each question:
1. Test DEEP understanding, not memorization
2. Use real-world scenarios and applications
3. Include mathematical concepts where relevant
4. Test conceptual reasoning and problem-solving
5. Avoid trivial or obvious questions
6. Make distractors plausible but definitively incorrect
7. Use precise, academic language
8. Test different cognitive levels (comprehension, application, analysis)

QUALITY STANDARDS:
- Question stem should be at least 20 words and present a clear scenario
- Each option should be substantive (at least 8 words)
- Correct answer must be unambiguous and defensible
- Distractors should reflect common misconceptions
- Include quantitative elements where appropriate

DIFFICULTY PROGRESSION:
- Questions 1-2: Fundamental concepts and definitions
- Questions 3-4: Application and analysis
- Question 5: Synthesis and evaluation

Return ONLY a JSON array with this exact format:
[
    {{
        "question": "In the context of [specific scenario], which approach would be most effective for [specific problem]? Consider the trade-offs between computational complexity and accuracy.",
        "options": [
            "A) [Detailed technical option with specific reasoning]",
            "B) [Alternative approach with different trade-offs]", 
            "C) [Common misconception with plausible reasoning]",
            "D) [Another misconception or oversimplified approach]"
        ],
        "correct": "A",
        "concept": "specific_technical_concept",
        "difficulty": 1,
        "explanation": "Why the correct answer is right and others are wrong"
    }}
]"""

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
        """Generate a comprehensive lesson outline based on topic and user assessment"""
        try:
            # Use assessment results to personalize outline
            knowledge_gaps = []
            strong_areas = []
            if user_assessment:
                knowledge_gaps = user_assessment.get('knowledge_gaps', [])
                strong_areas = user_assessment.get('strong_areas', [])
            
            prompt = f"""Create a comprehensive lesson outline for learning "{topic}" at {difficulty} level.

User's Knowledge Profile:
- Knowledge gaps: {knowledge_gaps}
- Strong areas: {strong_areas}

Create a structured outline with:
1. Learning objectives (3-5 clear, measurable goals)
2. Lesson structure with 4-6 modules
3. Each module should have:
   - Title and estimated time
   - Key concepts covered
   - Learning activities
   - Assessment checkpoints
4. Prerequisites and recommended background
5. Resources and materials needed
6. Expected outcomes

Focus on addressing the user's knowledge gaps while building on their strengths.

Return ONLY a JSON object with this format:
{{
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "estimatedDuration": "2-3 hours",
    "learningObjectives": [
        "Objective 1: Students will be able to...",
        "Objective 2: Students will understand...",
        "Objective 3: Students will apply..."
    ],
    "prerequisites": ["Basic understanding of...", "Familiarity with..."],
    "modules": [
        {{
            "id": "module_1",
            "title": "Module Title",
            "estimatedTime": "30 minutes",
            "description": "What this module covers",
            "keyConcepts": ["Concept 1", "Concept 2"],
            "activities": ["Activity 1", "Activity 2"],
            "assessmentType": "quiz/discussion/practical",
            "addressesGaps": ["gap1", "gap2"]
        }}
    ],
    "resources": ["Resource 1", "Resource 2"],
    "expectedOutcomes": ["Outcome 1", "Outcome 2"]
}}"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
                timeout=30
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
        """Generate a fallback lesson outline when AI generation fails"""
        return {
            "topic": topic,
            "difficulty": difficulty,
            "estimatedDuration": "2-3 hours",
            "learningObjectives": [
                f"Understand the fundamental concepts of {topic}",
                f"Apply basic principles of {topic} to simple problems",
                f"Recognize the importance and applications of {topic}"
            ],
            "prerequisites": ["Basic computer literacy", "Interest in learning"],
            "modules": [
                {
                    "id": "module_1",
                    "title": f"Introduction to {topic}",
                    "estimatedTime": "20 minutes",
                    "description": f"Overview of {topic} and its significance",
                    "keyConcepts": ["Definition", "History", "Importance"],
                    "activities": ["Reading", "Video overview"],
                    "assessmentType": "quiz",
                    "addressesGaps": []
                },
                {
                    "id": "module_2", 
                    "title": "Core Concepts",
                    "estimatedTime": "40 minutes",
                    "description": "Deep dive into the main ideas",
                    "keyConcepts": ["Key principles", "Terminology", "Examples"],
                    "activities": ["Interactive examples", "Practice exercises"],
                    "assessmentType": "practical",
                    "addressesGaps": []
                },
                {
                    "id": "module_3",
                    "title": "Applications and Practice",
                    "estimatedTime": "30 minutes", 
                    "description": "Real-world applications and hands-on practice",
                    "keyConcepts": ["Use cases", "Best practices", "Common patterns"],
                    "activities": ["Case studies", "Hands-on exercises"],
                    "assessmentType": "discussion",
                    "addressesGaps": []
                },
                {
                    "id": "module_4",
                    "title": "Summary and Next Steps",
                    "estimatedTime": "20 minutes",
                    "description": "Review and planning for continued learning",
                    "keyConcepts": ["Key takeaways", "Advanced topics", "Resources"],
                    "activities": ["Review quiz", "Planning session"],
                    "assessmentType": "quiz",
                    "addressesGaps": []
                }
            ],
            "resources": [
                "Course materials and readings",
                "Online tutorials and documentation",
                "Practice exercises and examples"
            ],
            "expectedOutcomes": [
                f"Solid understanding of {topic} fundamentals",
                "Ability to apply concepts to basic problems",
                "Confidence to pursue advanced topics"
            ],
            "generated_at": datetime.now().isoformat()
        }