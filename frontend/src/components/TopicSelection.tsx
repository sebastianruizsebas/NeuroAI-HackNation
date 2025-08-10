import React, { useState } from 'react';
import { apiService } from '../services/api';

interface TopicSelectionProps {
  userId: string;
  userName: string;
  onTopicSelected: (customTopic: CustomTopic) => void;
}

export interface CustomTopic {
  id: string;
  title: string;
  description: string;
  userInput: string;
  baseTopic: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedHours: number;
  createdAt: string;
  deadline?: string;
  intensity: 'light' | 'moderate' | 'intensive';
}

export const TopicSelection: React.FC<TopicSelectionProps> = ({ userId, userName, onTopicSelected }) => {
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedTopics, setSuggestedTopics] = useState<CustomTopic[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleInputSubmit = async () => {
    if (!userInput.trim()) return;
    
    try {
      setLoading(true);
      
      // Generate custom topics based on user input
      const response = await apiService.generateCustomTopics(userId, userInput);
      setSuggestedTopics(response.suggestions);
      setShowSuggestions(true);
    } catch (error) {
      console.error('Failed to generate topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTopicSelect = async (topic: CustomTopic) => {
    try {
      // Save the custom topic to user's library
      await apiService.saveCustomTopic(userId, topic);
      onTopicSelected(topic);
    } catch (error) {
      console.error('Failed to save topic:', error);
    }
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'light': return '#22c55e';
      case 'moderate': return '#3b82f6';
      case 'intensive': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getDifficultyEmoji = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '🌱';
      case 'intermediate': return '🌿';
      case 'advanced': return '🌳';
      default: return '📚';
    }
  };

  return (
    <div className="topic-selection">
      <div className="card">
        <h2>What would you like to learn about, {userName}? 🎯</h2>
        <p>Tell me about any topic you're curious about - I'll create a personalized learning experience just for you!</p>
        
        <div className="input-section">
          <div className="form-group">
            <label className="form-label">
              Describe what you want to learn:
            </label>
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="e.g., 'I want to understand how neural networks work in self-driving cars' or 'I'm interested in learning about AI ethics and bias in hiring algorithms' or 'How does machine learning help in medical diagnosis?'"
              className="topic-input"
              rows={4}
              disabled={loading}
            />
          </div>
          
          <div className="input-actions">
            <button 
              className="btn btn-primary"
              onClick={handleInputSubmit}
              disabled={!userInput.trim() || loading}
            >
              {loading ? '🧠 Generating Topics...' : '✨ Create My Learning Path'}
            </button>
          </div>
        </div>

        {showSuggestions && suggestedTopics.length > 0 && (
          <div className="suggestions-section">
            <h3>🎨 Personalized Learning Options</h3>
            <p>I've created these custom topics based on your interests:</p>
            
            <div className="topics-grid">
              {suggestedTopics.map((topic, index) => (
                <div key={index} className="custom-topic-card">
                  <div className="topic-header">
                    <div className="topic-title">
                      <span className="difficulty-emoji">{getDifficultyEmoji(topic.difficulty)}</span>
                      <h4>{topic.title}</h4>
                    </div>
                    <div className="topic-badges">
                      <span className={`intensity-badge ${topic.intensity}`}>
                        {topic.intensity}
                      </span>
                      <span className="duration-badge">
                        ⏱️ {topic.estimatedHours}h
                      </span>
                    </div>
                  </div>
                  
                  <p className="topic-description">{topic.description}</p>
                  
                  {topic.deadline && (
                    <div className="deadline-info">
                      <span className="deadline-label">🎯 Suggested completion:</span>
                      <span className="deadline-date">{topic.deadline}</span>
                    </div>
                  )}
                  
                  <div className="topic-meta-info">
                    <div className="base-topic">
                      <span>📋 Based on: {topic.baseTopic}</span>
                    </div>
                  </div>
                  
                  <button 
                    className="btn btn-primary"
                    onClick={() => handleTopicSelect(topic)}
                  >
                    Start Learning This! 🚀
                  </button>
                </div>
              ))}
            </div>
            
            <div className="try-again-section">
              <p>Not quite what you had in mind?</p>
              <button 
                className="btn btn-ghost"
                onClick={() => {
                  setShowSuggestions(false);
                  setUserInput('');
                  setSuggestedTopics([]);
                }}
              >
                Try a Different Description
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
