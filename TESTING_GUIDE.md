# LLM Session Manager - Complete Testing Guide

## 🧪 Step-by-Step Testing Instructions

This guide will walk you through testing every component of the LLM Session Manager.

---

## 📋 Prerequisites

Before testing, ensure you have:
```bash
# Check Python version (3.10+)
python --version

# Check Poetry is installed
poetry --version

# In the project directory
cd /Users/gagan/llm-session-manager
```

---

## 🎯 Testing Workflow

### **Phase 1: Component Tests** (Bottom-Up)
### **Phase 2: Integration Tests** (Components Together)
### **Phase 3: CLI Tests** (User Interface)
### **Phase 4: End-to-End Tests** (Full Workflow)

---

## ✅ Phase 1: Component Tests

### **Test 1: Data Models**
Test that Session and Memory models work correctly.

```bash
# Run Python REPL
python

# Test Session model
>>> from llm_session_manager.models import Session, SessionType, SessionStatus
>>> from datetime import datetime
>>>
>>> # Create a session
>>> session = Session(
...     id="test_1",
...     pid=12345,
...     type=SessionType.CLAUDE_CODE,
...     status=SessionStatus.ACTIVE,
...     working_directory="/test"
... )
>>>
>>> # Test to_dict()
>>> data = session.to_dict()
>>> print(data['type'])  # Should print: claude_code
>>>
>>> # Test from_dict()
>>> session2 = Session.from_dict(data)
>>> print(session2.id)  # Should print: test_1
>>>
>>> # Exit
>>> exit()
```

**Expected Result:**
- ✅ Session creates successfully
- ✅ to_dict() returns dictionary
- ✅ from_dict() recreates session
- ✅ No errors

---

### **Test 2: Database Layer**
Test SQLite database operations.

```bash
# Run the database test
python << 'EOF'
from llm_session_manager.storage.database import Database
from llm_session_manager.models import Session, SessionType, SessionStatus
from datetime import datetime

# Initialize database
db = Database("data/test_sessions.db")
db.init_db()

# Create test session
session = Session(
    id="test_session_1",
    pid=99999,
    type=SessionType.CLAUDE_CODE,
    status=SessionStatus.ACTIVE,
    working_directory="/test",
    token_count=5000,
    health_score=85.0
)

# Add session
db.add_session(session)
print("✓ Session added to database")

# Retrieve session
retrieved = db.get_session("test_session_1")
print(f"✓ Retrieved session: {retrieved.id}, tokens: {retrieved.token_count}")

# Get all sessions
all_sessions = db.get_all_sessions()
print(f"✓ Total sessions in DB: {len(all_sessions)}")

# Add history entry
db.add_history_entry("test_session_1", 5000, 85.0, "active")
print("✓ History entry added")

# Get history
history = db.get_session_history("test_session_1")
print(f"✓ History entries: {len(history)}")

# Clean up
db.delete_session("test_session_1")
print("✓ Session deleted")

print("\n✅ Database tests passed!")
EOF
```

**Expected Result:**
```
✓ Session added to database
✓ Retrieved session: test_session_1, tokens: 5000
✓ Total sessions in DB: 1
✓ History entry added
✓ History entries: 1
✓ Session deleted

✅ Database tests passed!
```

---

### **Test 3: Session Discovery**
Test process discovery with your existing test script.

```bash
python test_discovery.py
```

**Expected Result:**
```
======================================================================
LLM Session Discovery Test
======================================================================

Scanning for running LLM assistant processes...

✅ Found X session(s):

Session 1:
  ID:          cursor_cli_1326_...
  Type:        cursor_cli
  PID:         1326
  Status:      active
  ...
```

**Verify:**
- ✅ Finds your active Claude Code session
- ✅ Shows correct PID
- ✅ Identifies session type correctly
- ✅ Extracts working directory

---

### **Test 4: Token Estimation**
Test token counting and file scanning.

```bash
python test_token_estimator.py
```

