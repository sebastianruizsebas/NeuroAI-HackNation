import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../services/api';

interface LearningTrackerProps {
  userId: string;
  topicId: string;
  topicTitle: string;
  onBreakRecommended: () => void;
  onSessionEnd: (duration: number) => void;
}

export const LearningTracker: React.FC<LearningTrackerProps> = ({ 
  userId, 
  topicId, 
  topicTitle, 
  onBreakRecommended,
  onSessionEnd 
}) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0); // in minutes
  const [isActive, setIsActive] = useState(false);
  const [showBreakReminder, setShowBreakReminder] = useState(false);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    startSession();
    return () => {
      if (sessionId) {
        endSession();
      }
    };
  }, []);

  useEffect(() => {
    if (isActive) {
      intervalRef.current = setInterval(() => {
        const now = new Date();
        if (startTime) {
          const minutes = Math.floor((now.getTime() - startTime.getTime()) / (1000 * 60));
          setElapsedTime(minutes);
          
          // Recommend break after 60 minutes
          if (minutes >= 60 && !showBreakReminder) {
            setShowBreakReminder(true);
            onBreakRecommended();
          }
        }
      }, 60000) as unknown as number; // Update every minute
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isActive, startTime, showBreakReminder]);

  const startSession = async () => {
    try {
      const response = await apiService.startLearningSession(userId, topicId);
      setSessionId(response.sessionId);
      setStartTime(new Date());
      setIsActive(true);
    } catch (error) {
      console.error('Failed to start learning session:', error);
    }
  };

  const endSession = async () => {
    if (!sessionId) return;
    
    try {
      const response = await apiService.endLearningSession(sessionId);
      setIsActive(false);
      onSessionEnd(response.duration);
    } catch (error) {
      console.error('Failed to end learning session:', error);
    }
  };

  const takeBreak = () => {
    setIsActive(false);
    setShowBreakReminder(false);
  };

  const resumeSession = () => {
    setIsActive(true);
  };

  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getProgressColor = (): string => {
    if (elapsedTime < 30) return '#22c55e'; // Green
    if (elapsedTime < 60) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  return (
    <div className="learning-tracker">
      <div className="tracker-header">
        <div className="session-info">
          <h4>📚 Learning: {topicTitle}</h4>
          <div className="time-display" style={{ color: getProgressColor() }}>
            ⏱️ {formatTime(elapsedTime)}
            {isActive && <span className="pulse-dot"></span>}
          </div>
        </div>
        
        <div className="session-controls">
          {isActive ? (
            <button className="btn btn-sm" onClick={takeBreak}>
              ⏸️ Pause
            </button>
          ) : (
            <button className="btn btn-primary btn-sm" onClick={resumeSession}>
              ▶️ Resume
            </button>
          )}
          <button className="btn btn-ghost btn-sm" onClick={endSession}>
            🏁 End Session
          </button>
        </div>
      </div>

      {showBreakReminder && (
        <div className="break-reminder">
          <div className="reminder-content">
            <span className="reminder-icon">☕</span>
            <div className="reminder-text">
              <strong>Time for a break!</strong>
              <p>You've been learning for over an hour. Taking a 10-15 minute break can help improve retention and focus.</p>
            </div>
            <div className="reminder-actions">
              <button className="btn btn-primary btn-sm" onClick={takeBreak}>
                Take Break
              </button>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowBreakReminder(false)}>
                Keep Going
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="session-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ 
              width: `${Math.min((elapsedTime / 120) * 100, 100)}%`,
              backgroundColor: getProgressColor()
            }}
          />
        </div>
        <div className="progress-labels">
          <span>0m</span>
          <span>30m</span>
          <span>1h</span>
          <span>2h</span>
        </div>
      </div>
    </div>
  );
};
