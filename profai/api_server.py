from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from V2.profai_engine import ProfAIEngine
import json
import time
from threading import Thread
import queue

app = Flask(__name__)
CORS(app)
engine = ProfAIEngine()

# Store active sessions and their output queues
active_sessions = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"message": "ProfAI API is running!"})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    user_id = engine.create_user(name)
    return jsonify({"user_id": user_id, "name": name})

@app.route('/api/assessment/<topic>', methods=['POST'])
def run_assessment(topic):
    try:
        questions = engine.generate_assessment_questions(topic)
        if not questions:
            return jsonify({"error": "Failed to generate questions"}), 500
        
        return jsonify({
            "questions": questions,
            "topic": topic
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/assessment/submit', methods=['POST'])
def submit_assessment():
    data = request.get_json()
    answers = data.get('answers', [])
    questions = data.get('questions', [])
    user_id = data.get('user_id')
    topic = data.get('topic')
    
    correct = 0
    for i, answer in enumerate(answers):
        if i < len(questions) and answer == questions[i]['correct']:
            correct += 1
    
    score = (correct / len(questions)) * 10 if questions else 0
    
    if user_id and topic:
        engine.update_user_competency(user_id, topic, score)
    
    return jsonify({
        "score": score,
        "correct": correct,
        "total": len(questions)
    })

@app.route('/api/lesson/<topic>/<user_id>', methods=['POST'])
def generate_lesson(topic, user_id):
    try:
        user = engine.get_user(user_id)
        lesson = engine.generate_lesson_content(topic, user)
        
        if not lesson:
            return jsonify({"error": "Failed to generate lesson"}), 500
        
        return jsonify(lesson)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    response_text = data.get('response')
    
    if not response_text:
        return jsonify({"error": "Response text is required"}), 400
    
    try:
        sentiment = engine.analyze_sentiment(response_text)
        return jsonify(sentiment)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/save', methods=['POST'])
def save_session():
    data = request.get_json()
    user_id = data.get('user_id')
    session_data = data.get('session_data')
    
    if not user_id or not session_data:
        return jsonify({"error": "user_id and session_data are required"}), 400
    
    try:
        engine.save_session(user_id, session_data)
        return jsonify({"message": "Session saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
