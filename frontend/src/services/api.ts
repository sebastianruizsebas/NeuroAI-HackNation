// API service for connecting to ProfAI backend
const API_BASE_URL = 'http://localhost:5000/api';

export interface User {
  user_id: string;
  name: string;
  user_data?: {
    name: string;
    created_at: string;
    competency_scores: Record<string, number>;
    knowledge_gaps: Record<string, string[]>;
    strong_areas: Record<string, string[]>;
    learning_path: string[];
    completed_lessons: string[];
    total_lessons: number;
    current_curriculum?: string;
  };
}

export interface Question {
  question: string;
  options: string[];
  correct: string;
  concept?: string;
  difficulty?: number;
  targets_weakness?: boolean;
}

export interface AssessmentResult {
  score: number;
  correct: number;
  total: number;
}

export interface EnhancedAssessmentResult {
  overall_score: number;
  knowledge_gaps: string[];
  strong_areas: string[];
  learning_path: string[];
  recommended_lessons: string[];
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
  frustration_level?: number;
  confidence_level: number;
  engagement_level?: number;
  understanding: string;
  suggestion: string;
  should_proceed?: boolean;
}

export interface UserProgress {
  user_id: string;
  name: string;
  overall_progress: {
    lessons_completed: number;
    total_lessons: number;
    average_quiz_score: number;
    learning_velocity: number;
    knowledge_improvement: Record<string, any>;
    session_history: string[];
  };
  current_competencies: Record<string, number>;
  knowledge_gaps: Record<string, string[]>;
  strong_areas: Record<string, string[]>;
  learning_path: string[];
  recommendations: string[];
}

export type TTSOptions = {
  voice_id?: string;
  model_id?: string;
  stability?: number;
  similarity_boost?: number;
  style?: number;
  speed?: number;
  use_speaker_boost?: boolean;
};

async function tts(text: string, opts: TTSOptions = {}): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/tts`, {  // << was '/api/tts'
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, ...opts }),
  });
  if (!res.ok) throw new Error('TTS failed');
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}




export const apiService = {
  // Create a new user (V2 Enhanced)
  async createUser(name: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    
    if (!response.ok) {
      throw new Error('Failed to create user');
    }
    
    const result = await response.json();
    return {
      user_id: result.user_id,
      name: name,
      user_data: result.user_data
    };
  },

  // Get user data (V2 Enhanced)
  async getUser(userId: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get user');
    }
    
    const userData = await response.json();
    return {
      user_id: userId,
      name: userData.name,
      user_data: userData
    };
  },

  // V2 Enhanced Assessment: Initial 5 questions
  async getInitialAssessment(topic: string): Promise<{ questions: Question[], type: string, total_questions: number }> {
    const response = await fetch(`${API_BASE_URL}/assessment/initial`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });
    
    if (!response.ok) {
      throw new Error('Failed to get initial assessment');
    }
    
    return response.json();
  },

  // V2 Enhanced Assessment: Adaptive 5 questions based on initial results
  async getAdaptiveAssessment(userId: string, topic: string, initialResults: Record<string, any>): Promise<{ questions: Question[], type: string, total_questions: number }> {
    const response = await fetch(`${API_BASE_URL}/assessment/adaptive`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, topic, initial_results: initialResults })
    });
    
    if (!response.ok) {
      throw new Error('Failed to get adaptive assessment');
    }
    
    return response.json();
  },

  // V2 Enhanced: Complete full 10-question assessment analysis
  async completeFullAssessment(
    userId: string, 
    topic: string, 
    initialAnswers: Record<string, string>, 
    adaptiveAnswers: Record<string, string>, 
    allQuestions: Question[]
  ): Promise<EnhancedAssessmentResult> {
    const response = await fetch(`${API_BASE_URL}/assessment/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        user_id: userId, 
        topic, 
        initial_answers: initialAnswers, 
        adaptive_answers: adaptiveAnswers, 
        all_questions: allQuestions 
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to complete assessment');
    }
    
    return response.json();
  },

  // Legacy compatibility for simple assessment
  async getAssessment(topic: string): Promise<{ questions: Question[], topic: string }> {
    const result = await this.getInitialAssessment(topic);
    return {
      questions: result.questions,
      topic: topic
    };
  },

  // Submit assessment answers (Legacy compatibility)
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

  // V2 Enhanced: Generate personalized curriculum
  async generateCurriculum(userId: string, topic: string, knowledgeGaps: string[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/curriculum/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, topic, knowledge_gaps: knowledgeGaps })
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate curriculum');
    }
    
    return response.json();
  },

  // Generate lesson content (V2 Enhanced endpoint)
  async generateLesson(topic: string, userId: string): Promise<Lesson> {
    const response = await fetch(`${API_BASE_URL}/lesson/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, user_id: userId })
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate lesson');
    }
    
    return response.json();
  },

  // V2 Enhanced: Get specific lesson content
  async getLesson(lessonId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/lesson/${lessonId}`, {
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get lesson');
    }
    
    return response.json();
  },

  // V2 Enhanced: Generate lesson quiz
  async generateLessonQuiz(lessonId: string, lessonContent: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/lesson/quiz`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lesson_id: lessonId, lesson_content: lessonContent })
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate lesson quiz');
    }
    
    return response.json();
  },

  // V2 Enhanced: Submit lesson quiz
  async submitLessonQuiz(userId: string, lessonId: string, answers: Record<string, string>, questions: Question[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, lesson_id: lessonId, answers, questions })
    });
    
    if (!response.ok) {
      throw new Error('Failed to submit lesson quiz');
    }
    
    return response.json();
  },

  // V2 Enhanced sentiment analysis with context
  async analyzeSentiment(responseText: string, lessonContext?: string): Promise<SentimentAnalysis> {
    const response = await fetch(`${API_BASE_URL}/sentiment/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        response: responseText, 
        lesson_context: lessonContext || '' 
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze sentiment');
    }
    
    return response.json();
  },

  // V2 Enhanced: Get user progress and analytics
  async getUserProgress(userId: string): Promise<UserProgress> {
    const response = await fetch(`${API_BASE_URL}/progress/${userId}`, {
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get user progress');
    }
    
    return response.json();
  },

  // V2 Enhanced: Generate final assessment
  async generateFinalAssessment(userId: string, topic: string, completedLessons: string[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/assessment/final`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, topic, completed_lessons: completedLessons })
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate final assessment');
    }
    
    return response.json();
  },

  // Save session (V2 Enhanced)
  async saveSession(userId: string, sessionData: any): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/session/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, session_data: sessionData })
    });
    
    if (!response.ok) {
      throw new Error('Failed to save session');
    }
  },

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    
    return response.json();
  },
  tts
};
