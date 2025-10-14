# LLM Session Manager

**The first CLI tool to manage multiple AI coding sessions with real-time health monitoring and token tracking.**

> Prevent token limit surprises. Detect context rot. Maximize AI assistant ROI.

A terminal-native tool for engineering teams running 5-10+ parallel AI coding sessions (Claude Code, Cursor, GitHub Copilot). Get real-time visibility into session health, token usage, and context degradation — all from your command line.

## Features

- 🔍 **Session Discovery** - Automatically finds running Claude Code, Cursor, and GitHub Copilot sessions
- 📊 **Real-time Dashboard** - Live TUI with auto-refresh
- 🪙 **Token Tracking** - Precise token counting with tiktoken (no more estimates!)
- ❤️ **Health Monitoring** - Multi-factor health scoring (tokens, duration, activity, errors)
- 💾 **Context Export/Import** - Save and restore sessions in JSON, YAML, or Markdown
- 🏷️ **Session Tagging** - Organize sessions with tags and project names
- ⚙️ **YAML Configuration** - Customize token limits, health weights, and thresholds
- 🤖 **Smart Recommendations** - AI-powered suggestions for session management
- 🎨 **Rich CLI** - Beautiful terminal output with colors and emojis

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

## Testing

Run the automated test suite:

```bash
./run_all_tests.sh
```

Or test individual components:

```bash
python test_discovery.py        # Test session discovery
python test_token_estimator.py  # Test token estimation
python test_health_monitor.py   # Test health scoring
python test_dashboard.py        # Test dashboard rendering
```

See `TESTING_GUIDE.md` for comprehensive testing instructions.

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

- `QUICK_TEST.md` - 5-minute testing guide
- `TESTING_GUIDE.md` - Comprehensive testing instructions
- `CLI_GUIDE.md` - Complete CLI reference
- `DASHBOARD_FEATURES.md` - Dashboard features and usage

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

Contributions welcome! Please read `TESTING_GUIDE.md` before submitting PRs.

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
