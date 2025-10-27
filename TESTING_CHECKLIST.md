# 🧪 Complete Testing Checklist - Pre-Launch

**Goal:** Test every feature systematically before launch

**How to use:** Check off ✅ as you test each item. Note any bugs in the "Issues" column.

---

## 📋 Testing Overview

| Category | Total Tests | Completed | Status |
|----------|-------------|-----------|--------|
| CLI Core | 25 | 0 | ⏳ Not Started |
| Collaboration | 20 | 0 | ⏳ Not Started |
| AI Insights | 10 | 0 | ⏳ Not Started |
| Installation | 5 | 0 | ⏳ Not Started |
| Performance | 8 | 0 | ⏳ Not Started |
| Security | 6 | 0 | ⏳ Not Started |
| **TOTAL** | **74** | **0** | **0%** |

---

## 1️⃣ CLI Core Features (25 tests)

### Session Discovery

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 1.1 | Discover Claude Code sessions | `llm-session list` | Shows active Claude Code sessions | ⬜ |  |
| 1.2 | Discover Cursor sessions | `llm-session list` | Shows active Cursor sessions | ⬜ |  |
| 1.3 | Discover Copilot sessions | `llm-session list` | Shows active Copilot sessions | ⬜ |  |
| 1.4 | No sessions running | `llm-session list` | Shows "No active sessions" | ⬜ |  |
| 1.5 | Multiple sessions | `llm-session list` | Shows all sessions | ⬜ |  |

**How to test:**
```bash
# Open Claude Code, Cursor, or Copilot
# Then run:
poetry run python -m llm_session_manager.cli list

# Expected: Should show all active sessions with:
# - Session ID
# - Type (claude_code, cursor, copilot)
# - Tokens used
# - Health score
```

---

### Token Tracking

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 2.1 | Token count accuracy | `llm-session list` | Shows correct token count | ⬜ |  |
| 2.2 | Token limit tracking | `llm-session list` | Shows usage vs limit (e.g., 164k/200k) | ⬜ |  |
| 2.3 | Token percentage | `llm-session health <id>` | Shows percentage used (e.g., 82%) | ⬜ |  |
| 2.4 | Token updates | Monitor over time | Token count increases as you use AI | ⬜ |  |

**How to test:**
```bash
# Use AI assistant for 5-10 minutes
# Run: poetry run python -m llm_session_manager.cli list
# Note token count
# Use AI assistant more
# Run list again
# Token count should increase
```

---

### Health Monitoring

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 3.1 | Health score calculation | `llm-session health <id>` | Shows health score 0-100% | ⬜ |  |
| 3.2 | Health breakdown | `llm-session health <id>` | Shows factors (tokens, duration, errors) | ⬜ |  |
| 3.3 | Healthy session | Fresh session | Health > 80% | ⬜ |  |
| 3.4 | Unhealthy session | Near token limit | Health < 50% | ⬜ |  |

**How to test:**
```bash
# Fresh session:
poetry run python -m llm_session_manager.cli health <session-id>
# Should show high health (>80%)

# Session near token limit:
# Should show lower health with warnings
```

---

### Export/Import

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 4.1 | Export to JSON | `llm-session export <id> --format json` | Creates JSON file | ⬜ |  |
| 4.2 | Export to YAML | `llm-session export <id> --format yaml` | Creates YAML file | ⬜ |  |
| 4.3 | Export to Markdown | `llm-session export <id> --format md` | Creates MD file | ⬜ |  |
| 4.4 | Import session | `llm-session import-context <file>` | Imports successfully | ⬜ |  |

**How to test:**
```bash
# Export:
poetry run python -m llm_session_manager.cli export <session-id> --format json --output test.json

# Verify:
cat test.json
# Should contain session data

# Import:
poetry run python -m llm_session_manager.cli import-context test.json
```

---

### Cross-Session Memory

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 5.1 | Add memory | `llm-session memory-add <id> "text"` | Saves memory | ⬜ |  |
| 5.2 | Search memory | `llm-session memory-search "query"` | Finds relevant memories | ⬜ |  |
| 5.3 | List memories | `llm-session memory-list` | Shows all memories | ⬜ |  |
| 5.4 | Memory stats | `llm-session memory-stats` | Shows statistics | ⬜ |  |

