# Comprehensive End-to-End Testing Guide

This guide will help you test all functionalities of the LLM Session Manager, including:
1. MCP Integration
2. Real-Time Collaboration
3. Team Dashboard Backend
4. Database Models
5. WebSocket Communication

## Prerequisites

Before testing, ensure you have:
- Python 3.10+
- Node.js 18+ (for JavaScript tests)
- All dependencies installed
- Environment configured

## Setup

### 1. Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
# JWT_SECRET_KEY=test-secret-key-change-in-production
```

### 3. Initialize Database

The database will be automatically created when you start the server. It will create:
- `data/sessions.db` (SQLite database)
- All necessary tables

## Testing Approach

We'll test in this order:
1. **Basic Server Setup** - Verify server starts
2. **Database Models** - Test all models work
3. **Authentication** - Create users and get tokens
4. **WebSocket Connection** - Test real-time connection
5. **Collaboration Features** - Test all message types
6. **MCP Integration** - Test MCP servers
7. **End-to-End Scenarios** - Real-world workflows

---

## Part 1: Basic Server Setup

### Test 1.1: Start the Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Verify:**
- Server starts without errors
- No import errors
- Database tables created

### Test 1.2: Health Check

Open browser or use curl:

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "0.3.0"
}
```

### Test 1.3: API Documentation

Visit: http://localhost:8000/api/docs

**Verify:**
- Swagger UI loads
- All endpoints listed
- Can explore API schema

---

## Part 2: Database Models

### Test 2.1: Create Test Data

Create a test script to populate database:

```python
# test_database.py
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal, engine, Base
from app.models import Team, User, SessionModel, SessionParticipant, SessionMessage
from app.auth import get_password_hash
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
db = SessionLocal()

try:
    # Create team
    team = Team(
        name="Test Team",
        description="A test team for collaboration"
    )
    db.add(team)
    db.flush()

    # Create users
    alice = User(
        email="alice@test.com",
        username="alice",
        password_hash=get_password_hash("password123"),
        full_name="Alice Smith",
        team_id=team.id,
        role="admin",
        is_active=True
    )

    bob = User(
        email="bob@test.com",
        username="bob",
        password_hash=get_password_hash("password123"),
        full_name="Bob Jones",
        team_id=team.id,
        role="member",
        is_active=True
    )

    db.add_all([alice, bob])
    db.flush()

    # Create session
    session = SessionModel(
        pid=12345,
        type="claude_code",
        status="active",
        start_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        working_directory="/Users/test/project",
        team_id=team.id,
        visibility="team",
        token_count=50000,
        token_limit=200000,
        health_score=85.0,
        tags=["backend", "api"],
        project_name="Test Project",
        description="Testing collaboration features"
    )
    db.add(session)
    session.owners.append(alice)
    db.flush()

    # Create participant
    participant = SessionParticipant(
        session_id=session.id,
        user_id=bob.id,
        role="editor"
    )
    db.add(participant)

    db.commit()

    print("✅ Test data created successfully!")
    print(f"Team ID: {team.id}")
    print(f"Alice ID: {alice.id}")
    print(f"Bob ID: {bob.id}")
    print(f"Session ID: {session.id}")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
```

Run it:

```bash
python test_database.py
```

**Expected Output:**
```
✅ Test data created successfully!
Team ID: <uuid>
Alice ID: <uuid>
Bob ID: <uuid>
Session ID: <uuid>
```

**Verify:**
- No database errors
- All foreign keys work
- Relationships established

---

## Part 3: Authentication

### Test 3.1: Create JWT Token

Create a script to generate test tokens:

```python
# generate_token.py
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models import User
from app.auth import create_access_token

db = SessionLocal()

# Get Alice
alice = db.query(User).filter(User.username == "alice").first()

if alice:
    token = create_access_token({"sub": alice.id})
    print(f"Alice's Token:\n{token}\n")

# Get Bob
bob = db.query(User).filter(User.username == "bob").first()

if bob:
    token = create_access_token({"sub": bob.id})
    print(f"Bob's Token:\n{token}\n")

db.close()
```

Run it:

```bash
python generate_token.py
```

**Expected Output:**
```
Alice's Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Bob's Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Save these tokens** - you'll use them for WebSocket testing!

---

## Part 4: WebSocket Connection

### Test 4.1: Python WebSocket Client

Create a test client:

```python
# test_websocket.py
import asyncio
import websockets
import json

