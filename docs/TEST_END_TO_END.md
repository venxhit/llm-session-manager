# End-to-End Testing Guide - Real-Time Collaboration

Complete walkthrough to test all collaboration features.

---

## Prerequisites Check

Before starting, verify you have:
- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] pip installed (`pip --version`)
- [ ] npm installed (`npm --version`)

---

## Step 1: Set Up Backend (5 minutes)

### 1.1 Navigate to backend directory
```bash
cd /Users/gagan/llm-session-manager/backend
```

### 1.2 Install Python dependencies
```bash
pip install -r requirements.txt
```

**Expected output:** All packages installed successfully

### 1.3 Create environment file
```bash
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./collaboration.db
JWT_SECRET_KEY=super-secret-key-for-testing-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
EOF
```

### 1.4 Verify .env file
```bash
cat .env
```

**Should show:**
```
DATABASE_URL=sqlite:///./collaboration.db
JWT_SECRET_KEY=super-secret-key-for-testing-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### 1.5 Start backend server
```bash
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

**✅ Backend is running!** Keep this terminal open.

---

## Step 2: Set Up Frontend (3 minutes)

### 2.1 Open a NEW terminal and navigate to frontend
```bash
cd /Users/gagan/llm-session-manager/frontend
```

### 2.2 Install Node dependencies
```bash
npm install
```

**Expected output:** Dependencies installed (may take 1-2 minutes)

### 2.3 Start frontend dev server
```bash
npm run dev
```

**Expected output:**
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**✅ Frontend is running!** Keep this terminal open.

---

## Step 3: Generate Test Tokens (1 minute)

### 3.1 Open a THIRD terminal
```bash
cd /Users/gagan/llm-session-manager/backend
```

### 3.2 Run token generation script
```bash
python3 << 'EOF'
from app.auth import create_access_token
from datetime import timedelta

# Generate 8-hour tokens for testing
alice_token = create_access_token(
    data={"sub": "alice", "user_id": "user_alice"},
    expires_delta=timedelta(hours=8)
)

bob_token = create_access_token(
    data={"sub": "bob", "user_id": "user_bob"},
    expires_delta=timedelta(hours=8)
)

charlie_token = create_access_token(
    data={"sub": "charlie", "user_id": "user_charlie"},
    expires_delta=timedelta(hours=8)
)

print("\n" + "="*70)
print("TEST TOKENS (valid for 8 hours)")
print("="*70)
print("\nALICE (Host):")
print(alice_token)
print("\nBOB (Editor):")
print(bob_token)
print("\nCHARLIE (Viewer):")
print(charlie_token)
print("\n" + "="*70)
print("Copy these tokens - you'll need them in the browser!")
print("="*70 + "\n")
EOF
```

**✅ Copy all three tokens!** You'll paste them in the browser.

---

## Step 4: Test Session Creation - Alice (Host)

### 4.1 Open Browser 1 (Chrome/Firefox)
Navigate to: **http://localhost:3000**

### 4.2 Create a new session
- Click the **"Create New Session"** button
- You'll be redirected to a session page

