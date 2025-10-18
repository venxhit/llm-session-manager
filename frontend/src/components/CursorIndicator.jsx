import React from 'react';

/**
 * Shows other users' cursor positions in the code editor
 */
const CursorIndicator = ({ participant, onClick }) => {
  const getUserColor = (userId) => {
    // Generate consistent color from user ID
    const colors = [
      'from-blue-500 to-blue-600',
      'from-green-500 to-green-600',
      'from-purple-500 to-purple-600',
      'from-pink-500 to-pink-600',
      'from-yellow-500 to-yellow-600',
      'from-red-500 to-red-600',
      'from-indigo-500 to-indigo-600',
      'from-teal-500 to-teal-600',
    ];

    const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  if (!participant.cursor) return null;

  const colorClass = getUserColor(participant.user_id);

  return (
    <div
      onClick={onClick}
      className="cursor-pointer hover:scale-105 transition-transform"
      title={`${participant.username} at ${participant.cursor.file}:${participant.cursor.line}:${participant.cursor.column}`}
    >
      <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg border border-gray-600">
        {/* User avatar */}
        <div className={`w-6 h-6 rounded-full bg-gradient-to-br ${colorClass} flex items-center justify-center text-white text-xs font-semibold`}>
          {participant.username?.charAt(0).toUpperCase()}
        </div>

        {/* Cursor info */}
        <div className="flex flex-col text-xs">
          <span className="text-white font-medium">
            {participant.username}
          </span>
          <span className="text-gray-400 font-mono">
            {participant.cursor.file?.split('/').pop()}:{participant.cursor.line}:{participant.cursor.column}
          </span>
        </div>

        {/* Animated cursor icon */}
        <div className="animate-pulse">
          📍
        </div>
      </div>
    </div>
  );
};

/**
 * Container for showing all active cursors
 */
export const CursorIndicatorList = ({ participants, currentUserId, onCursorClick }) => {
  const activeCursors = participants.filter(
    p => p.user_id !== currentUserId && p.cursor
  );

  if (activeCursors.length === 0) return null;

  return (
    <div className="card p-3">
      <div className="text-sm font-semibold text-white mb-2">
        Active Cursors ({activeCursors.length})
      </div>
      <div className="space-y-2">
        {activeCursors.map((participant) => (
          <CursorIndicator
            key={participant.user_id}
            participant={participant}
            onClick={() => onCursorClick && onCursorClick(participant)}
          />
        ))}
      </div>
    </div>
  );
};

export default CursorIndicator;