**Expected Result:**
```
======================================================================
Token Estimator Test
======================================================================

Session: test_session_1
Working Directory: /Users/gagan/llm-session-manager
Message Count: 25

Estimating tokens...

Token Breakdown:
  Base Tokens:      1,000
  Message Tokens:   5,000 (25 × 200)
  File Tokens:      XX,XXX
  ----------------------------------------
  Total Estimate:   XX,XXX tokens

Token Usage:
  Current:          XX,XXX tokens
  Limit:            200,000 tokens
  Usage:            X.X%
  Critical? (>90%): ✅ No
```

**Verify:**
- ✅ Scans project files
- ✅ Estimates tokens correctly
- ✅ Calculates percentages
- ✅ Shows cache statistics

---

### **Test 5: Health Monitor**
Test health scoring system.

```bash
python test_health_monitor.py
```

**Expected Result:**
```
======================================================================
Health Monitor Test
======================================================================

Testing various session health scenarios...

Session: Healthy Session
✅ Overall Health: 98.8% - HEALTHY
Component Scores:
  Token        [████████████████████] 100.0%
  Duration     [████████████████████] 100.0%
  ...

Session: Critical Session
🔴 Overall Health: 22.5% - CRITICAL
...
🔄 RESTART RECOMMENDED: Critical health score
💤 WARNING: Session appears to be stale/abandoned
```

**Verify:**
- ✅ Calculates health scores correctly
- ✅ Shows component breakdowns
- ✅ Provides recommendations
- ✅ Different scenarios produce different results

---

### **Test 6: Dashboard (Single Refresh)**
Test dashboard rendering without live mode.

```bash
python test_dashboard.py
```

**Expected Result:**
```
Initializing LLM Session Manager Dashboard...

╭──────────────────────────────────────────────────────────╮
│          🖥️  LLM Session Manager - Dashboard             │
│          Total Sessions: X  •  Active: X  •  Idle: 0     │
╰──────────────────────────────────────────────────────────╯

                      Active Sessions
┏━━━━━━━━━┳━━━━━━┳━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ ID      ┃ Type ┃ PI ┃ Statu ┃ Durati ┃ Tokens  ┃ Healt ┃
┡━━━━━━━━━╇━━━━━━╇━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ ...     │ ...  │... │ ...   │ ...    │ ...     │ ...   │
└─────────┴──────┴────┴───────┴────────┴─────────┴───────┘

Sessions discovered: X
```

**Verify:**
- ✅ Dashboard renders correctly
- ✅ Sessions appear in table
- ✅ Colors and emojis display
- ✅ Token bars show correctly

---

## ✅ Phase 2: Integration Tests

### **Test 7: Discovery + Token + Health**
Test components working together.

```bash
python << 'EOF'
from llm_session_manager.core.session_discovery import SessionDiscovery
from llm_session_manager.core.health_monitor import HealthMonitor
from llm_session_manager.utils.token_estimator import TokenEstimator

print("Testing integrated workflow...\n")

# Initialize components
discovery = SessionDiscovery()
health_monitor = HealthMonitor()
token_estimator = TokenEstimator()

# Discover sessions
print("1. Discovering sessions...")
sessions = discovery.discover_sessions()
print(f"   ✓ Found {len(sessions)} session(s)")

# Update tokens
print("2. Estimating tokens...")
token_estimator.update_token_counts(sessions)
for s in sessions:
    print(f"   ✓ Session {s.pid}: {s.token_count:,} tokens")

# Update health
print("3. Calculating health...")
health_monitor.update_health_scores(sessions)
for s in sessions:
    status = health_monitor.get_health_status(s.health_score / 100)
    print(f"   ✓ Session {s.pid}: {s.health_score:.0f}% ({status})")

print("\n✅ Integration test passed!")
EOF
```

**Expected Result:**
```
Testing integrated workflow...

1. Discovering sessions...
   ✓ Found 2 session(s)
2. Estimating tokens...
   ✓ Session 1326: 6,977,329 tokens
   ✓ Session 28373: 32,068 tokens
3. Calculating health...
   ✓ Session 1326: 42% (warning)
   ✓ Session 28373: 86% (healthy)

✅ Integration test passed!
```

---

### **Test 8: Database + Discovery**
Test saving discovered sessions to database.

