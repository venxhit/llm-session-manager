# CLI ↔ Web Integration Plan

## Goal

Connect the CLI tool (which monitors real LLM sessions) with the web collaboration interface, so teammates can see and collaborate on your actual coding sessions.

## Current Real Sessions Detected

```
✅ claude_code_1227 (PID 1227)    - Claude Desktop - 42h running
✅ claude_code_98703 (PID 98703)  - Claude updater  - 22h running
✅ cursor_cli_60433 (PID 60433)   - Cursor         - 1h 33m running
✅ claude_code_65260 (PID 65260)  - Claude Code    - 1h 17m (current!)
✅ claude_code_66393 (PID 66393)  - Claude Code    - 1h 13m running
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  USER'S MACHINE                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐                                       │
│  │  Claude Code         │◄─── Your actual coding session        │
│  │  (PID 65260)         │                                       │
│  └──────────┬───────────┘                                       │
│             │                                                    │
│             │ monitors                                           │
│             ↓                                                    │
│  ┌──────────────────────┐                                       │
│  │  CLI Tool            │                                       │
│  │  llm-session-manager │                                       │
│  └──────────┬───────────┘                                       │
│             │                                                    │
│             │ 1. Discovers session                              │
│             │ 2. Exports to DB                                  │
│             │ 3. Starts web server                              │
│             │ 4. Real-time sync                                 │
│             ↓                                                    │
│  ┌──────────────────────┐       ┌────────────────────┐         │
│  │  Collaboration DB    │◄──────┤  Web Backend       │         │
│  │  (SQLite)            │       │  (FastAPI)         │         │
│  └──────────────────────┘       └────────┬───────────┘         │
│                                           │                      │
│                                           │ WebSocket            │
│                                           ↓                      │
│                                  ┌────────────────────┐         │
│                                  │  Frontend (React)  │         │
│                                  └────────────────────┘         │
└──────────────────────────────────────────┬───────────────────────┘
                                           │
                                           │ http://localhost:3000
                                           ↓
                                  ┌────────────────────┐
                                  │  Teammate Browser  │
                                  │                    │
                                  │  Sees:             │
                                  │  • Your session    │
                                  │  • Token usage     │
                                  │  • Files           │
                                  │  • Can chat        │
                                  └────────────────────┘
```

## Implementation Steps

### 1. Session Export Service

**File:** `llm_session_manager/services/session_exporter.py`

```python
class SessionExporter:
    """Export CLI sessions to collaboration database."""

    def export_session(self, session: Session) -> str:
        """
        Export a CLI session to web collaboration DB.
        Returns: collaboration_session_id
        """
        # Convert CLI session → Web SessionModel
        # Save to collaboration DB
        # Return new ID

    def sync_session_updates(self, session_id: str):
        """
        Continuously sync session updates.
        Monitors CLI session and pushes updates to web.
        """
```

### 2. CLI Share Command

**File:** `llm_session_manager/cli.py`

```python
@app.command()
def share(
    session_id: str,
    port: int = 8000,
    auto_open: bool = True
):
    """
    Share a session for real-time collaboration.

    Example:
        llm-session-manager share claude_code_65260
    """
    # 1. Get session from discovery
    # 2. Export to collaboration DB
    # 3. Start web server (if not running)
    # 4. Start real-time sync
    # 5. Generate share URL
    # 6. Print instructions
```

### 3. Real-Time Sync

**File:** `llm_session_manager/services/realtime_sync.py`

```python
class RealtimeSync:
    """Sync CLI session data to web in real-time."""

    def start_sync(self, session_id: str):
        """
        Start background sync for session.

        Updates every 5 seconds:
        - Token count
        - Health score
        - Last activity
        - Files modified
        """

    def stop_sync(self, session_id: str):
        """Stop syncing a session."""
```

### 4. Web UI Updates

**File:** `frontend/src/pages/CollaborativeSession.jsx`

Add real session data display:
- Show actual token count (live)
- Show health score
- Show files being worked on
- Show session duration
- Show token usage chart

### 5. WebSocket Session Events

**File:** `backend/app/websocket.py`

Add new message types:
- `session_data_update` - Real session metrics
- `session_health_update` - Health changes
- `session_file_update` - File modifications

