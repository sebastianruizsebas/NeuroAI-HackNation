import React, { useState } from 'react';
import { apiService, User } from './services/api';
import { UserSetup } from './components/UserSetup';
import { Assessment } from './components/Assessment';
import { LessonView } from './components/LessonView';

type AppState = 'setup' | 'assessment' | 'lesson' | 'complete';

const uniq = (arr: string[] = []) => Array.from(new Set(arr));

function pickConcepts(enhanced: any) {
  const perf = enhanced?.concept_performance || {};
  const rows = Object.keys(perf).map(k => {
    const a = perf[k]?.attempted || 0;
    const c = perf[k]?.correct || 0;
    return { concept: k, attempted: a, correct: c, acc: a ? c / a : 0 };
  });

  // sort for strengths (high acc) and gaps (low acc, attempted >=1)
  const strengths = rows
    .filter(r => r.attempted >= 1)
    .sort((a,b) => b.acc - a.acc)
    .slice(0, 5)
    .map(r => r.concept);

  const gaps = rows
    .filter(r => r.attempted >= 1)
    .sort((a,b) => a.acc - b.acc)
    .slice(0, 5)
    .map(r => r.concept);

  return {
    strengths: uniq(strengths),
    gaps: uniq(gaps),
    learningPath: uniq(enhanced?.learning_path || gaps),
  };
}

function summarizeSentiment(arr: any[] | null) {
  if (!arr || !arr.length) return null;
  const n = arr.length;
  const avg = (k: string) =>
    (arr.reduce((s, x) => s + (Number(x?.[k]) || 0), 0) / n).toFixed(2);
  return {
    confusion: avg('confusion_level'),
    confidence: avg('confidence_level'),
    engagement: avg('engagement_level'),
    // quick “coach” line
    note:
      parseFloat(avg('confusion_level')) > 0.6
        ? 'You showed notable confusion—worth a short review before moving on.'
        : parseFloat(avg('confidence_level')) >= 0.7
        ? 'Confidence looked good—nice! Consider tackling a slightly tougher exercise.'
        : 'Solid effort—keep a steady pace and review tricky bits briefly.',
  };
}


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

  const [sessionSentiments, setSessionSentiments] = useState<any[] | null>(null);

  const handleLessonComplete = async (sentiments: any[]) => {
    if (!user) return;

    // Move UI forward immediately
    setSessionSentiments(sentiments);
    setCurrentState('complete');

    const sessionData = {
      topic,
      pre_assessment_score: assessmentScore,
      sentiment_analysis: sentiments,
      completed: true,
    };

    try {
      await apiService.saveSession(user.user_id, sessionData);
    } catch (e) {
      console.error('Failed to save session:', e);
    } finally {
      // refresh progress so counts & averages update
      try {
        const progress = await apiService.getUserProgress(user.user_id);
        setUserProgress(progress);
      } catch {}
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

            {/* Sentiment snapshot */}
            {sessionSentiments && (() => {
              const s = summarizeSentiment(sessionSentiments)!;
              return (
                <div className="card" style={{marginTop: '1rem'}}>
                  <h3>🧠 Session Insights</h3>
                  <p>Confidence: {s.confidence} • Engagement: {s.engagement} • Confusion: {s.confusion}</p>
                  <em>{s.note}</em>
                  {parseFloat(s.engagement) < 0.6 && (
                    <p>Tip: Engagement dipped—try breaking sessions into smaller chunks or using more interactive materials.</p>
                  )}
                  {parseFloat(s.confusion) > 0.6 && (
                    <p>Tip: Confusion was high—spend 10–15 min revisiting the key takeaways above.</p>
                  )}
                </div>
              );
            })()}


            {/* Concept analysis */}
            {enhancedAssessmentResult && (() => {
              const picks = pickConcepts(enhancedAssessmentResult);
              return (
                <div className="card" style={{marginTop: '1rem'}}>
                  <h3>📊 Detailed Analysis</h3>

                  {picks.strengths.length > 0 && (
                    <div className="strong-areas">
                      <h4>💪 Strong Areas:</h4>
                      <ul>{picks.strengths.map((c, i) => <li key={i}>{c}</li>)}</ul>
                    </div>
                  )}

                  {picks.gaps.length > 0 && (
                    <div className="gaps">
                      <h4>🎯 Focus Next:</h4>
                      <ul>{picks.gaps.map((c, i) => <li key={i}>{c}</li>)}</ul>
                    </div>
                  )}

                  {picks.learningPath.length > 0 && (
                    <div className="learning-path">
                      <h4>🗺️ Recommended Learning Path:</h4>
                      <ol>{picks.learningPath.map((c, i) => <li key={i}>{c}</li>)}</ol>
                    </div>
                  )}
                </div>
              );
            })()}

            {/* Your Progress (fresh) */}
            {userProgress && (
              <div className="card" style={{marginTop: '1rem'}}>
                <h3>📈 Your Progress</h3>
                <p>Lessons completed: {userProgress?.overall_progress?.lessons_completed ?? 0}</p>
                <p>Average quiz score: {(userProgress?.overall_progress?.average_quiz_score ?? 0).toFixed(1)}</p>
                {Array.isArray(userProgress?.recommendations) && userProgress.recommendations.length > 0 && (
                  <div className="recommendations">
                    <h4>💡 Recommendations:</h4>
                    <ul>{userProgress.recommendations.map((r: string, i: number) => <li key={i}>{r}</li>)}</ul>
                  </div>
                )}
              </div>
            )}

            {/* Clear next-step CTA */}
            <div style={{display:'flex', gap:8, marginTop:'12px', flexWrap:'wrap'}}>
              <button className="btn btn-primary" onClick={() => setCurrentState('lesson')}>
                Review Weakest Concept
              </button>
              <button className="btn" onClick={() => setCurrentState('assessment')}>
                Retake Adaptive Quiz
              </button>
              <button className="btn btn-primary" onClick={() => {
                setCurrentState('setup');
                setEnhancedAssessmentResult(null);
                setUserProgress(null);
              }}>
                Start New Session
              </button>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
