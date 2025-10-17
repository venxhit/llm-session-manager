# LLM Session Manager

**The first CLI tool to manage multiple AI coding sessions with real-time health monitoring and token tracking.**

> Prevent token limit surprises. Detect context rot. Maximize AI assistant ROI.

A terminal-native tool for engineering teams running 5-10+ parallel AI coding sessions (Claude Code, Cursor, GitHub Copilot). Get real-time visibility into session health, token usage, and context degradation — all from your command line.

## Features

### Core Features
- 🔍 **Session Discovery** - Automatically finds running Claude Code, Cursor, and GitHub Copilot sessions
- 📊 **Real-time Dashboard** - Live TUI with auto-refresh
- 🪙 **Token Tracking** - Precise token counting with tiktoken (no more estimates!)
- ❤️ **Health Monitoring** - Multi-factor health scoring (tokens, duration, activity, errors)
- 💾 **Context Export/Import** - Save and restore sessions in JSON, YAML, or Markdown
- 🧠 **Cross-Session Memory** - Semantic search across all sessions using ChromaDB
- ⚙️ **YAML Configuration** - Customize token limits, health weights, and thresholds
- 🤖 **Smart Recommendations** - AI-powered suggestions for session management
- 🎨 **Rich CLI** - Beautiful terminal output with colors and emojis

### NEW Features (v0.2.0) 🎉
- 🏷️ **AI-Powered Auto-Tagging** - Intelligent tag suggestions using Claude AI + heuristic analysis
- 📝 **AI-Generated Descriptions** - Automatic session descriptions based on project analysis
- 🔍 **Description Search** - Find sessions by searching description text
- 🧠 **Tag Learning System** - Learns from your accept/reject decisions to improve suggestions
- 🚀 **Batch Close Operations** - Close multiple sessions at once with filtering
- 📊 **Tag Feedback Analytics** - Track which tags work best for different project types
- 🔌 **MCP Integration** - Model Context Protocol support for Claude Desktop and other MCP clients
- 🌐 **MCP Server** - Expose sessions via standardized protocol (resources, tools, prompts)
- 🔧 **Enhanced Session Servers** - Deep integration with git, file system, and real-time metrics

## Installation

```bash
# Clone the repository
cd llm-session-manager

# Install with Poetry
poetry install

# Or install dependencies directly
pip install -r requirements.txt
```

## Quick Start

```bash
# List all active sessions
python -m llm_session_manager.cli list

# Start the interactive dashboard
python -m llm_session_manager.cli monitor

# Export a session
python -m llm_session_manager.cli export <session-id> -o context.json

# Check session health
python -m llm_session_manager.cli health <session-id>

# Show tool info
python -m llm_session_manager.cli info
```

## Commands

### `monitor`
Start the real-time dashboard with auto-refresh (default: 5 seconds).

**Keyboard shortcuts:**
- `q` - Quit
- `r` - Force refresh
- `h` - Show help

```bash
python -m llm_session_manager.cli monitor
python -m llm_session_manager.cli monitor --interval 10  # Custom interval
```

### `list`
List all active LLM sessions.

```bash
python -m llm_session_manager.cli list                    # Table format
python -m llm_session_manager.cli list --format json      # JSON format
python -m llm_session_manager.cli list --status active    # Filter by status
python -m llm_session_manager.cli list --tag backend      # Filter by tag
python -m llm_session_manager.cli list --project "My App" # Filter by project
```

### `tag / untag / set-project`
Organize sessions with tags and project names.

```bash
python -m llm_session_manager.cli tag <session-id> backend api feature-xyz
python -m llm_session_manager.cli untag <session-id> old-tag
python -m llm_session_manager.cli set-project <session-id> "My Web App"
```

### `auto-tag` (NEW! 🎉)
AI-powered automatic tag suggestions with learning from user feedback.

```bash
# Heuristic-based suggestions (file extensions, imports, keywords)
python -m llm_session_manager.cli auto-tag <session-id>

# AI-powered suggestions (requires ANTHROPIC_API_KEY)
python -m llm_session_manager.cli auto-tag <session-id> --ai

# Interactive selection (choose tags one by one)
python -m llm_session_manager.cli auto-tag <session-id> --interactive

# Auto-apply without confirmation
python -m llm_session_manager.cli auto-tag <session-id> --apply
```

**Features:**
- **Heuristic Analysis**: Analyzes file extensions, directory structure, imports, and keywords
- **AI-Powered**: Uses Claude to understand project context and suggest relevant tags
- **Learning System**: Records your accept/reject decisions to improve future suggestions
- **Interactive Mode**: Choose which tags to apply individually

### `describe` (ENHANCED! ✨)
Add or generate AI-powered descriptions for sessions.

