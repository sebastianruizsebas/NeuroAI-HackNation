import React, { useState, useEffect } from 'react';
import { apiService, Question } from '../services/api';

interface AssessmentProps {
  topic: string;
  userId: string;
  onComplete: (score: number) => void;
}

export const Assessment: React.FC<AssessmentProps> = ({ topic, userId, onComplete }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        const data = await apiService.getAssessment(topic);
        setQuestions(data.questions);
        setAnswers(new Array(data.questions.length).fill(''));
        setLoading(false);
      } catch (error) {
        console.error('Failed to load assessment:', error);
        setLoading(false);
      }
    };

    loadQuestions();
  }, [topic]);

  const handleAnswerSelect = (answer: string) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answer;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      const result = await apiService.submitAssessment(answers, questions, userId, topic);
      onComplete(result.score);
    } catch (error) {
      console.error('Failed to submit assessment:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading assessment...</div>;
  }

  if (questions.length === 0) {
    return <div className="card">No questions available for this topic.</div>;
  }

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="card question-card">
      <div className="card-header">
        <h2>Pre-Assessment: {topic}</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
        <p>Question {currentQuestion + 1} of {questions.length}</p>
      </div>

      <div className="question-content">
        <h3>{question.question}</h3>
        <div className="options">
          {question.options.map((option, index) => (
            <label key={index} className="option">
              <input
                type="radio"
                name={`question-${currentQuestion}`}
                value={option}
                checked={answers[currentQuestion] === option}
                onChange={() => handleAnswerSelect(option)}
              />
              {option}
            </label>
          ))}
        </div>
      </div>

      <div className="assessment-controls">
        <button 
          className="btn btn-secondary" 
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
        >
          Previous
        </button>
        
        {currentQuestion < questions.length - 1 ? (
          <button 
            className="btn btn-primary" 
            onClick={handleNext}
            disabled={!answers[currentQuestion]}
          >
            Next
          </button>
        ) : (
          <button 
            className="btn btn-primary" 
            onClick={handleSubmit}
            disabled={answers.some(answer => !answer)}
          >
            Submit Assessment
          </button>
        )}
      </div>
    </div>
  );
};

export default Assessment;