```bash
python << 'EOF'
from llm_session_manager.storage.database import Database
from llm_session_manager.core.session_discovery import SessionDiscovery

print("Testing database integration...\n")

# Initialize
db = Database("data/test_integration.db")
db.init_db()
discovery = SessionDiscovery()

# Discover and save
print("1. Discovering sessions...")
sessions = discovery.discover_sessions()
print(f"   ✓ Found {len(sessions)} session(s)")

print("2. Saving to database...")
for session in sessions:
    db.add_session(session)
    print(f"   ✓ Saved session {session.id[:20]}...")

print("3. Retrieving from database...")
saved_sessions = db.get_all_sessions()
print(f"   ✓ Retrieved {len(saved_sessions)} session(s)")

print("\n✅ Database integration test passed!")
EOF
```

**Expected Result:**
```
Testing database integration...

1. Discovering sessions...
   ✓ Found 2 session(s)
2. Saving to database...
   ✓ Saved session cursor_cli_1326_...
   ✓ Saved session claude_code_28373...
3. Retrieving from database...
   ✓ Retrieved 2 session(s)

✅ Database integration test passed!
```

---

## ✅ Phase 3: CLI Tests

### **Test 9: CLI Help**
Test that all commands are registered.

```bash
python -m llm_session_manager.cli --help
```

**Expected Result:**
```
Usage: python -m llm_session_manager.cli [OPTIONS] COMMAND [ARGS]...

LLM Session Manager - Track and manage AI coding assistant sessions

╭─ Commands ───────────────────────────────────────────────╮
│ monitor          Start the real-time dashboard...        │
│ list             List all active LLM coding sessions.    │
│ export           Export session context to a JSON file.  │
│ import-context   Import session context from a JSON...   │
│ health           Show detailed health breakdown...       │
│ info             Show information about the tool.        │
╰──────────────────────────────────────────────────────────╯
```

**Verify:**
- ✅ All 6 commands appear
- ✅ Help text is clear
- ✅ No errors

---

### **Test 10: CLI List Command**
Test listing sessions.

```bash
# Table format (default)
python -m llm_session_manager.cli list

# JSON format
python -m llm_session_manager.cli list --format json

# Filter by status
python -m llm_session_manager.cli list --status active
```

**Expected Result:**
- ✅ Shows sessions in table format
- ✅ JSON format is valid
- ✅ Filtering works
- ✅ Colors and emojis display

---

### **Test 11: CLI Export Command**
Test exporting session context.

```bash
# Export a session (use actual session ID from list command)
python -m llm_session_manager.cli export claude_code_28373 --output test_export.json

# Verify the file was created
ls -lh test_export.json

# View the exported JSON
cat test_export.json | head -30
```

**Expected Result:**
```
✓ Session exported to: test_export.json
  Session ID: claude_code_28373_...
  Type: claude_code
  Tokens: 32,068
  Health: 86%
```

**Verify:**
- ✅ File is created
- ✅ JSON is valid
- ✅ Contains all expected fields
- ✅ File list is populated

---

### **Test 12: CLI Import Command**
Test importing session context.

```bash
# Import the previously exported session
python -m llm_session_manager.cli import-context test_export.json

# Try with session ID override
python -m llm_session_manager.cli import-context test_export.json --session-id custom-123
```

**Expected Result:**
```
✓ Context imported successfully!

╭────────────── Imported Session Context ──────────────╮
│ Session ID: claude_code_28373_...                   │
│ Type: claude_code                                    │
│ Tokens: 32,068                                       │
│ Health: 86%                                          │
│ Files: X files                                       │
╰──────────────────────────────────────────────────────╯
```

**Verify:**
- ✅ Imports successfully
- ✅ Displays session info
- ✅ Session ID override works
- ✅ Validates JSON format

---

### **Test 13: CLI Health Command**
Test detailed health analysis.

```bash
# Get health details for a session
python -m llm_session_manager.cli health claude_code_28373
```