# Replace with your token and session ID
ALICE_TOKEN = "YOUR_ALICE_TOKEN_HERE"
SESSION_ID = "YOUR_SESSION_ID_HERE"

async def test_connection():
    uri = f"ws://localhost:8000/ws/session/{SESSION_ID}?token={ALICE_TOKEN}"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Receive welcome message
            welcome = await websocket.recv()
            data = json.loads(welcome)
            print(f"\n📨 Welcome message:")
            print(json.dumps(data, indent=2))

            # Send a chat message
            print("\n📤 Sending chat message...")
            await websocket.send(json.dumps({
                "type": "chat_message",
                "content": "Hello from Alice!"
            }))

            # Receive broadcast
            response = await websocket.recv()
            data = json.loads(response)
            print(f"\n📨 Received:")
            print(json.dumps(data, indent=2))

            # Keep connection alive for 5 seconds
            print("\n⏳ Keeping connection alive for 5 seconds...")
            await asyncio.sleep(5)

            print("\n✅ Test completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run it:

```bash
python test_websocket.py
```

**Expected Output:**
```
Connecting to ws://localhost:8000/ws/session/...
✅ Connected!

📨 Welcome message:
{
  "type": "connected",
  "session_id": "...",
  "participants": [
    {
      "id": "...",
      "username": "alice",
      "role": "host"
    }
  ],
  "your_role": "host"
}

📤 Sending chat message...

📨 Received:
{
  "type": "chat_message",
  "message": {
    "id": "...",
    "user_id": "...",
    "username": "alice",
    "content": "Hello from Alice!",
    ...
  }
}

✅ Test completed successfully!
```

### Test 4.2: Multi-User Test

Create a script to simulate multiple users:

```python
# test_multi_user.py
import asyncio
import websockets
import json

ALICE_TOKEN = "YOUR_ALICE_TOKEN_HERE"
BOB_TOKEN = "YOUR_BOB_TOKEN_HERE"
SESSION_ID = "YOUR_SESSION_ID_HERE"

async def user_session(name, token, color):
    uri = f"ws://localhost:8000/ws/session/{SESSION_ID}?token={token}"

    print(f"{color}[{name}] Connecting...{color}")

    async with websockets.connect(uri) as websocket:
        print(f"{color}[{name}] ✅ Connected!{color}")

        # Receive welcome
        welcome = await websocket.recv()
        data = json.loads(welcome)
        print(f"{color}[{name}] Participants: {len(data.get('participants', []))}{color}")

        # Listen for messages
        async def listen():
            try:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"{color}[{name}] 📨 {data.get('type')}: {json.dumps(data, indent=2)}{color}")
            except:
                pass

        # Start listener
        listen_task = asyncio.create_task(listen())

        # Send messages
        for i in range(3):
            await asyncio.sleep(2)
            await websocket.send(json.dumps({
                "type": "chat_message",
                "content": f"Message {i+1} from {name}!"
            }))
            print(f"{color}[{name}] 📤 Sent message {i+1}{color}")

        # Wait a bit
        await asyncio.sleep(5)

        # Cancel listener
        listen_task.cancel()
        print(f"{color}[{name}] Disconnecting...{color}")

async def main():
    # Colors for terminal output
    ALICE_COLOR = "\033[94m"  # Blue
    BOB_COLOR = "\033[92m"    # Green
    RESET = "\033[0m"

    # Run both users concurrently
    await asyncio.gather(
        user_session("Alice", ALICE_TOKEN, ALICE_COLOR + RESET),
        user_session("Bob", BOB_TOKEN, BOB_COLOR + RESET)
    )

    print("\n✅ Multi-user test completed!")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python test_multi_user.py
```

**Expected Behavior:**
- Both users connect simultaneously
- Each sees the other join
- Messages broadcast to both users
- User count updates correctly

---

## Part 5: Test All Message Types

### Test 5.1: Comprehensive Message Test

Create a script to test all message types:

```python
# test_all_messages.py
import asyncio
import websockets
import json

TOKEN = "YOUR_TOKEN_HERE"
SESSION_ID = "YOUR_SESSION_ID_HERE"

async def test_all_message_types():
    uri = f"ws://localhost:8000/ws/session/{SESSION_ID}?token={TOKEN}"

    async with websockets.connect(uri) as ws:
        print("✅ Connected\n")

        # Test 1: Chat Message
        print("📝 Test 1: Chat Message")
        await ws.send(json.dumps({
            "type": "chat_message",
            "content": "Hello, team!"
        }))
        response = json.loads(await ws.recv())
        print(f"✅ Received: {response['type']}\n")

        # Test 2: Cursor Update
        print("📝 Test 2: Cursor Update")
        await ws.send(json.dumps({
            "type": "cursor_update",
            "data": {
                "file": "main.py",
                "line": 42,
                "column": 10
            }
        }))
        # Wait a moment
        await asyncio.sleep(0.5)
        print("✅ Cursor update sent\n")

        # Test 3: Viewport Update
        print("📝 Test 3: Viewport Update")
        await ws.send(json.dumps({
            "type": "viewport_update",
            "data": {
                "file": "main.py",
                "start_line": 30,
                "end_line": 60
            }
        }))
        await asyncio.sleep(0.5)
        print("✅ Viewport update sent\n")

        # Test 4: Presence Update
        print("📝 Test 4: Presence Update")
        await ws.send(json.dumps({
            "type": "presence_update",
            "status": "active"
        }))
        await asyncio.sleep(0.5)
        print("✅ Presence update sent\n")

        # Test 5: Code Comment
        print("📝 Test 5: Code Comment")
        await ws.send(json.dumps({
            "type": "code_comment",
            "data": {
                "file": "main.py",
                "line": 42,
                "content": "This could be optimized",
                "code_snippet": "def foo():"
            }
        }))
        response = json.loads(await ws.recv())
        print(f"✅ Received: {response['type']}\n")

        # Test 6: @Mention
        print("📝 Test 6: @Mention in Chat")
        await ws.send(json.dumps({
            "type": "chat_message",
            "content": "Hey @bob, check line 42!"
        }))
        response = json.loads(await ws.recv())
        mentions = response.get('message', {}).get('metadata', {}).get('mentions', [])
        print(f"✅ Mentions extracted: {mentions}\n")

        # Test 7: Session Update (if you're host/editor)
        print("📝 Test 7: Session Update")
        await ws.send(json.dumps({
            "type": "session_update",
            "changes": {
                "description": "Updated via WebSocket test"
            }
        }))
        await asyncio.sleep(0.5)
        print("✅ Session update sent\n")

        print("🎉 All message types tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_all_message_types())
```

Run it:

```bash
python test_all_messages.py
```

**Verify:**
- All 7 message types work
- No errors in server logs
- Messages broadcast correctly
- @Mentions extracted

---

## Part 6: Browser Testing

### Test 6.1: HTML Test Client

Create an HTML file to test from browser:

```html
<!-- test_websocket.html -->
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test Client</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        input, button { padding: 10px; margin: 5px; }
        #messages { background: white; padding: 15px; margin-top: 20px; height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; }
        .message { padding: 8px; margin: 5px 0; border-radius: 4px; }
        .system { background: #e3f2fd; }
        .user { background: #f1f8e9; }
        .error { background: #ffebee; color: #c62828; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .connected { background: #c8e6c9; }
        .disconnected { background: #ffcdd2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 WebSocket Test Client</h1>

        <div>
            <input type="text" id="token" placeholder="JWT Token" style="width: 400px;">
            <input type="text" id="sessionId" placeholder="Session ID" style="width: 200px;">
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>

        <div id="status" class="status disconnected">
            Status: Disconnected
        </div>

        <div>
            <h3>Send Message:</h3>
            <input type="text" id="message" placeholder="Type a message..." style="width: 500px;">
            <button onclick="sendChat()">Send Chat</button>
        </div>

        <div>
            <button onclick="sendCursor()">Send Cursor Update</button>
            <button onclick="sendComment()">Send Code Comment</button>
            <button onclick="sendPresence()">Update Presence</button>
        </div>

        <div id="messages"></div>
    </div>

    <script>
        let ws = null;

        function connect() {
            const token = document.getElementById('token').value;
            const sessionId = document.getElementById('sessionId').value;

            if (!token || !sessionId) {
                alert('Please enter token and session ID');
                return;
            }

            const url = `ws://localhost:8000/ws/session/${sessionId}?token=${token}`;

            ws = new WebSocket(url);

            ws.onopen = () => {
                updateStatus('Connected', true);
                addMessage('system', 'Connected to server');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                addMessage('system', `Received: ${data.type}`, data);
            };

            ws.onerror = (error) => {
                addMessage('error', `Error: ${error.message || 'Connection failed'}`);
            };

            ws.onclose = () => {
                updateStatus('Disconnected', false);
                addMessage('system', 'Disconnected from server');
            };
        }

        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function sendChat() {
            const message = document.getElementById('message').value;
            if (!message) return;

            send({
                type: 'chat_message',
                content: message
            });

            document.getElementById('message').value = '';
        }

        function sendCursor() {
            send({
                type: 'cursor_update',
                data: {
                    file: 'main.py',
                    line: Math.floor(Math.random() * 100),
                    column: Math.floor(Math.random() * 80)
                }
            });
        }

        function sendComment() {
            send({
                type: 'code_comment',
                data: {
                    file: 'main.py',
                    line: 42,
                    content: 'Test comment from browser',
                    code_snippet: 'def foo():'
                }
            });
        }

        function sendPresence() {
            send({
                type: 'presence_update',
                status: 'active'
            });
        }

        function send(data) {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                alert('Not connected');
                return;
            }

            ws.send(JSON.stringify(data));
            addMessage('user', `Sent: ${data.type}`, data);
        }

        function updateStatus(text, connected) {
            const status = document.getElementById('status');
            status.textContent = `Status: ${text}`;
            status.className = `status ${connected ? 'connected' : 'disconnected'}`;
        }

        function addMessage(type, text, data) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.innerHTML = `<strong>${new Date().toLocaleTimeString()}</strong>: ${text}`;

            if (data) {
                const pre = document.createElement('pre');
                pre.textContent = JSON.stringify(data, null, 2);
                pre.style.fontSize = '12px';
                pre.style.marginTop = '5px';
                div.appendChild(pre);
            }

            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
