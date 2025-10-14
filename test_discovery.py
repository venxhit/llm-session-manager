"""Test script for session discovery."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_session_manager.core.session_discovery import SessionDiscovery
import structlog

# Configure basic logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)

def main():
    """Test session discovery."""
    print("=" * 70)
    print("LLM Session Discovery Test")
    print("=" * 70)
    print()

    discovery = SessionDiscovery()

    print("Scanning for running LLM assistant processes...")
    print()

    sessions = discovery.discover_sessions()

    if not sessions:
        print("❌ No LLM assistant sessions found.")
        print()
        print("Looking for processes containing: 'claude' or 'cursor'")
    else:
        print(f"✅ Found {len(sessions)} session(s):")
        print()

        for i, session in enumerate(sessions, 1):
            print(f"Session {i}:")
            print(f"  ID:          {session.id}")
            print(f"  Type:        {session.type.value}")
            print(f"  PID:         {session.pid}")
            print(f"  Status:      {session.status.value}")
            print(f"  Started:     {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Working Dir: {session.working_directory or '(not available)'}")
            print(f"  Health:      {session.health_score}/100")
            print()

if __name__ == "__main__":
    main()
