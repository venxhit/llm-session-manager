import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Home page with session creation/joining
 */
const Home = () => {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState('');

  const handleCreateSession = () => {
    const newSessionId = 'session_' + Date.now();
    navigate(`/session/${newSessionId}`);
  };

  const handleJoinSession = (e) => {
    e.preventDefault();
    if (sessionId.trim()) {
      navigate(`/session/${sessionId}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2">
            LLM Session Manager
          </h1>
          <p className="text-lg text-gray-400">
            Real-Time Collaborative Sessions
          </p>
        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Create Session Card */}
          <div className="card p-6">
            <div className="mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center text-2xl mb-3">
                ✨
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Create Session
              </h2>
              <p className="text-sm text-gray-400">
                Start a new collaborative session and invite others to join
              </p>
            </div>
            <button
              onClick={handleCreateSession}
              className="btn-primary w-full"
            >
              Create New Session
            </button>
          </div>

          {/* Join Session Card */}
          <div className="card p-6">
            <div className="mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-teal-500 rounded-lg flex items-center justify-center text-2xl mb-3">
                🚀
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Join Session
              </h2>
              <p className="text-sm text-gray-400">
                Enter a session ID to join an existing collaboration
              </p>
            </div>
            <form onSubmit={handleJoinSession} className="space-y-3">
              <input
                type="text"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                placeholder="Enter session ID"
                className="input-field"
                required
              />
              <button
                type="submit"
                className="btn-primary w-full"
              >
                Join Session
              </button>
            </form>
          </div>
        </div>

        {/* Features */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Features
          </h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl mb-2">💬</div>
              <div className="text-sm font-medium text-white">Real-time Chat</div>
              <div className="text-xs text-gray-400">Instant messaging</div>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">📍</div>
              <div className="text-sm font-medium text-white">Cursor Tracking</div>
              <div className="text-xs text-gray-400">See where others are</div>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">👥</div>
              <div className="text-sm font-medium text-white">Presence</div>
              <div className="text-xs text-gray-400">Online status</div>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">💭</div>
              <div className="text-sm font-medium text-white">Code Comments</div>
              <div className="text-xs text-gray-400">Annotate code</div>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🎭</div>
              <div className="text-sm font-medium text-white">Roles</div>
              <div className="text-xs text-gray-400">Host/Editor/Viewer</div>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">⚡</div>
              <div className="text-sm font-medium text-white">Real-time</div>
              <div className="text-xs text-gray-400">WebSocket powered</div>
            </div>
          </div>
        </div>

        {/* Quick Start */}
        <div className="card p-6 bg-blue-900 bg-opacity-20 border-blue-700">
          <h3 className="text-lg font-semibold text-white mb-2">
            Quick Start Guide
          </h3>
          <ol className="text-sm text-gray-300 space-y-2 list-decimal list-inside">
            <li>Create or join a session</li>
            <li>Enter your username and authentication token</li>
            <li>Start collaborating with your team in real-time</li>
            <li>Use chat for communication and code comments for annotations</li>
          </ol>
          <div className="mt-4 p-3 bg-gray-800 rounded text-xs font-mono">
            <div className="text-gray-400 mb-1">Backend must be running:</div>
            <div className="text-green-400">uvicorn app.main:app --reload</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
