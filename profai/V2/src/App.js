import React, { useState, useEffect } from 'react';
import { BookOpen, Brain, CheckCircle, Clock, User, BarChart3, ArrowRight, Play, RefreshCw, Loader, ChevronLeft, ChevronRight, MessageCircle } from 'lucide-react';
import './App.css';

// API Service
const API_BASE_URL = 'http://localhost:5000/api';

const apiService = {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      console.log(`Making request to: ${url}`, config);
      const response = await fetch(url, config);
      const data = await response.json();
      
      console.log(`Response from ${url}:`, data);
      
      if (!response.ok) {
        throw new Error(data.error || 'API request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  async createUser(name) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  },

  async generateAssessmentQuestions(topic) {
    return this.request('/assessment/questions', {
      method: 'POST',
      body: JSON.stringify({ topic }),
    });
  },

  async submitAssessment(userId, topic, answers, questions) {
    return this.request('/assessment/submit', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        topic,
        answers,
        questions,
      }),
    });
  },

  async generateLesson(topic, userId) {
    return this.request('/lesson/generate', {
      method: 'POST',
      body: JSON.stringify({
        topic,
        user_id: userId,
      }),
    });
  },

  async analyzeSentiment(response) {
    return this.request('/sentiment/analyze', {
      method: 'POST',
      body: JSON.stringify({ response }),
    });
  },

  async saveSession(userId, sessionData) {
    return this.request('/session/save', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        session_data: sessionData,
      }),
    });
  }
};

