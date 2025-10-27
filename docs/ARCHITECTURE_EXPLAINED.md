# LLM Session Manager - Architecture Explained

## The Big Picture: What Is This Project?

This project has **TWO PARTS** that work together:

```
┌─────────────────────────────────────────────────────────────┐
│  LLM SESSION MANAGER                                        │
│                                                              │
│  ┌────────────────────────┐    ┌────────────────────────┐  │
│  │  PART 1: CLI Tool      │    │  PART 2: Collaboration │  │
│  │  (Original)            │    │  (New - v0.3.0)        │  │
│  │                        │    │                        │  │
│  │  • Monitor sessions    │    │  • Multi-user sessions │  │
│  │  • Track tokens        │    │  • Real-time chat      │  │
│  │  • Health checks       │    │  • Cursor tracking     │  │
│  │  • Export/import       │    │  • Web UI              │  │
│  │  • Memory search       │    │  • Code comments       │  │
│  │  • MCP integration     │    │  • WebSocket API       │  │
│  │                        │    │                        │  │
│  │  Terminal-based        │    │  Browser-based         │  │
│  └────────────────────────┘    └────────────────────────┘  │
│           ↓                              ↓                  │
│     Your Local CLI              Shared Web Interface       │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 1: Original CLI Tool (Still Works!)

### What It Does
Monitors your AI coding sessions (Claude Code, Cursor, Copilot) from the command line.

### Location
```
llm_session_manager/
├── cli.py              # Command-line interface
├── core/               # Session discovery, health monitoring
├── models/             # Data models
├── storage/            # SQLite database
├── ui/                 # Terminal UI (Rich)
└── utils/              # Token estimation, etc.
```

### How to Use
```bash
# Still works exactly as before!
python -m llm_session_manager.cli list
python -m llm_session_manager.cli monitor
python -m llm_session_manager.cli health <session-id>
python -m llm_session_manager.cli memory-search "authentication"
```

**This is YOUR tool** - runs on your machine, monitors your sessions.

---

## Part 2: New Collaboration Features (Just Added)

### What It Does
Allows **multiple developers** to work together in the same LLM coding session through a web interface.

### Location
```
backend/                # New FastAPI server for collaboration
├── app/
│   ├── main.py              # Web server
│   ├── websocket.py         # Real-time communication
│   ├── auth.py              # User authentication
│   ├── models.py            # Database models
│   ├── collaboration/
│   │   ├── chat.py          # Chat messages
│   │   ├── presence.py      # Who's online
│   │   └── connection_manager.py
│   └── routers/             # API endpoints

frontend/               # React web interface
├── src/
│   ├── components/          # UI components
│   ├── pages/               # Chat, presence, etc.
│   └── hooks/               # WebSocket connection
```

### How to Use
```bash
# Start the web server
cd backend
uvicorn app.main:app --reload

# Open browser
# http://localhost:3000
# Multiple people can join the same session
```

**This is for TEAMS** - web-based, multiple people collaborate.

---

## Why Is There a Backend?

### The Problem We're Solving

**Scenario:**
```
Alice: Working on auth feature in Claude Code
Bob: Wants to help Alice debug
Charlie: Learning by watching

WITHOUT collaboration:
❌ They can't see what each other is doing
❌ No way to discuss in real-time
❌ Can't point to specific lines of code
❌ Have to use Slack/Zoom separately