**How to test:**
```bash
# Add memory:
poetry run python -m llm_session_manager.cli memory-add <session-id> "Implemented JWT authentication using passlib"

# Search:
poetry run python -m llm_session_manager.cli memory-search "authentication"
# Should find the memory we just added

# List:
poetry run python -m llm_session_manager.cli memory-list

# Stats:
poetry run python -m llm_session_manager.cli memory-stats
```

---

### AI Insights (Requires Cognee)

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 6.1 | Get insights | `llm-session insights <id>` | Shows AI recommendations | ⬜ |  |
| 6.2 | Pattern recognition | `llm-session insights <id>` | Identifies patterns | ⬜ |  |
| 6.3 | Recommendations | `llm-session insights <id>` | Provides actionable advice | ⬜ |  |

**How to test:**
```bash
# Set API key:
export LLM_API_KEY="your-openai-or-anthropic-key"

# Get insights:
poetry run python -m llm_session_manager.cli insights <session-id>

# Should show:
# - Health analysis
# - Token usage insights
# - Recommendations
# - Similar sessions
```

---

### Other CLI Commands

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 7.1 | Monitor command | `llm-session monitor` | Shows real-time dashboard | ⬜ |  |
| 7.2 | Tagging | `llm-session tag <id> test` | Adds tag | ⬜ |  |
| 7.3 | Search | `llm-session search "query"` | Finds sessions | ⬜ |  |
| 7.4 | Init command | `llm-session init` | Initializes setup | ⬜ |  |
| 7.5 | Info command | `llm-session info` | Shows info | ⬜ |  |

---

## 2️⃣ Collaboration Features (20 tests)

### Backend Startup

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 8.1 | Backend starts | `cd backend && uvicorn app.main:app` | Starts without errors | ⬜ |  |
| 8.2 | Health check | `curl http://localhost:8000/health` | Returns 200 OK | ⬜ |  |
| 8.3 | API docs | Open http://localhost:8000/docs | Shows Swagger UI | ⬜ |  |
| 8.4 | WebSocket endpoint | Check logs | WebSocket route registered | ⬜ |  |

**How to test:**
```bash
# Terminal 1:
cd backend
uvicorn app.main:app --reload

# Should see:
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000

# Terminal 2:
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# Browser:
open http://localhost:8000/docs
# Should show API documentation
```

---

### Frontend Startup

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 9.1 | Frontend starts | `cd frontend && npm run dev` | Starts without errors | ⬜ |  |
| 9.2 | Home page loads | Open http://localhost:3000 | Shows home page | ⬜ |  |
| 9.3 | No console errors | Check browser console | No errors | ⬜ |  |

**How to test:**
```bash
# Terminal:
cd frontend
npm run dev

# Should see:
# VITE v5.0.8  ready in 500 ms
# ➜  Local:   http://localhost:3000/

# Browser:
open http://localhost:3000
# Press F12 (dev tools)
# Check Console tab
# Should be no errors
```

---

### Authentication

| # | Test | How to Test | Expected Result | Status | Issues |
|---|------|-------------|-----------------|--------|--------|
| 10.1 | Token generation | Run `python3 backend/generate_tokens.py` | Generates 3 tokens | ⬜ |  |
| 10.2 | Valid token login | Use generated token | Logs in successfully | ⬜ |  |
| 10.3 | Invalid token | Use fake token | Shows error | ⬜ |  |
| 10.4 | Expired token | Use old token | Shows error | ⬜ |  |

**How to test:**
```bash
# Generate tokens:
cd backend
python3 generate_tokens.py

# Copy Alice's token
# Go to http://localhost:3000
# Create new session
# Paste token
# Should log in successfully

# Try with fake token:
# Should show "Invalid token" error
```

---

### Real-Time Chat

| # | Test | How to Test | Expected Result | Status | Issues |
|---|------|-------------|-----------------|--------|--------|
| 11.1 | Send message | User A sends message | User B sees it instantly | ⬜ |  |
| 11.2 | Receive message | User B sends message | User A sees it instantly | ⬜ |  |
| 11.3 | Message persistence | Refresh page | Messages still there | ⬜ |  |
| 11.4 | Emoji reactions | React to message | Shows reaction | ⬜ |  |