function App() {
  const [currentView, setCurrentView] = useState('welcome');
  const [userName, setUserName] = useState('');
  const [userId, setUserId] = useState('');
  const [currentTopic, setCurrentTopic] = useState('Types of AI Models');
  const [assessmentScore, setAssessmentScore] = useState(null);
  const [lessonProgress, setLessonProgress] = useState(0);
  const [currentChunk, setCurrentChunk] = useState(0);
  const [userResponse, setUserResponse] = useState('');
  const [sentimentFeedback, setSentimentFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [assessmentQuestions, setAssessmentQuestions] = useState([]);
  const [lessonContent, setLessonContent] = useState(null);
  const [error, setError] = useState('');
  const [userResponses, setUserResponses] = useState([]);

  const WelcomeScreen = () => {
    const handleStartJourney = async () => {
      if (!userName.trim()) return;

      setIsLoading(true);
      setError('');

      try {
        console.log('Creating user:', userName.trim());
        const response = await apiService.createUser(userName.trim());
        console.log('User created:', response);
        setUserId(response.user_id);
        setCurrentView('dashboard');
      } catch (err) {
        setError('Failed to create user. Make sure your Flask API is running on http://localhost:5000');
        console.error('Error creating user:', err);
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="welcome-screen">
        <div className="welcome-card">
          <div className="logo">
            <Brain size={32} color="white" />
          </div>
          <h1>Welcome to ProfAI</h1>
          <p>Your AI-powered learning companion with emotional intelligence. Let's personalize your learning experience.</p>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <div className="input-section">
            <input
              type="text"
              placeholder="What's your name?"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleStartJourney()}
              disabled={isLoading}
            />
            <button
              onClick={handleStartJourney}
              disabled={!userName.trim() || isLoading}
              className="primary-button"
            >
              {isLoading ? (
                <>
                  <Loader size={16} className="spinner" />
                  <span>Creating Profile...</span>
                </>
              ) : (
                <span>Start Learning Journey</span>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const Dashboard = () => {
    const handleStartAssessment = async () => {
      setIsLoading(true);
      setError('');

      try {
        console.log('Generating assessment for topic:', currentTopic);
        const response = await apiService.generateAssessmentQuestions(currentTopic);
        console.log('Assessment response:', response);
        
        if (response && response.questions && response.questions.length > 0) {
          setAssessmentQuestions(response.questions);
          console.log('Setting view to assessment with questions:', response.questions);
          setCurrentView('assessment');
        } else {
          throw new Error('No questions received from API');
        }
      } catch (err) {
        setError(`Failed to generate assessment questions: ${err.message}`);
        console.error('Error generating assessment:', err);
      } finally {
        setIsLoading(false);
      }
    };

    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-content">
            <div className="logo-section">
              <div className="logo small">
                <Brain size={20} color="white" />
              </div>
              <h1>ProfAI</h1>
            </div>
            <div className="user-info">
              <User size={16} />
              <span>{userName}</span>
            </div>
          </div>
        </header>

        <main className="dashboard-main">
          <div className="dashboard-title">
            <h2>Learning Dashboard</h2>
            <p>Continue your AI learning journey with personalized lessons</p>
          </div>

          {error && (
            <div className="error-banner">
              {error}
              <button onClick={() => setError('')}>Dismiss</button>
            </div>
          )}

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-header">
                <div className="stat-icon blue">
                  <BookOpen size={20} />
                </div>
                <span className="stat-number">1</span>
              </div>
              <h3>Active Lessons</h3>
              <p>Currently learning</p>
            </div>

            <div className="stat-card">
              <div className="stat-header">
                <div className="stat-icon green">
                  <CheckCircle size={20} />
                </div>
                <span className="stat-number">{lessonContent ? 1 : 0}</span>
              </div>
              <h3>Completed</h3>
              <p>Lessons finished</p>
            </div>

            <div className="stat-card">
              <div className="stat-header">
                <div className="stat-icon purple">
                  <BarChart3 size={20} />
                </div>
                <span className="stat-number">
                  {assessmentScore ? assessmentScore.toFixed(1) : '--'}
                </span>
              </div>
              <h3>Latest Score</h3>
              <p>Assessment result</p>
            </div>
          </div>

          <div className="lesson-card">
            <div className="lesson-header">
              <div>
                <h3>Current Topic</h3>
                <p>{currentTopic}</p>
              </div>
              <div className="lesson-time">
                <Clock size={16} />
                <span>~15 min</span>
              </div>
            </div>

            <div className="progress-section">
              <div className="progress-header">
                <span>Progress</span>
                <span>{lessonProgress}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${lessonProgress}%` }}
                ></div>
              </div>
            </div>

            <div className="lesson-actions">
              {lessonContent ? (
                <button
                  onClick={() => setCurrentView('lesson')}
                  className="primary-button flex-1"
                >
                  <Play size={16} />
                  <span>Continue Lesson</span>
                </button>
              ) : (
                <button
                  onClick={handleStartAssessment}
                  disabled={isLoading}
                  className="primary-button flex-1"
                >
                  {isLoading ? (
                    <>
                      <Loader size={16} className="spinner" />
                      <span>Loading...</span>
                    </>
                  ) : (
                    <>
                      <Play size={16} />
                      <span>Start Assessment</span>
                    </>
                  )}
                </button>
              )}
              <button className="secondary-button">
                <RefreshCw size={16} />
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  };

  const Assessment = () => {
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState({});
    const [showResults, setShowResults] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    console.log('Assessment component rendered with questions:', assessmentQuestions);

    const handleAnswer = (answer) => {
      setAnswers({...answers, [currentQ]: answer});
    };

    const nextQuestion = async () => {
      if (currentQ < assessmentQuestions.length - 1) {
        setCurrentQ(currentQ + 1);
      } else {
        setSubmitting(true);
        try {
          const response = await apiService.submitAssessment(
            userId, 
            currentTopic, 
            answers, 
            assessmentQuestions
          );
          setAssessmentScore(response.score);
          setShowResults(true);
        } catch (err) {
          setError('Failed to submit assessment. Please try again.');
          console.error('Error submitting assessment:', err);
        } finally {
          setSubmitting(false);
        }
      }
    };

    const startLesson = async () => {
      setIsLoading(true);
      try {
        const lesson = await apiService.generateLesson(currentTopic, userId);
        setLessonContent(lesson);
        setCurrentChunk(0);
        setCurrentView('lesson');
      } catch (err) {
        setError('Failed to generate lesson. Please try again.');
        console.error('Error generating lesson:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (showResults) {
      return (
        <div className="welcome-screen">
          <div className="welcome-card">
            <div className="logo">
              <CheckCircle size={32} color="green" />
            </div>
            <h1>Assessment Complete</h1>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#2563eb', margin: '16px 0' }}>
              {assessmentScore?.toFixed(1)}/10
            </div>
            <p>Your pre-lesson assessment score</p>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
            
            <div className="input-section">
              <button
                onClick={startLesson}
                disabled={isLoading}
                className="primary-button"
              >
                {isLoading ? (
                  <>
                    <Loader size={16} className="spinner" />
                    <span>Generating Lesson...</span>
                  </>
                ) : (
                  <>
                    <span>Begin Lesson</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      );
    }

    if (!assessmentQuestions.length) {
      return (
        <div className="welcome-screen">
          <div className="welcome-card">
            <Loader size={32} className="spinner" style={{ color: '#2563eb', margin: '0 auto 16px' }} />
            <p>Loading assessment questions...</p>
          </div>
        </div>
      );
    }

    const question = assessmentQuestions[currentQ];
    
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-content">
            <h1>Pre-Assessment</h1>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              Question {currentQ + 1} of {assessmentQuestions.length}
            </div>
          </div>
        </header>

        <main className="dashboard-main">
          <div className="lesson-card">
            <div className="progress-section">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${((currentQ + 1) / assessmentQuestions.length) * 100}%` }}
                ></div>
              </div>
            </div>

            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937', marginBottom: '24px' }}>
              {question.question}
            </h2>

            <div style={{ marginBottom: '32px' }}>
              {question.options.map((option, idx) => {
                const letter = option.charAt(0);
                return (
                  <button
                    key={idx}
                    onClick={() => handleAnswer(letter)}
                    style={{
                      width: '100%',
                      padding: '16px',
                      textAlign: 'left',
                      borderRadius: '8px',
                      border: answers[currentQ] === letter ? '2px solid #3b82f6' : '1px solid #d1d5db',
                      backgroundColor: answers[currentQ] === letter ? '#eff6ff' : 'white',
                      color: answers[currentQ] === letter ? '#1d4ed8' : '#374151',
                      cursor: 'pointer',
                      marginBottom: '12px',
                      transition: 'all 0.2s'
                    }}
                  >
                    {option}
                  </button>
                );
              })}
            </div>

            <button
              onClick={nextQuestion}
              disabled={!answers[currentQ] || submitting}
              className="primary-button"
            >
              {submitting ? (
                <>
                  <Loader size={16} className="spinner" />
                  <span>Submitting...</span>
                </>
              ) : (
                <span>{currentQ < assessmentQuestions.length - 1 ? 'Next Question' : 'Complete Assessment'}</span>
              )}
            </button>
          </div>
        </main>
      </div>
    );
  };

  const LessonView = () => {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [showFeedback, setShowFeedback] = useState(false);

    const handleResponseSubmit = async () => {
      if (!userResponse.trim()) return;

      setIsAnalyzing(true);
      try {
        const sentiment = await apiService.analyzeSentiment(userResponse);
        setSentimentFeedback(sentiment);
        setShowFeedback(true);
        
        // Store user response
        const newResponses = [...userResponses];
        newResponses[currentChunk] = {
          response: userResponse,
          sentiment: sentiment,
          timestamp: new Date().toISOString()
        };
        setUserResponses(newResponses);
        
        setUserResponse('');
      } catch (err) {
        setError('Failed to analyze response. Please try again.');
        console.error('Error analyzing sentiment:', err);
      } finally {
        setIsAnalyzing(false);
      }
    };

    const nextChunk = () => {
      if (currentChunk < lessonContent.chunks.length - 1) {
        setCurrentChunk(currentChunk + 1);
        setShowFeedback(false);
        // Update progress
        const newProgress = ((currentChunk + 2) / lessonContent.chunks.length) * 100;
        setLessonProgress(newProgress);
      } else {
        // Lesson complete
        setLessonProgress(100);
        completeLesson();
      }
    };

    const prevChunk = () => {
      if (currentChunk > 0) {
        setCurrentChunk(currentChunk - 1);
        setShowFeedback(false);
        const newProgress = (currentChunk / lessonContent.chunks.length) * 100;
        setLessonProgress(newProgress);
      }
    };

    const completeLesson = async () => {
      try {
        // Save session data
        const sessionData = {
          topic: currentTopic,
          pre_assessment_score: assessmentScore,
          lesson_completed: true,
          user_responses: userResponses,
          completion_time: new Date().toISOString()
        };
        
        await apiService.saveSession(userId, sessionData);
        
        // Show completion message
        setCurrentView('completion');
      } catch (err) {
        console.error('Error saving session:', err);
        setError('Failed to save progress, but lesson is complete!');
        // Still proceed to completion view even if save fails
        setCurrentView('completion');
      }
    };

    if (!lessonContent) {
      return (
        <div className="welcome-screen">
          <div className="welcome-card">
            <Loader size={32} className="spinner" style={{ color: '#2563eb', margin: '0 auto 16px' }} />
            <p>Loading lesson content...</p>
          </div>
        </div>
      );
    }

    const chunk = lessonContent.chunks[currentChunk];
    const isLastChunk = currentChunk === lessonContent.chunks.length - 1;

    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-content">
            <button 
              onClick={() => setCurrentView('dashboard')}
              style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <ChevronLeft size={16} />
              <span>Back to Dashboard</span>
            </button>
            <h1>{currentTopic}</h1>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              Part {currentChunk + 1} of {lessonContent.chunks.length}
            </div>
          </div>
        </header>

        <main className="dashboard-main">
          {/* Lesson Overview (only show on first chunk) */}
          {currentChunk === 0 && (
            <div className="lesson-card" style={{ marginBottom: '24px' }}>
              <h3 style={{ color: '#2563eb', marginBottom: '16px' }}>📋 Lesson Overview</h3>
              <p style={{ color: '#6b7280', lineHeight: '1.6' }}>{lessonContent.overview}</p>
            </div>
          )}

          {/* Progress Bar */}
          <div className="progress-section" style={{ marginBottom: '24px' }}>
            <div className="progress-header">
              <span>Lesson Progress</span>
              <span>{Math.round(lessonProgress)}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${lessonProgress}%` }}
              ></div>
            </div>
          </div>

          {/* Main Lesson Content */}
          <div className="lesson-card">
            <h2 style={{ color: '#1f2937', marginBottom: '24px', fontSize: '24px' }}>
              📖 {chunk.title}
            </h2>
            
            <div style={{ 
              backgroundColor: '#f9fafb', 
              padding: '24px', 
              borderRadius: '12px', 
              marginBottom: '24px',
              lineHeight: '1.7',
              color: '#374151'
            }}>
              {chunk.content}
            </div>

            <div style={{
              backgroundColor: '#eff6ff',
              border: '1px solid #bfdbfe',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '32px'
            }}>
              <h4 style={{ color: '#1d4ed8', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                🎯 Key Point
              </h4>
              <p style={{ color: '#1e40af', margin: 0, fontWeight: '500' }}>{chunk.key_point}</p>
            </div>

            {/* User Reflection Section */}
            <div style={{ marginBottom: '24px' }}>
              <h4 style={{ color: '#1f2937', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MessageCircle size={18} />
                Reflection Question
              </h4>
              <p style={{ color: '#6b7280', marginBottom: '16px' }}>
                In your own words, what did you understand from this section? How might you apply this knowledge?
              </p>
              
              <textarea
                value={userResponse}
                onChange={(e) => setUserResponse(e.target.value)}
                placeholder="Share your understanding and thoughts..."
                style={{
                  width: '100%',
                  minHeight: '120px',
                  padding: '12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '16px',
                  lineHeight: '1.5',
                  resize: 'vertical'
                }}
                disabled={isAnalyzing}
              />
              
              <button
                onClick={handleResponseSubmit}
                disabled={!userResponse.trim() || isAnalyzing}
                style={{
                  marginTop: '12px',
                  padding: '8px 16px',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                {isAnalyzing ? (
                  <>
                    <Loader size={16} className="spinner" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <span>Submit Reflection</span>
                )}
              </button>
            </div>

            {/* AI Feedback */}
            {showFeedback && sentimentFeedback && (
              <div style={{
                backgroundColor: sentimentFeedback.confidence_level > 0.7 ? '#f0fdf4' : '#fef3c7',
                border: `1px solid ${sentimentFeedback.confidence_level > 0.7 ? '#bbf7d0' : '#fde68a'}`,
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '24px'
              }}>
                <h4 style={{ 
                  color: sentimentFeedback.confidence_level > 0.7 ? '#166534' : '#92400e',
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  🤖 AI Feedback
                </h4>
                <p style={{ 
                  color: sentimentFeedback.confidence_level > 0.7 ? '#15803d' : '#b45309',
                  margin: 0 
                }}>
                  {sentimentFeedback.suggestion || 'Great understanding! You can proceed to the next section.'}
                </p>
              </div>
            )}

            {/* Navigation */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                onClick={prevChunk}
                disabled={currentChunk === 0}
                style={{
                  padding: '12px 20px',
                  backgroundColor: currentChunk === 0 ? '#f3f4f6' : '#6b7280',
                  color: currentChunk === 0 ? '#9ca3af' : 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: currentChunk === 0 ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <ChevronLeft size={16} />
                <span>Previous</span>
              </button>

              <div style={{ fontSize: '14px', color: '#6b7280' }}>
                {currentChunk + 1} / {lessonContent.chunks.length}
              </div>

              <button
                onClick={nextChunk}
                disabled={!showFeedback && userResponse.trim() === '' && !userResponses[currentChunk]}
                className="primary-button"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <span>{isLastChunk ? 'Complete Lesson' : 'Next Section'}</span>
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          {/* Key Takeaways (show on last chunk) */}
          {isLastChunk && (
            <div className="lesson-card" style={{ marginTop: '24px' }}>
              <h3 style={{ color: '#059669', marginBottom: '16px' }}>🎯 Key Takeaways</h3>
              <ul style={{ color: '#374151', lineHeight: '1.6' }}>
                {lessonContent.key_takeaways?.map((takeaway, idx) => (
                  <li key={idx} style={{ marginBottom: '8px' }}>{takeaway}</li>
                ))}
              </ul>
            </div>
          )}
        </main>
      </div>
    );
  };

  const CompletionView = () => {
    return (
      <div className="welcome-screen">
        <div className="welcome-card">
          <div className="logo">
            <CheckCircle size={48} color="green" />
          </div>
          <h1>🎉 Lesson Complete!</h1>
          <p style={{ fontSize: '18px', marginBottom: '24px' }}>
            Congratulations! You've successfully completed the lesson on <strong>{currentTopic}</strong>.
          </p>
          
          <div style={{ 
            backgroundColor: '#f0fdf4', 
            border: '1px solid #bbf7d0',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '24px',
            textAlign: 'left'
          }}>
            <h3 style={{ color: '#166534', marginBottom: '12px' }}>📊 Session Summary</h3>
            <div style={{ color: '#15803d' }}>
              <p><strong>Pre-assessment Score:</strong> {assessmentScore?.toFixed(1)}/10</p>
              <p><strong>Lesson Progress:</strong> {lessonProgress}%</p>
              <p><strong>Reflections Submitted:</strong> {userResponses.length}</p>
              <p><strong>Topic Mastered:</strong> {currentTopic}</p>
            </div>
          </div>

          <div className="input-section">
            <button
              onClick={() => {
                setCurrentView('dashboard');
                setLessonContent(null);
                setCurrentChunk(0);
                setUserResponses([]);
                setSentimentFeedback(null);
              }}
              className="primary-button"
              style={{ marginRight: '12px' }}
            >
              <span>Back to Dashboard</span>
            </button>
            <button
              onClick={() => {
                // Reset for new lesson
                setCurrentView('dashboard');
                setLessonContent(null);
                setCurrentChunk(0);
                setUserResponses([]);
                setSentimentFeedback(null);
                setAssessmentScore(null);
                setLessonProgress(0);
              }}
              className="secondary-button"
            >
              <span>Start New Lesson</span>
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Render the appropriate view
  console.log('Current view:', currentView);
  console.log('Assessment questions:', assessmentQuestions);

  if (currentView === 'welcome') {
    return <WelcomeScreen />;
  } else if (currentView === 'assessment') {
    return <Assessment />;
  } else if (currentView === 'lesson') {
    return <LessonView />;
  } else if (currentView === 'completion') {
    return <CompletionView />;
  } else {
    return <Dashboard />;
  }
}

export default App;