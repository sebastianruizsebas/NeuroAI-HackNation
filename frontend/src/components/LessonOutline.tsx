import React, { useState, useEffect } from 'react';

interface Module {
  id: string;
  title: string;
  estimatedTime: string;
  description: string;
  keyConcepts: string[];
  activities: string[];
  assessmentType: string;
  addressesGaps: string[];
}

interface LessonOutlineData {
  topic: string;
  difficulty: string;
  estimatedDuration: string;
  learningObjectives: string[];
  prerequisites: string[];
  modules: Module[];
  resources: string[];
  expectedOutcomes: string[];
  generated_at?: string;
}

interface LessonOutlineProps {
  topic: string;
  difficulty: string;
  assessmentResults?: any;
  onStartLesson: () => void;
  onBackToAssessment: () => void;
}

const LessonOutline: React.FC<LessonOutlineProps> = ({ 
  topic, 
  difficulty, 
  assessmentResults, 
  onStartLesson, 
  onBackToAssessment 
}) => {
  const [outline, setOutline] = useState<LessonOutlineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    generateOutline();
  }, [topic, difficulty, assessmentResults]);

  const generateOutline = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/lesson/outline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          difficulty,
          assessment_results: assessmentResults
        }),
      });

      if (response.ok) {
        const outlineData = await response.json();
        setOutline(outlineData);
      } else {
        setError('Failed to generate lesson outline');
      }
    } catch (err) {
      setError('Error generating lesson outline');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (diff: string) => {
    switch (diff.toLowerCase()) {
      case 'beginner': return '#22c55e';
      case 'intermediate': return '#eab308';
      case 'advanced': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getAssessmentTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'quiz': return '📝';
      case 'practical': return '🛠️';
      case 'discussion': return '💬';
      default: return '✅';
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{ fontSize: '18px', color: '#6b7280', marginBottom: '10px' }}>
          🎯 Generating your personalized lesson outline...
        </div>
        <div style={{ 
          width: '300px', 
          height: '6px', 
          backgroundColor: '#e5e7eb', 
          borderRadius: '3px', 
          margin: '0 auto',
          overflow: 'hidden'
        }}>
          <div style={{ 
            width: '100%', 
            height: '100%', 
            backgroundColor: '#3b82f6',
            animation: 'loading 2s ease-in-out infinite'
          }} />
        </div>
        <style>{`
          @keyframes loading {
            0% { transform: translateX(-100%); }
            50% { transform: translateX(0%); }
            100% { transform: translateX(100%); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{ color: '#ef4444', marginBottom: '20px' }}>
          ❌ {error}
        </div>
        <button
          onClick={generateOutline}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            marginRight: '10px'
          }}
        >
          Try Again
        </button>
        <button
          onClick={onBackToAssessment}
          style={{
            backgroundColor: '#6b7280',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Back to Assessment
        </button>
      </div>
    );
  }

  if (!outline) return null;

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
          <h1 style={{ color: '#1f2937', margin: 0, marginRight: '16px' }}>
            📚 Lesson Outline: {outline.topic}
          </h1>
          <span style={{ 
            backgroundColor: getDifficultyColor(outline.difficulty),
            color: 'white',
            padding: '4px 12px',
            borderRadius: '16px',
            fontSize: '14px',
            fontWeight: 'bold'
          }}>
            {outline.difficulty}
          </span>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div>
            <strong style={{ color: '#374151' }}>Duration:</strong>
            <div style={{ color: '#6b7280' }}>{outline.estimatedDuration}</div>
          </div>
          <div>
            <strong style={{ color: '#374151' }}>Modules:</strong>
            <div style={{ color: '#6b7280' }}>{outline.modules.length} modules</div>
          </div>
          {assessmentResults && (
            <div>
              <strong style={{ color: '#374151' }}>Personalized:</strong>
              <div style={{ color: '#22c55e' }}>✅ Based on your assessment</div>
            </div>
          )}
        </div>
      </div>

      {/* Learning Objectives */}
      <div style={{ 
        backgroundColor: '#f0f9ff',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        border: '1px solid #0ea5e9'
      }}>
        <h3 style={{ color: '#0c4a6e', marginBottom: '12px' }}>🎯 Learning Objectives</h3>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          {outline.learningObjectives.map((objective, index) => (
            <li key={index} style={{ color: '#0c4a6e', marginBottom: '8px' }}>
              {objective}
            </li>
          ))}
        </ul>
      </div>

      {/* Prerequisites */}
      {outline.prerequisites.length > 0 && (
        <div style={{ 
          backgroundColor: '#fef3c7',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '20px',
          border: '1px solid #f59e0b'
        }}>
          <h4 style={{ color: '#92400e', marginBottom: '8px' }}>📋 Prerequisites</h4>
          <div style={{ color: '#92400e' }}>
            {outline.prerequisites.join(' • ')}
          </div>
        </div>
      )}

      {/* Modules */}
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ color: '#1f2937', marginBottom: '16px' }}>📖 Lesson Modules</h3>
        {outline.modules.map((module, index) => (
          <div key={module.id} style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '16px',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <div>
                <h4 style={{ color: '#1f2937', margin: 0, marginBottom: '4px' }}>
                  {index + 1}. {module.title}
                </h4>
                <p style={{ color: '#6b7280', margin: 0, fontSize: '14px' }}>
                  {module.description}
                </p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ 
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '12px'
                }}>
                  ⏱️ {module.estimatedTime}
                </span>
                <span style={{ fontSize: '20px' }}>
                  {getAssessmentTypeIcon(module.assessmentType)}
                </span>
              </div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <strong style={{ color: '#374151', fontSize: '14px' }}>Key Concepts:</strong>
                <ul style={{ margin: '4px 0 0 0', paddingLeft: '16px' }}>
                  {module.keyConcepts.map((concept, i) => (
                    <li key={i} style={{ color: '#6b7280', fontSize: '14px', marginBottom: '2px' }}>
                      {concept}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <strong style={{ color: '#374151', fontSize: '14px' }}>Activities:</strong>
                <ul style={{ margin: '4px 0 0 0', paddingLeft: '16px' }}>
                  {module.activities.map((activity, i) => (
                    <li key={i} style={{ color: '#6b7280', fontSize: '14px', marginBottom: '2px' }}>
                      {activity}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {module.addressesGaps.length > 0 && (
              <div style={{ 
                marginTop: '12px',
                padding: '8px',
                backgroundColor: '#fef2f2',
                borderRadius: '4px',
                border: '1px solid #fecaca'
              }}>
                <strong style={{ color: '#dc2626', fontSize: '12px' }}>
                  🎯 Addresses your knowledge gaps: 
                </strong>
                <span style={{ color: '#dc2626', fontSize: '12px' }}>
                  {module.addressesGaps.join(', ')}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Resources and Expected Outcomes */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
        <div style={{ 
          backgroundColor: '#f0fdf4',
          borderRadius: '8px',
          padding: '16px',
          border: '1px solid #22c55e'
        }}>
          <h4 style={{ color: '#15803d', marginBottom: '8px' }}>📚 Resources</h4>
          <ul style={{ margin: 0, paddingLeft: '16px' }}>
            {outline.resources.map((resource, index) => (
              <li key={index} style={{ color: '#15803d', fontSize: '14px', marginBottom: '4px' }}>
                {resource}
              </li>
            ))}
          </ul>
        </div>

        <div style={{ 
          backgroundColor: '#faf5ff',
          borderRadius: '8px',
          padding: '16px',
          border: '1px solid #a855f7'
        }}>
          <h4 style={{ color: '#7c3aed', marginBottom: '8px' }}>🏆 Expected Outcomes</h4>
          <ul style={{ margin: 0, paddingLeft: '16px' }}>
            {outline.expectedOutcomes.map((outcome, index) => (
              <li key={index} style={{ color: '#7c3aed', fontSize: '14px', marginBottom: '4px' }}>
                {outcome}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '16px',
        padding: '20px',
        backgroundColor: '#f9fafb',
        borderRadius: '8px'
      }}>
        <button
          onClick={onStartLesson}
          style={{
            backgroundColor: '#22c55e',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          🚀 Start Learning Journey
        </button>
        
        <button
          onClick={onBackToAssessment}
          style={{
            backgroundColor: '#6b7280',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          ← Back to Assessment
        </button>
      </div>
    </div>
  );
};

export default LessonOutline;
