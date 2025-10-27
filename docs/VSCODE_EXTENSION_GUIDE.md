# VS Code Extension Guide

Complete guide for the LLM Session Manager VS Code extension.

## Table of Contents
- [Installation](#installation)
- [Features](#features)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Installation

### Quick Start
```bash
# 1. Navigate to extension directory
cd vscode-extension

# 2. Install dependencies
npm install

# 3. Build the extension
npm run compile

# 4. Package (optional)
npm run package

# 5. Install
code --install-extension llm-session-manager-0.1.0.vsix
```

### Development Installation
For development and testing:
```bash
# Open in VS Code
code vscode-extension/

# Press F5 to launch Extension Development Host
# Extension will be active in the new window
```

## Features

### 1. Session Sidebar

The sidebar provides a comprehensive view of all active LLM sessions.

**Features:**
- Real-time session list
- Health indicators (🟢 🟡 🔴)
- Token usage percentage
- Session type identification
- Quick actions (analyze, share, export)

**Views:**
1. **Active Sessions**: All running sessions
2. **Session Details**: Metrics breakdown for selected session
3. **AI Insights**: Recommendations and warnings

### 2. Status Bar Integration

Always-visible session monitoring in the status bar.

**Display Format:**
```
[Icon] [Token%] | [Health%]
```

**Icons:**
- ✅ `pass`: Healthy (80-100% health, <75% tokens)
- ⚠️ `warning`: Warning (60-79% health, 75-89% tokens)
- ❌ `error`: Critical (<60% health, >90% tokens)

**Click Action:**
Opens web dashboard in browser

### 3. Smart Notifications

Context-aware notifications with quick actions.

**Notification Types:**

**Token Warnings:**
- At 75%: "Token usage at 75%" (Warning)
- At 90%: "Token usage critical (90%)" (Error)

**Health Alerts:**
- <80%: "Health declining (X%)" (Warning)
- <60%: "Health critical (X%)" (Error)

**Error Alerts:**
- >10 errors: "High error count (X)" (Warning)

**Quick Actions:**
- Analyze: Get AI insights
- Export: Save session data
- View Details: Open in sidebar
- Dismiss: Clear notification

**Cooldown:**
5 minutes between similar notifications per session

### 4. AI Insights Panel

Powered by Cognee, provides intelligent analysis.

**Categories:**

**💡 Recommendations**
- When to start fresh
- Best practices based on patterns
- Resource optimization tips

**⚠️ Warnings**
- Token acceleration alerts
- Error pattern detection
- Historical failure indicators

**🔍 Patterns**
- Similar session analysis
- Team insights
- Success/failure trends

**📊 Similar Sessions**
- Count of related sessions
- Common solutions
- Team knowledge

## Configuration

### Settings

Access via: `Settings > Extensions > LLM Session Manager`

#### Basic Settings

**llm-session-manager.cliPath**
- Type: `string`
- Default: `""`
- Description: Path to CLI executable (empty = use poetry)
- Example: `/usr/local/bin/llm-session`

**llm-session-manager.backendUrl**
- Type: `string`
- Default: `"http://localhost:8000"`
- Description: Backend API server URL
- Example: `"http://192.168.1.100:8000"`

**llm-session-manager.autoRefresh**
- Type: `boolean`
- Default: `true`
- Description: Automatically refresh session data

**llm-session-manager.refreshInterval**
- Type: `number`
- Default: `30`
- Description: Refresh interval in seconds
- Range: 10-300

#### Alert Settings

**llm-session-manager.tokenWarningThreshold**
- Type: `number`
- Default: `75`
- Description: Show warning at X% token usage
- Range: 50-100

**llm-session-manager.tokenCriticalThreshold**
- Type: `number`
- Default: `90`
- Description: Show critical alert at X% token usage
- Range: 75-100

**llm-session-manager.showNotifications**
- Type: `boolean`
- Default: `true`
- Description: Enable in-editor notifications

**llm-session-manager.enableStatusBar**
- Type: `boolean`
- Default: `true`
- Description: Show status bar indicator

### Configuration Examples

#### Individual Developer
```json
{
  "llm-session-manager.autoRefresh": true,
  "llm-session-manager.refreshInterval": 30,
  "llm-session-manager.showNotifications": true,
  "llm-session-manager.tokenWarningThreshold": 75
}
```

#### Team Environment
```json
{
  "llm-session-manager.backendUrl": "http://team-server:8000",
  "llm-session-manager.autoRefresh": true,
  "llm-session-manager.refreshInterval": 15,
  "llm-session-manager.showNotifications": true,
  "llm-session-manager.tokenWarningThreshold": 70,
  "llm-session-manager.tokenCriticalThreshold": 85
}
```

#### Aggressive Monitoring
```json
{
  "llm-session-manager.autoRefresh": true,
  "llm-session-manager.refreshInterval": 10,
  "llm-session-manager.showNotifications": true,
  "llm-session-manager.tokenWarningThreshold": 60,
  "llm-session-manager.tokenCriticalThreshold": 80
}
```

## Usage

### Common Workflows

#### 1. Monitor Current Session
```
1. Start coding with Claude Code/Cursor/Copilot
2. Extension auto-detects session
3. View in sidebar
4. Monitor status bar for token usage
5. Receive alerts when thresholds hit
```

#### 2. Analyze Session Health
```
1. Click session in sidebar
2. View details panel:
   - Overview (type, duration, status)
   - Health Breakdown (factors)
   - Metrics (tokens, errors)
3. Right-click → "Analyze Session"
4. View AI insights panel
5. Follow recommendations
```

#### 3. Share with Team
```
1. Right-click session in sidebar
2. Select "Share Session"
3. Choose action:
   - Copy URL: Share link with team
   - Open in Browser: View collaborative dashboard
4. Team members access:
   - Real-time metrics
   - Chat
   - Code comments
```

#### 4. Export Session Data
```
1. Right-click session
2. Select "Export Session"
3. Choose format:
   - JSON: Machine-readable
   - YAML: Human-friendly config
   - Markdown: Documentation
4. Select save location
5. File created with all session data
```

#### 5. Respond to Alerts
```
When notification appears:

Token Warning (75%):
→ Click "View Details"
→ Review AI insights
→ Plan to start fresh soon
→ Export important context

Health Critical (<60%):
→ Click "Analyze"
→ Review error patterns
→ Check AI recommendations
→ Start new session

High Errors (>10):
→ Click "Analyze"
→ Review error log
→ Find similar sessions
→ Apply team solutions
```

### Commands Reference

| Command | Shortcut | Description |
|---------|----------|-------------|
| Refresh Sessions | - | Manually update session list |
| Analyze Session | - | Get AI insights |
| Share Session | - | Share with team |
| Export Session | - | Save session data |
| Open Web Dashboard | - | Open collaborative UI |
| Start Monitoring | - | Enable auto-refresh |
| Stop Monitoring | - | Disable auto-refresh |
| Get AI Insights | - | Fetch recommendations |

### Custom Keybindings

Add to `keybindings.json`:
```json
[
  {
    "key": "ctrl+alt+s",
    "command": "llm-session-manager.refreshSessions",
    "when": "editorFocus"
  },
  {
    "key": "ctrl+alt+a",
    "command": "llm-session-manager.analyzeSession",
    "when": "editorFocus"
  },
  {
    "key": "ctrl+alt+d",
    "command": "llm-session-manager.openDashboard",
    "when": "editorFocus"
  }
]
```

## Development

### Project Structure
```
vscode-extension/
├── src/
│   ├── extension.ts              # Entry point
│   ├── cliService.ts             # CLI wrapper
│   ├── sessionListProvider.ts    # Sidebar tree
│   ├── sessionDetailsProvider.ts # Details view
│   ├── sessionInsightsProvider.ts# AI insights
│   ├── statusBarManager.ts       # Status bar
│   ├── notificationManager.ts    # Alerts
│   └── sessionMonitor.ts         # Background job
├── package.json                  # Manifest
├── tsconfig.json                 # TS config
└── webpack.config.js             # Build
```

### Build Commands
```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode (development)
npm run watch

# Package for distribution
npm run package

# Run linter
npm run lint

# Run tests
npm test
```

### Testing
```bash
# Unit tests
npm test

# Manual testing
# 1. Open in VS Code
code vscode-extension/

# 2. Press F5 (Launch Extension Development Host)

# 3. Test features:
# - Open sidebar
# - Run commands
# - Check status bar
# - Verify notifications
```

### Debugging
```typescript
// Add console.log statements
console.log('Session data:', sessions);

// View in Output panel:
// View > Output > LLM Session Manager
```

## Troubleshooting

### Sessions Not Detected

**Symptom:** Sidebar shows "No active sessions"

**Causes & Solutions:**
1. **No AI session running**
   - Start Claude Code, Cursor, or Copilot
   - Verify session is active

2. **CLI not found**
   - Check `cliPath` setting
   - Or ensure poetry is installed: `poetry --version`

3. **CLI error**
   - Check Output panel for errors
   - Verify LLM Session Manager is installed: `poetry run python -m llm_session_manager.cli list`

### Status Bar Not Visible

**Symptom:** No status bar item

**Solutions:**
1. Check setting: `llm-session-manager.enableStatusBar` = `true`
2. Ensure at least one session exists
3. Restart VS Code
4. Check for other extension conflicts

### Notifications Not Appearing

**Symptom:** No alerts shown

**Solutions:**
1. Check setting: `llm-session-manager.showNotifications` = `true`
2. Verify VS Code notifications enabled globally
3. Check cooldown (5 min between similar alerts)
4. Review threshold settings (may be too high)

### AI Insights Not Working

**Symptom:** Insights panel empty or error

**Solutions:**
1. Verify environment variable: `echo $LLM_API_KEY`
2. Check backend running: `curl http://localhost:8000/health`
3. Ensure Cognee installed: `poetry run pip list | grep cognee`
4. Check backend logs for API errors

### Backend Connection Failed

**Symptom:** "Failed to fetch session data"

**Solutions:**
1. **Backend not running**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Wrong URL**
   - Check `backendUrl` setting
   - Default: `http://localhost:8000`

3. **Firewall blocking**
   - Check firewall rules
   - Test: `curl http://localhost:8000/health`

4. **CORS issues**
   - Check backend CORS configuration
   - Verify allowed origins

### High CPU Usage

**Symptom:** VS Code using excessive CPU

**Solutions:**
1. Increase refresh interval:
   ```json
   "llm-session-manager.refreshInterval": 60
   ```

2. Disable auto-refresh:
   ```json
   "llm-session-manager.autoRefresh": false
   ```

3. Stop monitoring:
   - Command: "Stop Monitoring"

### Extension Not Activating

**Symptom:** Extension not loading

**Solutions:**
1. Check VS Code version (must be 1.85.0+)
2. Reinstall extension:
   ```bash
   code --uninstall-extension llm-session-manager
   code --install-extension llm-session-manager-0.1.0.vsix
   ```
3. Check Extension Host logs:
   - Help > Toggle Developer Tools
   - Console tab

## FAQ

**Q: Does this work offline?**
A: Session monitoring works offline. AI insights require API access.

**Q: Which AI tools are supported?**
A: Claude Code, Cursor, and GitHub Copilot.

**Q: Can I monitor remote sessions?**
A: Yes, configure `backendUrl` to point to remote server.

**Q: How much does this impact performance?**
A: Minimal. Polling every 30s uses <1% CPU.

**Q: Can I customize alert thresholds?**
A: Yes, via settings (token warning/critical thresholds).

**Q: Is data sent to external servers?**
A: Only if using Cognee AI insights (requires API key).

**Q: Can I use without the CLI?**
A: No, the CLI is required for session detection.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/llm-session-manager/issues)
- **Docs**: [Documentation](../docs/)
- **Main Project**: [README](../README.md)

---

**Happy Coding!** 🚀
