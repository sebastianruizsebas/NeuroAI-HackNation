import React, { useState } from 'react';
import { apiService, User } from './services/api';
import { UserSetup } from './components/UserSetup';
import { Dashboard } from './components/Dashboard';
import { TopicSelection, CustomTopic } from './components/TopicSelection';
import { LearningTracker } from './components/LearningTracker';
import { Assessment } from './components/Assessment';
import { LessonView } from './components/LessonView';
import QualityReport from './components/QualityReport';
import LessonOutline from './components/LessonOutline';
import { TopicsLibrary } from './components/TopicsLibrary';

type AppState = 'setup' | 'dashboard' | 'library' | 'topic-selection' | 'assessment' | 'lesson-outline' | 'lesson' | 'complete' | 'quality-test';

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
  const [currentTopic, setCurrentTopic] = useState<string>("Types of AI Models"); // Dynamic topic
  const [selectedCustomTopic, setSelectedCustomTopic] = useState<CustomTopic | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [showBreakReminder, setShowBreakReminder] = useState(false);

  const handleUserCreated = (newUser: User) => {
    setUser(newUser);
    loadUserProgress(newUser.user_id);
    setCurrentState('dashboard'); // Go to dashboard instead of assessment
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
    setCurrentState('lesson-outline');
  };

  const [sessionSentiments, setSessionSentiments] = useState<any[] | null>(null);

  const handleLessonComplete = async (sentiments: any[]) => {
    if (!user) return;

    // Move UI forward immediately
    setSessionSentiments(sentiments);
    setCurrentState('complete');

    const sessionData = {
      topic: currentTopic,
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

  // Dashboard handlers
  const handleStartLesson = (topic: string) => {
    setCurrentTopic(topic);
    setCurrentState('lesson');
  };

  const handleStartAssessment = (topic: string) => {
    setCurrentTopic(topic);
    setCurrentState('assessment');
  };

  const handleCreateNewTopic = () => {
    setCurrentState('topic-selection');
  };

  const handleTopicSelected = (customTopic: CustomTopic) => {
    setSelectedCustomTopic(customTopic);
    setCurrentTopic(customTopic.title);
    setCurrentState('assessment'); // Start with assessment for custom topics
  };

  const handleBreakRecommended = () => {
    setShowBreakReminder(true);
  };

  const handleSessionEnd = (duration: number) => {
    setCurrentSessionId(null);
    // Update topic progress with time spent
    if (selectedCustomTopic && user) {
      apiService.updateTopicProgress(user.user_id, selectedCustomTopic.id, 0, duration);
    }
    // Navigate back to dashboard after ending session
    setCurrentState('dashboard');
    setSelectedCustomTopic(null);
    setCurrentTopic('');
  };

  const handleBackToDashboard = () => {
    setCurrentState('dashboard');
    setEnhancedAssessmentResult(null);
    setSelectedCustomTopic(null);
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
          <div>
            <UserSetup onUserCreated={handleUserCreated} />
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <button 
                onClick={() => setCurrentState('quality-test')}
                style={{ 
                  backgroundColor: '#6b7280', 
                  color: 'white', 
                  padding: '8px 16px', 
                  border: 'none', 
                  borderRadius: '4px', 
                  fontSize: '14px' 
                }}
              >
                Test Quality Vetting System
              </button>
            </div>
          </div>
        )}
        
        {currentState === 'quality-test' && (
          <div>
            <QualityReport />
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button 
                onClick={() => setCurrentState('setup')}
                style={{ 
                  backgroundColor: '#3b82f6', 
                  color: 'white', 
                  padding: '8px 16px', 
                  border: 'none', 
                  borderRadius: '4px' 
                }}
              >
                Back to Setup
              </button>
            </div>
          </div>
        )}
        
        {currentState === 'dashboard' && user && (
          <Dashboard 
            user={user}
            onStartLesson={handleStartLesson}
            onStartAssessment={handleStartAssessment}
            onCreateNewTopic={handleCreateNewTopic}
          />
        )}
        
        {currentState === 'topic-selection' && user && (
          <TopicSelection
            userId={user.user_id}
            userName={user.name}
            onTopicSelected={handleTopicSelected}
          />
        )}
        
        {currentState === 'assessment' && user && (
          <div>
            {selectedCustomTopic && (
              <LearningTracker
                userId={user.user_id}
                topicId={selectedCustomTopic.id}
                topicTitle={selectedCustomTopic.title}
                onBreakRecommended={handleBreakRecommended}
                onSessionEnd={handleSessionEnd}
              />
            )}
            <Assessment 
              topic={currentTopic}
              userId={user.user_id}
              onComplete={handleAssessmentComplete}
            />
          </div>
        )}
        
        {currentState === 'lesson-outline' && user && currentTopic && (
          <LessonOutline
            topic={currentTopic}
            difficulty={selectedCustomTopic?.difficulty || 'beginner'}
            assessmentResults={enhancedAssessmentResult}
            onStartLesson={() => setCurrentState('lesson')}
            onBackToAssessment={() => setCurrentState('assessment')}
          />
        )}
        
        {currentState === 'lesson' && user && (
          <div>
            {selectedCustomTopic && (
              <LearningTracker
                userId={user.user_id}
                topicId={selectedCustomTopic.id}
                topicTitle={selectedCustomTopic.title}
                onBreakRecommended={handleBreakRecommended}
                onSessionEnd={handleSessionEnd}
              />
            )}
            <LessonView
              topic={currentTopic}
              userId={user.user_id}
              onComplete={handleLessonComplete}
            />
          </div>
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

            {/* Navigation buttons */}
            <div style={{display:'flex', gap:8, marginTop:'12px', flexWrap:'wrap', justifyContent:'center'}}>
              <div style={{display:'flex', gap:8, marginBottom:'8px', width:'100%'}}>
                <button className="btn btn-primary" style={{flex:1}} onClick={() => setCurrentState('lesson')}>
                  Next Lesson
                </button>
              </div>
              <div style={{display:'flex', gap:8, width:'100%'}}>
                <button className="btn btn-secondary" style={{flex:1}} onClick={handleBackToDashboard}>
                  Back to Topic Dashboard
                </button>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