**How to test:**
```bash
# Browser 1 (Alice):
# Open http://localhost:3000
# Create session
# Login with Alice's token

# Browser 2 (Bob) - use incognito:
# Open http://localhost:3000
# Join same session
# Login with Bob's token

# In Alice's browser:
# Type "Hello Bob!" and send

# In Bob's browser:
# Should see "Hello Bob!" appear immediately

# In Bob's browser:
# Type "Hi Alice!" and send

# In Alice's browser:
# Should see "Hi Alice!" appear immediately
```

---

### Cursor Tracking

| # | Test | How to Test | Expected Result | Status | Issues |
|---|------|-------------|-----------------|--------|--------|
| 12.1 | Update cursor | User A updates cursor | User B sees update | ⬜ |  |
| 12.2 | Cursor position | Check cursor details | Shows file:line:column | ⬜ |  |
| 12.3 | Multiple cursors | 3+ users | Shows all cursors | ⬜ |  |

**How to test:**
```bash
# In Bob's browser:
# Find "Cursor Simulator" section
# Enter:
#   File: main.py
#   Line: 42
#   Column: 10
# Click "Update Cursor"

# In Alice's browser:
# Should see: "Bob is at main.py:42:10"
```

---

### Code Comments

| # | Test | How to Test | Expected Result | Status | Issues |
|---|------|-------------|-----------------|--------|--------|
| 13.1 | Add code comment | User A adds comment | Shows yellow message | ⬜ |  |
| 13.2 | Comment location | Check comment | Shows file:line | ⬜ |  |
| 13.3 | All users see | User B sees comment | Visible to everyone | ⬜ |  |

**How to test:**
```bash
# In Alice's browser:
# Toggle to "Code Comment" mode
# Enter:
#   File: auth.py
#   Line: 125
#   Comment: "Needs review"
# Click Send

# In Bob's browser:
# Should see yellow message: "📝 auth.py:125 - Needs review"
```

---

### Presence System

| # | Test | How to Test | Expected Result | Status | Issues |
|---|------|-------------|-----------------|--------|--------|
| 14.1 | Join notification | User joins | All see "X joined" | ⬜ |  |
| 14.2 | Leave notification | User leaves | All see "X left" | ⬜ |  |
| 14.3 | Presence indicators | Check presence bar | Shows online users | ⬜ |  |
| 14.4 | Status changes | Set idle/away | Status updates | ⬜ |  |

**How to test:**
```bash
# When Bob joins:
# Alice should see: "Bob joined the session"

# When Bob closes browser:
# Alice should see: "Bob left the session"

# Check presence bar:
# Should show:
#   Alice 👑 (Host)
#   Bob ✏️ (Editor)

# In Bob's browser:
# Change status to "away"
# Alice should see Bob's indicator change color
```

---

### WebSocket Connection

| # | Test | How to Test | Expected Result | Status | Issues |
|---|------|-------------|-----------------|--------|--------|
| 15.1 | Initial connection | Open session | Shows "Connected" | ⬜ |  |
| 15.2 | Reconnection | Kill server, restart | Auto-reconnects | ⬜ |  |
| 15.3 | Connection indicator | Check UI | Green when connected | ⬜ |  |

---

## 3️⃣ AI Insights (Cognee) (10 tests)

### Cognee Integration

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 16.1 | Cognee initialization | `llm-session insights <id>` | Initializes without errors | ⬜ |  |
| 16.2 | Graph projection | Check logs | Shows node/edge count | ⬜ |  |
| 16.3 | Session analysis | View output | Shows insights | ⬜ |  |
| 16.4 | Recommendations | View output | Shows actionable advice | ⬜ |  |
| 16.5 | Pattern recognition | Multiple sessions | Identifies patterns | ⬜ |  |
| 16.6 | Historical comparison | View output | Compares to past sessions | ⬜ |  |
| 16.7 | Error handling | Bad session ID | Shows helpful error | ⬜ |  |
| 16.8 | API key missing | No LLM_API_KEY | Shows clear error | ⬜ |  |
| 16.9 | Performance | Time execution | Completes in <30s | ⬜ |  |
| 16.10 | Output quality | Review insights | Helpful and accurate | ⬜ |  |

---

## 4️⃣ Installation & Setup (5 tests)

### One-Command Setup

| # | Test | Command | Expected Result | Status | Issues |
|---|------|---------|-----------------|--------|--------|
| 17.1 | Setup script | `./setup.sh` | Runs without errors | ⬜ |  |
| 17.2 | Prerequisites check | Run setup | Checks Python, Poetry, Node | ⬜ |  |
| 17.3 | Dependency installation | Run setup | Installs all dependencies | ⬜ |  |
| 17.4 | Configuration | Run setup | Creates .env files | ⬜ |  |
| 17.5 | Success message | Run setup | Shows next steps | ⬜ |  |

