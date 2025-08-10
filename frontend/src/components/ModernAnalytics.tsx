import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  TimeScale,
  Filler
} from 'chart.js';
import {
  Pie,
  Line,
  Bar,
  Doughnut
} from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import './ModernAnalytics.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  TimeScale,
  Filler
);

interface AnalyticsData {
  pieChart: any;
  progressOverTime: any;
  topicPerformance: any;
  weeklyActivity: any;
  summary: {
    totalLearningTime: number;
    totalTopics: number;
    averageSessionTime: number;
  };
}

interface AnalyticsProps {
  userId: string;
}

const ModernAnalytics: React.FC<AnalyticsProps> = ({ userId }) => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'time' | 'performance' | 'activity'>('overview');

  useEffect(() => {
    fetchAnalyticsData();
  }, [userId]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/analytics/all/${userId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch analytics data');
      }
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Base chart options - can be extended for specific chart types
  // const chartOptions = {
  //   responsive: true,
  //   maintainAspectRatio: false,
  //   plugins: {
  //     legend: {
  //       position: 'top' as const,
  //     },
  //   },
  // };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} min (${percentage}%)`;
          }
        }
      }
    },
    animation: {
      animateRotate: true,
      animateScale: true,
      duration: 2000
    }
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'day' as const,
        },
        title: {
          display: true,
          text: 'Date'
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Minutes'
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    },
    animation: {
      duration: 2000,
      easing: 'easeInOutQuart' as const
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Score (%)'
        }
      }
    },
    animation: {
      delay: (context: any) => context.dataIndex * 200,
      duration: 1500
    }
  };

  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="card">
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div className="loading-spinner"></div>
            <p>Loading your analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-container">
        <div className="card error-state">
          <h3>⚠️ Unable to Load Analytics</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchAnalyticsData}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="analytics-container">
        <div className="card">
          <p>No analytics data available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      {/* Header */}
      <div className="card analytics-header">
        <h2>📊 Learning Analytics Dashboard</h2>
        <p>Track your progress and discover learning patterns</p>
      </div>

      {/* Summary Cards */}
      <div className="analytics-summary">
        <div className="summary-card">
          <div className="summary-icon">⏱️</div>
          <div className="summary-content">
            <div className="summary-value">{formatTime(analyticsData.summary.totalLearningTime)}</div>
            <div className="summary-label">Total Learning Time</div>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">📚</div>
          <div className="summary-content">
            <div className="summary-value">{analyticsData.summary.totalTopics}</div>
            <div className="summary-label">Topics Studied</div>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">📈</div>
          <div className="summary-content">
            <div className="summary-value">{formatTime(analyticsData.summary.averageSessionTime)}</div>
            <div className="summary-label">Avg Session Time</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="card">
        <div className="analytics-tabs">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'time' ? 'active' : ''}`}
            onClick={() => setActiveTab('time')}
          >
            ⏰ Time Tracking
          </button>
          <button 
            className={`tab-btn ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            🎯 Performance
          </button>
          <button 
            className={`tab-btn ${activeTab === 'activity' ? 'active' : ''}`}
            onClick={() => setActiveTab('activity')}
          >
            📅 Activity
          </button>
        </div>
      </div>

      {/* Chart Content */}
      {activeTab === 'overview' && (
        <div className="analytics-grid">
          <div className="card chart-card">
            <h3>📈 Learning Progress Over Time</h3>
            <div className="chart-container" style={{ height: '300px' }}>
              <Line data={analyticsData.progressOverTime} options={lineOptions} />
            </div>
          </div>
          <div className="card chart-card">
            <h3>🥧 Time Distribution by Topic</h3>
            <div className="chart-container" style={{ height: '300px' }}>
              <Pie data={analyticsData.pieChart} options={pieOptions} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'time' && (
        <div className="analytics-grid">
          <div className="card chart-card full-width">
            <h3>⏰ Learning Time Distribution</h3>
            <div className="chart-container" style={{ height: '400px' }}>
              <Doughnut data={analyticsData.pieChart} options={pieOptions} />
            </div>
          </div>
          <div className="card chart-card full-width">
            <h3>📊 Progress Timeline</h3>
            <div className="chart-container" style={{ height: '400px' }}>
              <Line data={analyticsData.progressOverTime} options={lineOptions} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'performance' && (
        <div className="analytics-grid">
          <div className="card chart-card full-width">
            <h3>🎯 Topic Performance Scores</h3>
            <div className="chart-container" style={{ height: '400px' }}>
              <Bar data={analyticsData.topicPerformance} options={barOptions} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="analytics-grid">
          <div className="card chart-card full-width">
            <h3>📅 Weekly Learning Activity</h3>
            <div className="chart-container" style={{ height: '400px' }}>
              <Bar data={analyticsData.weeklyActivity} options={barOptions} />
            </div>
          </div>
        </div>
      )}

      {/* Insights Panel */}
      <div className="card insights-panel">
        <h3>💡 Learning Insights</h3>
        <div className="insights-grid">
          <div className="insight-item">
            <span className="insight-icon">🏆</span>
            <div className="insight-content">
              <strong>Most Studied Topic:</strong>
              <p>{analyticsData.pieChart.labels[0] || 'N/A'}</p>
            </div>
          </div>
          <div className="insight-item">
            <span className="insight-icon">⚡</span>
            <div className="insight-content">
              <strong>Learning Streak:</strong>
              <p>Keep up the great work!</p>
            </div>
          </div>
          <div className="insight-item">
            <span className="insight-icon">🎯</span>
            <div className="insight-content">
              <strong>Focus Area:</strong>
              <p>Consider spending more time on challenging topics</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModernAnalytics;
