# Quick Integration Test Guide

Test the CLI-to-Web integration in 3 minutes!

---

## Prerequisites

✅ Backend running on port 8000
✅ Frontend dependencies installed (`npm install` in frontend/)
✅ Test users in database (alice, bob, charlie)

---

## Option 1: Quick Frontend Test (No Sharing)

**Step 1: Start Frontend**
```bash
cd frontend
npm run dev
```

**Step 2: Get Test Tokens**
```bash
cd backend
python3 generate_tokens.py
```

**Step 3: Open Browser**
```
http://localhost:3000/session/claude_code_65260_1760808775
```

**Step 4: Login**
- Username: `alice`
- Token: [Paste Alice's token from step 2]

**Expected Result:**
- ✅ SessionMetrics component displays
- ✅ Shows token count, health score, metrics
- ✅ Data auto-refreshes every 5 seconds

---

## Option 2: Full Share Command Test

**Step 1: Share a Session**
```bash
# Terminal 1 - Run share command
poetry run python -m llm_session_manager.cli share 65260
```

This will:
- Export the session to collaboration DB
- Start backend server (if not running)
- Start real-time sync (every 5s)
- Open browser automatically to: `http://localhost:3000/session/[session-id]`

**Step 2: Login**
- Username: `alice`
- Token: [Get from `backend/test_tokens.txt` or run `python3 backend/generate_tokens.py`]

**Step 3: Open Second Browser** (Incognito/Private)
- Go to the same URL
- Username: `bob`
- Token: [Paste Bob's token]

**Expected Result:**
- ✅ Both users see the same session metrics
- ✅ SessionMetrics shows real-time data
- ✅ Token count updates every 5 seconds
- ✅ Health score displays with color coding
- ✅ Both users can chat while viewing metrics

---

## What You Should See

### SessionMetrics Component

```
┌──────────────────────────────────────────┐
│  📊 Session Metrics                      │
├──────────────────────────────────────────┤
│  Token Usage                             │
│  [██░░░░░░░░░░] 0 / 200,000 (0%)         │
│                                          │
│  Health Score: 💚 100%                   │
│                                          │
│  Messages: 0  │  Files: 0  │  Errors: 0  │
│                                          │
│  Working Dir: /Users/gagan/llm-session…  │
│  Type: claude_code  │  PID: 65260        │
│  Last Updated: 2 seconds ago             │
└──────────────────────────────────────────┘
```

### Color Coding

**Token Usage:**
- Green: 0-70%
- Yellow: 70-90%
- Red: 90-100%

**Health Score:**
- 💚 Green (80-100%): Healthy
- 💛 Yellow (60-80%): Warning
- 🔴 Red (0-60%): Critical

---

## Troubleshooting

### "Session not found" Error

**Check if session was exported:**
```bash
curl http://localhost:8000/api/sessions/claude_code_65260_1760808775
```

If empty response, re-run export:
```bash
bash test_export_only.sh
```

### Frontend Won't Start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend Error "User not found"

Generate tokens and reinitialize database:
```bash
cd backend
python3 init_database.py
python3 generate_tokens.py
```

### Token Expired

Tokens are valid for 8 hours. Regenerate:
```bash
python3 backend/generate_tokens.py
```

---

## Testing Real-time Sync

**Step 1: Start Share Command**
```bash
poetry run python -m llm_session_manager.cli share 65260
```

**Step 2: Open Browser to Session**
Wait for the share command to open browser automatically.

**Step 3: Trigger Token Usage**
In the Claude Code session (PID 65260), perform actions that use tokens:
- Send messages
- Edit files
- Run commands

**Step 4: Watch Metrics Update**
- Token count should increase within 5 seconds
- Health score may change based on usage
- Last updated timestamp refreshes

---

## Verifying API Responses

**Get Session Data:**
```bash
curl http://localhost:8000/api/sessions/claude_code_65260_1760808775 | python3 -m json.tool
```

**List All Sessions:**
```bash
curl http://localhost:8000/api/sessions | python3 -m json.tool
```

**Check WebSocket Status:**
```bash
curl http://localhost:8000/health
```

---

## Success Criteria

After testing, you should have:

- ✅ Session exported from CLI to web database
- ✅ Backend API returning session data
- ✅ Frontend displaying SessionMetrics component
- ✅ Metrics auto-refreshing every 5 seconds
- ✅ Multiple users can view the same session
- ✅ Real-time sync updating data (if using share command)
- ✅ Chat and collaboration features working alongside metrics

---

## Next Steps

Once integration testing is complete, you can:

1. **Add More Sessions**
   ```bash
   poetry run python -m llm_session_manager.cli share <session-id>
   ```

2. **Test with Multiple Sessions**
   - Share multiple CLI sessions
   - Switch between them in the web UI

3. **Test Collaboration Features**
   - Chat between users viewing a session
   - Add code comments
   - Track cursor positions
   - Test presence status

4. **Production Deployment**
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guide
   - Configure environment variables
   - Set up persistent database
   - Deploy to cloud hosting

---

## Quick Commands Reference

```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev

# Generate tokens
python3 backend/generate_tokens.py

# Share a session
poetry run python -m llm_session_manager.cli share <pid-or-session-id>

# Export session without sharing
bash test_export_only.sh

# List active sessions
poetry run python -m llm_session_manager.cli list

# Check session in database
curl http://localhost:8000/api/sessions/<session-id>
```

---

For comprehensive testing documentation, see [TEST_END_TO_END.md](TEST_END_TO_END.md).

For integration architecture details, see [INTEGRATION_TEST_RESULTS.md](INTEGRATION_TEST_RESULTS.md).
