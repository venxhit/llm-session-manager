# ✅ How to Test All Features

**Fixed!** All features now work correctly with session persistence.

## Quick Test (2 minutes)

```bash
# Step 1: List sessions (this discovers AND saves them to database)
poetry run python -m llm_session_manager.cli list

# Step 2: Copy a session ID from the output
# Example: claude_code_15825_1761613519

# Step 3: Set it as environment variable
export SESSION_ID="claude_code_15825_1761613519"

# Step 4: Test core features
poetry run python -m llm_session_manager.cli show $SESSION_ID
poetry run python -m llm_session_manager.cli health $SESSION_ID
poetry run python -m llm_session_manager.cli tag $SESSION_ID testing demo
poetry run python -m llm_session_manager.cli export $SESSION_ID --format json --output /tmp/test.json
poetry run python -m llm_session_manager.cli describe $SESSION_ID "My test session"
poetry run python -m llm_session_manager.cli search "test"
```

## What Was Fixed?

1. **Session Persistence**: Sessions are now saved to database when you run `list`
2. **New `show` Command**: Added dedicated command to view session details
3. **Database Lookup**: All commands now check database first, then active sessions
4. **Session IDs Fully Visible**: Column width increased to show complete IDs

## Key Commands

| Command | What It Does |
|---------|-------------|
| `list` | Discover active sessions & save to database |
| `show <id>` | View detailed info about a session |
| `health <id>` | Check health score and recommendations |
| `tag <id> <tags...>` | Add tags to organize sessions |
| `export <id>` | Export session data (JSON/YAML/Markdown) |
| `describe <id> <text>` | Add description |
| `search <query>` | Search sessions by description |
| `memory-stats` | View memory system statistics |
| `mcp-config` | Get MCP configuration for Claude Desktop |

## Important Notes

- **Always run `list` first** to discover and save active sessions
- The `info` command shows tool information, not session details (use `show` instead)
- Session IDs are now fully visible (not truncated)
- Sessions persist in database even after process ends

## All 29 Commands

See [MANUAL_TESTING_GUIDE.md](MANUAL_TESTING_GUIDE.md) for complete testing documentation.
