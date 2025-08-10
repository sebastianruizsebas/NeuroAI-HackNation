import React, { useState, useEffect } from 'react';
import { apiService, Question } from '../services/api';

interface AssessmentProps {
  topic: string;
  userId: string;
  onComplete: (score: number, enhancedResult?: any) => void;
}

export const Assessment: React.FC<AssessmentProps> = ({ topic, userId, onComplete }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [assessmentPhase, setAssessmentPhase] = useState<'initial' | 'adaptive' | 'complete'>('initial');
  const [initialQuestions, setInitialQuestions] = useState<Question[]>([]);
  const [adaptiveQuestions, setAdaptiveQuestions] = useState<Question[]>([]);
  const [initialAnswers, setInitialAnswers] = useState<Record<string, string>>({});
  const [adaptiveAnswers, setAdaptiveAnswers] = useState<Record<string, string>>({});
  const [allQuestions, setAllQuestions] = useState<Question[]>([]);

  useEffect(() => {
    const loadQuestions = async () => {
      try {
        // V2 Enhanced: Start with initial assessment
        console.log('Loading V2 enhanced initial assessment...');
        const data = await apiService.getInitialAssessment(topic);
        setInitialQuestions(data.questions);
        setQuestions(data.questions);
        setAnswers(new Array(data.questions.length).fill(''));
        setAllQuestions([...data.questions]); // Start building complete question set
        setLoading(false);
      } catch (error) {
        console.error('Failed to load initial assessment, falling back to legacy:', error);
        // Fallback to legacy assessment
        try {
          const data = await apiService.getAssessment(topic);
          setQuestions(data.questions);
          setAnswers(new Array(data.questions.length).fill(''));
          setAssessmentPhase('complete'); // Skip adaptive phase
          setLoading(false);
        } catch (fallbackError) {
          console.error('Failed to load assessment:', fallbackError);
          setLoading(false);
        }
      }
    };

    loadQuestions();
  }, [topic]);

  const handleAnswerSelect = (answer: string) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answer;
    setAnswers(newAnswers);
  };

  const handleNext = async () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Completed current phase
      if (assessmentPhase === 'initial') {
        try {
          console.log('Transitioning to adaptive assessment phase...');
          // Store initial answers
          const answersMap: Record<string, string> = {};
          questions.forEach((_q, index) => {
            answersMap[`q${index}`] = answers[index];
          });
          setInitialAnswers(answersMap);

          // Get adaptive questions based on initial responses
          const adaptiveData = await apiService.getAdaptiveAssessment(userId, topic, answersMap);
          setAdaptiveQuestions(adaptiveData.questions);
          setQuestions(adaptiveData.questions);
          setAnswers(new Array(adaptiveData.questions.length).fill(''));
          setCurrentQuestion(0);
          setAssessmentPhase('adaptive');
          setAllQuestions([...allQuestions, ...adaptiveData.questions]);
        } catch (error) {
          console.error('Failed to load adaptive assessment, proceeding to completion:', error);
          await completeAssessment();
        }
      } else if (assessmentPhase === 'adaptive') {
        // Store adaptive answers and complete assessment
        const adaptiveAnswersMap: Record<string, string> = {};
        questions.forEach((_q, index) => {
          adaptiveAnswersMap[`q${index}`] = answers[index];
        });
        setAdaptiveAnswers(adaptiveAnswersMap);
        await completeAssessment();
      } else {
        // Legacy completion
        await completeAssessment();
      }
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const completeAssessment = async () => {
    try {
      console.log('Completing V2 enhanced assessment...');
      let result: any;
      
      if (assessmentPhase === 'adaptive' || assessmentPhase === 'initial') {
        // V2 Enhanced completion with full assessment analysis
        result = await apiService.completeFullAssessment(userId, topic, initialAnswers, adaptiveAnswers, allQuestions);
        // Enhanced result has overall_score
        onComplete(result.overall_score || 0, result);
      } else {
        // Legacy completion - use submitAssessment instead
        result = await apiService.submitAssessment(answers, questions, userId, topic);
        // Legacy result has score
        onComplete(result.score || 0, result);
      }
    } catch (error) {
      console.error('Failed to complete assessment:', error);
      // Fallback completion
      try {
        const result = await apiService.submitAssessment(answers, questions, userId, topic);
        onComplete(result.score || 0);
      } catch (fallbackError) {
        console.error('Fallback completion failed:', fallbackError);
      }
    }
  };

  const handleSubmit = async () => {
    await completeAssessment();
  };

  if (loading) {
    return <div className="loading">Loading assessment...</div>;
  }

  if (questions.length === 0) {
    return <div className="card">No questions available for this topic.</div>;
  }

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const phaseTitle = assessmentPhase === 'initial' ? 'Initial Assessment' : 
                    assessmentPhase === 'adaptive' ? 'Adaptive Assessment' : 'Assessment';

  return (
    <div className="card question-card">
      <div className="card-header">
        <h2>{phaseTitle}: {topic}</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
        <p>Question {currentQuestion + 1} of {questions.length}</p>
        {assessmentPhase !== 'complete' && (
          <div className="assessment-phase-indicator">
            Phase: {assessmentPhase === 'initial' ? '1/2 - Initial Assessment' : '2/2 - Adaptive Assessment'}
          </div>
        )}
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
            {assessmentPhase === 'initial' ? 'Continue to Adaptive Assessment' : 'Complete Assessment'}
          </button>
        )}
      </div>
    </div>
  );
};

export default Assessment;