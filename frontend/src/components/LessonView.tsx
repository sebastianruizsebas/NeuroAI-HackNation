import React, { useState, useEffect } from 'react';
import { apiService, Lesson, SentimentAnalysis } from '../services/api';

interface LessonViewProps {
  topic: string;
  userId: string;
  onComplete: (sentimentData: SentimentAnalysis[]) => void;
}

export const LessonView: React.FC<LessonViewProps> = ({ topic, userId, onComplete }) => {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentChunk, setCurrentChunk] = useState(0);
  const [responses, setResponses] = useState<string[]>([]);
  const [sentimentData, setSentimentData] = useState<SentimentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLesson = async () => {
      try {
        const lessonData = await apiService.generateLesson(topic, userId);
        setLesson(lessonData);
        setResponses(new Array(lessonData.chunks.length).fill(''));
        setLoading(false);
      } catch (error) {
        console.error('Failed to load lesson:', error);
        setLoading(false);
      }
    };

    loadLesson();
  }, [topic, userId]);

  const handleResponseChange = (response: string) => {
    const newResponses = [...responses];
    newResponses[currentChunk] = response;
    setResponses(newResponses);
  };

  // inside LessonView.tsx
  const handleNext = async () => {
    let updated = sentimentData;

    if (responses[currentChunk].trim()) {
      try {
        const lessonContext = `${chunk.title}: ${chunk.content}\nKey Point: ${chunk.key_point}`;
        const sentiment = await apiService.analyzeSentiment(responses[currentChunk], lessonContext);
        updated = [...sentimentData];
        updated[currentChunk] = sentiment;
        setSentimentData(updated);
      } catch (err) {
        console.error('Sentiment w/ context failed, trying basic...', err);
        try {
          const sentiment = await apiService.analyzeSentiment(responses[currentChunk]);
          updated = [...sentimentData];
          updated[currentChunk] = sentiment;
          setSentimentData(updated);
        } catch (fallbackErr) {
          console.error('Basic sentiment also failed:', fallbackErr);
          // still proceed with whatever we have
          updated = [...sentimentData];
        }
      }
    }

    const isLast = lesson && currentChunk >= lesson.chunks.length - 1;
    if (!isLast) {
      setCurrentChunk(currentChunk + 1);
      return;
    }

    // Last section → finish with the freshest data we have
    onComplete(updated);
  };


  if (loading) {
    return <div className="loading">Generating your personalized lesson...</div>;
  }

  if (!lesson) {
    return <div className="card">Failed to load lesson content.</div>;
  }

  const chunk = lesson.chunks[currentChunk];
  const progress = ((currentChunk + 1) / lesson.chunks.length) * 100;
  const currentSentiment = sentimentData[currentChunk];

  return (
    <div>
      <div className="card lesson-chunk">
        <div className="card-header">
          <h2>{topic} - Lesson</h2>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
          <p>Section {currentChunk + 1} of {lesson.chunks.length}</p>
        </div>

        <div className="lesson-content">
          <h3>{chunk.title}</h3>
          <p>{chunk.content}</p>
          
          <div className="key-point">
            <strong>Key Point:</strong> {chunk.key_point}
          </div>

          <div className="response-section">
            <label htmlFor="response">
              How would you explain this concept in your own words?
            </label>
            <textarea
              id="response"
              value={responses[currentChunk]}
              onChange={(e) => handleResponseChange(e.target.value)}
              placeholder="Share your understanding..."
              rows={4}
            />
          </div>

          {currentSentiment && (
            <div className={`card sentiment-${currentSentiment.understanding.toLowerCase()}`}>
              <h4>Feedback</h4>
              <p><strong>Understanding Level:</strong> {currentSentiment.understanding}</p>
              <p><strong>Suggestion:</strong> {currentSentiment.suggestion}</p>
              <div className="sentiment-metrics">
                <span>Confidence: {Math.round(currentSentiment.confidence_level * 100)}%</span>
                <span>Confusion: {Math.round(currentSentiment.confusion_level * 100)}%</span>
              </div>
            </div>
          )}
        </div>

        <div className="lesson-controls">
          <button 
            className="btn btn-primary" 
            onClick={handleNext}
            disabled={!responses[currentChunk].trim()}
          >
            {currentChunk < lesson.chunks.length - 1 ? 'Next Section' : 'Complete Lesson'}
          </button>
        </div>
      </div>

      {currentChunk === lesson.chunks.length - 1 && (
        <div className="card">
          <h3>Key Takeaways</h3>
          <ul>
            {lesson.key_takeaways.map((takeaway, index) => (
              <li key={index}>{takeaway}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LessonView;