**How to test:**
```bash
# Fresh environment (use Docker or VM):
./setup.sh

# Should:
# 1. Check Python, Poetry, Node.js
# 2. Install dependencies
# 3. Create configuration files
# 4. Generate test tokens
# 5. Show success message with next steps
```

---

## 5️⃣ Performance (8 tests)

### Load Testing

| # | Test | Tool | Expected Result | Status | Issues |
|---|------|------|-----------------|--------|--------|
| 18.1 | 10 concurrent users | Manual | No lag | ⬜ |  |
| 18.2 | 50 concurrent users | Apache Bench | Response time <1s | ⬜ |  |
| 18.3 | 100 concurrent users | k6/Locust | No crashes | ⬜ |  |
| 18.4 | WebSocket load | 100 connections | Stable | ⬜ |  |
| 18.5 | Memory usage | Check metrics | <500MB | ⬜ |  |
| 18.6 | CPU usage | Check metrics | <50% | ⬜ |  |
| 18.7 | Database queries | Check logs | Optimized | ⬜ |  |
| 18.8 | API response time | Measure | <500ms | ⬜ |  |

**How to test:**
```bash
# Simple load test:
ab -n 1000 -c 10 http://localhost:8000/health

# Results should show:
# - All requests successful
# - Average response time < 100ms
# - No errors
```

---

## 6️⃣ Security (6 tests)

### Security Checks

| # | Test | Tool | Expected Result | Status | Issues |
|---|------|------|-----------------|--------|--------|
| 19.1 | SQL injection | Manual | Protected | ⬜ |  |
| 19.2 | XSS protection | Manual | Sanitized | ⬜ |  |
| 19.3 | CSRF tokens | Check headers | Present | ⬜ |  |
| 19.4 | Rate limiting | Spam requests | Gets limited | ⬜ |  |
| 19.5 | JWT validation | Invalid token | Rejected | ⬜ |  |
| 19.6 | HTTPS/SSL | Check connection | Secure | ⬜ |  |

---

## 🐛 Bug Tracking Template

When you find a bug, document it here:

### Bug #1
- **Severity:** Critical / High / Medium / Low
- **Component:** CLI / Backend / Frontend / AI
- **Description:** [What's wrong?]
- **Steps to Reproduce:**
  1. Step 1
  2. Step 2
  3. Step 3
- **Expected:** [What should happen?]
- **Actual:** [What actually happens?]
- **Screenshots:** [If applicable]
- **Status:** Open / In Progress / Fixed
- **Fixed in:** [Version/commit]

---

## ✅ Testing Sessions Log

### Session 1: [Date]
- **Tester:** [Name]
- **Duration:** [Time]
- **Tests Completed:** [X/74]
- **Bugs Found:** [Count]
- **Notes:** [Key findings]

### Session 2: [Date]
- **Tester:** [Name]
- **Duration:** [Time]
- **Tests Completed:** [X/74]
- **Bugs Found:** [Count]
- **Notes:** [Key findings]

---

## 🎯 Testing Priority

### P0 (Critical - Must Fix Before Launch)
- CLI session discovery
- Token tracking
- Backend/frontend startup
- WebSocket connection
- Payment flow

### P1 (High - Fix Before Launch)
- All collaboration features
- AI insights
- Export/import
- Authentication

### P2 (Medium - Fix Soon After Launch)
- Performance optimization
- Edge cases
- UX improvements

### P3 (Low - Nice to Have)
- Additional features
- Polish
- Minor bugs

---

## 📊 Progress Tracking

Update daily:

**Day 1:** 0/74 tests (0%)
**Day 2:** __/74 tests (__%)
**Day 3:** __/74 tests (__%)
**Day 4:** __/74 tests (__%)
**Day 5:** __/74 tests (__%)
**Day 6:** __/74 tests (__%)
**Day 7:** __/74 tests (__%)

**Goal:** 74/74 tests (100%) by end of Week 1

---

## 🚀 Ready to Test!

Let's start with **Day 1: CLI Core Features**

Run through tests 1.1 - 7.5 systematically.

**Ready?** Let me know which feature you want to test first! 🧪
