# Real-Time Collaboration - Quick Start Demo 🚀

Get the real-time collaboration prototype running in 5 minutes!

---

## Prerequisites

- Python 3.9+
- Node.js 18+
- Git

---

## Step 1: Clone & Setup (1 minute)

```bash
cd /Users/gagan/llm-session-manager

# Verify you're in the right directory
ls -la | grep -E "backend|frontend"
```

---

## Step 2: Start Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./collaboration.db
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ Backend is running at http://localhost:8000

---

## Step 3: Start Frontend (2 minutes)

Open a **new terminal**:

```bash
cd /Users/gagan/llm-session-manager/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected output:**
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

✅ Frontend is running at http://localhost:3000

---

## Step 4: Generate Test Tokens (30 seconds)

Open a **third terminal**:

```bash
cd /Users/gagan/llm-session-manager/backend

# Generate tokens for Alice and Bob
python3 << 'EOF'
from app.auth import create_access_token
from datetime import timedelta

# Generate long-lived tokens for demo
alice_token = create_access_token(
    data={"sub": "alice", "user_id": "user_alice"},
    expires_delta=timedelta(hours=8)
)
bob_token = create_access_token(
    data={"sub": "bob", "user_id": "user_bob"},
    expires_delta=timedelta(hours=8)
)

print("\n" + "="*60)
print("DEMO TOKENS (valid for 8 hours)")
print("="*60)
print("\nALICE'S TOKEN:")
print(alice_token)
print("\nBOB'S TOKEN:")
print(bob_token)
print("\n" + "="*60)
print("\nCopy these tokens - you'll need them in the browser!")
print("="*60 + "\n")
EOF
```

**Copy the tokens** - you'll need them next!

---

## Step 5: Demo the Prototype (1 minute)

### Browser 1: Alice (Host)

1. Open http://localhost:3000
2. Click **"Create New Session"**
3. Enter:
   - **Username:** `alice`
   - **Auth Token:** [Paste Alice's token from Step 4]
4. Click **"Join Session"**
5. **Copy the Session ID** from the URL (e.g., `session_1729180800000`)

### Browser 2: Bob (Editor)

1. Open http://localhost:3000 in a **new browser/incognito window**
2. Click **"Join Session"**
3. Enter the Session ID you copied from Alice's browser
4. Enter:
   - **Username:** `bob`
   - **Auth Token:** [Paste Bob's token from Step 4]
5. Click **"Join Session"**

---

## Step 6: Test Collaboration Features! 🎉

Now you should see both Alice and Bob in the **Presence Bar**!

### Test Real-Time Chat

**In Alice's browser:**
- Type: "Hi Bob! Can you review main.py?"
- Press **Send**

**In Bob's browser:**
- You should see Alice's message instantly!
- Reply: "Sure! Looking at it now."

### Test Cursor Tracking

**In Bob's browser:**
- Find the **"Cursor Simulator"** panel on the left
- Enter:
  - File: `main.py`
  - Line: `42`
  - Column: `10`
- Click **"Update Cursor"**

**In Alice's browser:**
- You should see Bob's cursor indicator showing `main.py:42:10`!

### Test Code Comments

**In Alice's browser:**
- Click the **"💬 Chat"** button to toggle to **"💬 Code Comment"** mode
- Enter:
  - File path: `main.py`
  - Line #: `42`
  - Code snippet: `def process_session():`
  - Message: "This function could be optimized"
- Click **Send**

**In Bob's browser:**
- You should see a yellow code comment with the file reference!

### Test Presence Status

**In either browser:**
- Find the **"Presence Status"** panel
- Click **"Set idle"** or **"Set away"**
- Watch the status indicator change in the Presence Bar!

---

## Verification Checklist

✅ Backend running on port 8000
✅ Frontend running on port 3000
✅ Both users can see each other in Presence Bar
✅ Chat messages appear instantly in both browsers
✅ Cursor positions are synchronized
✅ Code comments are displayed correctly
✅ Presence status updates in real-time
✅ User roles are shown (Host/Editor)
✅ Connection status is green

---

## Troubleshooting

### Backend Won't Start

```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9

# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall
```

### Frontend Won't Start

```bash
# Clear npm cache
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### WebSocket Connection Failed

