# Real-Time Collaboration Architecture

## Overview

Enable multiple developers to work together in the same AI coding session with real-time context sharing, presence awareness, chat, and collaborative editing indicators.

## Vision

**Current State:** One developer per session, isolated work
**Future State:** Google Docs-style collaboration for AI coding sessions

**Use Cases:**
- 🎯 Pair programming with AI assistant
- 🎯 Onboarding junior developers (watch & learn)
- 🎯 Code reviews in real-time
- 🎯 Team debugging sessions
- 🎯 Knowledge sharing during implementation

## Architecture

### Tech Stack

**Backend:**
- **WebSocket** - Real-time bidirectional communication
- **Redis (optional)** - Pub/sub for multi-server scaling
- **Operational Transform (OT)** or **CRDTs** - Conflict resolution
- **FastAPI WebSocket** - WebSocket endpoint

**Frontend:**
- **WebSocket Client** - Browser WebSocket API
- **Y.js** - CRDT library for collaborative editing
- **Presence API** - Track active users
- **Rich Text Editor** - Collaborative commenting

**Infrastructure:**
- **Redis Pub/Sub** - Message broadcasting (multi-server)
- **Nginx** - WebSocket proxy (production)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser Clients                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  User A  │  │  User B  │  │  User C  │  │  User D  │   │
│  │  (Host)  │  │ (Editor) │  │ (Viewer) │  │ (Viewer) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
        │              │              │              │
        └──────────────┴──────────────┴──────────────┘
                         │
                    WebSocket
                         │
┌─────────────────────────────────────────────────────────────┐
│              Collaboration Server (FastAPI)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         WebSocket Connection Manager               │    │
│  │  - Track active connections                        │    │
│  │  - Maintain session→users mapping                  │    │
│  │  - Handle join/leave events                        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Presence Management                        │    │
│  │  - Who's online in each session                    │    │
│  │  - User cursors and viewport positions             │    │
│  │  - Activity status (active, idle, typing)          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Context Synchronization                    │    │
│  │  - Broadcast session updates                       │    │
│  │  - Token count changes                             │    │
│  │  - File modifications                              │    │
│  │  - Health score updates                            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Chat & Comments                            │    │
│  │  - In-session chat messages                        │    │
│  │  - Code comments                                   │    │
│  │  - @mentions                                       │    │
│  │  - Reactions                                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Event Broadcasting                         │    │
│  │  - Message routing                                 │    │
│  │  - Permission checks                               │    │
│  │  - Event filtering by role                         │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                         │
                         │
┌─────────────────────────────────────────────────────────────┐
│                  Redis Pub/Sub (Optional)                    │
│  - Multi-server message distribution                         │
│  - Session state persistence                                 │
│  - Presence synchronization                                  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite/Postgres)                │
│  - Session data                                              │
│  - Chat history                                              │
│  - User permissions                                          │
│  - Activity logs                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Models

### Extended Database Schema

#### `session_participants`
```sql
CREATE TABLE session_participants (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'host', 'editor', 'viewer'
    joined_at TIMESTAMP NOT NULL,
    left_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE(session_id, user_id)
);

CREATE INDEX idx_session_participants ON session_participants(session_id, is_active);
```

#### `session_messages`
```sql
CREATE TABLE session_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    message_type TEXT NOT NULL,  -- 'chat', 'comment', 'system'
    content TEXT NOT NULL,
    metadata JSON,  -- {mentions: [], reactions: {}, code_ref: {...}}
    parent_id TEXT,  -- For threaded comments
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES session_messages (id) ON DELETE CASCADE
);

CREATE INDEX idx_session_messages ON session_messages(session_id, created_at DESC);
```

#### `session_events`
```sql
CREATE TABLE session_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_id TEXT,
    event_type TEXT NOT NULL,  -- 'join', 'leave', 'edit', 'cursor_move', etc.
    event_data JSON NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX idx_session_events ON session_events(session_id, timestamp DESC);
```

