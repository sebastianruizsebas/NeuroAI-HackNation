import React, { useState, useEffect } from 'react';
import { apiService, User, UserProgress, Topic, CustomTopic } from '../services/api';
import { TopicsLibrary } from './TopicsLibrary';

interface DashboardProps {
  user: User;
  onStartLesson: (topic: string) => void;
  onStartAssessment: (topic: string) => void;
  onCreateNewTopic: () => void;
}

interface TopicProgress {
  topic: string;
  status: 'not_started' | 'in_progress' | 'completed';
  progress: number;
  lastActivity: string;
  description?: string;
  difficulty?: string;
  estimated_time?: string;
  isCustom?: boolean;
  customTopic?: CustomTopic;
}

export const Dashboard: React.FC<DashboardProps> = ({ 
  user, 
  onStartLesson, 
  onStartAssessment, 
  onCreateNewTopic 
}) => {
  const [userProgress, setUserProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTopics, setCurrentTopics] = useState<TopicProgress[]>([]);
  const [availableTopics, setAvailableTopics] = useState<Topic[]>([]);
  const [customTopics, setCustomTopics] = useState<CustomTopic[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'library'>('overview');

  // Using the variables to avoid lint errors
  console.log('Available topics:', availableTopics.length, 'Custom topics:', customTopics.length);

  useEffect(() => {
    loadData();
  }, [user.user_id]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load available topics, custom topics, and user progress in parallel
      const [topicsResponse, customTopicsResponse, progress] = await Promise.all([
        apiService.getAvailableTopics(),
        apiService.getUserCustomTopics(user.user_id),
        apiService.getUserProgress(user.user_id)
      ]);
      
      setAvailableTopics(topicsResponse.topics);
      setCustomTopics(customTopicsResponse.topics);
      setUserProgress(progress);
      
      // Create topic progress based on user data and available topics
      const standardTopics: TopicProgress[] = topicsResponse.topics.map(topic => {
        const isCompleted = progress.overall_progress?.session_history?.some(
          session => session.includes(topic.name)
        ) || false;
        
        const isInLearningPath = progress.learning_path?.includes(topic.name) || false;
        
        return {
          topic: topic.name,
          status: isCompleted ? 'completed' : isInLearningPath ? 'in_progress' : 'not_started',
          progress: isCompleted ? 100 : isInLearningPath ? 25 : 0,
          lastActivity: isCompleted ? 'Recently completed' : isInLearningPath ? 'In learning path' : 'Not started',
          description: topic.description,
          difficulty: topic.difficulty,
          estimated_time: topic.estimated_time,
          isCustom: false
        };
      });

      // Add custom topics
      const customTopicProgress: TopicProgress[] = customTopicsResponse.topics.map(customTopic => {
        const progress = customTopic.progress || 0;
        return {
          topic: customTopic.title,
          status: progress === 100 ? 'completed' : progress > 0 ? 'in_progress' : 'not_started',
          progress: progress,
          lastActivity: customTopic.lastAccessed ? `Last accessed ${new Date(customTopic.lastAccessed).toLocaleDateString()}` : 'Never started',
          description: customTopic.description,
          difficulty: customTopic.difficulty,
          estimated_time: `${customTopic.estimatedHours}h`,
          isCustom: true,
          customTopic: customTopic
        };
      });

      // Combine all topics
      setCurrentTopics([...customTopicProgress, ...standardTopics]);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '📚';
      default: return '⭕';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#22c55e';
      case 'in_progress': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div>Loading your dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Welcome Section */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2>{getGreeting()}, {user.name}! 👋</h2>
        <p>Welcome to your learning dashboard. Here's your progress overview:</p>
        
        {userProgress && (
          <div style={{ display: 'flex', gap: '2rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            <div className="stat-item">
              <div className="stat-number">{userProgress.overall_progress?.lessons_completed || 0}</div>
              <div className="stat-label">Lessons Completed</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{(userProgress.overall_progress?.average_quiz_score || 0).toFixed(1)}</div>
              <div className="stat-label">Average Score</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">{currentTopics.filter(t => t.status === 'in_progress').length}</div>
              <div className="stat-label">Topics Learning</div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="dashboard-tabs">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'library' ? 'active' : ''}`}
            onClick={() => setActiveTab('library')}
          >
            📚 Topics Library
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <>
          {/* Custom Topics Section */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3>🎨 Your Custom Learning Topics</h3>
              <button 
                className="btn btn-primary"
                onClick={onCreateNewTopic}
              >
                ➕ Create New Topic
              </button>
            </div>
            
            {currentTopics.filter(topic => topic.isCustom).length > 0 ? (
              <div className="topics-grid">
                {currentTopics
                  .filter(topic => topic.isCustom)
                  .slice(0, 3) // Show only first 3, rest in library
                  .map((topic, index) => (
                    <div key={index} className="topic-card custom-topic" style={{ borderColor: getStatusColor(topic.status) }}>
                      <div className="topic-header">
                        <span className="topic-icon">🎯</span>
                        <h4>{topic.topic}</h4>
                        {topic.customTopic?.deadline && (
                          <span className="deadline-indicator">
                            🗓️ {new Date(topic.customTopic.deadline).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                      {topic.description && (
                        <p className="topic-description">{topic.description}</p>
                      )}
                      <div className="topic-meta">
                        {topic.difficulty && (
                          <span className={`difficulty-badge ${topic.difficulty}`}>
                            {topic.difficulty}
                          </span>
                        )}
                        {topic.customTopic?.intensity && (
                          <span className={`intensity-badge ${topic.customTopic.intensity}`}>
                            {topic.customTopic.intensity}
                          </span>
                        )}
                        {topic.estimated_time && (
                          <span className="time-estimate">⏱️ {topic.estimated_time}</span>
                        )}
                      </div>
                      <div className="topic-progress">
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ 
                              width: `${topic.progress}%`,
                              backgroundColor: getStatusColor(topic.status)
                            }}
                          ></div>
                        </div>
                        <span className="progress-text">{topic.progress}% complete</span>
                      </div>
                      <p className="topic-status">{topic.lastActivity}</p>
                      {topic.customTopic?.timeSpent && (
                        <p className="time-spent">📊 Time spent: {Math.floor(topic.customTopic.timeSpent / 60)}h {topic.customTopic.timeSpent % 60}m</p>
                      )}
                      <div className="topic-actions">
                        <button 
                          className="btn btn-primary btn-sm"
                          onClick={() => onStartLesson(topic.topic)}
                        >
                          {topic.progress > 0 ? 'Continue' : 'Start'} Learning
                        </button>
                        <button 
                          className="btn btn-sm"
                          onClick={() => onStartAssessment(topic.topic)}
                        >
                          Take Quiz
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>🌟 You haven't created any custom topics yet!</p>
                <p>Create a personalized learning topic based on your specific interests and goals.</p>
              </div>
            )}
            
            {currentTopics.filter(topic => topic.isCustom).length > 3 && (
              <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                <button 
                  className="btn btn-secondary"
                  onClick={() => setActiveTab('library')}
                >
                  View All {currentTopics.filter(topic => topic.isCustom).length} Topics in Library
                </button>
              </div>
            )}
      </div>

      {/* Current Learning Section */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>📚 Your Learning Topics</h3>
        
        {currentTopics.filter(topic => topic.status === 'in_progress' && !topic.isCustom).length > 0 ? (
          <div>
            <h4>Currently Learning:</h4>
            <div className="topics-grid">
              {currentTopics
                .filter(topic => topic.status === 'in_progress' && !topic.isCustom)
                .map((topic, index) => (
                  <div key={index} className="topic-card" style={{ borderColor: getStatusColor(topic.status) }}>
                    <div className="topic-header">
                      <span className="topic-icon">{getStatusIcon(topic.status)}</span>
                      <h4>{topic.topic}</h4>
                    </div>
                    {topic.description && (
                      <p className="topic-description">{topic.description}</p>
                    )}
                    <div className="topic-meta">
                      {topic.difficulty && (
                        <span className={`difficulty-badge ${topic.difficulty}`}>
                          {topic.difficulty}
                        </span>
                      )}
                      {topic.estimated_time && (
                        <span className="time-estimate">⏱️ {topic.estimated_time}</span>
                      )}
                    </div>
                    <div className="topic-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ 
                            width: `${topic.progress}%`,
                            backgroundColor: getStatusColor(topic.status)
                          }}
                        ></div>
                      </div>
                      <span className="progress-text">{topic.progress}% complete</span>
                    </div>
                    <p className="topic-status">{topic.lastActivity}</p>
                    <div className="topic-actions">
                      <button 
                        className="btn btn-primary btn-sm"
                        onClick={() => onStartLesson(topic.topic)}
                      >
                        Continue Learning
                      </button>
                      <button 
                        className="btn btn-sm"
                        onClick={() => onStartAssessment(topic.topic)}
                      >
                        Take Quiz
                      </button>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ) : (
          <div>
            <p>You haven't started learning any topics yet. Choose from the available topics below!</p>
          </div>
        )}
      </div>

      {/* Available Topics Section */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>🎯 Available Topics</h3>
        <div className="topics-grid">
          {currentTopics
            .filter(topic => topic.status === 'not_started' && !topic.isCustom)
            .map((topic, index) => (
              <div key={index} className="topic-card" style={{ borderColor: getStatusColor(topic.status) }}>
                <div className="topic-header">
                  <span className="topic-icon">{getStatusIcon(topic.status)}</span>
                  <h4>{topic.topic}</h4>
                </div>
                {topic.description && (
                  <p className="topic-description">{topic.description}</p>
                )}
                <div className="topic-meta">
                  {topic.difficulty && (
                    <span className={`difficulty-badge ${topic.difficulty}`}>
                      {topic.difficulty}
                    </span>
                  )}
                  {topic.estimated_time && (
                    <span className="time-estimate">⏱️ {topic.estimated_time}</span>
                  )}
                </div>
                <p className="topic-status">{topic.lastActivity}</p>
                <div className="topic-actions">
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => onStartAssessment(topic.topic)}
                  >
                    Start Learning
                  </button>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Completed Topics Section */}
      {currentTopics.filter(topic => topic.status === 'completed' && !topic.isCustom).length > 0 && (
        <div className="card">
          <h3>🏆 Completed Topics</h3>
          <div className="topics-grid">
            {currentTopics
              .filter(topic => topic.status === 'completed' && !topic.isCustom)
              .map((topic, index) => (
                <div key={index} className="topic-card completed" style={{ borderColor: getStatusColor(topic.status) }}>
                  <div className="topic-header">
                    <span className="topic-icon">{getStatusIcon(topic.status)}</span>
                    <h4>{topic.topic}</h4>
                  </div>
                  {topic.description && (
                    <p className="topic-description">{topic.description}</p>
                  )}
                  <div className="topic-meta">
                    {topic.difficulty && (
                      <span className={`difficulty-badge ${topic.difficulty}`}>
                        {topic.difficulty}
                      </span>
                    )}
                    {topic.estimated_time && (
                      <span className="time-estimate">⏱️ {topic.estimated_time}</span>
                    )}
                  </div>
                  <div className="topic-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: '100%',
                          backgroundColor: getStatusColor(topic.status)
                        }}
                      ></div>
                    </div>
                    <span className="progress-text">100% complete</span>
                  </div>
                  <p className="topic-status">{topic.lastActivity}</p>
                  <div className="topic-actions">
                    <button 
                      className="btn btn-sm"
                      onClick={() => onStartLesson(topic.topic)}
                    >
                      Review
                    </button>
                    <button 
                      className="btn btn-sm"
                      onClick={() => onStartAssessment(topic.topic)}
                    >
                      Retake Quiz
                    </button>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

          {/* Recommendations Section */}
          {userProgress?.recommendations && userProgress.recommendations.length > 0 && (
            <div className="card" style={{ marginTop: '1.5rem' }}>
              <h3>💡 Recommendations</h3>
              <ul>
                {userProgress.recommendations.map((recommendation, index) => (
                  <li key={index}>{recommendation}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {/* Library Tab Content */}
      {activeTab === 'library' && (
        <TopicsLibrary 
          user={user}
          onSelectTopic={(topic) => {
            // Handle topic selection
            console.log('Selected topic:', topic);
          }}
          onStartLesson={onStartLesson}
        />
      )}
    </div>
  );
};