1. **Check backend logs** for errors
2. **Verify token is valid** (not expired)
3. **Try generating new tokens** (Step 4)
4. **Check browser console** for errors (F12)

### Can't See Other User

1. **Verify both users are in the same session ID**
2. **Check green connection status indicator**
3. **Refresh both browsers**
4. **Check backend terminal for connection logs**

---

## Demo Script for Presentations

Use this script to demo the prototype to others:

### 1. Introduction (30 seconds)
"This is a real-time collaboration system for LLM sessions. Multiple developers can work together in the same session, seeing each other's cursors and communicating via chat."

### 2. Create Session (30 seconds)
"Let me create a new session as Alice, the session host."
- Create session
- Show session ID

### 3. Join Session (30 seconds)
"Now Bob joins the same session as an editor."
- Join with Bob
- Show both users in Presence Bar

### 4. Chat Demo (1 minute)
"They can chat in real-time."
- Alice: "Can you review the authentication code?"
- Bob: "Sure, I'm looking at auth.py now"
- Show instant messaging

### 5. Cursor Tracking (1 minute)
"They can see where each other is working."
- Bob updates cursor to `auth.py:125:15`
- Alice sees Bob's cursor indicator
- Click on cursor to "jump" to that location

### 6. Code Comments (1 minute)
"They can add comments at specific lines of code."
- Alice adds code comment at `auth.py:125`
- Bob sees the comment with file reference
- Show threaded discussion

### 7. Presence Status (30 seconds)
"The system tracks everyone's status automatically."
- Change status to idle/away
- Show status indicators

### 8. Conclusion (30 seconds)
"This system supports unlimited users, role-based permissions, and is built on WebSocket for real-time performance."

**Total demo time: ~5 minutes**

---

## Next Steps

### For Development

1. **Add file viewer** with syntax highlighting
2. **Implement collaborative editing** with operational transforms
3. **Add voice/video chat** integration
4. **Create VS Code extension** for native integration

### For Production

1. **Switch to PostgreSQL** database
2. **Add Redis** for multi-server scaling
3. **Implement rate limiting**
4. **Add comprehensive tests**
5. **Deploy to cloud** (AWS/GCP/Azure)
6. **Add monitoring** (Prometheus/Grafana)

### For Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for:
- Unit tests
- Integration tests
- Stress tests
- Security tests

---

## Useful Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload                    # Start server
python -m pytest tests/                          # Run tests
python -m app.database                           # Initialize DB

# Frontend
cd frontend
npm run dev                                       # Start dev server
npm run build                                     # Production build
npm run preview                                   # Preview build
npm run lint                                      # Lint code

# Generate tokens
cd backend
python -c "from app.auth import create_access_token; print(create_access_token({'sub': 'test'}))"

# Check WebSocket
wscat -c "ws://localhost:8000/ws/session/test123?token=YOUR_TOKEN"

# Database
cd backend
sqlite3 collaboration.db ".tables"                # List tables
sqlite3 collaboration.db ".schema session_messages"  # View schema
```

---

## Architecture Overview

```
┌─────────────┐                                ┌─────────────┐
│  Browser 1  │                                │  Browser 2  │
│   (Alice)   │                                │    (Bob)    │
└──────┬──────┘                                └──────┬──────┘
       │                                              │
       │ WebSocket                    WebSocket      │
       │                                              │
       ├──────────────────┐     ┐────────────────────┤
       │                  │     │                    │
       ▼                  ▼     ▼                    ▼
┌────────────────────────────────────────────────────────┐
│              FastAPI WebSocket Server                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Connection   │  │  Presence    │  │    Chat      │ │
│  │  Manager     │  │  Manager     │  │  Manager     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   SQLite DB   │
                 │  (Sessions,   │
                 │   Messages,   │
                 │   Events)     │
                 └───────────────┘
```

---

## Support

**Issues?** Check:
1. [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing
2. [REALTIME_COLLABORATION_COMPLETE.md](REALTIME_COLLABORATION_COMPLETE.md) - Full documentation
3. [backend/README.md](backend/README.md) - Backend details
4. [frontend/README.md](frontend/README.md) - Frontend details

**Still stuck?** Check the logs:
- Backend: Terminal where uvicorn is running
- Frontend: Browser console (F12)
- Database: `backend/collaboration.db`

---

Happy collaborating! 🎉
