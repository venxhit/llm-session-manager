# MCP Quick Start Guide

Get up and running with MCP integration in 5 minutes.

## Prerequisites

- Python 3.10+
- LLM Session Manager installed
- Claude Desktop (optional, for testing)

## Step 1: Install MCP

```bash
pip install mcp
```

## Step 2: Test the MCP Server

```bash
# Run the test suite
python manual_tests/test_mcp.py
```

You should see:
```
✓ MCP Server initialized successfully
✓ Found X resources
✓ Found X tools
✓ Found X prompts
```

## Step 3: Start the MCP Server

```bash
python -m llm_session_manager.cli mcp-server
```

You should see:
```
Starting LLM Session Manager MCP Server...
✓ MCP Server initialized successfully
Database: data/sessions.db
Memory: data/memories

Server is running. Connect via MCP client (e.g., Claude Desktop)
```

## Step 4: Configure Claude Desktop

Generate the configuration:

```bash
python -m llm_session_manager.cli mcp-config
```

Copy the output and add it to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Example configuration:
```json
{
  "mcpServers": {
    "llm-session-manager": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "llm_session_manager.cli", "mcp-server"],
      "env": {
        "PYTHONPATH": "/path/to/llm-session-manager"
      }
    }
  }
}
```

## Step 5: Restart Claude Desktop

Close and reopen Claude Desktop. The MCP server will start automatically.

## Step 6: Test in Claude Desktop

Try these commands:

### List Sessions
```
Can you list all my LLM coding sessions?
```

### Find Sessions by Tag
```
Show me all sessions tagged with "backend"
```

### Search Memory
```
Search my past sessions for anything about JWT authentication
```

### Get Recommendations
```
I'm working on user authentication. Which session should I use?
```

### Check Health
```
Check the health of all my sessions and give me recommendations
```

### Export Session
```
Export session abc123 as markdown
```

## What's Available?

### Resources (Data you can query)
- `session://list` - All sessions
- `session://active` - Active sessions only
- `session://{id}/info` - Session details
- `session://{id}/health` - Health metrics
- `session://{id}/memories` - Session memories
- `memory://stats` - Memory statistics

### Tools (Functions you can call)
- `search_memory` - Semantic search across sessions
- `recommend_session` - Get intelligent recommendations
- `export_session` - Export session context
- `find_session` - Filter sessions by criteria
- `update_session_health` - Recalculate health
- `discover_sessions` - Find new sessions

### Prompts (Pre-built workflows)
- `session_health_check` - Overview of all sessions
- `find_relevant_session` - Match sessions to tasks
- `session_summary` - Detailed session report
- `cross_session_search` - Search all sessions

## Troubleshooting

### "MCP not installed"
```bash
pip install mcp
```

### "No sessions found"
Make sure you have some coding sessions running first:
```bash
python -m llm_session_manager.cli list
```

### "Claude Desktop can't connect"
1. Check that the Python path in config is absolute
2. Verify the PYTHONPATH points to your project directory
3. Restart Claude Desktop after config changes
4. Check Claude Desktop logs for errors

### "Memory search returns nothing"
```bash
# Install ChromaDB
pip install chromadb

# Add some test memories
python -m llm_session_manager.cli memory-add <session-id> "Test memory"
```

## Next Steps

- Read the [full MCP integration guide](MCP_INTEGRATION.md)
- Set up [enhanced session servers](MCP_INTEGRATION.md#phase-2-session-wrapper-servers) for deeper monitoring
- Explore [advanced usage](MCP_INTEGRATION.md#advanced-usage)

## Quick Reference

```bash
# Start main server
python -m llm_session_manager.cli mcp-server

# Start session-specific server
python -m llm_session_manager.cli mcp-session-server <session-id>

# Generate config
python -m llm_session_manager.cli mcp-config

# Run tests
python manual_tests/test_mcp.py

# List sessions
python -m llm_session_manager.cli list

# Add memory
python -m llm_session_manager.cli memory-add <session-id> "Your knowledge here"
```

---

**Need Help?** Check out [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for detailed documentation.
