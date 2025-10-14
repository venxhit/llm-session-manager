"""Test script for health monitoring."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_session_manager.core.health_monitor import HealthMonitor
from llm_session_manager.models import Session, SessionType, SessionStatus


def create_test_session(
    name: str,
    token_usage_percent: float = 50.0,
    hours_running: float = 2.0,
    minutes_idle: float = 5.0,
    error_count: int = 0
) -> Session:
    """Create a test session with specific characteristics."""
    now = datetime.now()
    token_limit = 200000
    token_count = int(token_limit * (token_usage_percent / 100))

    return Session(
        id=f"test_{name}",
        pid=12345,
        type=SessionType.CLAUDE_CODE,
        status=SessionStatus.ACTIVE,
        start_time=now - timedelta(hours=hours_running),
        last_activity=now - timedelta(minutes=minutes_idle),
        working_directory="/test",
        token_count=token_count,
        token_limit=token_limit,
        error_count=error_count,
        message_count=50,
        file_count=10,
    )


def print_session_health(monitor: HealthMonitor, session: Session, name: str):
    """Print detailed health information for a session."""
    summary = monitor.get_health_summary(session)

    print(f"\n{'=' * 70}")
    print(f"Session: {name}")
    print(f"{'=' * 70}")
    print(f"\n{summary['emoji']} Overall Health: {summary['overall_percentage']:.1f}% - {summary['status'].upper()}")
    print(f"Color: {summary['color']}")
    print()

    print("Component Scores:")
    for component, score in summary['component_scores'].items():
        bar = '█' * int(score * 20)
        print(f"  {component.capitalize():12s} [{bar:20s}] {score * 100:5.1f}%")
    print()

    print("Metrics:")
    metrics = summary['metrics']
    print(f"  Duration:      {metrics['duration_hours']:.1f} hours")
    print(f"  Idle Time:     {metrics['idle_minutes']:.1f} minutes")
    print(f"  Token Usage:   {metrics['token_usage_percent']:.1f}%")
    print(f"  Error Count:   {metrics['error_count']}")
    print()

    if summary['recommendations']:
        print("⚠️  Recommendations:")
        for rec in summary['recommendations']:
            print(f"  • {rec}")
    else:
        print("✅ No recommendations - session is healthy!")

    # Check restart recommendation
    should_restart, reason = monitor.should_restart_session(session)
    if should_restart:
        print(f"\n🔄 RESTART RECOMMENDED: {reason}")

    # Check if stale
    if monitor.is_session_stale(session):
        print("\n💤 WARNING: Session appears to be stale/abandoned")


def main():
    """Test health monitoring with various scenarios."""
    print("=" * 70)
    print("Health Monitor Test")
    print("=" * 70)
    print()
    print("Testing various session health scenarios...")

    monitor = HealthMonitor()

    # Scenario 1: Healthy session
    healthy_session = create_test_session(
        "healthy",
        token_usage_percent=30.0,
        hours_running=2.0,
        minutes_idle=5.0,
        error_count=1
    )
    print_session_health(monitor, healthy_session, "Healthy Session")

    # Scenario 2: High token usage
    high_tokens_session = create_test_session(
        "high_tokens",
        token_usage_percent=92.0,
        hours_running=3.0,
        minutes_idle=10.0,
        error_count=2
    )
    print_session_health(monitor, high_tokens_session, "High Token Usage")

    # Scenario 3: Long running session
    long_session = create_test_session(
        "long_running",
        token_usage_percent=60.0,
        hours_running=9.0,
        minutes_idle=8.0,
        error_count=5
    )
    print_session_health(monitor, long_session, "Long Running Session")

    # Scenario 4: Idle session
    idle_session = create_test_session(
        "idle",
        token_usage_percent=45.0,
        hours_running=3.0,
        minutes_idle=45.0,
        error_count=0
    )
    print_session_health(monitor, idle_session, "Idle Session")

    # Scenario 5: Error-prone session
    error_session = create_test_session(
        "errors",
        token_usage_percent=50.0,
        hours_running=2.5,
        minutes_idle=5.0,
        error_count=12
    )
    print_session_health(monitor, error_session, "Error-Prone Session")

    # Scenario 6: Critical - multiple issues
    critical_session = create_test_session(
        "critical",
        token_usage_percent=95.0,
        hours_running=10.0,
        minutes_idle=60.0,
        error_count=15
    )
    print_session_health(monitor, critical_session, "Critical Session")

    print(f"\n{'=' * 70}")
    print("Health Thresholds:")
    print(f"{'=' * 70}")
    print(f"Healthy:   >= {monitor.THRESHOLD_HEALTHY * 100:.0f}%")
    print(f"Warning:   >= {monitor.THRESHOLD_WARNING * 100:.0f}%")
    print(f"Critical:  <  {monitor.THRESHOLD_WARNING * 100:.0f}%")
    print()


if __name__ == "__main__":
    main()
