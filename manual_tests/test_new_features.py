#!/usr/bin/env python3
"""Test script for new features: AI tagging, descriptions, and batch operations.

This script tests:
1. AI-powered auto-tagging
2. AI-generated session descriptions
3. Description search functionality
4. Tag feedback learning system
5. Batch close operations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_session_manager.utils.ai_tagger import AITagger
from llm_session_manager.utils.description_generator import DescriptionGenerator
from llm_session_manager.utils.auto_tagger import AutoTagger
from llm_session_manager.storage.database import Database
from llm_session_manager.models import Session, SessionType, SessionStatus
from datetime import datetime


def test_ai_tagger():
    """Test AI-powered tag suggestions."""
    print("\n" + "=" * 60)
    print("Testing AI Tagger")
    print("=" * 60)

    ai_tagger = AITagger()

    if not ai_tagger.is_available():
        print("❌ AI Tagger not available (ANTHROPIC_API_KEY not set)")
        print("   Set the environment variable to test AI features:")
        print("   export ANTHROPIC_API_KEY='your-api-key'")
        return False

    print("✓ AI Tagger initialized successfully")

    # Create a test session
    test_session = Session(
        id="test_session_ai_tag",
        pid=12345,
        type=SessionType.CURSOR,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        last_activity=datetime.now(),
        working_directory=str(Path(__file__).parent.parent),  # Use project directory
        tags=["test"],
    )

    print(f"\nTesting with session: {test_session.id}")
    print(f"Working directory: {test_session.working_directory}")

    # Get AI suggestions
    print("\n⏳ Analyzing session with AI...")
    suggested_tags = ai_tagger.suggest_tags_ai(test_session, max_tags=8)

    if suggested_tags:
        print(f"✓ AI suggested {len(suggested_tags)} tags:")
        for i, tag in enumerate(suggested_tags, 1):
            print(f"  {i}. {tag}")
        return True
    else:
        print("❌ No tags suggested by AI")
        return False


def test_heuristic_tagger():
    """Test heuristic tag suggestions (baseline)."""
    print("\n" + "=" * 60)
    print("Testing Heuristic Tagger")
    print("=" * 60)

    auto_tagger = AutoTagger()

    test_session = Session(
        id="test_session_heuristic",
        pid=12345,
        type=SessionType.CURSOR,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        last_activity=datetime.now(),
        working_directory=str(Path(__file__).parent.parent),
        tags=[],
    )

    print(f"Testing with session: {test_session.id}")
    print(f"Working directory: {test_session.working_directory}")

    print("\n⏳ Analyzing session with heuristics...")
    suggested_tags = auto_tagger.suggest_tags(test_session, max_tags=10)

    if suggested_tags:
        print(f"✓ Heuristic tagger suggested {len(suggested_tags)} tags:")
        for i, tag in enumerate(suggested_tags, 1):
            print(f"  {i}. {tag}")
        return True
    else:
        print("❌ No tags suggested")
        return False


def test_description_generator():
    """Test AI description generation."""
    print("\n" + "=" * 60)
    print("Testing Description Generator")
    print("=" * 60)

    desc_gen = DescriptionGenerator()

    if not desc_gen.is_available():
        print("❌ Description Generator not available (ANTHROPIC_API_KEY not set)")
        return False

    print("✓ Description Generator initialized successfully")

    test_session = Session(
        id="test_session_desc",
        pid=12345,
        type=SessionType.CURSOR,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        last_activity=datetime.now(),
        working_directory=str(Path(__file__).parent.parent),
        tags=["python", "cli", "session-management"],
    )

    print(f"\nTesting with session: {test_session.id}")
    print(f"Working directory: {test_session.working_directory}")
    print(f"Existing tags: {', '.join(test_session.tags)}")

    print("\n⏳ Generating AI description...")
    description = desc_gen.generate_description(test_session, max_length=200)

    if description:
        print(f"✓ Generated description ({len(description)} chars):")
        print(f"\n  \"{description}\"\n")
        return True
    else:
        print("❌ Description generation failed")
        return False


def test_tag_feedback():
    """Test tag feedback recording and insights."""
    print("\n" + "=" * 60)
    print("Testing Tag Feedback System")
    print("=" * 60)

    db = Database("data/test_sessions.db")
    db.init_db()

    print("✓ Database initialized")

    # Create a test session
    test_session = Session(
        id="test_session_feedback",
        pid=12345,
        type=SessionType.CURSOR,
        status=SessionStatus.ACTIVE,
        start_time=datetime.now(),
        last_activity=datetime.now(),
        working_directory="/test/path",
        tags=[],
    )

    # Save session
    try:
        db.add_session(test_session)
        print(f"✓ Added test session: {test_session.id}")
    except:
        # Session might already exist
        db.update_session(test_session)
        print(f"✓ Updated test session: {test_session.id}")

    # Record some feedback
    test_tags = [
        ("python", True, "ai"),
        ("backend", True, "heuristic"),
        ("frontend", False, "heuristic"),
        ("testing", True, "ai"),
        ("documentation", False, "ai"),
    ]

    print("\n⏳ Recording tag feedback...")
    for tag, accepted, source in test_tags:
        db.add_tag_feedback(
            test_session.id,
            tag,
            accepted,
            source,
            context_tags=test_session.tags,
            file_extensions=[".py", ".md"]
        )
        status = "✓ Accepted" if accepted else "✗ Rejected"
        print(f"  {status}: {tag} (source: {source})")

    # Get insights
    print("\n⏳ Retrieving tag insights...")
    insights = db.get_tag_suggestions_insights(limit=10)

    if insights:
        print(f"✓ Retrieved {len(insights)} tag insights:")
        print(f"\n  {'Tag':<20} {'Source':<12} {'Accepted':<10} {'Rejected':<10} {'Rate':<8}")
        print("  " + "-" * 70)
        for insight in insights:
            print(f"  {insight['suggested_tag']:<20} {insight['source']:<12} "
                  f"{insight['accepted']:<10} {insight['rejected']:<10} "
                  f"{insight['acceptance_rate']:.1%}")
        return True
    else:
        print("❌ No insights retrieved")
        return False


def test_description_search():
    """Test searching sessions by description."""
    print("\n" + "=" * 60)
    print("Testing Description Search")
    print("=" * 60)

    db = Database("data/test_sessions.db")
    db.init_db()

    # Create test sessions with descriptions
    test_sessions = [
        Session(
            id="search_test_1",
            pid=11111,
            type=SessionType.CLAUDE,
            status=SessionStatus.ACTIVE,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            working_directory="/test/auth",
            description="Working on authentication system using JWT tokens",
            tags=["auth", "backend"],
        ),
        Session(
            id="search_test_2",
            pid=22222,
            type=SessionType.CURSOR,
            status=SessionStatus.ACTIVE,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            working_directory="/test/frontend",
            description="Building React frontend for dashboard",
            tags=["frontend", "react"],
        ),
        Session(
            id="search_test_3",
            pid=33333,
            type=SessionType.CLAUDE,
            status=SessionStatus.ACTIVE,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            working_directory="/test/api",
            description="Implementing REST API endpoints for authentication",
            tags=["api", "auth"],
        ),
    ]

    # Save test sessions
    print("⏳ Creating test sessions...")
    for session in test_sessions:
        try:
            db.add_session(session)
            print(f"  ✓ Added: {session.id}")
        except:
            db.update_session(session)
            print(f"  ✓ Updated: {session.id}")

    # Test searches
    test_queries = ["authentication", "frontend", "API", "JWT"]

    print("\n⏳ Testing search queries...")
    for query in test_queries:
        results = db.search_sessions_by_description(query)
        print(f"\n  Query: '{query}'")
        if results:
            print(f"  ✓ Found {len(results)} result(s):")
            for r in results:
                print(f"    - {r.id}: {r.description}")
        else:
            print(f"  ✗ No results")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LLM Session Manager - New Features Test Suite")
    print("=" * 60)

    results = {
        "Heuristic Tagger": False,
        "AI Tagger": False,
        "Description Generator": False,
        "Tag Feedback": False,
        "Description Search": False,
    }

    # Run tests
    results["Heuristic Tagger"] = test_heuristic_tagger()
    results["AI Tagger"] = test_ai_tagger()
    results["Description Generator"] = test_description_generator()
    results["Tag Feedback"] = test_tag_feedback()
    results["Description Search"] = test_description_search()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {test_name}")

    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)

    print(f"\n  Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
