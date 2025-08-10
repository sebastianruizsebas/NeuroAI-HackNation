// API service for connecting to ProfAI backend
const API_BASE_URL = 'http://localhost:5000/api';

export interface User {
  user_id: string;
  name: string;
}

export interface Question {
  question: string;
  options: string[];
  correct: string;
}

export interface AssessmentResult {
  score: number;
  correct: number;
  total: number;
}

export interface LessonChunk {
  title: string;
  content: string;
  key_point: string;
}

export interface Lesson {
  overview: string;
  chunks: LessonChunk[];
  key_takeaways: string[];
}

export interface SentimentAnalysis {
  confusion_level: number;
  frustration_level: number;
  confidence_level: number;
  understanding: string;
  suggestion: string;
}

export const apiService = {
  // Create a new user
  async createUser(name: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    
    if (!response.ok) {
      throw new Error('Failed to create user');
    }
    
    return response.json();
  },

  // Get assessment questions
  async getAssessment(topic: string): Promise<{ questions: Question[], topic: string }> {
    const response = await fetch(`${API_BASE_URL}/assessment/${encodeURIComponent(topic)}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get assessment');
    }
    
    return response.json();
  },

  // Submit assessment answers
  async submitAssessment(answers: string[], questions: Question[], userId: string, topic: string): Promise<AssessmentResult> {
    const response = await fetch(`${API_BASE_URL}/assessment/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers, questions, user_id: userId, topic })
    });
    
    if (!response.ok) {
      throw new Error('Failed to submit assessment');
    }
    
    return response.json();
  },

  // Generate lesson content
  async generateLesson(topic: string, userId: string): Promise<Lesson> {
    const response = await fetch(`${API_BASE_URL}/lesson/${encodeURIComponent(topic)}/${userId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate lesson');
    }
    
    return response.json();
  },

  // Analyze sentiment
  async analyzeSentiment(responseText: string): Promise<SentimentAnalysis> {
    const response = await fetch(`${API_BASE_URL}/sentiment/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response: responseText })
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze sentiment');
    }
    
    return response.json();
  },

  // Save session
  async saveSession(userId: string, sessionData: any): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/session/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, session_data: sessionData })
    });
    
    if (!response.ok) {
      throw new Error('Failed to save session');
    }
  }
};
