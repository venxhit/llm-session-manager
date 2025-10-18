import React from 'react';

/**
 * Individual message bubble component
 */
const MessageBubble = ({ message, currentUserId, onReaction }) => {
  const isCurrentUser = message.user_id === currentUserId;
  const isCodeComment = message.message_type === 'code_comment';

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getMessageTypeIcon = (type) => {
    switch (type) {
      case 'code_comment':
        return '💬';
      case 'system':
        return '🔔';
      default:
        return '';
    }
  };

  return (
    <div
      className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'} mb-3`}
    >
      <div
        className={`max-w-[70%] rounded-lg p-3 ${
          isCurrentUser
            ? 'bg-primary-600 text-white'
            : isCodeComment
            ? 'bg-yellow-900 border border-yellow-700'
            : 'bg-gray-700 text-white'
        }`}
      >
        {/* Header */}
        <div className="flex items-center gap-2 mb-1">
          {!isCurrentUser && (
            <span className="text-xs font-semibold">
              {message.username}
            </span>
          )}
          {isCodeComment && (
            <span className="text-xs" title="Code comment">
              {getMessageTypeIcon(message.message_type)}
            </span>
          )}
          <span className="text-xs opacity-70">
            {formatTime(message.created_at)}
          </span>
        </div>

        {/* Code comment metadata */}
        {isCodeComment && message.metadata && (
          <div className="text-xs mb-2 p-2 bg-black bg-opacity-30 rounded">
            <div className="font-mono">
              📁 {message.metadata.file}:{message.metadata.line}
            </div>
            {message.metadata.code_snippet && (
              <pre className="mt-1 text-xs overflow-x-auto">
                <code>{message.metadata.code_snippet}</code>
              </pre>
            )}
          </div>
        )}

        {/* Message content */}
        <div className="text-sm whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* Reactions */}
        {message.metadata?.reactions && Object.keys(message.metadata.reactions).length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {Object.entries(message.metadata.reactions).map(([emoji, users]) => (
              <button
                key={emoji}
                onClick={() => onReaction && onReaction(message.id, emoji)}
                className="px-2 py-1 bg-gray-800 rounded text-xs hover:bg-gray-600 transition-colors"
                title={users.join(', ')}
              >
                {emoji} {users.length}
              </button>
            ))}
          </div>
        )}

        {/* Reply indicator */}
        {message.parent_id && (
          <div className="text-xs opacity-70 mt-1">
            ↩️ Reply
          </div>
        )}

        {/* Edited indicator */}
        {message.updated_at && message.updated_at !== message.created_at && (
          <div className="text-xs opacity-50 mt-1">
            (edited)
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
