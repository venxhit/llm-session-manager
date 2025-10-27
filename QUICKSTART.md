# Quick Start Guide - Real-Time Collaboration

Get up and running in 5 minutes!

---

## Prerequisites

✅ Python 3.11.7 installed
✅ Node.js 18+ installed
✅ All dependencies installed

---

## Step 1: Start Backend (Terminal 1)

```bash
cd /Users/gagan/llm-session-manager/backend

# Start the server
uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

✅ Backend is running at http://localhost:8000

---

## Step 2: Start Frontend (Terminal 2)

```bash
cd /Users/gagan/llm-session-manager/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
VITE v5.0.8  ready in 500 ms
➜  Local:   http://localhost:3000/
```

✅ Frontend is running at http://localhost:3000

---

## Step 3: Get Your Tokens (Terminal 3)

```bash
cd /Users/gagan/llm-session-manager/backend

# Generate test tokens
python3 generate_tokens.py
```

**You'll get 3 tokens:**
- **ALICE (Host)** - eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
- **BOB (Editor)** - eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
- **CHARLIE (Viewer)** - eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

💾 Tokens are also saved to `test_tokens.txt`

---

## Step 4: Test in Browser

### Browser 1 - Alice (Host)

1. Open: **http://localhost:3000**
2. Click: **"Create New Session"**
3. Login:
   - Username: `alice`
   - Token: [Paste Alice's token]
4. Click: **"Join Session"**
5. **Copy the Session ID** from URL (e.g., `session_1729180800000`)

### Browser 2 - Bob (Editor) - Use Incognito/Private Window!

1. Open: **http://localhost:3000** (in incognito mode)
2. Click: **"Join Session"**
3. Paste the **Session ID** from Alice
4. Login:
   - Username: `bob`
   - Token: [Paste Bob's token]
5. Click: **"Join Session"**

---

## Step 5: Test Features!

### ✅ You Should See:
- Both Alice and Bob in the **Presence Bar**
- Green connection indicator
- Alice has crown 👑 (Host)
- Bob has pencil ✏️ (Editor)

### 🎯 Try These:

**Test Chat:**
- Alice: Type "Hi Bob!" and press Send
- Bob: Type "Hi Alice!" and press Send
- ✅ Messages appear instantly in both browsers

**Test Cursor Tracking:**
- In Bob's browser, find "Cursor Simulator"
- Enter: File `main.py`, Line `42`, Column `10`
- Click "Update Cursor"
- ✅ Alice sees Bob's cursor at main.py:42:10

**Test Code Comments:**
- In Alice's browser, click the chat button to toggle to "Code Comment" mode
- Enter: File `auth.py`, Line `125`, Comment "Needs review"
- Click Send
- ✅ Bob sees a yellow code comment with file reference

**Test Presence:**
- In Bob's browser, click "Set idle" or "Set away"
- ✅ Bob's status indicator changes color in Alice's browser

---

## Troubleshooting

### Backend won't start
```bash
# Check if dependencies are installed
cd backend
pip list | grep -E "fastapi|uvicorn|jose|passlib"

# Reinstall if needed
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
```

### Frontend won't start
```bash
# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Can't generate tokens
```bash
# Check if you're in backend directory
cd /Users/gagan/llm-session-manager/backend

# Try again
python3 generate_tokens.py
```

### WebSocket won't connect
1. Make sure backend is running (Terminal 1)
2. Check browser console for errors (F12)
3. Regenerate tokens if they expired
4. Refresh the page

---

## Quick Reference

### Useful Commands

```bash
# Backend (Terminal 1)
cd /Users/gagan/llm-session-manager/backend
uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd /Users/gagan/llm-session-manager/frontend
npm run dev

# Generate Tokens (Terminal 3)
cd /Users/gagan/llm-session-manager/backend
python3 generate_tokens.py

# View saved tokens
cat backend/test_tokens.txt
```

### URLs
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Test Users
- **Alice** - Host (full permissions)
- **Bob** - Editor (can chat, comment, share cursor)
- **Charlie** - Viewer (read-only)

---

## What You Can Do

### Collaboration Features
✅ Multi-user sessions (unlimited users)
✅ Real-time chat messaging
✅ Code comments at specific file:line
✅ Cursor position tracking
✅ Presence status (active/idle/away)
✅ Emoji reactions
✅ Join/leave notifications
✅ Role-based permissions
✅ Auto-reconnection
✅ Event logging

### Use Cases
- **Code Reviews** - Discuss code in real-time
- **Pair Programming** - Share cursor positions
- **Team Collaboration** - Work together on same session
- **Mentoring** - Guide junior developers
- **Debugging** - Collaborate on bug fixes

---

## Next Steps

### Learn More
- **[TEST_END_TO_END.md](TEST_END_TO_END.md)** - Comprehensive testing guide
- **[ARCHITECTURE_EXPLAINED.md](ARCHITECTURE_EXPLAINED.md)** - Understanding the system
- **[REALTIME_COLLABORATION_COMPLETE.md](REALTIME_COLLABORATION_COMPLETE.md)** - Full documentation

### Extend the System
- Add file viewer with syntax highlighting
- Implement collaborative editing
- Add voice/video chat
- Create VS Code extension
- Deploy to production

---

## Success!

If you can:
- ✅ See both users in Presence Bar
- ✅ Send messages that appear instantly
- ✅ Update cursor positions
- ✅ Add code comments
- ✅ Change presence status

**Congratulations! Your real-time collaboration system is working!** 🎉

---

For detailed testing and troubleshooting, see [TEST_END_TO_END.md](TEST_END_TO_END.md)