#### `session_presence` (in-memory or Redis)
```python
# Structure (not SQL - stored in memory/Redis)
{
    "session_id": {
        "user_id_1": {
            "username": "alice",
            "role": "host",
            "status": "active",  # active, idle, away
            "cursor": {"file": "main.py", "line": 42, "col": 10},
            "viewport": {"file": "main.py", "start": 30, "end": 60},
            "last_activity": "2025-10-17T10:30:00Z"
        },
        "user_id_2": {...}
    }
}
```

### WebSocket Message Protocol

#### Client → Server Messages

**Join Session:**
```json
{
    "type": "join_session",
    "session_id": "abc123",
    "auth_token": "jwt-token-here"
}
```

**Update Cursor:**
```json
{
    "type": "cursor_update",
    "session_id": "abc123",
    "data": {
        "file": "src/main.py",
        "line": 42,
        "column": 10
    }
}
```

**Send Chat Message:**
```json
{
    "type": "chat_message",
    "session_id": "abc123",
    "content": "Hey @alice, check line 42",
    "mentions": ["user_id_alice"]
}
```

**Add Comment:**
```json
{
    "type": "add_comment",
    "session_id": "abc123",
    "data": {
        "file": "src/main.py",
        "line": 42,
        "content": "This could be optimized",
        "code_snippet": "def foo():"
    }
}
```

**Update Presence:**
```json
{
    "type": "presence_update",
    "session_id": "abc123",
    "status": "active",  // or "idle", "away"
    "viewport": {
        "file": "src/main.py",
        "start_line": 30,
        "end_line": 60
    }
}
```

#### Server → Client Messages

**User Joined:**
```json
{
    "type": "user_joined",
    "session_id": "abc123",
    "user": {
        "id": "user123",
        "username": "alice",
        "avatar": "https://...",
        "role": "editor"
    },
    "timestamp": "2025-10-17T10:30:00Z"
}
```

**User Left:**
```json
{
    "type": "user_left",
    "session_id": "abc123",
    "user_id": "user123",
    "username": "alice",
    "timestamp": "2025-10-17T10:35:00Z"
}
```

**Session Update:**
```json
{
    "type": "session_update",
    "session_id": "abc123",
    "changes": {
        "token_count": 150000,
        "health_score": 75.0,
        "status": "active"
    },
    "updated_by": "user123",
    "timestamp": "2025-10-17T10:30:05Z"
}
```

**Presence Update:**
```json
{
    "type": "presence_update",
    "session_id": "abc123",
    "user_id": "user123",
    "presence": {
        "status": "active",
        "cursor": {"file": "main.py", "line": 42, "col": 10},
        "viewport": {"file": "main.py", "start": 30, "end": 60}
    }
}
```

**Chat Message:**
```json
{
    "type": "chat_message",
    "session_id": "abc123",
    "message": {
        "id": "msg123",
        "user_id": "user123",
        "username": "alice",
        "content": "Hey @bob, check line 42",
        "mentions": ["user_id_bob"],
        "timestamp": "2025-10-17T10:30:10Z"
    }
}
```

**Code Comment:**
```json
{
    "type": "code_comment",
    "session_id": "abc123",
    "comment": {
        "id": "comment123",
        "user_id": "user123",
        "username": "alice",
        "file": "src/main.py",
        "line": 42,
        "content": "This could be optimized",
        "code_snippet": "def foo():",
        "timestamp": "2025-10-17T10:30:15Z"
    }
}
```

**Error:**
```json
{
    "type": "error",
    "error_code": "PERMISSION_DENIED",
    "message": "You don't have permission to edit this session",
    "timestamp": "2025-10-17T10:30:20Z"
}
```

## Permission System

### Roles

**Host:**
- Full control over session
- Can invite/remove participants
- Can promote/demote roles
- Can end session for everyone

**Editor:**
- Can view session data
- Can send chat messages
- Can add comments
- Can see other users' cursors
- Cannot modify session settings
- Cannot remove participants

