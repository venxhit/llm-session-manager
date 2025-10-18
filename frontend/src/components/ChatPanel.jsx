import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

/**
 * Chat panel component for real-time messaging
 */
const ChatPanel = ({
  messages,
  currentUserId,
  onSendMessage,
  onSendCodeComment,
  onReaction,
  isConnected
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isCodeCommentMode, setIsCodeCommentMode] = useState(false);
  const [codeCommentData, setCodeCommentData] = useState({
    file: '',
    line: '',
    code_snippet: '',
  });
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    if (isCodeCommentMode) {
      // Send code comment
      if (!codeCommentData.file || !codeCommentData.line) {
        alert('Please provide file and line number for code comment');
        return;
      }

      onSendCodeComment(
        codeCommentData.file,
        parseInt(codeCommentData.line),
        inputValue,
        codeCommentData.code_snippet || null
      );

      // Reset code comment mode
      setIsCodeCommentMode(false);
      setCodeCommentData({ file: '', line: '', code_snippet: '' });
    } else {
      // Send regular chat message
      onSendMessage(inputValue);
    }

    setInputValue('');
    inputRef.current?.focus();
  };

  const toggleCodeCommentMode = () => {
    setIsCodeCommentMode(!isCodeCommentMode);
    if (!isCodeCommentMode) {
      inputRef.current?.focus();
    }
  };

  return (
    <div className="card flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Chat
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleCodeCommentMode}
              className={`px-3 py-1 rounded text-xs ${
                isCodeCommentMode
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
              title="Toggle code comment mode"
            >
              {isCodeCommentMode ? '💬 Code Comment' : '💬 Chat'}
            </button>
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`}
              title={isConnected ? 'Connected' : 'Disconnected'}
            />
          </div>
        </div>
      </div>

      {/* Code comment form */}
      {isCodeCommentMode && (
        <div className="p-3 bg-yellow-900 bg-opacity-20 border-b border-yellow-700">
          <div className="text-xs text-yellow-300 mb-2">
            📝 Code Comment Mode
          </div>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="text"
              placeholder="File path"
              value={codeCommentData.file}
              onChange={(e) => setCodeCommentData(prev => ({ ...prev, file: e.target.value }))}
              className="input-field text-sm py-1"
            />
            <input
              type="number"
              placeholder="Line #"
              value={codeCommentData.line}
              onChange={(e) => setCodeCommentData(prev => ({ ...prev, line: e.target.value }))}
              className="input-field text-sm py-1"
            />
          </div>
          <textarea
            placeholder="Code snippet (optional)"
            value={codeCommentData.code_snippet}
            onChange={(e) => setCodeCommentData(prev => ({ ...prev, code_snippet: e.target.value }))}
            className="input-field text-sm py-1 mt-2 font-mono"
            rows="2"
          />
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            No messages yet. Start the conversation!
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            currentUserId={currentUserId}
            onReaction={onReaction}
          />
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              isCodeCommentMode
                ? "Write your code comment..."
                : "Type a message..."
            }
            className="input-field"
            disabled={!isConnected}
          />
          <button
            type="submit"
            disabled={!isConnected || !inputValue.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
        <div className="text-xs text-gray-400 mt-2">
          {isConnected
            ? '✓ Connected • Press Enter to send'
            : '✗ Disconnected • Reconnecting...'}
        </div>
      </form>
    </div>
  );
};

export default ChatPanel;
