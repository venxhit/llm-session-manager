import React, { useState, useEffect } from 'react';

/**
 * Display real session metrics from CLI
 */
const SessionMetrics = ({ sessionId }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch session metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}`);
        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
          setError(null);
        } else {
          setError('Failed to load session metrics');
        }
      } catch (err) {
        setError('Could not connect to backend');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();

    // Refresh metrics every 5 seconds
    const interval = setInterval(fetchMetrics, 5000);

    return () => clearInterval(interval);
  }, [sessionId]);

  if (loading) {
    return (
      <div className="card p-4">
        <div className="text-center text-gray-400">
          Loading session metrics...
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="card p-4">
        <div className="text-center text-gray-400">
          {error || 'No session data available'}
        </div>
      </div>
    );
  }

  const getHealthColor = (score) => {
    if (score >= 70) return 'text-green-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getHealthIcon = (score) => {
    if (score >= 70) return '✅';
    if (score >= 40) return '⚠️';
    return '🔴';
  };

  const tokenPercentage = (metrics.token_count / metrics.token_limit) * 100;
  const getTokenColor = (percentage) => {
    if (percentage < 80) return 'bg-green-500';
    if (percentage < 100) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatDuration = (start) => {
    const now = new Date();
    const startDate = new Date(start);
    const diff = Math.floor((now - startDate) / 1000); // seconds

    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  return (
    <div className="card p-4 mb-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">
          Session Metrics
        </h2>
        <span className="text-xs text-gray-400">
          Live • Updates every 5s
        </span>
      </div>

      {/* Session Info */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-xs text-gray-400">Session ID</div>
          <div className="text-sm font-mono text-white">{metrics.id}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Type</div>
          <div className="text-sm text-white capitalize">{metrics.type.replace('_', ' ')}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Duration</div>
          <div className="text-sm text-white">{formatDuration(metrics.start_time)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Status</div>
          <div className="text-sm text-white capitalize">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span>
            {metrics.status}
          </div>
        </div>
      </div>

      {/* Token Usage */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs text-gray-400">Token Usage</div>
          <div className="text-sm text-white">
            {metrics.token_count.toLocaleString()} / {metrics.token_limit.toLocaleString()}
            <span className="text-xs ml-2">
              ({tokenPercentage.toFixed(0)}%)
            </span>
          </div>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${getTokenColor(tokenPercentage)}`}
            style={{ width: `${Math.min(tokenPercentage, 100)}%` }}
          ></div>
        </div>
        {tokenPercentage > 100 && (
          <div className="text-xs text-red-400 mt-1">
            ⚠️ Token limit exceeded!
          </div>
        )}
      </div>

      {/* Health Score */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-400">Health Score</div>
          <div className={`text-2xl font-bold ${getHealthColor(metrics.health_score)}`}>
            {getHealthIcon(metrics.health_score)} {metrics.health_score.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-gray-700 rounded p-2">
          <div className="text-xs text-gray-400">Messages</div>
          <div className="text-lg font-semibold text-white">{metrics.message_count}</div>
        </div>
        <div className="bg-gray-700 rounded p-2">
          <div className="text-xs text-gray-400">Files</div>
          <div className="text-lg font-semibold text-white">{metrics.file_count}</div>
        </div>
        <div className="bg-gray-700 rounded p-2">
          <div className="text-xs text-gray-400">Errors</div>
          <div className="text-lg font-semibold text-white">{metrics.error_count}</div>
        </div>
      </div>

      {/* Working Directory */}
      {metrics.working_directory && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Working Directory</div>
          <div className="text-xs font-mono text-gray-300 truncate">
            {metrics.working_directory}
          </div>
        </div>
      )}

      {/* Project Name */}
      {metrics.project_name && (
        <div className="mt-2">
          <div className="text-xs text-gray-400 mb-1">Project</div>
          <div className="text-sm text-white">{metrics.project_name}</div>
        </div>
      )}

      {/* Tags */}
      {metrics.tags && metrics.tags.length > 0 && (
        <div className="mt-2">
          <div className="text-xs text-gray-400 mb-1">Tags</div>
          <div className="flex flex-wrap gap-1">
            {metrics.tags.map((tag, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-blue-900 text-blue-300 rounded text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionMetrics;