```bash
# Manual description
python -m llm_session_manager.cli describe <session-id> "Working on auth feature"

# AI-generated description (requires ANTHROPIC_API_KEY)
python -m llm_session_manager.cli describe <session-id> --ai

# View current description
python -m llm_session_manager.cli describe <session-id> --show
```

**AI descriptions analyze:**
- Project structure and file types
- README content
- Package metadata (package.json, pyproject.toml)
- Code patterns and frameworks
- Existing tags and project context

### `search` (NEW! 🔍)
Search sessions by description text.

```bash
# Basic search
python -m llm_session_manager.cli search "authentication"

# Show full details
python -m llm_session_manager.cli search "API" --details
```

**Perfect for:**
- Finding sessions working on specific features
- Locating sessions by technology or framework
- Quick lookup across all your coding sessions

### `export`
Export session context to JSON, YAML, or Markdown.

```bash
python -m llm_session_manager.cli export <session-id> --output context.json
python -m llm_session_manager.cli export <session-id> --output report.md --format markdown
python -m llm_session_manager.cli export <session-id> --output data.yaml --format yaml
```

### `import-context`
Import session context from JSON file.

```bash
python -m llm_session_manager.cli import-context context.json
python -m llm_session_manager.cli import-context context.json --session-id new-id
```

### `health`
Show detailed health breakdown for a session.

```bash
python -m llm_session_manager.cli health <session-id>
```

### `recommend`
Get smart recommendations for session management.

```bash
python -m llm_session_manager.cli recommend
```

Provides intelligent suggestions for:
- Restarting unhealthy sessions
- Closing idle sessions
- Merging similar sessions
- Token usage warnings

### `init-config / show-config`
Manage YAML configuration.

```bash
python -m llm_session_manager.cli init-config   # Create default config
python -m llm_session_manager.cli show-config   # View current config
```

Edit `~/.config/llm-session-manager/config.yaml` to customize:
- Token limits for different AI assistants
- Health score weights
- Warning/critical thresholds
- Dashboard preferences

### `memory-add / memory-search / memory-list / memory-stats`
Cross-session memory with semantic search (🔥 KILLER FEATURE!)

Save knowledge from one session and find it in another using AI-powered semantic search.

```bash
# Save important learnings
python -m llm_session_manager.cli memory-add <session-id> \
  "Implemented JWT auth using jose library" \
  --tag auth --tag backend

# Search across ALL sessions semantically
python -m llm_session_manager.cli memory-search "how to do authentication"

# List memories
python -m llm_session_manager.cli memory-list --session <session-id>

# View stats
python -m llm_session_manager.cli memory-stats
```

**How it works:**
- Memories are embedded using ChromaDB's semantic search
- Searches understand meaning, not just keywords
- Example: Searching "auth" will find "JWT authentication" and "login system"
- Knowledge persists across all sessions
- No more re-explaining context when switching sessions!

### `batch-tag / batch-export / batch-close` (ENHANCED! 🚀)
Perform operations on multiple sessions at once.

```bash
# Tag multiple sessions
python -m llm_session_manager.cli batch-tag all backend api
python -m llm_session_manager.cli batch-tag "test-*" testing experimental

# Export multiple sessions
python -m llm_session_manager.cli batch-export all --output-dir ./exports --format json
python -m llm_session_manager.cli batch-export "project-*" --format markdown

# Close multiple sessions (NEW!)
python -m llm_session_manager.cli batch-close "test-*"
python -m llm_session_manager.cli batch-close all --status idle  # Close only idle sessions
python -m llm_session_manager.cli batch-close all --force        # Skip confirmation
```

**Use cases:**
- Clean up multiple test/experimental sessions at once
- Close all idle sessions to free up resources
- Batch export for backups or documentation
- Apply consistent tagging across related sessions

**Safety features:**
- Confirmation prompts before destructive operations
- Session filtering by pattern and status
- Preview of affected sessions before execution

### `mcp-server / mcp-session-server / mcp-config` (NEW! 🔌)
Model Context Protocol integration for Claude Desktop and other MCP clients.

```bash
# Start main MCP server (exposes all sessions)
python -m llm_session_manager.cli mcp-server

# Start enhanced server for specific session
python -m llm_session_manager.cli mcp-session-server <session-id>

# Generate Claude Desktop configuration
python -m llm_session_manager.cli mcp-config
```

**What you can do in Claude Desktop:**
- "List all my coding sessions"
- "Find sessions tagged with 'backend'"
- "Search my past sessions for JWT authentication examples"
- "Which session should I use for this authentication task?"
- "Export session abc123 as markdown"
- "Check health of all my sessions"

**Features:**
- **Resources**: Query session data, health metrics, memory stats
- **Tools**: Search memory, find sessions, export context, get recommendations
- **Prompts**: Pre-built workflows for common tasks
- **Phase 2 Enhancement**: Real-time git analysis, file monitoring, enhanced metrics