**Viewer:**
- Read-only access
- Can see session data
- Can see chat (cannot send)
- Can see other users' presence
- Cannot interact

### Permission Matrix

| Action | Host | Editor | Viewer |
|--------|------|--------|--------|
| View session | ✅ | ✅ | ✅ |
| See presence | ✅ | ✅ | ✅ |
| Send chat | ✅ | ✅ | ❌ |
| Add comments | ✅ | ✅ | ❌ |
| Edit session | ✅ | ✅ | ❌ |
| Invite users | ✅ | ❌ | ❌ |
| Remove users | ✅ | ❌ | ❌ |
| End session | ✅ | ❌ | ❌ |

## Implementation Components

### 1. WebSocket Connection Manager

```python
# backend/app/collaboration/connection_manager.py

from typing import Dict, Set
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # session_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # session_id -> user_id -> connection info
        self.session_users: Dict[str, Dict[str, dict]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str, role: str):
        """Connect user to session."""
        await websocket.accept()

        # Add to connections
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

        # Track user info
        if session_id not in self.session_users:
            self.session_users[session_id] = {}

        self.session_users[session_id][user_id] = {
            "websocket": websocket,
            "role": role,
            "joined_at": datetime.utcnow()
        }

    async def disconnect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Disconnect user from session."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)

        if session_id in self.session_users:
            self.session_users[session_id].pop(user_id, None)

    async def broadcast_to_session(self, session_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in session."""
        if session_id not in self.active_connections:
            return

        disconnected = set()
        for user_id, info in self.session_users.get(session_id, {}).items():
            if exclude_user and user_id == exclude_user:
                continue

            websocket = info["websocket"]
            try:
                await websocket.send_json(message)
            except:
                disconnected.add(websocket)

        # Clean up disconnected
        for ws in disconnected:
            self.active_connections[session_id].discard(ws)

    async def send_to_user(self, session_id: str, user_id: str, message: dict):
        """Send message to specific user."""
        if session_id in self.session_users:
            if user_id in self.session_users[session_id]:
                websocket = self.session_users[session_id][user_id]["websocket"]
                try:
                    await websocket.send_json(message)
                except:
                    pass

    def get_session_users(self, session_id: str) -> list:
        """Get list of users in session."""
        return list(self.session_users.get(session_id, {}).keys())

    def get_user_count(self, session_id: str) -> int:
        """Get number of users in session."""
        return len(self.session_users.get(session_id, {}))
```

### 2. Presence Manager

```python
# backend/app/collaboration/presence.py

from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio

class PresenceManager:
    def __init__(self):
        # session_id -> user_id -> presence data
        self.presence: Dict[str, Dict[str, dict]] = {}

        # Start cleanup task
        asyncio.create_task(self._cleanup_stale_presence())

    def update_presence(self, session_id: str, user_id: str, data: dict):
        """Update user presence in session."""
        if session_id not in self.presence:
            self.presence[session_id] = {}

        self.presence[session_id][user_id] = {
            **data,
            "last_update": datetime.utcnow()
        }

    def get_presence(self, session_id: str) -> dict:
        """Get all presence data for session."""
        return self.presence.get(session_id, {})

    def remove_user(self, session_id: str, user_id: str):
        """Remove user from presence."""
        if session_id in self.presence:
            self.presence[session_id].pop(user_id, None)

    async def _cleanup_stale_presence(self):
        """Remove stale presence data (> 5 minutes inactive)."""
        while True:
            await asyncio.sleep(60)  # Check every minute

            now = datetime.utcnow()
            for session_id in list(self.presence.keys()):
                for user_id in list(self.presence[session_id].keys()):
                    last_update = self.presence[session_id][user_id].get("last_update")
                    if last_update and (now - last_update) > timedelta(minutes=5):
                        self.remove_user(session_id, user_id)
```

### 3. Chat Manager