**Expected Result:**
```
Health Report: claude_code_28373_...

╭─────────────── Overall Health ───────────────╮
│ ✅ 85.5% - HEALTHY                           │
╰──────────────────────────────────────────────╯

Component Scores:
  Token       ████████████████████    100%
  Duration    █████░░░░░░░░░░░░░░░     28%
  Activity    ████████████████████    100%
  Errors      ████████████████████    100%

Metrics:
  Duration:        11.3 hours
  Idle Time:       0.0 minutes
  Token Usage:     14.9%
  Error Count:     0

⚠️  Recommendations:
  • Session has been running for a long time...
```

**Verify:**
- ✅ Shows overall health
- ✅ Component bars display correctly
- ✅ Metrics are accurate
- ✅ Recommendations appear

---

### **Test 14: CLI Info Command**
Test tool information display.

```bash
python -m llm_session_manager.cli info
```

**Expected Result:**
```
LLM Session Manager
Version: 0.1.0

A CLI tool for tracking and managing multiple AI coding assistant sessions.

Features:
  • Real-time session monitoring
  • Token usage tracking
  • Health scoring
  • Context export/import

Commands:
  monitor       - Start the real-time dashboard
  list          - List all active sessions
  ...
```

**Verify:**
- ✅ Version displays
- ✅ Features listed
- ✅ Commands listed

---

### **Test 15: CLI Monitor Command (Interactive)**
Test the live dashboard.

```bash
# Start the interactive dashboard
python -m llm_session_manager.cli monitor
```

**What to Test:**
1. **Dashboard appears** - Header, table, footer visible
2. **Auto-refresh works** - Data updates every 5 seconds
3. **Press 'r'** - Forces immediate refresh
4. **Press 'h'** - Shows help panel
5. **Press 'q'** - Exits gracefully

**Expected Behavior:**
- ✅ Dashboard starts and displays sessions
- ✅ Auto-refresh updates data
- ✅ Keyboard controls work
- ✅ Clean exit on 'q'

---

## ✅ Phase 4: End-to-End Tests

### **Test 16: Complete Workflow**
Test the entire user journey.

```bash
#!/bin/bash

echo "🧪 End-to-End Test - Complete Workflow"
echo "========================================"
echo ""

# Step 1: List sessions
echo "Step 1: List active sessions"
python -m llm_session_manager.cli list
echo ""
read -p "Press Enter to continue..."

# Step 2: Get session ID from user
echo ""
echo "Step 2: Copy a session ID from above"
read -p "Enter session ID (or partial): " SESSION_ID

# Step 3: Check health
echo ""
echo "Step 3: Check session health"
python -m llm_session_manager.cli health "$SESSION_ID"
echo ""
read -p "Press Enter to continue..."

# Step 4: Export session
echo ""
echo "Step 4: Export session context"
python -m llm_session_manager.cli export "$SESSION_ID" --output test_workflow.json
echo ""
read -p "Press Enter to continue..."

# Step 5: View export
echo ""
echo "Step 5: View exported file"
cat test_workflow.json | head -40
echo ""
read -p "Press Enter to continue..."

# Step 6: Import session
echo ""
echo "Step 6: Import session context"
python -m llm_session_manager.cli import-context test_workflow.json
echo ""

# Step 7: View in JSON format
echo ""
echo "Step 7: View sessions as JSON"
python -m llm_session_manager.cli list --format json | head -50
echo ""

echo "✅ End-to-end test complete!"
```

Save this as `test_e2e.sh` and run:
```bash
chmod +x test_e2e.sh
./test_e2e.sh
```

---

## ✅ Phase 5: Error Handling Tests

### **Test 17: Invalid Session ID**
Test error handling for non-existent sessions.

```bash
# Try to export non-existent session
python -m llm_session_manager.cli export invalid_session_123

# Expected: Error message, exit code 1
```

**Expected Result:**
```
Session 'invalid_session_123' not found.
```

---

### **Test 18: Invalid JSON Import**
Test error handling for corrupt JSON.

```bash
# Create invalid JSON
echo "{ invalid json }" > invalid.json

# Try to import
python -m llm_session_manager.cli import-context invalid.json

# Expected: Error message about invalid JSON
```

**Expected Result:**
```
Invalid JSON format: ...
```

---

### **Test 19: Missing File**
Test error handling for missing files.

