# Changelog

All notable changes to LLM Session Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-14

### Added
- **GitHub Copilot Support**: Now detects and monitors GitHub Copilot sessions
  - Added `GITHUB_COPILOT` to `SessionType` enum
  - Updated process detection patterns to find Copilot processes
  - Added Copilot token limits (8K context window)
  - Detects `github.copilot`, `copilot-agent` processes
- **Updated Author Information**: Set proper author details in pyproject.toml
- **tiktoken Dependency**: Added for future precise token counting

### Changed
- Enhanced session discovery to support 3 AI coding assistants (Claude Code, Cursor, GitHub Copilot)
- Improved process pattern matching for better detection accuracy

## [0.1.0] - 2025-01-14

### Added
- **Initial Release**: Complete MVP with core functionality
- **Session Discovery**: Auto-discovers Claude Code and Cursor sessions
- **Token Estimation**: Estimates token usage with file scanning and caching
- **Health Monitoring**: 4-factor weighted health scoring system
  - Token Usage (40%): Proximity to token limit
  - Duration (20%): Session longevity and context rot potential
  - Activity (20%): Time since last interaction
  - Errors (20%): Error count impact
- **Rich TUI Dashboard**: Real-time monitoring with auto-refresh
  - Session table with color-coded health indicators
  - Progress bars for token usage
  - Emoji health indicators
  - Auto-refresh every 5 seconds (configurable)
  - Keyboard controls (q/r/h)
- **CLI Interface**: 6 core commands
  - `list`: Show all active sessions (table or JSON format)
  - `monitor`: Interactive dashboard with live updates
  - `export`: Save session context to JSON
  - `import-context`: Load session context from JSON
  - `health`: Detailed health breakdown for a session
  - `info`: Tool information and version
- **SQLite Database**: Persistent storage for sessions and history
- **Session Management**: Full CRUD operations
- **Context Export/Import**: Save and restore session states
- **Comprehensive Testing**: 14+ automated tests
- **Documentation**: Complete testing guides and CLI reference

### Technical Details
- **Python 3.10+** requirement
- **Dependencies**: typer, rich, textual, psutil, pyyaml, structlog, chromadb, sqlalchemy
- **Architecture**: Modular design with separate layers for models, storage, core logic, utils, and UI
- **Token Estimation Algorithm**: Base (1000) + Messages (200/msg) + Files (~4 chars/token)
- **Caching**: mtime-based file token caching for performance

[0.2.0]: https://github.com/iamgagan/llm-session-manager/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/iamgagan/llm-session-manager/releases/tag/v0.1.0
