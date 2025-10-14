"""Test script for token estimation."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_session_manager.utils.token_estimator import TokenEstimator
from llm_session_manager.models import Session, SessionType, SessionStatus
from datetime import datetime


def main():
    """Test token estimation."""
    print("=" * 70)
    print("Token Estimator Test")
    print("=" * 70)
    print()

    estimator = TokenEstimator()

    # Create a test session for this project
    session = Session(
        id="test_session_1",
        pid=12345,
        type=SessionType.CLAUDE_CODE,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        last_activity=datetime.now(),
        working_directory="/Users/gagan/llm-session-manager",
        message_count=25,  # Simulate 25 messages
        file_count=10,
        error_count=0,
    )

    print(f"Session: {session.id}")
    print(f"Working Directory: {session.working_directory}")
    print(f"Message Count: {session.message_count}")
    print()

    # Estimate tokens
    print("Estimating tokens...")
    estimated_tokens = estimator.estimate_session_tokens(session)

    print()
    print("Token Breakdown:")
    print(f"  Base Tokens:      {TokenEstimator.BASE_TOKENS:,}")
    print(f"  Message Tokens:   {session.message_count * TokenEstimator.TOKENS_PER_MESSAGE:,} ({session.message_count} × {TokenEstimator.TOKENS_PER_MESSAGE})")
    print(f"  File Tokens:      {estimated_tokens - TokenEstimator.BASE_TOKENS - (session.message_count * TokenEstimator.TOKENS_PER_MESSAGE):,}")
    print(f"  " + "-" * 40)
    print(f"  Total Estimate:   {estimated_tokens:,} tokens")
    print()

    # Update session with estimated tokens
    session.token_count = estimated_tokens

    # Calculate percentage
    percentage = estimator.calculate_token_percentage(session)
    remaining = estimator.get_remaining_tokens(session)
    is_critical = estimator.is_token_limit_critical(session)

    print("Token Usage:")
    print(f"  Current:          {session.token_count:,} tokens")
    print(f"  Limit:            {session.token_limit:,} tokens")
    print(f"  Usage:            {percentage:.1f}%")
    print(f"  Remaining:        {remaining:,} tokens")
    print(f"  Critical? (>90%): {'⚠️  YES' if is_critical else '✅ No'}")
    print()

    # Show token limits for different plans
    print("Token Limits by Plan:")
    for plan, limit in TokenEstimator.TOKEN_LIMITS.items():
        print(f"  {plan:20s} {limit:,} tokens")
    print()

    # Cache stats
    cache_stats = estimator.get_cache_stats()
    print("Cache Statistics:")
    print(f"  Cached Files:     {cache_stats['cached_files']}")
    print(f"  Cached Tokens:    {cache_stats['total_cached_tokens']:,}")
    print()

    # Test a single file
    print("Single File Test:")
    test_file = "/Users/gagan/llm-session-manager/llm_session_manager/models/session.py"
    file_tokens = estimator.estimate_file_tokens(test_file)
    print(f"  File: {Path(test_file).name}")
    print(f"  Estimated Tokens: {file_tokens:,}")


if __name__ == "__main__":
    main()
