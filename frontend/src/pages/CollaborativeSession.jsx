import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';
import PresenceBar from '../components/PresenceBar';
import ChatPanel from '../components/ChatPanel';
import { CursorIndicatorList } from '../components/CursorIndicator';

/**
 * Main collaborative session page
 */
const CollaborativeSession = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  // User state (in production, this would come from auth context)
  const [currentUser, setCurrentUser] = useState(() => {
    const stored = localStorage.getItem('currentUser');
    return stored ? JSON.parse(stored) : null;
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem('authToken') || '';
  });

  // Messages state
  const [messages, setMessages] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // WebSocket message handler
  const handleMessage = useCallback((data) => {
    console.log('Received message:', data);

    switch (data.type) {
      case 'connected':
        addNotification(`Connected to session ${sessionId}`, 'success');
        break;

      case 'user_joined':
        addNotification(`${data.user.username} joined the session`, 'info');
        break;

      case 'user_left':
        addNotification(`${data.username} left the session`, 'info');
        break;

      case 'chat_message':
      case 'code_comment':
        setMessages(prev => [...prev, {
          id: data.message_id || Date.now(),
          user_id: data.user_id,
          username: data.username,
          content: data.content,
          message_type: data.type === 'code_comment' ? 'code_comment' : 'chat',
          metadata: data.metadata || {},
          created_at: data.timestamp || new Date().toISOString(),
          updated_at: data.timestamp || new Date().toISOString(),
        }]);
        break;

      case 'reaction_update':
        setMessages(prev => prev.map(msg =>
          msg.id === data.message_id
            ? { ...msg, metadata: { ...msg.metadata, reactions: data.reactions } }
            : msg
        ));
        break;

      case 'error':
        addNotification(data.message || 'An error occurred', 'error');
        break;

      default:
        console.log('Unhandled message type:', data.type);
    }
  }, [sessionId]);

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  // WebSocket connection
  const {
    isConnected,
    participants,
    sendChatMessage,
    sendCodeComment,
    sendReaction,
    sendCursorUpdate,
    sendPresenceUpdate,
    disconnect,
  } = useWebSocket(sessionId, token, {
    onMessage: handleMessage,
    onConnect: () => addNotification('Connected to session', 'success'),
    onDisconnect: () => addNotification('Disconnected from session', 'warning'),
    onError: (error) => addNotification('Connection error', 'error'),
  });

  // Handle cursor updates (simulation for demo)
  const handleCursorMove = useCallback((file, line, column) => {
    sendCursorUpdate(file, line, column);
  }, [sendCursorUpdate]);

  // Handle cursor click (navigate to that location)
  const handleCursorClick = useCallback((participant) => {
    if (participant.cursor) {
      addNotification(
        `Jumping to ${participant.username}'s cursor at ${participant.cursor.file}:${participant.cursor.line}`,
        'info'
      );
      // In a real app, this would scroll the editor to that location
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  // Login form if not authenticated
  if (!currentUser || !token) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="card p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-white mb-6">Join Session</h1>
          <form onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const username = formData.get('username');
            const token = formData.get('token');

            if (username && token) {
              const user = {
                user_id: 'user_' + Date.now(),
                username,
              };
              setCurrentUser(user);
              setToken(token);
              localStorage.setItem('currentUser', JSON.stringify(user));
              localStorage.setItem('authToken', token);
            }
          }}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  placeholder="Enter your username"
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Auth Token
                </label>
                <input
                  type="text"
                  name="token"
                  placeholder="Enter your JWT token"
                  className="input-field"
                  required
                />
                <p className="text-xs text-gray-400 mt-1">
                  Get your token from the backend authentication endpoint
                </p>
              </div>
              <button type="submit" className="btn-primary w-full">
                Join Session
              </button>
            </div>
          </form>
          <div className="mt-4 text-center">
            <button
              onClick={() => navigate('/')}
              className="text-sm text-primary-400 hover:text-primary-300"
            >
              ← Back to home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-4">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">
              Collaborative Session
            </h1>
            <p className="text-sm text-gray-400">
              Session ID: {sessionId}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                localStorage.removeItem('currentUser');
                localStorage.removeItem('authToken');
                setCurrentUser(null);
                setToken('');
                disconnect();
              }}
              className="btn-secondary"
            >
              Leave Session
            </button>
          </div>
        </div>
      </div>

      {/* Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map(notification => (
          <div
            key={notification.id}
            className={`card p-3 shadow-lg animate-slide-in ${
              notification.type === 'error'
                ? 'bg-red-900 border-red-700'
                : notification.type === 'success'
                ? 'bg-green-900 border-green-700'
                : notification.type === 'warning'
                ? 'bg-yellow-900 border-yellow-700'
                : 'bg-blue-900 border-blue-700'
            }`}
          >
            <p className="text-sm text-white">{notification.message}</p>
          </div>
        ))}
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto">
        {/* Presence bar */}
        <PresenceBar
          participants={participants}
          currentUserId={currentUser.user_id}
        />

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left sidebar - Cursor indicators */}
          <div className="lg:col-span-1 space-y-4">
            <CursorIndicatorList
              participants={participants}
              currentUserId={currentUser.user_id}
              onCursorClick={handleCursorClick}
            />

            {/* Demo cursor simulator */}
            <div className="card p-4">
              <h3 className="text-sm font-semibold text-white mb-3">
                Cursor Simulator (Demo)
              </h3>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  const file = formData.get('file');
                  const line = parseInt(formData.get('line'));
                  const column = parseInt(formData.get('column'));
                  handleCursorMove(file, line, column);
                  e.target.reset();
                }}
                className="space-y-2"
              >
                <input
                  type="text"
                  name="file"
                  placeholder="File path"
                  className="input-field text-sm"
                  required
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    name="line"
                    placeholder="Line"
                    className="input-field text-sm"
                    required
                  />
                  <input
                    type="number"
                    name="column"
                    placeholder="Column"
                    className="input-field text-sm"
                    required
                  />
                </div>
                <button type="submit" className="btn-primary w-full text-sm">
                  Update Cursor
                </button>
              </form>
            </div>

            {/* Status controls */}
            <div className="card p-4">
              <h3 className="text-sm font-semibold text-white mb-3">
                Presence Status
              </h3>
              <div className="space-y-2">
                {['active', 'idle', 'away'].map(status => (
                  <button
                    key={status}
                    onClick={() => sendPresenceUpdate(status)}
                    className="btn-secondary w-full text-sm capitalize"
                  >
                    Set {status}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right side - Chat */}
          <div className="lg:col-span-2 h-[600px]">
            <ChatPanel
              messages={messages}
              currentUserId={currentUser.user_id}
              onSendMessage={sendChatMessage}
              onSendCodeComment={sendCodeComment}
              onReaction={sendReaction}
              isConnected={isConnected}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CollaborativeSession;
