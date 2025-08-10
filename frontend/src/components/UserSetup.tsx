import React, { useState } from 'react';
import { apiService, User } from '../services/api';

interface UserSetupProps {
  onUserCreated: (user: User) => void;
}

const UserSetup: React.FC<UserSetupProps> = ({ onUserCreated }) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('Please enter your name');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const result = await apiService.createUser(name.trim());
      onUserCreated(result);
    } catch (error) {
      setError('Failed to create user. Please try again.');
      console.error('Error creating user:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div className="card" style={{ maxWidth: '400px', width: '100%', margin: '2rem' }}>
        <div className="card-header" style={{ textAlign: 'center' }}>
          <h1 style={{ color: 'var(--primary-color)', marginBottom: '0.5rem' }}>
            🧠 ProfAI
          </h1>
          <div className="card-title">Welcome to Your AI Learning Assistant</div>
          <div className="card-description">
            Let's personalize your learning experience. Enter your name to get started.
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name" className="form-label">
              Your Name
            </label>
            <input
              type="text"
              id="name"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your full name"
              disabled={loading}
            />
          </div>

          {error && (
            <div style={{
              color: 'var(--danger-color)',
              fontSize: '0.9rem',
              marginBottom: '1rem',
              padding: '0.5rem',
              background: '#fee2e2',
              borderRadius: '4px'
            }}>
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? (
              <>
                <span className="pulse">⏳</span>
                Creating your profile...
              </>
            ) : (
              <>
                🚀 Start Learning
              </>
            )}
          </button>
        </form>

        <div style={{ 
          marginTop: '1.5rem', 
          textAlign: 'center', 
          fontSize: '0.85rem',
          color: 'var(--text-secondary)'
        }}>
          ProfAI will generate personalized lessons and assessments based on your learning progress.
        </div>
      </div>
    </div>
  );
};

export { UserSetup };
export default UserSetup;
