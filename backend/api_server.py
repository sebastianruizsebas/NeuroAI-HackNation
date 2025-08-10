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
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        # Create the user
        user_id = engine.create_user(name)
        if not user_id:
            return jsonify({'error': 'Failed to create user'}), 500
            
        # Get the user data
        user_data = engine.get_user(user_id)
        if not user_data:
            return jsonify({'error': 'User created but failed to retrieve data'}), 500
            
        return jsonify({
            'user_id': user_id,
            'user_data': user_data
        })
    except Exception as e:
        print(f"Error in create_user endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

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
        print(f"Generating assessment questions for topic: {topic}")
        questions = engine.generate_initial_assessment(topic)  # Use new enhanced method
        return jsonify({
            'questions': questions,
            'total_questions': len(questions)
        })
    except Exception as e:
        print(f"Error generating assessment questions: {str(e)}")
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)