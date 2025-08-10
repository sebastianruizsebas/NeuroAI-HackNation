import React, { useState } from 'react';

interface QualityValidation {
  is_valid: boolean;
  quality_score: number;
  issues: string[];
  suggestions: string[];
}

interface QuestionReport {
  question_number: number;
  question_text: string;
  quality_score: number;
  is_valid: boolean;
  issues: string[];
  suggestions: string[];
}

interface QualityReportData {
  summary: {
    total_questions: number;
    average_quality_score: number;
    passed_validation: number;
    overall_grade: string;
  };
  individual_reports: QuestionReport[];
  common_issues: Record<string, number>;
  recommendations: string[];
}

interface Question {
  question: string;
  options: string[];
  correct: string;
  concept?: string;
  difficulty?: number;
}

const QualityReport: React.FC = () => {
  const [qualityReport, setQualityReport] = useState<QualityReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [testQuestions] = useState<Question[]>([
    {
      question: "What is the primary purpose of transformers?",
      options: [
        "A) To process natural language",
        "B) To solve mathematical equations", 
        "C) To create images",
        "D) To manage databases"
      ],
      correct: "A",
      concept: "Basic Understanding",
      difficulty: 1
    },
    {
      question: "Which field is most closely related to transformers?",
      options: [
        "A) Computer Science and AI",
        "B) Mechanical Engineering",
        "C) Chemistry", 
        "D) Geography"
      ],
      correct: "A",
      concept: "Domain Knowledge", 
      difficulty: 1
    },
    {
      question: "What would be a typical application of transformers?",
      options: [
        "A) Solving complex problems and analysis",
        "B) Building physical structures",
        "C) Cooking meals",
        "D) Painting artwork"
      ],
      correct: "A",
      concept: "Applications",
      difficulty: 1
    }
  ]);

  const testQualityVetting = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/assessment/quality', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questions: testQuestions,
          topic: 'transformers'
        }),
      });

      if (response.ok) {
        const report = await response.json();
        setQualityReport(report);
      } else {
        console.error('Failed to get quality report');
      }
    } catch (error) {
      console.error('Error testing quality vetting:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'Excellent': return '#22c55e';
      case 'Good': return '#eab308';
      case 'Needs Improvement': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#22c55e';
    if (score >= 0.6) return '#eab308';
    return '#ef4444';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>Question Quality Vetting System</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <p style={{ color: '#6b7280', marginBottom: '15px' }}>
          This system evaluates the quality and coherence of generated assessment questions using multiple criteria:
        </p>
        <ul style={{ color: '#6b7280', paddingLeft: '20px' }}>
          <li>Topic relevance and alignment</li>
          <li>Question structure and clarity</li>
          <li>Answer option quality and distinctness</li>
          <li>Educational value assessment</li>
          <li>AI-powered coherence validation</li>
        </ul>
      </div>

      <button
        onClick={testQualityVetting}
        disabled={loading}
        style={{
          backgroundColor: '#3b82f6',
          color: 'white',
          padding: '10px 20px',
          border: 'none',
          borderRadius: '6px',
          cursor: loading ? 'not-allowed' : 'pointer',
          marginBottom: '20px',
          opacity: loading ? 0.6 : 1
        }}
      >
        {loading ? 'Analyzing Questions...' : 'Test Quality Vetting'}
      </button>

      {qualityReport && (
        <div style={{ 
          backgroundColor: 'white', 
          border: '1px solid #e5e7eb', 
          borderRadius: '8px', 
          padding: '20px',
          marginTop: '20px'
        }}>
          <h3 style={{ color: '#1f2937', marginBottom: '15px' }}>Quality Assessment Report</h3>
          
          {/* Summary Section */}
          <div style={{ 
            backgroundColor: '#f9fafb', 
            padding: '15px', 
            borderRadius: '6px', 
            marginBottom: '20px' 
          }}>
            <h4 style={{ color: '#1f2937', marginBottom: '10px' }}>Summary</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
              <div>
                <strong>Total Questions:</strong> {qualityReport.summary.total_questions}
              </div>
              <div>
                <strong>Passed Validation:</strong> {qualityReport.summary.passed_validation}
              </div>
              <div>
                <strong>Average Score:</strong> 
                <span style={{ 
                  color: getScoreColor(qualityReport.summary.average_quality_score),
                  marginLeft: '5px',
                  fontWeight: 'bold'
                }}>
                  {qualityReport.summary.average_quality_score.toFixed(2)}
                </span>
              </div>
              <div>
                <strong>Overall Grade:</strong> 
                <span style={{ 
                  color: getGradeColor(qualityReport.summary.overall_grade),
                  marginLeft: '5px',
                  fontWeight: 'bold'
                }}>
                  {qualityReport.summary.overall_grade}
                </span>
              </div>
            </div>
          </div>

          {/* Individual Question Reports */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ color: '#1f2937', marginBottom: '15px' }}>Individual Question Analysis</h4>
            {qualityReport.individual_reports.map((report, index) => (
              <div key={index} style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '6px', 
                padding: '15px', 
                marginBottom: '10px',
                backgroundColor: report.is_valid ? '#f0fdf4' : '#fef2f2'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <h5 style={{ color: '#1f2937', margin: 0 }}>Question {report.question_number}</h5>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <span style={{ 
                      backgroundColor: report.is_valid ? '#22c55e' : '#ef4444',
                      color: 'white',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '12px'
                    }}>
                      {report.is_valid ? 'PASSED' : 'FAILED'}
                    </span>
                    <span style={{ 
                      color: getScoreColor(report.quality_score),
                      fontWeight: 'bold'
                    }}>
                      Score: {report.quality_score.toFixed(2)}
                    </span>
                  </div>
                </div>
                
                <p style={{ color: '#6b7280', fontSize: '14px', margin: '5px 0' }}>
                  {report.question_text}
                </p>
                
                {report.issues.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <strong style={{ color: '#ef4444', fontSize: '14px' }}>Issues:</strong>
                    <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                      {report.issues.map((issue, i) => (
                        <li key={i} style={{ color: '#ef4444', fontSize: '14px' }}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {report.suggestions.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <strong style={{ color: '#f59e0b', fontSize: '14px' }}>Suggestions:</strong>
                    <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                      {report.suggestions.map((suggestion, i) => (
                        <li key={i} style={{ color: '#f59e0b', fontSize: '14px' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Recommendations */}
          {qualityReport.recommendations.length > 0 && (
            <div style={{ 
              backgroundColor: '#eff6ff', 
              padding: '15px', 
              borderRadius: '6px' 
            }}>
              <h4 style={{ color: '#1f2937', marginBottom: '10px' }}>Recommendations</h4>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                {qualityReport.recommendations.map((rec, index) => (
                  <li key={index} style={{ color: '#3b82f6', marginBottom: '5px' }}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QualityReport;
