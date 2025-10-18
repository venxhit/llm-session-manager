import React from 'react';

/**
 * Shows all active participants in the session
 */
const PresenceBar = ({ participants, currentUserId }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'idle':
        return 'bg-yellow-500';
      case 'away':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'host':
        return 'text-purple-400';
      case 'editor':
        return 'text-blue-400';
      case 'viewer':
        return 'text-gray-400';
      default:
        return 'text-gray-400';
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'host':
        return '👑';
      case 'editor':
        return '✏️';
      case 'viewer':
        return '👁️';
      default:
        return '';
    }
  };

  return (
    <div className="card p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-white">
          Active Participants ({participants.length})
        </h2>
      </div>

      <div className="flex flex-wrap gap-3">
        {participants.map((participant) => {
          const isCurrentUser = participant.user_id === currentUserId;

          return (
            <div
              key={participant.user_id}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                isCurrentUser
                  ? 'bg-primary-900 border border-primary-600'
                  : 'bg-gray-700'
              }`}
            >
              {/* Status indicator */}
              <div className="relative">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                  {participant.username?.charAt(0).toUpperCase()}
                </div>
                <div
                  className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-gray-800 ${getStatusColor(
                    participant.status
                  )}`}
                  title={participant.status}
                />
              </div>

              {/* User info */}
              <div className="flex flex-col">
                <div className="flex items-center gap-1">
                  <span className="text-sm font-medium text-white">
                    {participant.username}
                    {isCurrentUser && ' (You)'}
                  </span>
                  <span className="text-xs" title={participant.role}>
                    {getRoleBadge(participant.role)}
                  </span>
                </div>
                <span className={`text-xs ${getRoleColor(participant.role)}`}>
                  {participant.role}
                </span>
              </div>

              {/* Cursor position indicator */}
              {participant.cursor && (
                <div className="ml-2 text-xs text-gray-400">
                  <div title={`${participant.cursor.file}:${participant.cursor.line}`}>
                    📍 {participant.cursor.file?.split('/').pop()}:{participant.cursor.line}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {participants.length === 0 && (
        <div className="text-center text-gray-400 py-4">
          No participants yet
        </div>
      )}
    </div>
  );
};

export default PresenceBar;