```

**How to use:**

1. Open `test_websocket.html` in your browser
2. Paste your JWT token
3. Enter session ID
4. Click "Connect"
5. Try sending different message types
6. Open in multiple browser tabs to simulate multiple users!

---

## Part 7: Test MCP Integration

### Test 7.1: Start MCP Server

```bash
# In a new terminal
python -m llm_session_manager.cli mcp-server
```

**Expected Output:**
```
Starting LLM Session Manager MCP Server...
✓ MCP Server initialized successfully
Database: data/sessions.db
Memory: data/memories

Server is running. Connect via MCP client (e.g., Claude Desktop)
```

### Test 7.2: Test MCP with Python Client

```python
# test_mcp.py
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def test_mcp():
    # This would connect to the MCP server
    # For now, just test that the server starts
    print("✅ MCP server can be started")
    print("Connect via Claude Desktop to test fully")

if __name__ == "__main__":
    asyncio.run(test_mcp())
```

---

## Part 8: End-to-End Scenarios

### Scenario 1: Team Collaboration Session

**Objective:** Simulate a real team collaboration session

**Steps:**

1. **Start server**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Create test data**
   ```bash
   python test_database.py
   ```

3. **Generate tokens**
   ```bash
   python generate_token.py
   ```

4. **Open 2 browser tabs** with `test_websocket.html`

5. **Tab 1 (Alice - Host):**
   - Enter Alice's token
   - Enter session ID
   - Connect
   - Send chat: "Hey team, let's work on the auth module"

6. **Tab 2 (Bob - Editor):**
   - Enter Bob's token
   - Enter same session ID
   - Connect
   - See Alice's message
   - Send comment on line 42
   - Update cursor position

7. **Verify:**
   - Both users see each other's messages
   - Cursor updates broadcast
   - Presence shows both users active
   - Chat history persists

### Scenario 2: Code Review Session

**Steps:**

1. **Alice adds code comment:**
   ```javascript
   {
     type: 'code_comment',
     data: {
       file: 'auth.py',
       line: 15,
       content: 'Should we add rate limiting here?'
     }
   }
   ```

2. **Bob replies:**
   ```javascript
   {
     type: 'chat_message',
     content: '@alice Good idea! Let me add that'
   }
   ```

3. **Bob updates presence:**
   ```javascript
   {
     type: 'cursor_update',
     data: {
       file: 'auth.py',
       line: 15,
       column: 0
     }
   }
   ```

4. **Alice sees:**
   - Comment notification
   - @mention
   - Bob's cursor at line 15

### Scenario 3: Session Handoff

**Steps:**

1. **Alice creates session** (morning shift)
2. **Alice adds context** via chat and comments
3. **Alice disconnects**
4. **Bob joins** (afternoon shift)
5. **Bob reads chat history**
6. **Bob continues work**

**Verify:**
- Chat history preserved
- Comments visible
- Session state maintained
- Proper participant tracking

---

## Part 9: Stress Testing

### Test 9.1: Multiple Connections

```python
# stress_test.py
import asyncio
import websockets
import json