See [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) for complete guide.

## Testing

Run the automated test suite:

```bash
./run_all_tests.sh
```

Or test individual components:

```bash
python manual_tests/test_discovery.py        # Test session discovery
python manual_tests/test_token_estimator.py  # Test token estimation
python manual_tests/test_health_monitor.py   # Test health scoring
python manual_tests/test_dashboard.py        # Test dashboard rendering
```

See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for comprehensive testing instructions.

## Architecture

```
llm_session_manager/
├── models/          # Data models (Session, Memory)
├── storage/         # Database layer (SQLite)
├── core/            # Core logic (discovery, health)
├── utils/           # Utilities (token estimation)
├── ui/              # User interface (Rich TUI)
└── cli.py           # CLI interface (Typer)
```

## Health Scoring

Sessions are scored based on 4 weighted factors:

- **Token Usage (40%)** - How close to the token limit
- **Duration (20%)** - How long the session has been running
- **Activity (20%)** - Time since last activity
- **Errors (20%)** - Number of errors encountered

Health thresholds:
- ✅ **Healthy**: >= 70%
- ⚠️ **Warning**: 40-70%
- 🔴 **Critical**: < 40%

## Token Estimation

Token counts are estimated using:
- **Base tokens**: 1,000 (system context)
- **Message tokens**: 200 per message
- **File tokens**: ~4 characters per token

The tool scans your project directory and caches results for performance.

## Development

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
pytest

# Format code
black .

# Lint
ruff check .

# Type check
mypy .
```

## Documentation

- [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md) - Model Context Protocol integration guide
- [docs/QUICK_TEST.md](docs/QUICK_TEST.md) - 5-minute testing guide
- [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) - Comprehensive testing instructions
- [docs/CLI_GUIDE.md](docs/CLI_GUIDE.md) - Complete CLI reference
- [docs/DASHBOARD_FEATURES.md](docs/DASHBOARD_FEATURES.md) - Dashboard features and usage

## Requirements

- Python 3.10+
- Poetry (for dependency management)
- Active Claude Code, Cursor, or GitHub Copilot session to monitor

## Project Status

✅ Completed (Steps 1-8 of 14):
- Project setup
- Data models
- Database layer
- Session discovery
- Token estimation
- Health monitoring
- Rich TUI dashboard
- CLI interface

🚧 In Progress:
- Context export/import enhancements
- Cross-session memory
- Configuration management

## License

MIT

## Contributing

Contributions welcome! Please read the testing guide before submitting PRs.

## Troubleshooting

**"No sessions found"**
- Make sure Claude Code or Cursor is running
- The tool looks for processes containing "claude" or "cursor"

**"Module not found"**
- Ensure you're in the project directory
- Run `export PYTHONPATH=$PWD:$PYTHONPATH`

**Permission errors during token estimation**
- Normal! The tool tries to read system files but handles permission errors gracefully
- These errors don't affect functionality

## Roadmap

**✅ Completed (v0.1.0):**
- Session discovery and monitoring
- Token estimation with caching
- Health scoring system
- Rich TUI dashboard
- CLI interface (6 commands)
- Comprehensive testing suite

**🚧 In Progress:**
- Context export/import enhancements
- Cross-session memory (ChromaDB)
- Configuration management

**📅 Upcoming:**
- Team dashboard (web UI)
- VS Code extension
- GitHub Actions integration
- Session collaboration features

See `PRODUCT_BRIEF.md` for detailed roadmap.

## Market & Competitive Landscape

**Why this tool is needed:**
- 53% of developers use Claude Code, 82% enterprise adoption of GitHub Copilot
- Teams run 5-10+ parallel sessions with zero visibility
- No existing tools manage multi-session AI coding workflows
- Novelty score: 8/10 (first in category)

See `MARKET_ANALYSIS.md` for competitive analysis and target companies.

## Pilot Program

We're looking for 3-5 companies to pilot with:
- **Free for 3 months** (normally $10/user/month)
- **5-20 engineers** using Claude Code or Cursor heavily
- **Weekly check-ins** to gather feedback and influence roadmap
- **Optional case study** if you see good results

Interested? See `PILOT_OUTREACH.md` or contact us at [your email].

## Contributing

Contributions welcome! Please read [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) before submitting PRs.

**Priority areas:**
- GitHub Copilot support
- Windows compatibility
- Token estimation accuracy improvements
- Additional export formats (Markdown, YAML)

## Support

- **Issues & Questions:** Open an issue on GitHub
- **Pilot Program:** See `PILOT_OUTREACH.md`
- **Product Info:** See `PRODUCT_BRIEF.md`
- **Market Analysis:** See `MARKET_ANALYSIS.md`
