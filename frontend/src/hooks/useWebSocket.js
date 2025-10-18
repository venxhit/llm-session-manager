import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Custom hook for managing WebSocket connections with auto-reconnect
 *
 * @param {string} sessionId - The session ID to connect to
 * @param {string} token - JWT authentication token
 * @param {Object} options - Configuration options
 * @returns {Object} WebSocket state and methods
 */
export const useWebSocket = (sessionId, token, options = {}) => {
  const {
    onMessage = () => {},
    onConnect = () => {},
    onDisconnect = () => {},
    onError = () => {},
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [participants, setParticipants] = useState([]);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const messageQueueRef = useRef([]);

  // Send message to WebSocket
  const sendMessage = useCallback((type, data = {}) => {
    const message = {
      type,
      ...data,
    };

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // Queue message if not connected
      messageQueueRef.current.push(message);
    }
  }, []);

  // Process queued messages
  const processQueue = useCallback(() => {
    while (messageQueueRef.current.length > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
      const message = messageQueueRef.current.shift();
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!sessionId || !token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/session/${sessionId}?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setReconnectAttempt(0);
        processQueue();
        onConnect();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Handle connected message with participants
          if (data.type === 'connected') {
            setParticipants(data.users || []);
          }

          // Handle user joined
          if (data.type === 'user_joined') {
            setParticipants(prev => [...prev, data.user]);
          }

          // Handle user left
          if (data.type === 'user_left') {
            setParticipants(prev => prev.filter(u => u.user_id !== data.user_id));
          }

          onMessage(data);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError(error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        onDisconnect();

        // Attempt to reconnect
        if (reconnectAttempt < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Reconnecting... (attempt ${reconnectAttempt + 1}/${maxReconnectAttempts})`);
            setReconnectAttempt(prev => prev + 1);
            connect();
          }, reconnectInterval);
        }
      };
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      onError(err);
    }
  }, [sessionId, token, reconnectAttempt, maxReconnectAttempts, reconnectInterval, onConnect, onDisconnect, onError, onMessage, processQueue]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setParticipants([]);
  }, []);

  // Send chat message
  const sendChatMessage = useCallback((content) => {
    sendMessage('chat_message', { content });
  }, [sendMessage]);

  // Send cursor update
  const sendCursorUpdate = useCallback((file, line, column) => {
    sendMessage('cursor_update', {
      data: { file, line, column }
    });
  }, [sendMessage]);

  // Send viewport update
  const sendViewportUpdate = useCallback((file, start_line, end_line) => {
    sendMessage('viewport_update', {
      data: { file, start_line, end_line }
    });
  }, [sendMessage]);

  // Send presence update
  const sendPresenceUpdate = useCallback((status) => {
    sendMessage('presence_update', {
      data: { status }
    });
  }, [sendMessage]);

  // Send code comment
  const sendCodeComment = useCallback((file, line, content, code_snippet = null) => {
    sendMessage('code_comment', {
      data: { file, line, content, code_snippet }
    });
  }, [sendMessage]);

  // Send reaction
  const sendReaction = useCallback((message_id, emoji) => {
    sendMessage('reaction', {
      data: { message_id, emoji }
    });
  }, [sendMessage]);

  // Connect on mount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [sessionId, token]);

  return {
    isConnected,
    participants,
    reconnectAttempt,
    sendMessage,
    sendChatMessage,
    sendCursorUpdate,
    sendViewportUpdate,
    sendPresenceUpdate,
    sendCodeComment,
    sendReaction,
    disconnect,
  };
};
