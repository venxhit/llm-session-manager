# Manual Test Scripts

This directory contains **manual test scripts** for interactive testing and verification during development. These are NOT automated unit/integration tests (those belong in the [tests/](../tests/) directory).

## Purpose

These scripts allow developers to:
- Quickly test individual components in isolation
- Verify functionality with real output during development
- Debug and troubleshoot issues interactively
- Demonstrate features to stakeholders

## Available Scripts

### Session Discovery
**File**: [test_discovery.py](test_discovery.py)

Tests the session discovery system that finds running LLM assistant processes (Claude Code, Cursor, etc.)

```bash
python manual_tests/test_discovery.py
```

**What it tests:**
- Process scanning and detection
- Session metadata extraction
- Display of discovered sessions

---

### Token Estimation
**File**: [test_token_estimator.py](test_token_estimator.py)

Tests token counting and estimation for sessions.

```bash
python manual_tests/test_token_estimator.py
```

**What it tests:**
- Token estimation for messages and files
- Usage percentage calculations
- Cache statistics
- Token limits by plan type

---

### Health Monitoring
**File**: [test_health_monitor.py](test_health_monitor.py)

Tests health scoring and monitoring for various session scenarios.

```bash
python manual_tests/test_health_monitor.py
```

**What it tests:**
- Health score calculations
- Component scoring (tokens, duration, activity, errors)
- Recommendations generation
- Restart/stale session detection
- Multiple health scenarios (healthy, warning, critical)

---

### Dashboard (Single Refresh)
**File**: [test_dashboard.py](test_dashboard.py)

Tests the Rich TUI dashboard with a single refresh cycle.

```bash
python manual_tests/test_dashboard.py
```

**What it tests:**
- Dashboard rendering
- Session display formatting
- Component integration
- Output without live updates

---

### Dashboard (Interactive)
**File**: [test_dashboard_interactive.py](test_dashboard_interactive.py)

Runs the full interactive dashboard with auto-refresh and keyboard controls.

```bash
python manual_tests/test_dashboard_interactive.py
```

**What it tests:**
- Live dashboard updates (5-second refresh)
- Keyboard controls (q=quit, r=refresh, h=help)
- Real-time session monitoring
- Full user experience

**Controls:**
- `q` - Quit
- `r` - Manual refresh
- `h` - Show help
- `Ctrl+C` - Exit

---

## Running All Manual Tests

You can run all manual tests sequentially using:

```bash
# Run discovery test
python manual_tests/test_discovery.py

# Run token estimator test
python manual_tests/test_token_estimator.py

# Run health monitor test
python manual_tests/test_health_monitor.py

# Run dashboard test (single refresh)
python manual_tests/test_dashboard.py

# Run interactive dashboard (will stay running until you quit)
python manual_tests/test_dashboard_interactive.py
```

## Automated Tests

For automated unit and integration tests using pytest, see the [tests/](../tests/) directory.

To run automated tests:

```bash
# Run all automated tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=llm_session_manager

# Run specific test file
poetry run pytest tests/unit/test_something.py
```

## Requirements

All manual test scripts:
- Are standalone and can be run directly with Python
- Add the project root to `sys.path` automatically
- Use the same dependencies as the main project
- Provide visual/formatted output for manual verification
- Are meant for development use, not CI/CD pipelines