### 4.3 Login as Alice
You'll see a login form. Enter:
- **Username:** `alice`
- **Auth Token:** [Paste Alice's token from Step 3]
- Click **"Join Session"**

### 4.4 Verify Alice is connected
You should see:
- ✅ Green connection indicator (top right of chat)
- ✅ "Connected to session" notification
- ✅ Alice in the Presence Bar with "Host" role and crown 👑
- ✅ Session ID in the URL bar (e.g., `session_1729180800000`)

### 4.5 Copy the Session ID
**Copy the session ID from the URL** - you'll need it for Bob!

Example: If URL is `http://localhost:3000/session/session_1729180800000`
Copy: `session_1729180800000`

**✅ Alice is ready!** Keep this browser window open.

---

## Step 5: Test Session Joining - Bob (Editor)

### 5.1 Open Browser 2 (Incognito/Private Window)
**Important:** Use incognito mode or a different browser!

Navigate to: **http://localhost:3000**

### 5.2 Join existing session
- Click **"Join Session"**
- Paste the Session ID you copied from Alice's browser
- Click **"Join Session"**

### 5.3 Login as Bob
- **Username:** `bob`
- **Auth Token:** [Paste Bob's token from Step 3]
- Click **"Join Session"**

### 5.4 Verify Bob is connected
In Bob's browser, you should see:
- ✅ Green connection indicator
- ✅ "Connected to session" notification
- ✅ Both Alice AND Bob in the Presence Bar
- ✅ Bob has "Editor" role with pencil ✏️

In Alice's browser, you should see:
- ✅ "bob joined the session" notification
- ✅ Bob appears in the Presence Bar

**✅ Both users connected!** Now let's test features.

---

## Step 6: Test Real-Time Chat

### 6.1 Alice sends a message
In **Alice's browser:**
- Type in the chat input: `Hi Bob! Can you review the authentication code?`
- Press **Send** or hit **Enter**

### 6.2 Verify message appears in both browsers
**In Alice's browser:**
- ✅ Message appears immediately on the right side (blue background)
- ✅ No username shown (it's your own message)

**In Bob's browser:**
- ✅ Message appears immediately on the left side (gray background)
- ✅ Shows "alice" as the sender
- ✅ Timestamp is displayed

### 6.3 Bob replies
In **Bob's browser:**
- Type: `Sure Alice! I'm looking at auth.py now`
- Press **Send**

### 6.4 Verify bidirectional chat
**In Bob's browser:**
- ✅ Bob's message appears on the right (blue)

**In Alice's browser:**
- ✅ Bob's message appears on the left (gray)
- ✅ Shows "bob" as sender

**✅ Real-time chat working!**

---

## Step 7: Test Cursor Tracking

### 7.1 Bob updates cursor position
In **Bob's browser:**
- Find the **"Cursor Simulator"** panel on the left side
- Enter:
  - **File path:** `auth.py`
  - **Line:** `125`
  - **Column:** `15`
- Click **"Update Cursor"**

### 7.2 Verify cursor appears in Alice's browser
In **Alice's browser:**
- ✅ Look for Bob's cursor indicator in the left sidebar
- ✅ Should show: `bob` with `auth.py:125:15`
- ✅ Has a colored avatar and animated pin icon 📍

### 7.3 Alice updates cursor
In **Alice's browser:**
- In the Cursor Simulator:
  - **File path:** `main.py`
  - **Line:** `42`
  - **Column:** `10`
- Click **"Update Cursor"**

### 7.4 Verify in Bob's browser
In **Bob's browser:**
- ✅ Alice's cursor indicator appears
- ✅ Shows `alice` with `main.py:42:10`

**✅ Cursor tracking working!**

---

## Step 8: Test Code Comments

### 8.1 Alice adds a code comment
In **Alice's browser:**
- Click the **"💬 Chat"** button to toggle to **"💬 Code Comment"** mode
- The button should turn yellow
- You'll see additional fields appear

### 8.2 Fill in code comment details
- **File path:** `auth.py`
- **Line #:** `125`
- **Code snippet (optional):** `def verify_token(token: str):`
- **Message:** `This function needs better error handling for expired tokens`
- Click **Send**

### 8.3 Verify code comment appears
**In Alice's browser:**
- ✅ Message appears with yellow/amber background
- ✅ Shows file reference: `auth.py:125`
- ✅ Shows code snippet in a code block
- ✅ Shows the comment text

**In Bob's browser:**
- ✅ Same code comment appears immediately
- ✅ Yellow background indicates it's a code comment
- ✅ Shows file location and code snippet

### 8.4 Toggle back to chat mode
In Alice's browser:
- Click **"💬 Code Comment"** button again to toggle back to **"💬 Chat"**

**✅ Code comments working!**

---

## Step 9: Test Presence Status

### 9.1 Bob changes status to "idle"
In **Bob's browser:**
- Find the **"Presence Status"** panel on the left
- Click **"Set idle"**

### 9.2 Verify status update
**In Alice's browser:**
- ✅ Bob's status indicator (small circle on his avatar) changes to yellow
- ✅ Happens instantly

### 9.3 Bob changes to "away"
In **Bob's browser:**
- Click **"Set away"**

**In Alice's browser:**
- ✅ Bob's status indicator turns gray

### 9.4 Bob changes back to "active"
In **Bob's browser:**
- Click **"Set active"**

**In Alice's browser:**
- ✅ Bob's status indicator turns green

**✅ Presence status working!**

---

## Step 10: Test Multiple Cursors (3rd User - Optional)

### 10.1 Open Browser 3 (Another incognito window)
Navigate to: **http://localhost:3000**

### 10.2 Join as Charlie
- Click **"Join Session"**
- Paste the same Session ID
- Username: `charlie`
- Token: [Charlie's token from Step 3]

### 10.3 Update Charlie's cursor
- File: `database.py`
- Line: `50`
- Column: `5`

### 10.4 Verify in all browsers
**All three browsers should now show:**
- ✅ Three users in Presence Bar
- ✅ Charlie has "Viewer" role 👁️
- ✅ All cursor positions visible

**✅ Multi-user tracking working!**

---

## Step 11: Test User Leaving

### 11.1 Bob leaves the session
In **Bob's browser:**
- Click **"Leave Session"** button

### 11.2 Verify disconnection
**In Bob's browser:**
- ✅ Redirected to login screen

**In Alice's browser:**
- ✅ "bob left the session" notification appears
- ✅ Bob disappears from Presence Bar
- ✅ Bob's cursor indicator disappears

**✅ User disconnect working!**

---

## Step 12: Verify Backend Logs

### 12.1 Check Terminal 1 (Backend)
You should see logs like:
```
INFO:     WebSocket connection accepted for session session_xxx
INFO:     User alice connected to session session_xxx
INFO:     User bob connected to session session_xxx
INFO:     Message received: chat_message from alice
INFO:     Message received: cursor_update from bob
INFO:     User bob disconnected from session session_xxx
```

**✅ Backend logging working!**

---

## Step 13: Test Error Handling

### 13.1 Try joining with invalid token
- Open a new incognito window
- Try to join a session with token: `invalid_token_123`

**Expected:**
- ✅ Error notification appears
- ✅ Connection status shows red/disconnected

### 13.2 Try sending message while disconnected
- Stop the backend server (Ctrl+C in Terminal 1)
- Try to send a message in Alice's browser

**Expected:**
- ✅ Connection status turns red
- ✅ "Disconnected from session" notification
- ✅ "Reconnecting..." indicator appears
- ✅ Send button is disabled

### 13.3 Test auto-reconnection
- Restart the backend server
- Wait 3-5 seconds

**Expected:**
- ✅ "Connected to session" notification appears
- ✅ Connection status turns green
- ✅ Send button becomes enabled

**✅ Error handling and reconnection working!**

---

## Complete Feature Checklist

Check off each feature as you test it:

### Connection & Authentication
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] JWT tokens generated successfully
- [ ] Alice can create session
- [ ] Bob can join session
- [ ] Green connection indicator shows
- [ ] WebSocket connected notification appears

### User Presence
- [ ] Alice appears in Presence Bar as Host 👑
- [ ] Bob appears in Presence Bar as Editor ✏️
- [ ] User count shows correctly
- [ ] Status indicators (green/yellow/gray) work
- [ ] "User joined" notifications appear
- [ ] "User left" notifications appear

### Real-Time Chat
- [ ] Alice can send messages
- [ ] Bob receives messages instantly
- [ ] Messages appear in correct order
- [ ] Timestamps are shown
- [ ] Sender names are displayed
- [ ] Own messages appear on right (blue)
- [ ] Others' messages appear on left (gray)

### Cursor Tracking
- [ ] Bob can update cursor position
- [ ] Alice sees Bob's cursor indicator
- [ ] Cursor shows file:line:column
- [ ] Multiple cursors display correctly
- [ ] Cursor indicators are color-coded
- [ ] Cursor updates happen in real-time

### Code Comments
- [ ] Can toggle to code comment mode
- [ ] UI changes to show file/line inputs
- [ ] Can add file path and line number
- [ ] Can add optional code snippet
- [ ] Code comment appears with yellow background
- [ ] File reference is displayed correctly
- [ ] Code snippet shows in code block
- [ ] Comments appear in both browsers

### Presence Status
- [ ] Can change status to "active"
- [ ] Can change status to "idle"
- [ ] Can change status to "away"
- [ ] Status indicator color changes
- [ ] Status updates appear in other browsers
- [ ] Status changes happen instantly

### Role-Based Permissions
- [ ] Host has crown icon 👑
- [ ] Editor has pencil icon ✏️
- [ ] Viewer has eye icon 👁️
- [ ] Roles display correctly
- [ ] Different role colors work

### Multi-User Support
- [ ] 3+ users can join same session
- [ ] All users visible in Presence Bar
- [ ] All cursors tracked simultaneously
- [ ] Chat works for all users
- [ ] No message loss or duplication

### Error Handling
- [ ] Invalid token shows error
- [ ] Disconnection is detected
- [ ] Reconnection happens automatically
- [ ] Messages queue while offline
- [ ] UI disables when disconnected
- [ ] Error notifications display

### UI/UX
- [ ] Dark mode looks good
- [ ] Layout is responsive
- [ ] Buttons are clickable
- [ ] Input fields work correctly
- [ ] Notifications auto-dismiss
- [ ] No visual glitches
- [ ] Performance is smooth

**Total Features:** 60+
**All Working:** ✅ Yes / ❌ No

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
lsof -ti:8000 | xargs kill -9

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Try again
uvicorn app.main:app --reload
```

### Frontend won't start
```bash
# Clear npm cache
rm -rf node_modules package-lock.json
npm install

# Try again
npm run dev
```

### Token generation fails
```bash
# Make sure you're in the backend directory
cd /Users/gagan/llm-session-manager/backend

# Check if app module can be imported
python3 -c "from app.auth import create_access_token; print('OK')"
```

### WebSocket won't connect
1. Check backend is running (Terminal 1)
2. Check browser console for errors (F12 → Console)
3. Verify token is not expired
4. Try generating a new token
5. Check .env file has correct JWT_SECRET_KEY

### Can't see other users
1. Verify all users are in the **same session ID**
2. Check green connection indicator
3. Refresh both browsers
4. Check backend terminal for connection logs

### Messages not appearing
1. Check connection status (green dot)
2. Check browser console for errors
3. Verify message is not empty
4. Try refreshing the page

---

## Performance Testing (Optional)

### Test with 5+ users
1. Open 5 different browsers/incognito windows
2. All join the same session
3. Have each user send messages
4. Verify all messages appear in all browsers
5. Check backend CPU/memory usage

### Test with 100+ messages
1. Send many messages quickly
2. Verify all appear in correct order
3. Check scrolling performance
4. Verify no memory leaks

### Test reconnection under load
1. Have 3 users connected
2. Stop backend
3. Wait 10 seconds
4. Restart backend
5. Verify all users reconnect

---

## Success Criteria

**✅ End-to-end test passes if:**
1. Backend and frontend start without errors
2. Users can create and join sessions
3. Real-time chat works bidirectionally
4. Cursor tracking shows all users
5. Code comments display correctly
6. Presence status updates instantly
7. Auto-reconnection works
8. No console errors in browser
9. No server errors in backend
10. All 60+ checklist items pass

---

## Next Steps After Testing

If all tests pass:
- ✅ Demo to stakeholders
- ✅ Write additional unit tests
- ✅ Deploy to staging environment
- ✅ Conduct user acceptance testing
- ✅ Plan production deployment

If issues found:
- 📝 Document the issue
- 🐛 Debug using browser console + backend logs
- 🔧 Fix and re-test
- ✅ Verify fix doesn't break other features

---

## Quick Reference

**Backend URL:** http://localhost:8000
**Frontend URL:** http://localhost:3000
**WebSocket URL:** ws://localhost:8000/ws/session/{session_id}

**Test Users:**
- Alice (Host) - Full permissions
- Bob (Editor) - Can chat, comment, share cursor
- Charlie (Viewer) - Read-only access

**Key Shortcuts:**
- Enter - Send message
- Ctrl+C - Stop server
- F12 - Open browser console

---

**Happy Testing! 🎉**

For more detailed testing, see [TESTING_GUIDE.md](TESTING_GUIDE.md)