WITH collaboration (what we built):
✅ All three join the same "session" in browser
✅ See each other's cursor positions
✅ Chat about the code
✅ Add comments at specific file:line locations
✅ Real-time updates via WebSocket
```

### Why Backend Is Needed

The backend provides:

1. **WebSocket Server** - Real-time bidirectional communication
2. **User Authentication** - Who can join which sessions
3. **Message Broadcasting** - Send chat to all users
4. **Presence Tracking** - Who's online, where their cursor is
5. **Data Storage** - Save chat history, events, participants

Without a backend, you can't have:
- Multiple browsers talking to each other
- Real-time updates
- Persistent chat history
- User authentication

---

## About the JWT Secret Key

### What Is JWT?

**JWT = JSON Web Token** - A secure way to identify users without passwords.

Think of it like a **backstage pass** at a concert:
- You show it once to get in
- It proves who you are
- It has an expiration time
- It's signed by the venue (backend) so it can't be forged

### The Secret Key

The JWT secret key is like the **stamp** that signs these passes.

**In the .env file:**
```bash
JWT_SECRET_KEY=super-secret-key-for-testing
```

**What it's used for:**
```python
# Backend creates a token when user logs in
token = create_access_token(data={"user": "alice"})
# Returns: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# User sends this token with every request
# Backend verifies it using the same secret
verify_token(token, secret_key)
# Returns: True (valid) or False (invalid/forged)
```

### Where to Get It?

**For Testing (Development):**
```bash
# Just make up any random string!
JWT_SECRET_KEY=my-super-secret-testing-key-123456
```

**For Production:**
```bash
# Generate a secure random key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# XQYjxnP_8vKR9dZG7yT4mBWc3hL2fN5pA1sD6vF9kE8
```

**Why it matters:**
- Anyone with the secret can forge tokens
- Keep it secret in production!
- Different key for dev vs production
- Change it if compromised

---

## How the Two Parts Work Together

### Current State (Separate)

Right now they're **independent**:

```
PART 1 (CLI):
You run: python -m llm_session_manager.cli monitor
↓
Monitors YOUR local Claude Code sessions
↓
Shows you token usage, health, etc.
↓
Terminal UI

PART 2 (Web):
You run: uvicorn app.main:app
↓
Web server starts
↓
Multiple people visit http://localhost:3000
↓
They collaborate in browser
```

### Future Integration (Possible)

They **could** be integrated:

```
Scenario:
1. Alice runs CLI tool monitoring her Claude Code session
2. CLI detects session_abc123
3. Alice runs: python -m llm_session_manager.cli share session_abc123
4. CLI starts web server and generates join link
5. Bob opens link in browser
6. Bob can now see Alice's session context, chat with her, etc.
```

**This would require:**
- CLI command to start web server
- Automatic session export to web interface
- Integration between SQLite (CLI) and PostgreSQL (web)

---

## The Chat Feature - Why?

### Use Case 1: Code Review

```
Alice: [shares cursor at auth.py:125]
Alice: "Can you review this JWT validation?"
Bob: [looks at auth.py:125]
Bob: "You're missing expiration check"
Alice: [adds code comment] "Need to validate exp claim"
Charlie: 👍 [reacts to comment]
```

**Without chat:** They'd need Slack + screen share + verbal description

**With chat:** Everything in one interface, tied to specific code locations

### Use Case 2: Pair Programming

```
Junior Dev: "I'm stuck on this API endpoint"
Senior Dev: [shares cursor at api.py:50]
Senior Dev: "Look here - you need to await this"
Junior Dev: "Oh! I see it now"
[Both see same cursor position in real-time]
```

### Use Case 3: Team Collaboration

```
Multiple devs working on same codebase:
- Alice: frontend (components/)
- Bob: backend (api/)
- Charlie: database (models/)