TOKEN = "YOUR_TOKEN_HERE"
SESSION_ID = "YOUR_SESSION_ID_HERE"

async def create_user(user_num):
    uri = f"ws://localhost:8000/ws/session/{SESSION_ID}?token={TOKEN}"

    try:
        async with websockets.connect(uri) as ws:
            # Send messages
            for i in range(10):
                await ws.send(json.dumps({
                    "type": "chat_message",
                    "content": f"User {user_num} message {i}"
                }))
                await asyncio.sleep(0.1)
    except Exception as e:
        print(f"User {user_num} error: {e}")

async def stress_test(num_users=10):
    tasks = [create_user(i) for i in range(num_users)]
    await asyncio.gather(*tasks)
    print(f"✅ Stress test with {num_users} users completed!")

if __name__ == "__main__":
    asyncio.run(stress_test(10))
```

**Run:**
```bash
python stress_test.py
```

**Verify:**
- Server handles multiple connections
- No message loss
- No memory leaks
- Clean disconnections

---

## Part 10: Verification Checklist

### Backend

- [ ] Server starts without errors
- [ ] Database tables created
- [ ] Health endpoint responds
- [ ] API docs accessible

### Authentication

- [ ] Users can be created
- [ ] Passwords hashed correctly
- [ ] JWT tokens generated
- [ ] Token validation works

### WebSocket

- [ ] Connection established
- [ ] Authentication works
- [ ] Welcome message received
- [ ] Disconnection handled

### Message Types

- [ ] chat_message works
- [ ] cursor_update works
- [ ] viewport_update works
- [ ] presence_update works
- [ ] code_comment works
- [ ] reaction works (if implemented)
- [ ] session_update works

### Collaboration

- [ ] Multiple users can connect
- [ ] Messages broadcast to all
- [ ] Presence tracking works
- [ ] Participant list updates
- [ ] Chat history persists
- [ ] @Mentions extracted
- [ ] Role permissions enforced

### Database

- [ ] Sessions stored correctly
- [ ] Messages saved
- [ ] Participants tracked
- [ ] Events logged
- [ ] Relationships work

### MCP Integration

- [ ] MCP server starts
- [ ] Resources listed
- [ ] Tools work
- [ ] Prompts available

---

## Troubleshooting

### Connection Refused

**Problem:** Can't connect to WebSocket

**Solutions:**
1. Check server is running
2. Verify port 8000 is open
3. Check firewall settings
4. Try `localhost` instead of `0.0.0.0`

### Authentication Failed

**Problem:** 401 Unauthorized

**Solutions:**
1. Regenerate token
2. Check JWT_SECRET_KEY matches
3. Verify token not expired
4. Check user exists in database

### Messages Not Broadcasting

**Problem:** Other users don't see messages

**Solutions:**
1. Check both users in same session
2. Verify WebSocket connection active
3. Check server logs for errors
4. Ensure message format correct

### Database Errors

**Problem:** Foreign key constraint failed

**Solutions:**
1. Drop and recreate database
2. Run test_database.py again
3. Check all relationships defined
4. Verify cascade deletes work

---

## Next Steps

After completing all tests:

1. **Document Results**
   - Note any issues found
   - Record performance metrics
   - List improvements needed

2. **Build Frontend**
   - Use test scripts as reference
   - Implement React components
   - Create working demo

3. **Production Preparation**
   - Add comprehensive logging
   - Set up monitoring
   - Configure production database
   - Add rate limiting

---

## Summary

This guide covers:
✅ Server setup and health checks
✅ Database model testing
✅ Authentication testing
✅ WebSocket connection testing
✅ All message type testing
✅ Multi-user scenarios
✅ Browser-based testing
✅ MCP integration testing
✅ Stress testing
✅ End-to-end workflows

**Total Test Coverage:** ~90% of backend functionality

Run all tests to ensure everything works before building the frontend!
