import React, { useState, useEffect } from 'react';
import { User, CustomTopic } from '../services/api';

interface TopicsLibraryProps {
  user: User;
  onSelectTopic: (topic: CustomTopic) => void;
  onStartLesson: (topic: string) => void;
}

interface LibraryStats {
  total_topics: number;
  completed_topics: number;
  in_progress: number;
  total_time_spent: number;
}

interface TopicsLibrary {
  by_category: { [key: string]: CustomTopic[] };
  by_difficulty: { [key: string]: CustomTopic[] };
  recent: CustomTopic[];
  favorites: CustomTopic[];
  completed: CustomTopic[];
  stats: LibraryStats;
}

export const TopicsLibrary: React.FC<TopicsLibraryProps> = ({ 
  user, 
  onSelectTopic, 
  onStartLesson 
}) => {
  const [library, setLibrary] = useState<TopicsLibrary | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CustomTopic[]>([]);
  const [activeView, setActiveView] = useState<'overview' | 'categories' | 'recent' | 'search'>('overview');
  const [selectedFilters, setSelectedFilters] = useState<{
    difficulty?: string;
    status?: string;
    category?: string;
  }>({});

  useEffect(() => {
    loadLibrary();
  }, [user.user_id]);

  useEffect(() => {
    if (searchQuery.trim()) {
      performSearch();
    } else {
      setSearchResults([]);
      if (activeView === 'search') {
        setActiveView('overview');
      }
    }
  }, [searchQuery, selectedFilters]);

  const loadLibrary = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/library/${user.user_id}`);
      const data = await response.json();
      setLibrary(data.library);
    } catch (error) {
      console.error('Failed to load library:', error);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await fetch(`http://localhost:5000/api/library/${user.user_id}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          filters: selectedFilters
        })
      });
      const data = await response.json();
      setSearchResults(data.results);
      setActiveView('search');
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
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

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '#10b981';
      case 'intermediate': return '#f59e0b';
      case 'advanced': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const renderTopicCard = (topic: CustomTopic, showDetails = true) => (
    <div 
      key={topic.id} 
      className="topic-card enhanced-card" 
      style={{ borderColor: getStatusColor(topic.status || 'not_started') }}
      onClick={() => onSelectTopic(topic)}
    >
      <div className="topic-header">
        <div className="topic-icon-section">
          <span className="topic-icon">🎯</span>
          <div className="topic-metadata">
            <span className={`difficulty-badge ${topic.difficulty}`}>
              {topic.difficulty}
            </span>
            {topic.intensity && (
              <span className={`intensity-badge ${topic.intensity}`}>
                {topic.intensity}
              </span>
            )}
          </div>
        </div>
        <div className="topic-status-icon">
          {getStatusIcon(topic.status || 'not_started')}
        </div>
      </div>
      
      <h4 className="topic-title">{topic.title}</h4>
      
      {showDetails && (
        <>
          <p className="topic-description">{topic.description}</p>
          
          <div className="topic-stats">
            <div className="stat-item">
              <span className="stat-label">Progress:</span>
              <span className="stat-value">{topic.progress || 0}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Time:</span>
              <span className="stat-value">{formatTime(topic.timeSpent || 0)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Estimate:</span>
              <span className="stat-value">{topic.estimatedHours}h</span>
            </div>
          </div>
          
          <div className="topic-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${topic.progress || 0}%`,
                  backgroundColor: getStatusColor(topic.status || 'not_started')
                }}
              ></div>
            </div>
          </div>
          
          {topic.tags && topic.tags.length > 0 && (
            <div className="topic-tags">
              {topic.tags.map((tag: string, index: number) => (
                <span key={index} className="topic-tag">{tag}</span>
              ))}
            </div>
          )}
          
          <div className="topic-actions">
            <button 
              className="btn btn-primary btn-sm"
              onClick={(e) => {
                e.stopPropagation();
                onStartLesson(topic.title);
              }}
            >
              {(topic.progress || 0) > 0 ? 'Continue' : 'Start'} Learning
            </button>
            <button 
              className="btn btn-secondary btn-sm"
              onClick={(e) => {
                e.stopPropagation();
                // TODO: Add to favorites
              }}
            >
              ⭐ Favorite
            </button>
          </div>
        </>
      )}
    </div>
  );

  const renderStats = () => {
    if (!library?.stats) return null;
    
    return (
      <div className="library-stats">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{library.stats.total_topics}</div>
            <div className="stat-label">Total Topics</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{library.stats.completed_topics}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{library.stats.in_progress}</div>
            <div className="stat-label">In Progress</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{formatTime(library.stats.total_time_spent)}</div>
            <div className="stat-label">Time Invested</div>
          </div>
        </div>
      </div>
    );
  };

  const renderCategoriesView = () => {
    if (!library?.by_category) return <div>No categories found</div>;
    
    return (
      <div className="categories-view">
        {Object.entries(library.by_category).map(([category, topics]) => (
          <div key={category} className="category-section">
            <h3 className="category-title">
              📂 {category.replace('_', ' ').toUpperCase()}
              <span className="topic-count">({topics.length})</span>
            </h3>
            <div className="topics-grid">
              {topics.map(topic => renderTopicCard(topic))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderRecentView = () => {
    if (!library?.recent || library.recent.length === 0) {
      return <div className="empty-state">No recent topics found</div>;
    }
    
    return (
      <div className="recent-view">
        <h3>📚 Recently Accessed</h3>
        <div className="topics-grid">
          {library.recent.map(topic => renderTopicCard(topic))}
        </div>
      </div>
    );
  };

  const renderSearchView = () => {
    return (
      <div className="search-view">
        <h3>🔍 Search Results ({searchResults.length})</h3>
        {searchResults.length > 0 ? (
          <div className="topics-grid">
            {searchResults.map(topic => renderTopicCard(topic))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No topics found matching your search.</p>
            <p>Try adjusting your search terms or filters.</p>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div>Loading your topics library...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="topics-library">
      {/* Header Section */}
      <div className="card library-header">
        <h2>📚 Your Topics Library</h2>
        <p>Organize, search, and track your learning journey</p>
        
        {/* Search Bar */}
        <div className="search-section">
          <div className="search-input-container">
            <input
              type="text"
              placeholder="Search your topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button className="search-btn" onClick={performSearch}>
              🔍
            </button>
          </div>
          
          {/* Filters */}
          <div className="search-filters">
            <select 
              value={selectedFilters.difficulty || ''}
              onChange={(e) => setSelectedFilters({...selectedFilters, difficulty: e.target.value || undefined})}
            >
              <option value="">All Difficulties</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
            
            <select 
              value={selectedFilters.status || ''}
              onChange={(e) => setSelectedFilters({...selectedFilters, status: e.target.value || undefined})}
            >
              <option value="">All Statuses</option>
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
        
        {/* Navigation */}
        <div className="library-navigation">
          <button 
            className={`nav-btn ${activeView === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveView('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`nav-btn ${activeView === 'categories' ? 'active' : ''}`}
            onClick={() => setActiveView('categories')}
          >
            📂 Categories
          </button>
          <button 
            className={`nav-btn ${activeView === 'recent' ? 'active' : ''}`}
            onClick={() => setActiveView('recent')}
          >
            📚 Recent
          </button>
        </div>
      </div>

      {/* Stats Section */}
      {activeView === 'overview' && (
        <div className="card">
          <h3>📈 Learning Statistics</h3>
          {renderStats()}
        </div>
      )}

      {/* Content Section */}
      <div className="card library-content">
        {activeView === 'overview' && renderCategoriesView()}
        {activeView === 'categories' && renderCategoriesView()}
        {activeView === 'recent' && renderRecentView()}
        {activeView === 'search' && renderSearchView()}
      </div>
    </div>
  );
};
