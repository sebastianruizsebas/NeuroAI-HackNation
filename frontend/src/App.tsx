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
  const [enhancedAssessmentResult, setEnhancedAssessmentResult] = useState<any>(null);
  const [userProgress, setUserProgress] = useState<any>(null);
  const topic = "Types of AI Models"; // Fixed topic for MVP

  const handleUserCreated = (newUser: User) => {
    setUser(newUser);
    loadUserProgress(newUser.user_id);
    setCurrentState('assessment');
  };

  const loadUserProgress = async (userId: string) => {
    try {
      const progress = await apiService.getUserProgress(userId);
      setUserProgress(progress);
    } catch (error) {
      console.error('Failed to load user progress:', error);
    }
  };

  const handleAssessmentComplete = (score: number, enhancedResult?: any) => {
    setAssessmentScore(score);
    if (enhancedResult) {
      setEnhancedAssessmentResult(enhancedResult);
    }
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
            
            {/* V2 Enhanced: Show detailed assessment results */}
            {enhancedAssessmentResult && (
              <div className="enhanced-results">
                <h3>📊 Detailed Analysis</h3>
                <div className="knowledge-analysis">
                  <div className="strong-areas">
                    <h4>💪 Strong Areas:</h4>
                    <ul>
                      {enhancedAssessmentResult.strong_areas?.map((area: string, index: number) => (
                        <li key={index}>{area}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {enhancedAssessmentResult.knowledge_gaps?.length > 0 && (
                    <div className="knowledge-gaps">
                      <h4>🎯 Areas for Improvement:</h4>
                      <ul>
                        {enhancedAssessmentResult.knowledge_gaps.map((gap: string, index: number) => (
                          <li key={index}>{gap}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {enhancedAssessmentResult.learning_path?.length > 0 && (
                    <div className="learning-path">
                      <h4>🗺️ Recommended Learning Path:</h4>
                      <ol>
                        {enhancedAssessmentResult.learning_path.map((step: string, index: number) => (
                          <li key={index}>{step}</li>
                        ))}
                      </ol>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* V2 Enhanced: Show user progress if available */}
            {userProgress && (
              <div className="progress-summary">
                <h3>📈 Your Progress</h3>
                <p>Lessons completed: {userProgress.overall_progress?.lessons_completed || 0}</p>
                <p>Average quiz score: {userProgress.overall_progress?.average_quiz_score?.toFixed(1) || 'N/A'}</p>
                {userProgress.recommendations?.length > 0 && (
                  <div className="recommendations">
                    <h4>💡 Recommendations:</h4>
                    <ul>
                      {userProgress.recommendations.map((rec: string, index: number) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            <button 
              className="btn btn-primary"
              onClick={() => {
                setCurrentState('setup');
                setEnhancedAssessmentResult(null);
                setUserProgress(null);
              }}
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
