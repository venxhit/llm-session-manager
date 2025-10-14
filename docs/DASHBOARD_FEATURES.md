# LLM Session Manager - Dashboard Features

## Complete Rich TUI Dashboard Implementation

The dashboard (`llm_session_manager/ui/dashboard.py`) provides a comprehensive, interactive terminal interface for monitoring LLM coding assistant sessions.

---

## ✅ Core Features Implemented

### 1. **Auto-Refresh Every 5 Seconds**
- Automatic session discovery and data refresh
- Configurable refresh interval (default: 5 seconds)
- Non-blocking refresh mechanism
- Visual timestamp showing last refresh time

### 2. **Manual Refresh on 'r' Key**
- Press 'r' to force immediate refresh
- Resets auto-refresh timer
- Shows confirmation message
- Updates all metrics instantly

### 3. **Clean Exit on 'q' Key**
- Press 'q' for graceful shutdown
- Alternative: Ctrl+C also supported
- Proper cleanup of resources
- Exit confirmation message

### 4. **Handle No Sessions Gracefully**
- Shows empty state message when no sessions found
- Table structure remains intact
- Clear visual feedback
- No errors or crashes

---

## 📊 Dashboard Layout

```
╭──────────────────────────────────────────────────────────────────╮
│          🖥️  LLM Session Manager - Dashboard                     │
│          Total Sessions: 2  •  Active: 2  •  Idle: 0             │
│          Last Refresh: 2025-10-12 13:23:58                       │
╰──────────────────────────────────────────────────────────────────╯

                        Active Sessions
┏━━━━━━━━━━━┳━━━━━━┳━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID        ┃ Type ┃ PID ┃ Status ┃ Duration ┃    Tokens    ┃  Health   ┃
┡━━━━━━━━━━━╇━━━━━━╇━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ session_1 │ cla… │ 123 │ active │ 02:15:30 │ 25K/200K 12% │ ✅ 95%    │
│           │      │     │        │          │ [██░░░░░░░…] │ (healthy) │
└───────────┴──────┴─────┴────────┴──────────┴──────────────┴───────────┘

╭──────────────────────────────────────────────────────────────────╮
│     Keyboard Shortcuts: [Q]uit  [R]efresh  [D]etails  [H]elp     │
╰──────────────────────────────────────────────────────────────────╯
```

---

## 🎨 Visual Components

### **Header Panel**
- **Title**: "🖥️ LLM Session Manager - Dashboard"
- **Session Count**: Total number of sessions
- **Status Breakdown**: Active vs Idle sessions
- **Timestamp**: Last refresh time
- **Border**: Cyan colored panel

### **Session Table**
Columns with rich formatting:

1. **ID** - Session identifier (truncated if long)
2. **Type** - Session type with color coding:
   - `claude_code` → Cyan
   - `cursor_cli` → Magenta
   - `unknown` → Dim white

3. **PID** - Process ID (right-aligned)

4. **Status** - Session status with colors:
   - `active` → Green
   - `idle` → Yellow
   - `waiting` → Blue
   - `error` → Red

5. **Duration** - Formatted as HH:MM:SS

6. **Tokens** - Visual progress bar:
   - Format: `25,000/200,000 [████████░░░░░░░] 12%`
   - Colors:
     - Green: < 70% usage
     - Yellow: 70-90% usage
     - Red: >= 90% usage

7. **Health** - Health score with emoji:
   - ✅ Green: >= 70% (healthy)
   - ⚠️ Yellow: 40-70% (warning)
   - 🔴 Red: < 40% (critical)

### **Footer Panel**
- Keyboard shortcuts with color-coded keys
- Always visible at bottom
- Dim white border

---

## ⌨️ Keyboard Controls

### **Interactive Commands**
| Key | Action | Description |
|-----|--------|-------------|
| `q` | Quit | Gracefully exit dashboard |
| `r` | Refresh | Force immediate data refresh |
| `h` | Help | Display help panel |
| `Ctrl+C` | Interrupt | Alternative exit method |

### **Key Handling Features**
- **Non-blocking input**: Dashboard continues updating while waiting for keys
- **Case-insensitive**: Both 'Q' and 'q' work
- **Graceful degradation**: Works even if terminal doesn't support special features
- **Cross-platform**: Uses `termios` on Unix, handles Windows gracefully

---

## 🔄 Auto-Refresh Behavior

### **Refresh Cycle**
```python
1. Discover sessions → SessionDiscovery.discover_sessions()
2. Update tokens   → TokenEstimator.update_token_counts()
3. Update health   → HealthMonitor.update_health_scores()
4. Update display  → Live.update(layout)
5. Wait 5 seconds  → Auto-refresh timer
6. Repeat
```

### **Refresh Triggers**
- **Automatic**: Every 5 seconds (configurable)
- **Manual**: Press 'r' key
- **Initial**: On dashboard startup

---