```bash
# Try to import non-existent file
python -m llm_session_manager.cli import-context nonexistent.json

# Expected: Error message
```

**Expected Result:**
```
File not found: nonexistent.json
```

---

### **Test 20: No Sessions Found**
Test behavior when no sessions are running.

**Setup:**
```bash
# Close all Claude Code and Cursor sessions
# Then run:
python -m llm_session_manager.cli list
```

**Expected Result:**
```
No active sessions found.
```

---

## 📊 Testing Checklist

Use this checklist to track your testing progress:

```
Component Tests:
[ ] Test 1: Data Models
[ ] Test 2: Database Layer
[ ] Test 3: Session Discovery
[ ] Test 4: Token Estimation
[ ] Test 5: Health Monitor
[ ] Test 6: Dashboard (Single Refresh)

Integration Tests:
[ ] Test 7: Discovery + Token + Health
[ ] Test 8: Database + Discovery

CLI Tests:
[ ] Test 9: CLI Help
[ ] Test 10: CLI List Command
[ ] Test 11: CLI Export Command
[ ] Test 12: CLI Import Command
[ ] Test 13: CLI Health Command
[ ] Test 14: CLI Info Command
[ ] Test 15: CLI Monitor Command (Interactive)

End-to-End Tests:
[ ] Test 16: Complete Workflow

Error Handling Tests:
[ ] Test 17: Invalid Session ID
[ ] Test 18: Invalid JSON Import
[ ] Test 19: Missing File
[ ] Test 20: No Sessions Found
```

---

## 🐛 Troubleshooting

### **Issue: "Module not found" errors**
```bash
# Solution: Make sure you're in the project directory
cd /Users/gagan/llm-session-manager

# And Python can find the module
export PYTHONPATH=/Users/gagan/llm-session-manager:$PYTHONPATH
```

### **Issue: Permission denied errors during token estimation**
```bash
# This is normal! Token estimator tries to read system files
# These errors are caught and logged, but don't affect functionality
# You'll see: [Errno 13] Permission denied: '/private/etc/...'
# This is expected behavior
```

### **Issue: No sessions found**
```bash
# Make sure you have Claude Code or Cursor running
# The tool looks for processes containing "claude" or "cursor"
```

### **Issue: Dashboard not refreshing**
```bash
# Press 'r' to force refresh
# Or restart the dashboard
```

---

## 🎯 Quick Test (5 minutes)

If you're short on time, run this quick test:

```bash
# 1. List sessions
python -m llm_session_manager.cli list

# 2. Export a session (use ID from step 1)
python -m llm_session_manager.cli export <session-id> -o quick_test.json

# 3. Import it back
python -m llm_session_manager.cli import-context quick_test.json

# 4. Check health
python -m llm_session_manager.cli health <session-id>

# If all 4 work, you're good! ✅
```

---

## 📝 Test Results Template

After testing, document your results:

```
# Test Results - [Date]

## Environment
- Python Version:
- OS:
- Sessions Found:

## Test Results
Component Tests: X/6 passed
Integration Tests: X/2 passed
CLI Tests: X/7 passed
End-to-End Tests: X/1 passed
Error Handling Tests: X/4 passed

Total: X/20 passed

## Issues Found
1. [Description]
2. [Description]

## Notes
[Any additional observations]
```

---

## ✅ Success Criteria

Your testing is complete when:
- ✅ All 20 tests pass
- ✅ No unhandled exceptions
- ✅ Sessions are discovered correctly
- ✅ Token estimation works
- ✅ Health scores calculate properly
- ✅ Export/import preserves data
- ✅ Dashboard displays correctly
- ✅ Error messages are helpful

---

## 🚀 Next Steps

After testing is complete:
1. **Document any bugs** - Create issues for problems found
2. **Fix critical issues** - Address blocking problems
3. **Move to Step 9** - Context export/import enhancements
4. **Continue building** - Cross-session memory, config, etc.

---

## 📞 Need Help?

If tests fail:
1. Check the error messages carefully
2. Review the component code
3. Add more logging to debug
4. Test components in isolation
5. Ask for help with specific errors

Good luck with testing! 🎉