```python
# backend/app/collaboration/chat.py

from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import SessionMessage, User
from datetime import datetime

class ChatManager:
    def __init__(self, db: Session):
        self.db = db

    def send_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        message_type: str = "chat",
        metadata: Optional[dict] = None,
        parent_id: Optional[str] = None
    ) -> SessionMessage:
        """Create and save chat message."""
        message = SessionMessage(
            session_id=session_id,
            user_id=user_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            parent_id=parent_id,
            created_at=datetime.utcnow()
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_messages(
        self,
        session_id: str,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[SessionMessage]:
        """Get chat messages for session."""
        query = self.db.query(SessionMessage).filter(
            SessionMessage.session_id == session_id,
            SessionMessage.deleted_at.is_(None)
        )

        if before:
            query = query.filter(SessionMessage.created_at < before)

        return query.order_by(
            SessionMessage.created_at.desc()
        ).limit(limit).all()

    def delete_message(self, message_id: str, user_id: str) -> bool:
        """Soft delete message (only by author)."""
        message = self.db.query(SessionMessage).filter(
            SessionMessage.id == message_id,
            SessionMessage.user_id == user_id
        ).first()

        if message:
            message.deleted_at = datetime.utcnow()
            self.db.commit()
            return True

        return False

    def add_reaction(self, message_id: str, user_id: str, emoji: str):
        """Add reaction to message."""
        message = self.db.query(SessionMessage).filter(
            SessionMessage.id == message_id
        ).first()

        if message:
            metadata = message.metadata or {}
            reactions = metadata.get("reactions", {})

            if emoji not in reactions:
                reactions[emoji] = []

            if user_id not in reactions[emoji]:
                reactions[emoji].append(user_id)

            metadata["reactions"] = reactions
            message.metadata = metadata
            self.db.commit()
```

## Frontend Components

### 1. Collaborative Session View

```jsx
// frontend/src/components/CollaborativeSession.jsx

import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import SessionHeader from './SessionHeader';
import PresenceBar from './PresenceBar';
import ChatPanel from './ChatPanel';
import SessionContent from './SessionContent';

export default function CollaborativeSession({ sessionId }) {
    const [participants, setParticipants] = useState([]);
    const [messages, setMessages] = useState([]);
    const [presence, setPresence] = useState({});

    const { send, lastMessage, connected } = useWebSocket(sessionId);

    useEffect(() => {
        if (!lastMessage) return;

        const data = JSON.parse(lastMessage.data);

        switch (data.type) {
            case 'user_joined':
                setParticipants(prev => [...prev, data.user]);
                break;

            case 'user_left':
                setParticipants(prev =>
                    prev.filter(p => p.id !== data.user_id)
                );
                break;

            case 'chat_message':
                setMessages(prev => [...prev, data.message]);
                break;

            case 'presence_update':
                setPresence(prev => ({
                    ...prev,
                    [data.user_id]: data.presence
                }));
                break;
        }
    }, [lastMessage]);

    const sendMessage = (content) => {
        send({
            type: 'chat_message',
            session_id: sessionId,
            content
        });
    };

    return (
        <div className="flex h-screen">
            <div className="flex-1 flex flex-col">
                <SessionHeader sessionId={sessionId} />
                <PresenceBar participants={participants} presence={presence} />
                <SessionContent sessionId={sessionId} presence={presence} />
            </div>

            <ChatPanel
                messages={messages}
                onSendMessage={sendMessage}
                participants={participants}
            />
        </div>
    );
}
```

### 2. Presence Bar (Who's Here)

