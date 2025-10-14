"""Interactive test script for Rich TUI dashboard with keyboard controls."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_session_manager.ui.dashboard import Dashboard
from llm_session_manager.core.session_discovery import SessionDiscovery
from llm_session_manager.core.health_monitor import HealthMonitor
from llm_session_manager.utils.token_estimator import TokenEstimator
import structlog

# Configure logging (less verbose for interactive mode)
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging_level=30)  # WARNING level
)


def main():
    """Run interactive dashboard with keyboard controls."""
    print("=" * 70)
    print("LLM Session Manager - Interactive Dashboard")
    print("=" * 70)
    print()
    print("Features:")
    print("  ✅ Auto-refresh every 5 seconds")
    print("  ✅ Press 'q' to quit")
    print("  ✅ Press 'r' to manually refresh")
    print("  ✅ Press 'h' to show help")
    print("  ✅ Press Ctrl+C to exit")
    print()
    print("Initializing components...")

    # Create instances
    discovery = SessionDiscovery()
    health_monitor = HealthMonitor()
    token_estimator = TokenEstimator()

    # Create dashboard with 5-second refresh interval
    dashboard = Dashboard(
        discovery=discovery,
        health_monitor=health_monitor,
        token_estimator=token_estimator,
        refresh_interval=5
    )

    print("Components initialized successfully!")
    print()

    # Run interactive dashboard
    try:
        dashboard.run_dashboard()
    except Exception as e:
        print(f"\nError running dashboard: {e}")
        import traceback
        traceback.print_exc()

    print("\nThank you for using LLM Session Manager!")


if __name__ == "__main__":
    main()
