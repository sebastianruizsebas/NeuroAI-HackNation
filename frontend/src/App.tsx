import React, { useState } from 'react';
import { apiService, User } from './services/api';
import { UserSetup } from './components/UserSetup';
import { Assessment } from './components/Assessment';
import { LessonView } from './components/LessonView';

type AppState = 'setup' | 'assessment' | 'lesson' | 'complete';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('setup');
  const [user, setUser] = useState<User | null>(null);
  const [assessmentScore, setAssessmentScore] = useState<number>(0);
  const topic = "Types of AI Models"; // Fixed topic for MVP

  const handleUserCreated = (newUser: User) => {
    setUser(newUser);
    setCurrentState('assessment');
  };

  const handleAssessmentComplete = (score: number) => {
    setAssessmentScore(score);
    setCurrentState('lesson');
  };

  const handleLessonComplete = async (sentimentData: any[]) => {
    if (user) {
      const sessionData = {
        topic,
        pre_assessment_score: assessmentScore,
        sentiment_analysis: sentimentData,
        completed: true
      };
      
      try {
        await apiService.saveSession(user.user_id, sessionData);
        setCurrentState('complete');
      } catch (error) {
        console.error('Failed to save session:', error);
      }
    }
  };

  if (!user) {
    return (
      <div className="app">
        <UserSetup onUserCreated={handleUserCreated} />
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎓 ProfAI</h1>
        {user && (
          <div className="user-info">
            <span>Welcome, {user.name}!</span>
            <div className="lesson-count">ID: {user.user_id}</div>
          </div>
        )}
      </header>
      
      <main className="app-main">
        {currentState === 'setup' && (
          <UserSetup onUserCreated={handleUserCreated} />
        )}
        
        {currentState === 'assessment' && user && (
          <Assessment 
            topic={topic}
            userId={user.user_id}
            onComplete={handleAssessmentComplete}
          />
        )}
        
        {currentState === 'lesson' && user && (
          <LessonView
            topic={topic}
            userId={user.user_id}
            onComplete={handleLessonComplete}
          />
        )}
        
        {currentState === 'complete' && (
          <div className="card">
            <h2>🎉 Lesson Complete!</h2>
            <p>Your progress has been saved.</p>
            <p>Pre-assessment score: {assessmentScore.toFixed(1)}/10</p>
            <button 
              className="btn btn-primary"
              onClick={() => setCurrentState('setup')}
            >
              Start New Session
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
