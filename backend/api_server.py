from flask import Flask, request, jsonify
from flask_cors import CORS
from profai_engine import ProfAIEngine
import json
import os, io, hashlib, requests
from flask import send_file
from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, DATA_DIR


app = Flask(__name__)
CORS(app)

# Initialize the engine
engine = ProfAIEngine()

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    print("[API] Received user creation request")
    print("[API] Request data:", request.get_json())
    try:
        print("[API] Starting user creation request")
        data = request.get_json()
        if not data:
            print("[API] No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400
            
        name = data.get('name')
        if not name:
            print("[API] Name is required but not provided")
            return jsonify({'error': 'Name is required'}), 400
        
        print(f"[API] Attempting to create user with name: {name}")
        # Create the user
        user_id = engine.create_user(name)
        if not user_id:
            print("[API] Failed to create user - engine returned None")
            return jsonify({'error': 'Failed to create user. Please check server logs for details.'}), 500
            
        print(f"[API] User created successfully with ID: {user_id}")
        # Get the user data
        user_data = engine.get_user(user_id)
        if not user_data:
            print(f"[API] Failed to retrieve data for user_id: {user_id}")
            return jsonify({'error': 'User created but failed to retrieve data'}), 500
            
        print("[API] Successfully retrieved user data")
        return jsonify({
            'user_id': user_id,
            'user_data': user_data
        })
    except Exception as e:
        import traceback
        print(f"[API] Error in create_user endpoint: {str(e)}")
        print(f"[API] Stack trace: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error. Please try again.'}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user data"""
    try:
        user_data = engine.get_user(user_id)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# LEGACY COMPATIBILITY ENDPOINTS (for current React app)
@app.route('/api/assessment/questions', methods=['POST'])
def generate_assessment_questions():
    """Generate assessment questions for a topic (legacy compatibility)"""
    data = request.get_json()
    topic = data.get('topic')
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    try:
        print(f"[API] Generating assessment questions for topic: {topic}")
        questions = engine.generate_initial_assessment(topic)  # Use new enhanced method
        return jsonify({
            'questions': questions,
            'total_questions': len(questions)
        })
    except Exception as e:
        print(f"[API] Error generating assessment questions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assessment/submit', methods=['POST'])
def submit_assessment():
    """Submit assessment answers and get score (legacy compatibility)"""
    data = request.get_json()
    user_id = data.get('user_id')
    topic = data.get('topic')
    answers = data.get('answers')
    questions = data.get('questions')
    
    if not all([user_id, topic, answers, questions]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Calculate score
        correct = 0
        for i, question in enumerate(questions):
            if str(answers.get(i)) == question.get('correct'):
                correct += 1
        
        score = (correct / len(questions)) * 10
        
        # Update user competency
        engine.update_user_competency(user_id, topic, score)
        
        return jsonify({
            'score': score,
            'correct': correct,
            'total': len(questions)
        })
    except Exception as e:
        print(f"Error submitting assessment: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route('/api/lesson/generate', methods=['POST'])
def generate_lesson():
    """Generate lesson content (legacy compatibility)"""
    data = request.get_json()
    topic = data.get('topic')
    user_id = data.get('user_id')
    
    if not all([topic, user_id]):
        return jsonify({'error': 'Topic and user_id are required'}), 400
    
    try:
        print(f"=== LESSON GENERATION START ===")
        print(f"Topic: {topic}")
        print(f"User ID: {user_id}")
        
        user_profile = engine.get_user(user_id)
        print(f"User profile retrieved: {user_profile}")
        
        print("Starting lesson content generation...")
        lesson = engine.generate_lesson_content(topic, user_profile)
        print(f"Lesson generated: {bool(lesson)}")
        print(f"Lesson keys: {lesson.keys() if lesson else 'None'}")
        
        if not lesson:
            print("ERROR: Empty lesson returned")
            return jsonify({'error': 'Failed to generate lesson content'}), 500
        
        print("=== LESSON GENERATION SUCCESS ===")
        return jsonify(lesson)
        
    except Exception as e:
        print(f"=== LESSON GENERATION ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return jsonify({'error': str(e)}), 500

# NEW ENHANCED ENDPOINTS
@app.route('/api/assessment/initial', methods=['POST'])
def generate_initial_assessment():
    """Generate initial 5 questions to identify knowledge gaps"""
    data = request.get_json()
    topic = data.get('topic')
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    try:
        print(f"Generating initial assessment for topic: {topic}")
        questions = engine.generate_initial_assessment(topic)
        return jsonify({
            'questions': questions,
            'type': 'initial',
            'total_questions': 5
        })
    except Exception as e:
        print(f"Error generating initial assessment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assessment/adaptive', methods=['POST'])
def generate_adaptive_assessment():
    """Generate adaptive 5 questions targeting weak areas"""
    data = request.get_json()
    user_id = data.get('user_id')
    topic = data.get('topic')
    initial_results = data.get('initial_results')  # Results from first 5 questions
    
    if not all([user_id, topic, initial_results]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        print(f"Generating adaptive assessment for user {user_id}")
        questions = engine.generate_adaptive_assessment(topic, initial_results)
        return jsonify({
            'questions': questions,
            'type': 'adaptive',
            'total_questions': 5
        })
    except Exception as e:
        print(f"Error generating adaptive assessment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/assessment/complete', methods=['POST'])
def complete_full_assessment():
    """Process both initial and adaptive assessments to create learning plan"""
    data = request.get_json()
    user_id = data.get('user_id')
    topic = data.get('topic')
    initial_answers = data.get('initial_answers')
    adaptive_answers = data.get('adaptive_answers')
    all_questions = data.get('all_questions')
    
    try:
        # Analyze results and create learning plan
        analysis = engine.analyze_full_assessment(
            user_id, topic, initial_answers, adaptive_answers, all_questions
        )
        
        # Update user competency with detailed breakdown
        engine.update_user_competency_detailed(user_id, topic, analysis)
        
        return jsonify({
            'overall_score': analysis['overall_score'],
            'knowledge_gaps': analysis['knowledge_gaps'],
            'strong_areas': analysis['strong_areas'],
            'learning_path': analysis['learning_path'],
            'recommended_lessons': analysis['recommended_lessons']
        })
    except Exception as e:
        print(f"Error completing assessment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/curriculum/generate', methods=['POST'])
def generate_curriculum():
    """Generate personalized curriculum based on assessment results"""
    data = request.get_json()
    user_id = data.get('user_id')
    topic = data.get('topic')
    knowledge_gaps = data.get('knowledge_gaps')
    
    try:
        curriculum = engine.generate_personalized_curriculum(user_id, topic, knowledge_gaps)
        return jsonify(curriculum)
    except Exception as e:
        print(f"Error generating curriculum: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lesson/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get specific lesson content"""
    try:
        lesson = engine.get_lesson_content(lesson_id)
        return jsonify(lesson)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lesson/quiz', methods=['POST'])
def generate_lesson_quiz():
    """Generate quiz for specific lesson"""
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    lesson_content = data.get('lesson_content')
    
    try:
        quiz = engine.generate_lesson_quiz(lesson_id, lesson_content)
        return jsonify(quiz)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/submit', methods=['POST'])
def submit_lesson_quiz():
    """Submit quiz answers and get results"""
    data = request.get_json()
    user_id = data.get('user_id')
    lesson_id = data.get('lesson_id')
    answers = data.get('answers')
    questions = data.get('questions')
    
    try:
        results = engine.evaluate_lesson_quiz(user_id, lesson_id, answers, questions)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Get detailed user progress and analytics"""
    try:
        progress = engine.get_user_progress(user_id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/lesson/outline', methods=['POST'])
def generate_lesson_outline():
    """Generate a lesson outline based on topic and assessment results"""
    try:
        data = request.get_json()
        topic = data.get('topic')
        difficulty = data.get('difficulty', 'beginner')
        user_assessment = data.get('assessment_results')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        outline = engine.generate_lesson_outline(topic, difficulty, user_assessment)
        return jsonify(outline)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assessment/final', methods=['POST'])
def generate_final_assessment():
    """Generate final wrap-up assessment"""
    data = request.get_json()
    user_id = data.get('user_id')
    topic = data.get('topic')
    completed_lessons = data.get('completed_lessons')
    
    try:
        final_assessment = engine.generate_final_assessment(user_id, topic, completed_lessons)
        return jsonify(final_assessment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """Analyze user response sentiment"""
    data = request.get_json()
    user_response = data.get('response')
    lesson_context = data.get('lesson_context', '')
    
    if not user_response:
        return jsonify({'error': 'Response is required'}), 400
    
    try:
        sentiment = engine.analyze_sentiment_enhanced(user_response, lesson_context)
        return jsonify(sentiment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/save', methods=['POST'])
def save_session():
    """Save a complete learning session"""
    data = request.get_json()
    user_id = data.get('user_id')
    session_data = data.get('session_data')
    
    if not all([user_id, session_data]):
        return jsonify({'error': 'user_id and session_data are required'}), 400
    
    try:
        engine.save_detailed_session(user_id, session_data)
        return jsonify({'message': 'Session saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topics', methods=['GET'])
def get_available_topics():
    """Get list of available learning topics"""
    try:
        # Default topics available for learning
        topics = [
            {
                'id': 'types_of_ai_models',
                'name': 'Types of AI Models',
                'description': 'Learn about different types of AI models and their applications',
                'difficulty': 'beginner',
                'estimated_time': '30-45 minutes'
            },
            {
                'id': 'machine_learning_fundamentals',
                'name': 'Machine Learning Fundamentals',
                'description': 'Core concepts of machine learning including supervised and unsupervised learning',
                'difficulty': 'beginner',
                'estimated_time': '45-60 minutes'
            },
            {
                'id': 'neural_networks',
                'name': 'Neural Networks',
                'description': 'Understanding neural networks, perceptrons, and basic architectures',
                'difficulty': 'intermediate',
                'estimated_time': '60-90 minutes'
            },
            {
                'id': 'deep_learning',
                'name': 'Deep Learning',
                'description': 'Advanced neural networks and deep learning techniques',
                'difficulty': 'intermediate',
                'estimated_time': '90-120 minutes'
            },
            {
                'id': 'natural_language_processing',
                'name': 'Natural Language Processing',
                'description': 'NLP fundamentals including text processing and language models',
                'difficulty': 'intermediate',
                'estimated_time': '60-90 minutes'
            },
            {
                'id': 'computer_vision',
                'name': 'Computer Vision',
                'description': 'Image processing and computer vision techniques',
                'difficulty': 'intermediate',
                'estimated_time': '60-90 minutes'
            },
            {
                'id': 'reinforcement_learning',
                'name': 'Reinforcement Learning',
                'description': 'Learning through interaction and reward systems',
                'difficulty': 'advanced',
                'estimated_time': '90-120 minutes'
            },
            {
                'id': 'ai_ethics_and_safety',
                'name': 'AI Ethics and Safety',
                'description': 'Ethical considerations and safety measures in AI development',
                'difficulty': 'beginner',
                'estimated_time': '30-45 minutes'
            }
        ]
        
        return jsonify({'topics': topics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topics/generate', methods=['POST'])
def generate_custom_topics():
    """Generate custom topics based on user input"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_input = data.get('user_input')
        
        if not user_id or not user_input:
            return jsonify({'error': 'User ID and user input are required'}), 400
        
        # Generate custom topics using the engine
        suggestions = engine.generate_custom_topics(user_id, user_input)
        
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topics/custom', methods=['POST'])
def save_custom_topic():
    """Save a custom topic to user's library"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        topic = data.get('topic')
        
        if not user_id or not topic:
            return jsonify({'error': 'User ID and topic are required'}), 400
        
        # Save the custom topic
        engine.save_custom_topic(user_id, topic)
        
        return jsonify({'message': 'Custom topic saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topics/custom/<user_id>', methods=['GET'])
def get_user_custom_topics(user_id):
    """Get user's custom topics library"""
    try:
        topics = engine.get_user_custom_topics(user_id)
        return jsonify({'topics': topics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topics/progress', methods=['PUT'])
def update_topic_progress():
    """Update custom topic progress"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        topic_id = data.get('topic_id')
        progress = data.get('progress')
        time_spent = data.get('time_spent')
        
        if not all([user_id, topic_id, progress is not None]):
            return jsonify({'error': 'User ID, topic ID, and progress are required'}), 400
        
        engine.update_topic_progress(user_id, topic_id, progress, time_spent)
        
        return jsonify({'message': 'Progress updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/start', methods=['POST'])
def start_learning_session():
    """Start a learning session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        topic_id = data.get('topic_id')
        
        if not user_id or not topic_id:
            return jsonify({'error': 'User ID and topic ID are required'}), 400
        
        session_id = engine.start_learning_session(user_id, topic_id)
        
        return jsonify({'sessionId': session_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/end', methods=['POST'])
def end_learning_session():
    """End a learning session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        duration = engine.end_learning_session(session_id)
        
        return jsonify({'duration': duration})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/active/<user_id>', methods=['GET'])
def get_active_sessions(user_id):
    """Get active learning sessions for a user"""
    try:
        sessions = engine.get_active_sessions(user_id)
        return jsonify({'sessions': sessions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = (data.get('text') or '').strip()
    voice_id = data.get('voice_id') or ELEVENLABS_VOICE_ID
    model_id = data.get('model_id') or 'eleven_multilingual_v2'

    if not text:
        return jsonify({'error':'text is required'}), 400
    if not ELEVENLABS_API_KEY:
        return jsonify({'error':'ELEVENLABS_API_KEY missing'}), 500

    # simple disk cache (avoid re-billing for same line)
    os.makedirs(os.path.join(DATA_DIR, 'tts_cache'), exist_ok=True)
    key = hashlib.sha1(f'{voice_id}::{model_id}::{text}'.encode('utf-8')).hexdigest()
    path = os.path.join(DATA_DIR, 'tts_cache', f'{key}.mp3')
    if os.path.exists(path):
        return send_file(path, mimetype='audio/mpeg', max_age=3600)

    # call ElevenLabs
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
    }
    payload = {
        'text': text,
        'model_id': model_id,
        'voice_settings': {
            'stability': 0.35,
            'similarity_boost': 0.85,
            'style': 0.4,
            'use_speaker_boost': True
        }
    }
    r = requests.post(url, json=payload, headers=headers, stream=True, timeout=60)
    r.raise_for_status()
    with open(path, 'wb') as f:
        for chunk in r.iter_content(8192):
            if chunk: f.write(chunk)

    return send_file(path, mimetype='audio/mpeg', max_age=3600)

@app.route('/api/library/<user_id>', methods=['GET'])
def get_topics_library(user_id):
    """Get organized topics library for user"""
    try:
        library = engine.get_topics_library(user_id)
        return jsonify({'library': library})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/library/<user_id>/search', methods=['POST'])
def search_topics_library(user_id):
    """Search user's topics library"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        filters = data.get('filters', {})
        
        results = engine.search_topics_library(user_id, query, filters)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lesson/enhanced', methods=['POST'])
def generate_enhanced_lesson():
    """Generate enhanced lesson content with academic rigor"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        user_id = data.get('user_id', '')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        # Get user profile for personalization
        user_data = engine.get_user(user_id) if user_id else {}
        user_profile = {
            'competency_scores': user_data.get('competency_scores', {}),
            'knowledge_gaps': user_data.get('knowledge_gaps', {}),
            'learning_path': user_data.get('learning_path', [])
        }
        
        lesson = engine.generate_lesson_content(topic, user_profile)
        return jsonify({'lesson': lesson})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)