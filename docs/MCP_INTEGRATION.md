# MCP Integration Guide

The LLM Session Manager now supports the **Model Context Protocol (MCP)**, enabling powerful integrations with MCP-compatible clients like Claude Desktop.

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Why MCP Integration?](#why-mcp-integration)
- [Architecture](#architecture)
- [Phase 1: Main MCP Server](#phase-1-main-mcp-server)
- [Phase 2: Session Wrapper Servers](#phase-2-session-wrapper-servers)
- [Setup Guide](#setup-guide)
- [Usage Examples](#usage-examples)
- [Available Resources](#available-resources)
- [Available Tools](#available-tools)
- [Available Prompts](#available-prompts)
- [Troubleshooting](#troubleshooting)

---

## What is MCP?

The **Model Context Protocol (MCP)** is an open protocol that standardizes how applications provide context to Large Language Models. It enables:

- **Resources**: Data that can be read (similar to GET endpoints)
- **Tools**: Functions that can be executed (similar to POST endpoints)
- **Prompts**: Reusable templates for LLM interactions

Think of it as a standardized API between your tools and AI assistants.

## Why MCP Integration?

### Current Limitations (Without MCP)
- Sessions are monitored externally via process inspection
- Token counts are **estimated**, not actual
- No bidirectional communication with AI tools
- Manual memory capture required
- Context export contains metadata only, not actual conversation

### Benefits with MCP
✅ **Query sessions directly from Claude Desktop**
✅ **Real-time session metrics** (with enhanced monitoring)
✅ **Semantic search across all sessions** from within conversations
✅ **Smart session recommendations** based on your current task
✅ **Automatic knowledge extraction** from sessions
✅ **Rich context export** (future: actual messages when AI tools support it)

---

## Architecture

### Two-Phase Implementation

```
┌─────────────────────────────────────────────────┐
│          Phase 1: Main MCP Server               │
│  (Exposes all session data & operations)        │
│                                                  │
│  Resources:                                      │
│  - session://list                                │
│  - session://{id}/health                         │
│  - memory://stats                                │
│                                                  │
│  Tools:                                          │
│  - search_memory                                 │
│  - recommend_session                             │
│  - export_session                                │
│  - find_session                                  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│       Phase 2: Session Wrapper Servers          │
│   (Deep integration with individual sessions)   │
│                                                  │
│  Resources:                                      │
│  - session://{id}/realtime_metrics               │
│  - session://{id}/git_status                     │
│  - session://{id}/recent_changes                 │
│                                                  │
│  Tools:                                          │
│  - analyze_session_health                        │
│  - get_file_content                              │
│  - analyze_git_commits                           │
└─────────────────────────────────────────────────┘
```

---

## Phase 1: Main MCP Server

The main server exposes **all** session data and cross-session operations.

### Key Features

**Resources:**
- List all sessions
- Get session details (info, health, memories)
- Memory system statistics

**Tools:**
- `search_memory`: Semantic search across all sessions
- `recommend_session`: Get intelligent session recommendations
- `export_session`: Export session in JSON/YAML/Markdown
- `find_session`: Filter sessions by criteria
- `update_session_health`: Recalculate health scores
- `discover_sessions`: Find new/updated sessions

**Prompts:**
- `session_health_check`: Overview of all sessions
- `find_relevant_session`: Match sessions to your current task
- `session_summary`: Detailed session report
- `cross_session_search`: Search knowledge across all sessions

---

## Phase 2: Session Wrapper Servers

Enhanced servers that wrap **individual sessions** for deep monitoring.

### Key Features

**Resources:**
- Real-time metrics (updated token counts, file counts)
- Git repository status
- Recent file changes
- Project file tree
- Context window estimates

**Tools:**
- `analyze_session_health`: Deep health analysis
- `get_file_content`: Read files from session's working directory
- `analyze_git_commits`: Examine recent commits
- `suggest_context_cleanup`: Identify files to exclude

**Prompts:**
- `session_status_report`: Comprehensive status
- `what_am_i_working_on`: Infer session focus from activity

---

## Setup Guide

### 1. Install MCP Dependency

```bash
# Add to your project
pip install mcp

# Or with Poetry
poetry add mcp
```

### 2. Start the Main MCP Server

```bash
# Start the server
python -m llm_session_manager.cli mcp-server

# With custom paths
python -m llm_session_manager.cli mcp-server --db data/sessions.db --memory data/memories
```

### 3. Configure Claude Desktop

Generate the configuration:

```bash
python -m llm_session_manager.cli mcp-config
```

This outputs the JSON configuration you need to add to Claude Desktop's config file.

**Configuration file location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Add this to the file:**

```json
{
  "mcpServers": {
    "llm-session-manager": {
      "command": "/path/to/python",
      "args": ["-m", "llm_session_manager.cli", "mcp-server"],
      "env": {
        "PYTHONPATH": "/path/to/llm-session-manager"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After updating the config, restart Claude Desktop. The MCP server will be automatically started when you open Claude Desktop.

### 5. Test the Connection

In Claude Desktop, try:

```
Can you list my LLM coding sessions?
```

Claude will use the MCP server to query your sessions!

---

## Usage Examples

### Example 1: Find Sessions by Tag

**In Claude Desktop:**
```
Find all my sessions tagged with "backend"
```

**Behind the scenes:**
Claude calls the `find_session` tool:
```json
{
  "tool": "find_session",
  "arguments": {
    "tag": "backend"
  }
}
```

### Example 2: Search Cross-Session Memory

**In Claude Desktop:**
```
Search my past sessions for anything about JWT authentication
```

**Behind the scenes:**
Claude calls the `search_memory` tool:
```json
{
  "tool": "search_memory",
  "arguments": {
    "query": "JWT authentication",
    "limit": 5
  }
}
```

### Example 3: Get Session Recommendations

**In Claude Desktop:**
```
I'm working on implementing user authentication. Which session should I use?
```

**Behind the scenes:**
Claude calls the `recommend_session` tool with context:
```json
{
  "tool": "recommend_session",
  "arguments": {
    "context": "implementing user authentication"
  }
}
```

### Example 4: Session Health Check

**In Claude Desktop:**
```
Check the health of all my sessions
```

**Behind the scenes:**
Claude uses the `session_health_check` prompt to get an overview.

---

## Available Resources

### Global Resources

| URI | Description | Data |
|-----|-------------|------|
| `session://list` | All sessions | Session list with metadata |
| `session://active` | Active sessions only | Filtered session list |
| `memory://stats` | Memory system stats | Memory count, sessions with memories |

### Per-Session Resources

| URI | Description | Data |
|-----|-------------|------|
| `session://{id}/info` | Session details | Full session metadata |
| `session://{id}/health` | Health metrics | Health score breakdown |
| `session://{id}/memories` | Session memories | Memories from this session |
| `session://{id}/realtime_metrics` | Live metrics (Phase 2) | Token count, file count, activity |
| `session://{id}/git_status` | Git status (Phase 2) | Branch, modified files, staged changes |
| `session://{id}/recent_changes` | Recent files (Phase 2) | Recently modified files with timestamps |
| `session://{id}/file_tree` | File structure (Phase 2) | Project directory tree |
| `session://{id}/context_estimate` | Context usage (Phase 2) | Estimated context window usage |

---

## Available Tools

### Main Server Tools

#### `search_memory`
Search cross-session memories using semantic search.

**Input:**
```json
{
  "query": "string (required)",
  "limit": "number (optional, default: 5)"
}
```

**Output:**
```json
{
  "query": "JWT authentication",
  "results": [
    {
      "id": "memory-id",
      "content": "Implemented JWT auth using jose library",
      "relevance": 0.92,
      "metadata": {
        "session_id": "abc123",
        "timestamp": "2025-10-15T14:30:00Z"
      }
    }
  ],
  "count": 1
}
```

#### `recommend_session`
Get intelligent session recommendations.

**Input:**
```json
{
  "context": "string (optional)"
}
```

**Output:**
```json
{
  "recommendations": [
    {
      "type": "restart",
      "session_id": "abc123",
      "reason": "Token usage >95%",
      "priority": "high"
    }
  ],
  "relevant_memories": [...],
  "context": "working on authentication"
}
```

#### `export_session`
Export session context in various formats.

**Input:**
```json
{
  "session_id": "string (required)",
  "format": "json|yaml|markdown (optional, default: json)"
}
```

#### `find_session`
Find sessions by criteria.

**Input:**
```json
{
  "tag": "string (optional)",
  "project": "string (optional)",
  "status": "active|idle|waiting|error (optional)",
  "description": "string (optional)"
}
```

#### `update_session_health`
Recalculate health score for a session.

**Input:**
```json
{
  "session_id": "string (required)"
}
```

#### `discover_sessions`
Discover new/updated sessions from running processes.

**Input:** `{}`

### Session Server Tools (Phase 2)

#### `analyze_session_health`
Deep health analysis with detailed breakdown.

#### `get_file_content`
Read file content from session's working directory.

**Input:**
```json
{
  "file_path": "relative/path/to/file.py"
}
```

#### `analyze_git_commits`
Analyze recent git commits.

**Input:**
```json
{
  "limit": "number (optional, default: 10)"
}
```

#### `suggest_context_cleanup`
Suggest files/context that could be removed to reduce token usage.

---

## Available Prompts

### `session_health_check`
Comprehensive health check across all sessions.

**Arguments:** None

**Output:**
- Total sessions count
- Active sessions count
- Health summary for each session
- Recommendations for unhealthy sessions

---

### `find_relevant_session`
Find the best session for a specific task.

**Arguments:**
- `task` (required): Description of what you're working on

**Output:**
- Relevant sessions with health scores
- Related memories from those sessions
- Recommendation on which session to use

---

### `session_summary`
Detailed summary of a specific session.

**Arguments:**
- `session_id` (required): Session to summarize

**Output:**
- Session metadata (type, status, working directory)
- Health breakdown (token usage, duration, activity, errors)
- Project info (tags, description)
- Recent memories

---

### `cross_session_search`
Search for knowledge across all sessions.

**Arguments:**
- `query` (required): What to search for

**Output:**
- Relevant memories ranked by relevance
- Source sessions for each result
- Relevance scores

---

## Troubleshooting

### MCP Server Not Starting

**Error:** `MCP not available`

**Solution:**
```bash
pip install mcp
# or
poetry add mcp
```

---

### Claude Desktop Can't Connect

**Check:**
1. Is the config file path correct for your platform?
2. Did you restart Claude Desktop after editing config?
3. Is Python path in config absolute (not relative)?

**Debug:**
```bash
# Test server manually
python -m llm_session_manager.cli mcp-server

# Should output: "MCP Server initialized successfully"
```

---

### No Sessions Found

**Causes:**
- No AI coding sessions are currently running
- Sessions haven't been discovered yet

**Solution:**
```bash
# Run discovery first
python -m llm_session_manager.cli list

# Then start MCP server
python -m llm_session_manager.cli mcp-server
```

---

### Memory Search Returns Nothing

**Causes:**
- No memories have been added yet
- ChromaDB not installed

**Solution:**
```bash
# Check if ChromaDB is installed
pip install chromadb

# Add some memories first
python -m llm_session_manager.cli memory-add <session-id> "Your learning here"

# Then search via MCP
```

---

## Advanced Usage

### Running Session-Specific Servers

For enhanced monitoring of a specific session:

```bash
# Get session ID
python -m llm_session_manager.cli list

# Start session-specific server
python -m llm_session_manager.cli mcp-session-server <session-id>
```

Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "session-abc123": {
      "command": "/path/to/python",
      "args": ["-m", "llm_session_manager.cli", "mcp-session-server", "abc123"]
    }
  }
}
```

Now Claude Desktop can access enhanced resources for that specific session!

---

### Custom Configuration

Create `~/.config/llm-session-manager/config.yaml`:

```yaml
mcp:
  server_name: "llm-session-manager"
  server_version: "0.2.0"

  # Paths
  db_path: "data/sessions.db"
  memory_path: "data/memories"

  # Feature flags
  enable_session_servers: true
  enable_memory_search: true
  enable_git_analysis: true

  # Limits
  max_sessions_exposed: 100
  max_memory_results: 10
  max_file_size_mb: 10

  # Performance
  cache_ttl_seconds: 60
  enable_resource_caching: true
```

---

## Future Enhancements

### When AI Tools Add MCP Support

Once Claude Code/Cursor/Copilot expose MCP servers:

**Available:**
- ✅ Actual token counts (not estimates)
- ✅ Real conversation history
- ✅ Context quality metrics
- ✅ Real-time error notifications
- ✅ Bidirectional communication

**Your MCP servers will automatically:**
- Query actual session state
- Export real conversation history
- Provide validated health metrics
- React to real-time events

---

## Contributing

Have ideas for MCP integration improvements? Open an issue or PR!

**Priority areas:**
- Enhanced resource caching
- More sophisticated prompts
- Tool composition (tools calling tools)
- Event subscriptions (when MCP supports it)

---

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/model-context-protocol)
- [LLM Session Manager Docs](../README.md)

---

**Version:** 0.2.0
**Last Updated:** October 2025
