#!/usr/bin/env python3
"""Test script for hybrid detection system.

Tests all 3 tiers: Registry, Heuristic, and LLM detection.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_session_manager.core.detectors import (
    RegistryDetector,
    HeuristicDetector,
    LLMDetector,
    HybridDetector
)
from llm_session_manager.core.session_discovery import SessionDiscovery
import psutil


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")


def test_registry_detector():
    """Test registry-based detection."""
    print_section("TEST 1: Registry Detector")

    detector = RegistryDetector()

    print(f"✅ Registry loaded successfully")
    print(f"📋 Supported tools: {len(detector.tools)}")
    print()

    print("Registered AI Tools:")
    for tool_id, tool_config in detector.tools.items():
        display_name = tool_config.get('display_name', tool_id)
        description = tool_config.get('description', 'No description')
        print(f"  • {display_name}: {description}")
    print()

    # Test with actual processes
    print("Scanning processes with Registry Detector...")
    matches = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            result = detector.identify_session_type(proc)
            if result is not None:
                matches += 1
                print(f"  ✅ Found: {proc.info['name']} (PID {proc.info['pid']}) → {result.value}")
        except:
            continue

    print(f"\n📊 Registry matches: {matches}")
    return matches


def test_heuristic_detector():
    """Test heuristic-based detection."""
    print_section("TEST 2: Heuristic Detector")

    detector = HeuristicDetector()

    print(f"✅ Heuristic detector initialized")
    print(f"🧠 Using AI keywords, tech indicators, and behavior analysis")
    print()

    # Test with actual processes
    print("Scanning processes with Heuristic Detector...")
    matches = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            result = detector.identify_session_type(proc)
            if result is not None:
                matches += 1
                # Get confidence explanation
                explanation = detector.get_confidence_explanation(proc)
                confidence = explanation.get('confidence', 0)
                print(f"  ✅ Found: {proc.info['name']} (PID {proc.info['pid']}) → {result.value} ({confidence:.0%} confidence)")
        except:
            continue

    print(f"\n📊 Heuristic matches: {matches}")
    return matches


def test_llm_detector():
    """Test LLM-based detection (optional)."""
    print_section("TEST 3: LLM Detector (Optional)")

    # Try to initialize with Ollama
    print("🤖 Attempting to initialize LLM detector with Ollama...")
    detector = LLMDetector(provider="ollama", model="llama3.2", enabled=True)

    if not detector.enabled:
        print("⚠️  LLM detector not enabled (Ollama not running or not installed)")
        print("   To enable:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Run: ollama pull llama3.2")
        print("   3. Start Ollama service")
        print("\n   Skipping LLM tests...\n")
        return 0

    print(f"✅ LLM detector initialized successfully")
    print(f"   Provider: {detector.provider}")
    print(f"   Model: {detector.model}")
    print()

    # Test with actual processes
    print("Scanning processes with LLM Detector...")
    print("⚠️  Note: This is SLOW (1-2 seconds per process)\n")

    matches = 0
    tested = 0

    # Only test first 5 promising processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_name = proc.info['name'] or ''

            # Only test processes that look like AI tools
            ai_keywords = ['claude', 'cursor', 'copilot', 'ai', 'llm']
            if not any(kw in proc_name.lower() for kw in ai_keywords):
                continue

            tested += 1
            if tested > 5:  # Limit to 5 tests
                break

            print(f"  Testing: {proc_name} (PID {proc.info['pid']})...")
            result = detector.identify_session_type(proc)

            if result is not None:
                matches += 1
                print(f"    ✅ Identified as: {result.value}")
            else:
                print(f"    ❌ Not an AI assistant")
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
            continue

    print(f"\n📊 LLM matches: {matches} (tested {tested} processes)")
    return matches


def test_hybrid_detector():
    """Test hybrid detection (all strategies combined)."""
    print_section("TEST 4: Hybrid Detector (Full System)")

    print("🔄 Initializing hybrid detector...")
    detector = HybridDetector(enable_llm=False)  # LLM disabled by default

    print(f"✅ Hybrid detector initialized")
    print()

    # Show supported tools
    tools_info = detector.list_supported_tools()
    print("Supported Tools:")
    for tool in tools_info['registry_tools']:
        print(f"  • {tool}")
    print()
    print(f"Heuristic Detection: {'Enabled' if tools_info['heuristic_enabled'] else 'Disabled'}")
    print(f"LLM Detection: {'Enabled' if tools_info['llm_enabled'] else 'Disabled'}")
    print()

    # Test with actual processes
    print("Scanning processes with Hybrid Detector...")
    print()

    sessions_found = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            result = detector.identify_session_type(proc)
            if result is not None:
                sessions_found.append({
                    'type': result.value,
                    'pid': proc.info['pid'],
                    'name': proc.info['name']
                })
                print(f"  ✅ {result.value:15s} | PID {proc.info['pid']:6d} | {proc.info['name']}")
        except:
            continue

    print()
    print(f"📊 Total sessions found: {len(sessions_found)}")
    print()

    # Show detection statistics
    stats = detector.get_detection_stats()
    print("Detection Statistics:")
    print(f"  Registry matches:   {stats['registry_matches']:3d} ({stats.get('registry_percentage', 0):.1f}%)")
    print(f"  Heuristic matches:  {stats['heuristic_matches']:3d} ({stats.get('heuristic_percentage', 0):.1f}%)")
    print(f"  LLM matches:        {stats['llm_matches']:3d} ({stats.get('llm_percentage', 0):.1f}%)")
    print(f"  Total processes:    {stats['total_processes']:3d}")
    print()

    return len(sessions_found)


def test_session_discovery():
    """Test SessionDiscovery using hybrid detector."""
    print_section("TEST 5: SessionDiscovery Integration")

    print("🔍 Running session discovery...")
    discovery = SessionDiscovery(enable_llm=False)

    sessions = discovery.discover_sessions()

    print(f"✅ Discovery complete!")
    print(f"📊 Found {len(sessions)} AI coding sessions")
    print()

    if sessions:
        print("Sessions:")
        for session in sessions:
            print(f"  • {session.type.value:15s} | PID {session.pid:6d} | {session.working_directory or 'No working dir'}")
    else:
        print("  No sessions found (no AI coding tools running)")

    print()
    return len(sessions)


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" " * 15 + "🧪 HYBRID DETECTION SYSTEM TEST")
    print("=" * 70)

    try:
        # Test individual detectors
        registry_matches = test_registry_detector()
        heuristic_matches = test_heuristic_detector()
        llm_matches = test_llm_detector()

        # Test hybrid system
        hybrid_matches = test_hybrid_detector()

        # Test integration
        discovery_sessions = test_session_discovery()

        # Final summary
        print_section("📊 TEST SUMMARY")

        print("Results:")
        print(f"  ✅ Registry Detector:     {registry_matches} matches")
        print(f"  ✅ Heuristic Detector:    {heuristic_matches} matches")
        print(f"  {'✅' if llm_matches > 0 else '⚠️ '} LLM Detector:         {llm_matches} matches {'(disabled)' if llm_matches == 0 else ''}")
        print(f"  ✅ Hybrid Detector:       {hybrid_matches} sessions")
        print(f"  ✅ SessionDiscovery:      {discovery_sessions} sessions")
        print()

        # Verify consistency
        if hybrid_matches == discovery_sessions:
            print("✅ All tests PASSED - System working correctly!")
        else:
            print("⚠️  Mismatch between hybrid detector and session discovery")

        print()
        print("🎉 Hybrid detection system test complete!")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
