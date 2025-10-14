"""Test script for Rich TUI dashboard."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_session_manager.ui.dashboard import Dashboard
from llm_session_manager.core.session_discovery import SessionDiscovery
from llm_session_manager.core.health_monitor import HealthMonitor
from llm_session_manager.utils.token_estimator import TokenEstimator
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)


def main():
    """Test the dashboard with live session discovery."""
    print("Initializing LLM Session Manager Dashboard...")
    print()

    # Create instances
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

    print("Dashboard starting in 3 seconds...")
    print("Press Ctrl+C to exit\n")

    import time
    time.sleep(3)

    # Run dashboard (single refresh for testing, not live)
    # For live mode, use: dashboard.run_dashboard()
    dashboard.run_once()

    print("\n" + "=" * 70)
    print("Dashboard Test Complete!")
    print("=" * 70)
    print()
    print("To run in live mode with auto-refresh, use:")
    print("  dashboard.run_dashboard()")
    print()
    print("Sessions discovered:", len(dashboard.sessions))
    print()


if __name__ == "__main__":
    main()