## 🎯 Sorting & Display Logic

### **Session Sorting**
- Sessions sorted by health score (worst first)
- Prioritizes sessions needing attention
- Critical sessions appear at top

### **Empty State**
When no sessions found:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ No active sessions found                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🛠️ Methods Reference

### **Public Methods**

#### `create_header() -> Panel`
Creates header panel with metadata

#### `create_session_table(sessions: List[Session]) -> Table`
Creates Rich table with session information

#### `create_footer() -> Panel`
Creates footer panel with keyboard shortcuts

#### `create_layout() -> Layout`
Combines all components into full layout

#### `run_dashboard()`
**Main entry point** - Runs interactive dashboard with live updates
- Features: Auto-refresh, keyboard input, error handling
- Blocks until user quits

#### `run_once()`
Single refresh without live updates (for testing)

#### `refresh_data()`
Performs full data refresh cycle

#### `stop_dashboard()`
Gracefully stops the dashboard

#### `display_help()`
Shows detailed help panel

#### `get_session_details(session_id: str) -> dict`
Retrieves detailed info for specific session

---

## 📦 Dependencies

```python
from rich.console import Console       # Main console
from rich.table import Table           # Table display
from rich.panel import Panel           # Bordered panels
from rich.layout import Layout         # Layout management
from rich.live import Live             # Live updating
from rich.text import Text             # Styled text
from rich.align import Align           # Text alignment
```

---

## 🚀 Usage Examples

### **Basic Usage**
```python
from llm_session_manager.ui.dashboard import Dashboard
from llm_session_manager.core.session_discovery import SessionDiscovery
from llm_session_manager.core.health_monitor import HealthMonitor
from llm_session_manager.utils.token_estimator import TokenEstimator

# Initialize components
discovery = SessionDiscovery()
health_monitor = HealthMonitor()
token_estimator = TokenEstimator()

# Create dashboard
dashboard = Dashboard(
    discovery=discovery,
    health_monitor=health_monitor,
    token_estimator=token_estimator,
    refresh_interval=5
)

# Run interactive dashboard
dashboard.run_dashboard()
```

### **Single Refresh (Testing)**
```python
dashboard.run_once()  # Display once, no live updates
```

### **Custom Refresh Interval**
```python
dashboard = Dashboard(
    discovery=discovery,
    health_monitor=health_monitor,
    token_estimator=token_estimator,
    refresh_interval=10  # Refresh every 10 seconds
)
```

---

## ✨ Advanced Features

### **Health Summary**
Detailed health breakdown available via:
```python
details = dashboard.get_session_details(session_id)
# Returns: {session: Session, health_summary: dict}
```

### **Help System**
Press 'h' to see:
- Dashboard commands
- Keyboard shortcuts
- Health indicators
- Threshold explanations

### **Error Handling**
- Graceful handling of process access errors
- File permission errors logged but don't crash
- Session disappearance handled cleanly
- Keyboard interrupt caught and cleaned up

---

## 🎨 Color Scheme

| Element | Color | Condition |
|---------|-------|-----------|
| Header | Cyan | Always |
| Table Border | Blue | Always |
| Health ✅ | Green | >= 70% |
| Health ⚠️ | Yellow | 40-70% |
| Health 🔴 | Red | < 40% |
| Token Bar | Green | < 70% |
| Token Bar | Yellow | 70-90% |
| Token Bar | Red | >= 90% |
| Claude Type | Cyan | Always |
| Cursor Type | Magenta | Always |
| Active Status | Green | Always |
| Idle Status | Yellow | Always |

---

## 📈 Performance

- **Non-blocking**: UI remains responsive during refresh
- **Efficient**: Updates only when data changes
- **Cached**: Token estimation caches file reads
- **Lightweight**: Minimal CPU usage (100ms sleep cycle)

---

## 🔧 Configuration

The dashboard is highly configurable:

```python
class Dashboard:
    def __init__(
        self,
        discovery: SessionDiscovery,
        health_monitor: HealthMonitor,
        token_estimator: TokenEstimator,
        refresh_interval: int = 5  # Configurable refresh rate
    ):
        # ...
```

---

## ✅ Implementation Checklist

- [x] Auto-refresh every 5 seconds
- [x] Manual refresh on 'r' key
- [x] Clean exit on 'q' key
- [x] Ctrl+C support
- [x] Handle no sessions gracefully
- [x] Rich table with all columns
- [x] Color-coded health indicators
- [x] Progress bars for tokens
- [x] Duration formatting (HH:MM:SS)
- [x] Header panel with metadata
- [x] Footer panel with shortcuts
- [x] Keyboard input handling
- [x] Non-blocking input
- [x] Help system
- [x] Error handling
- [x] Structured logging
- [x] Empty state handling
- [x] Sort by health (worst first)

---

## 🎉 Status: COMPLETE ✅

The dashboard is fully implemented with all requested features and more!