## User Experience

### Before Integration (Current)

```bash
# Terminal 1: Monitor sessions
python -m llm_session_manager.cli monitor

# Terminal 2: Start collaboration (unrelated)
cd backend && uvicorn app.main:app --reload

# Problem: Teammate can't see your actual sessions!
```

### After Integration (Goal)

```bash
# Terminal 1: Share your actual session
python -m llm_session_manager.cli share claude_code_65260

# Output:
# ✅ Session exported to collaboration
# 🚀 Starting web server...
# 🔗 Share this link: http://localhost:3000/session/claude_code_65260
#
# Teammates can now:
#  • See your token usage (247,730 / 200,000)
#  • View session health (60%)
#  • See files you're working on
#  • Chat with you in real-time
#
# Press Ctrl+C to stop sharing
```

Teammate opens link and sees:

```
┌──────────────────────────────────────────────────────────┐
│  Session: claude_code_65260 (Gagan's Session)           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Status: 🟢 Active                                       │
│  Duration: 1h 17m                                        │
│  Type: Claude Code (Cursor)                             │
│                                                           │
│  Token Usage: 247,730 / 200,000 (124%) ⚠️               │
│  Health: 60% ⚠️                                          │
│                                                           │
│  Files:                                                  │
│   • backend/app/models.py (modified 2m ago)             │
│   • backend/app/websocket.py (modified 5m ago)          │
│   • INTEGRATION_PLAN.md (modified now)                  │
│                                                           │
│  Chat: [Gagan is typing...]                             │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Implementation Order

1. ✅ **Session Export Service** - Convert CLI sessions to web format
2. ✅ **Database Bridge** - Connect CLI SQLite to Web SQLite
3. ✅ **Share Command** - CLI command to start sharing
4. ✅ **Real-time Sync** - Background process to sync updates
5. ✅ **Web UI Updates** - Display real session data
6. ✅ **End-to-End Test** - Share actual session, teammate joins

## Benefits

### For You (Session Owner)
- Share sessions with one command
- Keep using CLI as normal
- Teammates see what you're working on
- Get help without screen sharing

### For Teammates
- See actual token usage
- Know when to help (health warnings)
- See which files are being modified
- Chat directly in context
- No need for Zoom/Slack separately

### For Teams
- Collaborative debugging
- Real-time code reviews
- Mentoring sessions
- Pair programming
- Knowledge sharing

## Technical Considerations

### Database Strategy

Two options:

**Option A: Shared Database (Simpler)**
```
llm_session_manager/
├── sessions.db          # CLI sessions (SQLite)
└── collaboration.db     # Web collaboration (SQLite)

SessionExporter copies from sessions.db → collaboration.db
```

**Option B: Single Database (Better)**
```
llm_session_manager/
└── sessions.db          # Single SQLite database

Both CLI and Web use same database
Add collaboration tables to existing schema
```

**Recommendation:** Option B (single database)

### Process Management

**Option A: CLI Manages Everything**
```bash
llm-session-manager share session_id
# Starts web server
# Starts sync process
# Blocks until Ctrl+C
```

**Option B: Separate Processes**
```bash
# Terminal 1: Web server (always running)
llm-session-manager serve

# Terminal 2: Share a session
llm-session-manager share session_id
```

**Recommendation:** Option A (simpler UX)

### Security

- Generate unique share tokens per session
- Expire tokens after 24 hours
- Only owner can share sessions
- Viewers need valid token to join
- Rate limit connections

## Next Steps

Should I proceed with implementation in this order:

1. **Session Exporter** (30 min)
   - Convert Session → SessionModel
   - Save to collaboration DB

2. **Share Command** (20 min)
   - Add CLI command
   - Auto-start server if needed
   - Generate share link

3. **Real-time Sync** (45 min)
   - Background process
   - WebSocket updates
   - Token/health sync

4. **Web UI Updates** (30 min)
   - Display real session data
   - Show live metrics
   - File list

5. **Testing** (15 min)
   - Share real session
   - Verify teammate sees it
   - Test chat + metrics

**Total: ~2.5 hours**

---

Ready to build this integration?
