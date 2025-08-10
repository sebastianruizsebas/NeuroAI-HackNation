from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from profai_engine import ProfAIEngine

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize ProfAI engine
engine = ProfAIEngine()

@app.route('/')
def index():
    """Main dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('setup'))
    
    user_data = engine.get_user(session['user_id'])
    return render_template('dashboard.html', user=user_data, user_id=session['user_id'])

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """User setup page"""
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            user_id = engine.create_user(name)
            session['user_id'] = user_id
            return redirect(url_for('index'))
    
    return render_template('setup.html')

@app.route('/assessment/<topic>')
def assessment(topic):
    """Assessment page for a specific topic"""
    if 'user_id' not in session:
        return redirect(url_for('setup'))
    
    questions = engine.generate_assessment_questions(topic)
    return render_template('assessment.html', topic=topic, questions=questions)

@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    """Submit assessment answers"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    topic = data.get('topic')
    answers = data.get('answers')
    
    # Calculate score (simplified)
    score = sum(1 for answer in answers if answer.get('correct', False))
    total = len(answers)
    competency_score = (score / total) * 10 if total > 0 else 0
    
    # Update user competency
    engine.update_user_competency(session['user_id'], topic, competency_score)
    
    return jsonify({
        'score': score,
        'total': total,
        'competency': competency_score,
        'redirect': url_for('lesson', topic=topic)
    })

@app.route('/lesson/<topic>')
def lesson(topic):
    """Lesson page for a specific topic"""
    if 'user_id' not in session:
        return redirect(url_for('setup'))
    
    user_data = engine.get_user(session['user_id'])
    lesson_content = engine.generate_lesson_content(topic, user_data)
    
    return render_template('lesson.html', topic=topic, lesson=lesson_content)

@app.route('/analyze_response', methods=['POST'])
def analyze_response():
    """Analyze user response during lesson"""
    data = request.get_json()
    response_text = data.get('response', '')
    
    sentiment = engine.analyze_sentiment(response_text)
    return jsonify(sentiment)

@app.route('/complete_lesson', methods=['POST'])
def complete_lesson():
    """Complete a lesson and save session data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    session_data = {
        'topic': data.get('topic'),
        'completed': True,
        'responses': data.get('responses', []),
        'time_spent': data.get('time_spent', 0)
    }
    
    engine.save_session(session['user_id'], session_data)
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return redirect(url_for('setup'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