```jsx
// frontend/src/components/PresenceBar.jsx

import React from 'react';
import Avatar from './Avatar';

export default function PresenceBar({ participants, presence }) {
    return (
        <div className="bg-gray-50 border-b px-4 py-2 flex items-center space-x-2">
            <span className="text-sm text-gray-600">
                {participants.length} {participants.length === 1 ? 'person' : 'people'} here:
            </span>

            <div className="flex -space-x-2">
                {participants.map(participant => (
                    <div key={participant.id} className="relative">
                        <Avatar
                            user={participant}
                            className="w-8 h-8 border-2 border-white"
                        />
                        {presence[participant.id]?.status === 'active' && (
                            <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full" />
                        )}
                    </div>
                ))}
            </div>

            {/* Show what others are viewing */}
            <div className="ml-auto flex items-center space-x-2 text-xs text-gray-500">
                {Object.entries(presence).map(([userId, data]) => (
                    data.viewport && (
                        <div key={userId} className="flex items-center space-x-1">
                            <span>{data.username}</span>
                            <span>→</span>
                            <code className="bg-gray-200 px-1 rounded">
                                {data.viewport.file}:{data.viewport.start}
                            </code>
                        </div>
                    )
                ))}
            </div>
        </div>
    );
}
```

### 3. Chat Panel

```jsx
// frontend/src/components/ChatPanel.jsx

import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

export default function ChatPanel({ messages, onSendMessage, participants }) {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = (e) => {
        e.preventDefault();
        if (input.trim()) {
            onSendMessage(input);
            setInput('');
        }
    };

    return (
        <div className="w-80 border-l flex flex-col bg-white">
            <div className="p-4 border-b">
                <h3 className="font-semibold">Chat</h3>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map(message => (
                    <MessageBubble
                        key={message.id}
                        message={message}
                        participants={participants}
                    />
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSend} className="p-4 border-t">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                    >
                        Send
                    </button>
                </div>
            </form>
        </div>
    );
}
```

## Scaling Considerations

### Multi-Server Deployment with Redis

```python
# backend/app/collaboration/redis_pubsub.py

import redis
import json
from typing import Callable

class RedisPubSub:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()

    def subscribe_to_session(self, session_id: str, callback: Callable):
        """Subscribe to session events."""
        channel = f"session:{session_id}"
        self.pubsub.subscribe(**{channel: callback})

    def publish_to_session(self, session_id: str, message: dict):
        """Publish message to session channel."""
        channel = f"session:{session_id}"
        self.redis.publish(channel, json.dumps(message))

    def start_listening(self):
        """Start listening for messages."""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                # Message will be handled by callback
                pass
```

## Security Considerations

1. **Authentication**: JWT tokens required for WebSocket connections
2. **Authorization**: Role-based permissions enforced server-side
3. **Rate Limiting**: Max 100 messages/minute per user
4. **Input Validation**: Sanitize all user inputs
5. **XSS Prevention**: Escape HTML in messages
6. **Session Hijacking**: Validate session ownership

## Performance Optimization

1. **Message Batching**: Batch presence updates (max 1/second)
2. **Lazy Loading**: Load chat history on demand
3. **Debouncing**: Debounce cursor updates
4. **Compression**: Use WebSocket compression
5. **Caching**: Cache session metadata in Redis

## Testing Strategy

```python
# tests/test_collaboration.py

async def test_user_joins_session(client, session_id, auth_token):
    """Test user joining session."""
    async with client.websocket_connect(
        f"/ws/session/{session_id}?token={auth_token}"
    ) as websocket:
        # Receive welcome message
        data = await websocket.receive_json()
        assert data["type"] == "connected"

async def test_chat_message_broadcast(client, session_id, users):
    """Test chat message broadcasting."""
    # User 1 sends message
    async with client.websocket_connect(...) as ws1:
        async with client.websocket_connect(...) as ws2:
            await ws1.send_json({
                "type": "chat_message",
                "content": "Hello!"
            })

            # User 2 receives message
            data = await ws2.receive_json()
            assert data["type"] == "chat_message"
            assert data["message"]["content"] == "Hello!"
```

## Metrics & Monitoring

**Track:**
- Active collaborations count
- Messages per session
- Average participants per session
- WebSocket connection duration
- Message delivery latency

---

**Next Steps:** Implement WebSocket connection manager and presence system.
