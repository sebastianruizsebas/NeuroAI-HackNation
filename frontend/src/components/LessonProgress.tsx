import React from 'react';
import { Deadline } from '../services/api';

interface LessonProgressProps {
  currentProgress: number;
  courseDeadline?: string;
  timeSpent: number;
  deadlines: Record<string, Deadline>;
  isComplete: boolean;
}

const formatTimeRemaining = (timeMs: number): string => {
  const days = Math.floor(timeMs / (1000 * 60 * 60 * 24));
  const hours = Math.floor((timeMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  return `${days}d ${hours}h remaining`;
};

const calculateTimeRemaining = (deadline: string): number => {
  const now = new Date().getTime();
  const deadlineTime = new Date(deadline).getTime();
  return Math.max(0, deadlineTime - now);
};

const LessonProgress: React.FC<LessonProgressProps> = ({
  currentProgress,
  courseDeadline,
  timeSpent,
  deadlines,
  isComplete
}) => {
  const timeRemainingMs = courseDeadline ? calculateTimeRemaining(courseDeadline) : 0;

  return (
    <div className="lesson-progress">
      <div className="progress-bar-container">
        <div 
          className="progress-bar"
          style={{ 
            width: '100%',
            height: '8px',
            backgroundColor: '#eee',
            borderRadius: '4px',
            overflow: 'hidden'
          }}
        >
          <div 
            className="progress-fill"
            style={{
              width: `${currentProgress}%`,
              height: '100%',
              backgroundColor: isComplete ? '#4CAF50' : '#2196F3',
              transition: 'width 0.3s ease'
            }}
          />
        </div>
      </div>

      <div className="progress-info">
        <div className="progress-stats">
          <span className="progress-percentage">
            Progress: {Math.round(currentProgress)}%
          </span>
          {courseDeadline && (
            <span className="deadline-info">
              {formatTimeRemaining(timeRemainingMs)}
            </span>
          )}
          <span className="time-spent">
            Time spent: {Math.floor(timeSpent / 60)}m {timeSpent % 60}s
          </span>
        </div>

        {deadlines && Object.keys(deadlines).length > 0 && (
          <div className="deadlines-list">
            <h4>Upcoming Deadlines</h4>
            {Object.entries(deadlines)
              .sort(([, a], [, b]) => 
                new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
              )
              .map(([id, deadline]) => (
                <div key={id} className="deadline-item">
                  <span className="deadline-date">
                    {new Date(deadline.due_date).toLocaleDateString()}
                  </span>
                  <span className={`deadline-status ${deadline.completed ? 'completed' : ''}`}>
                    {deadline.completed ? 'Completed' : formatTimeRemaining(calculateTimeRemaining(deadline.due_date))}
                  </span>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonProgress;