They're all in same "session":
- See who's working on what
- Quick questions via chat
- No context switching
- Async code comments
```

---

## What You Have Now

### Directory Structure

```
llm-session-manager/
│
├── llm_session_manager/          # PART 1: Original CLI
│   ├── cli.py                    # Commands: list, monitor, health, etc.
│   ├── core/
│   │   ├── discovery.py          # Find Claude/Cursor sessions
│   │   ├── health_monitor.py     # Calculate session health
│   │   └── memory.py             # Cross-session memory
│   ├── models/
│   │   ├── session.py            # Session data model
│   │   └── memory.py             # Memory data model
│   ├── storage/
│   │   └── database.py           # SQLite for CLI
│   ├── ui/
│   │   └── dashboard.py          # Terminal UI
│   ├── utils/
│   │   └── token_estimator.py    # Count tokens
│   └── mcp/                      # Model Context Protocol
│       ├── server.py             # MCP integration
│       └── session_server.py
│
├── backend/                      # PART 2: Web Collaboration
│   ├── app/
│   │   ├── main.py               # FastAPI web server
│   │   ├── websocket.py          # Real-time WebSocket
│   │   ├── auth.py               # JWT authentication
│   │   ├── models.py             # Database models
│   │   ├── collaboration/
│   │   │   ├── chat.py           # Chat functionality
│   │   │   ├── presence.py       # User presence
│   │   │   └── connection_manager.py
│   │   └── routers/              # API endpoints
│   └── requirements.txt
│
├── frontend/                     # PART 2: Web UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.jsx     # Chat interface
│   │   │   ├── PresenceBar.jsx   # Who's online
│   │   │   └── CursorIndicator.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx          # Landing page
│   │   │   └── CollaborativeSession.jsx
│   │   └── hooks/
│   │       └── useWebSocket.js   # WebSocket connection
│   └── package.json
│
├── docs/                         # Documentation
├── manual_tests/                 # Test scripts
└── README.md                     # Main documentation
```

---

## What Each Component Does

### CLI (llm_session_manager/)

**Purpose:** Monitor YOUR local AI coding sessions

**Key Files:**
- `cli.py` - Command-line interface
- `core/discovery.py` - Finds running Claude Code/Cursor processes
- `core/health_monitor.py` - Calculates health scores
- `utils/token_estimator.py` - Estimates token usage
- `storage/database.py` - Stores session data locally

**When to use:** Daily development, monitoring your own sessions

### Backend (backend/)

**Purpose:** Enable multi-user collaboration

**Key Files:**
- `app/main.py` - FastAPI web server
- `app/websocket.py` - Real-time communication (chat, presence)
- `app/auth.py` - User authentication with JWT
- `app/collaboration/chat.py` - Chat messages and code comments
- `app/collaboration/presence.py` - Track who's online, cursor positions
- `app/models.py` - Database schema (users, messages, participants)

**When to use:** Team collaboration, code reviews, pair programming

### Frontend (frontend/)

**Purpose:** Web interface for collaboration

**Key Files:**
- `src/pages/CollaborativeSession.jsx` - Main collaboration UI
- `src/components/ChatPanel.jsx` - Chat interface
- `src/components/PresenceBar.jsx` - Shows active users
- `src/hooks/useWebSocket.js` - Manages WebSocket connection

**When to use:** Accessed via browser when collaborating

---

## How to Use Each Part

### Use Case 1: Solo Developer (Just CLI)

```bash
# Only need the original CLI
python -m llm_session_manager.cli monitor

# No backend, no frontend needed
# Everything runs locally
```

### Use Case 2: Team Collaboration (CLI + Web)

```bash
# Developer 1: Monitors their session with CLI
python -m llm_session_manager.cli list

# Developer 2: Starts web server for team
cd backend
uvicorn app.main:app --reload

# Developer 3: Opens web UI
cd frontend
npm run dev

# All developers: Visit http://localhost:3000
# Join same session, collaborate in browser
```

### Use Case 3: Just Testing Collaboration

```bash
# Skip CLI entirely
# Just test the new web collaboration feature

# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Browser: http://localhost:3000
# Create/join sessions, test features
```

---

## Why We Built This

Based on your earlier conversation, you wanted:

1. ✅ **Real-Time Collaboration** - Multiple people in one session
2. ✅ **Shared context updates** - See what others are doing
3. ✅ **Chat and comments** - Communicate while coding

We delivered:
- WebSocket-based real-time updates
- Multi-user sessions
- Chat with code comments at specific lines
- Cursor tracking
- Presence awareness
- Beautiful web UI

---

## Summary

### What You Originally Had
**LLM Session Manager CLI** - Monitor your AI coding sessions from terminal

### What We Added (v0.3.0)
**Real-Time Collaboration** - Web-based multi-user sessions with chat

### Why There's a Backend
Needed for:
- WebSocket communication (real-time)
- User authentication (JWT)
- Message broadcasting
- Presence tracking
- Data persistence

### Why There's Chat
Enables:
- Team collaboration
- Code reviews
- Pair programming
- Quick questions
- Code comments at specific lines

### JWT Secret Key
- Just a random string for signing tokens
- Proves users are who they say they are
- Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## Next Steps

### Option 1: Use Only CLI (Original Tool)
```bash
python -m llm_session_manager.cli monitor
# No backend needed
```

### Option 2: Test Collaboration Features
```bash
# Follow TEST_END_TO_END.md
# Start backend + frontend
# Test chat, presence, cursors
```

### Option 3: Integrate Both
```bash
# Future: CLI exports session to web interface
# Team can join and collaborate on your session
```

---

**Does this clarify the architecture?** Let me know if you have questions about any specific part!
