#!/usr/bin/env python3
"""Test script for MCP integration.

This script tests both Phase 1 (Main MCP Server) and Phase 2 (Session Wrapper Servers).
"""

import sys
import asyncio
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_session_manager.storage.database import Database
from llm_session_manager.core.session_discovery import SessionDiscovery
from llm_session_manager.core.memory_manager import MemoryManager
from llm_session_manager.models.session import Session, SessionType, SessionStatus


async def test_main_mcp_server():
    """Test Phase 1: Main MCP Server."""
    print("\n" + "="*60)
    print("PHASE 1: Main MCP Server Tests")
    print("="*60 + "\n")

    try:
        from llm_session_manager.mcp.server import MCPServer

        # Initialize server
        print("✓ Initializing MCP Server...")
        server = MCPServer(
            db_path="data/test_sessions.db",
            memory_path="data/test_memories"
        )
        print("✓ MCP Server initialized successfully\n")

        # Test resource listing
        print("Testing resource listing...")
        resources = await server.server._list_resources_handler()
        print(f"✓ Found {len(resources)} resources")
        print(f"  Sample resources:")
        for resource in resources[:5]:
            print(f"    - {resource.uri}: {resource.name}")
        print()

        # Test tool listing
        print("Testing tool listing...")
        tools = await server.server._list_tools_handler()
        print(f"✓ Found {len(tools)} tools")
        print(f"  Available tools:")
        for tool in tools:
            print(f"    - {tool.name}: {tool.description}")
        print()

        # Test prompt listing
        print("Testing prompt listing...")
        prompts = await server.server._list_prompts_handler()
        print(f"✓ Found {len(prompts)} prompts")
        print(f"  Available prompts:")
        for prompt in prompts:
            print(f"    - {prompt.name}: {prompt.description}")
        print()

        # Test reading a resource
        print("Testing resource reading...")
        try:
            content = await server.server._read_resource_handler("session://list")
            data = json.loads(content)
            print(f"✓ Read resource 'session://list'")
            print(f"  Sessions found: {data.get('count', 0)}")
        except Exception as e:
            print(f"✗ Error reading resource: {e}")
        print()

        # Test calling a tool
        print("Testing tool execution...")
        try:
            result = await server.server._call_tool_handler(
                "discover_sessions",
                {}
            )
            print(f"✓ Executed tool 'discover_sessions'")
            print(f"  Result: {result[0].text[:100]}...")
        except Exception as e:
            print(f"✗ Error calling tool: {e}")
        print()

        print("[SUCCESS] Phase 1 tests completed!\n")
        return True

    except ImportError as e:
        print(f"✗ MCP not installed: {e}")
        print("  Install with: pip install mcp")
        return False
    except Exception as e:
        print(f"✗ Error in Phase 1 tests: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_session_mcp_server():
    """Test Phase 2: Session Wrapper Server."""
    print("\n" + "="*60)
    print("PHASE 2: Session Wrapper Server Tests")
    print("="*60 + "\n")

    try:
        from llm_session_manager.mcp.session_server import SessionMCPServer

        # Create a test session
        print("✓ Creating test session...")
        test_session = Session(
            id="test-session-123",
            pid=12345,
            type=SessionType.CLAUDE_CODE,
            status=SessionStatus.ACTIVE,
            working_directory=str(Path.cwd()),
            token_count=50000,
            token_limit=200000,
            health_score=85.0,
            tags=["test", "mcp"],
            project_name="Test Project",
            description="Test session for MCP integration"
        )
        print("✓ Test session created\n")

        # Initialize session server
        print("✓ Initializing Session MCP Server...")
        server = SessionMCPServer(test_session)
        print("✓ Session MCP Server initialized successfully\n")

        # Test resource listing
        print("Testing session resource listing...")
        resources = await server.server._list_resources_handler()
        print(f"✓ Found {len(resources)} resources")
        print(f"  Session resources:")
        for resource in resources:
            print(f"    - {resource.uri}: {resource.name}")
        print()

        # Test tool listing
        print("Testing session tool listing...")
        tools = await server.server._list_tools_handler()
        print(f"✓ Found {len(tools)} tools")
        print(f"  Session tools:")
        for tool in tools:
            print(f"    - {tool.name}: {tool.description}")
        print()

        # Test reading real-time metrics
        print("Testing real-time metrics...")
        try:
            metrics = await server._get_realtime_metrics()
            print(f"✓ Retrieved real-time metrics")
            print(f"  Token count: {metrics.get('token_count', 0):,}")
            print(f"  Token usage: {metrics.get('token_usage_percent', 0):.1f}%")
            print(f"  Health score: {metrics.get('health_score', 0):.1f}%")
        except Exception as e:
            print(f"✗ Error getting metrics: {e}")
        print()

        # Test git status (if in git repo)
        print("Testing git status...")
        try:
            git_status = await server._get_git_status()
            if 'error' not in git_status:
                print(f"✓ Retrieved git status")
                print(f"  Branch: {git_status.get('branch', 'N/A')}")
                print(f"  Modified files: {len(git_status.get('modified', []))}")
                print(f"  Untracked files: {len(git_status.get('untracked', []))}")
            else:
                print(f"  Not a git repository (expected for test)")
        except Exception as e:
            print(f"✗ Error getting git status: {e}")
        print()

        # Test recent changes
        print("Testing recent changes...")
        try:
            changes = await server._get_recent_changes()
            if 'error' not in changes:
                print(f"✓ Retrieved recent changes")
                print(f"  Total files: {changes.get('total_files', 0)}")
                print(f"  Recent files (top 3):")
                for file in changes.get('recent_files', [])[:3]:
                    print(f"    - {file.get('path', 'N/A')}")
            else:
                print(f"✗ Error: {changes.get('error')}")
        except Exception as e:
            print(f"✗ Error getting changes: {e}")
        print()

        # Test health analysis
        print("Testing health analysis...")
        try:
            analysis = await server._analyze_health()
            print(f"✓ Health analysis completed")
            print(f"  Overall health: {analysis.get('overall_health', 0):.1f}%")
            print(f"  Issues: {len(analysis.get('issues', []))}")
            for issue in analysis.get('issues', []):
                print(f"    - {issue}")
        except Exception as e:
            print(f"✗ Error analyzing health: {e}")
        print()

        print("[SUCCESS] Phase 2 tests completed!\n")
        return True

    except ImportError as e:
        print(f"✗ MCP not installed: {e}")
        print("  Install with: pip install mcp")
        return False
    except Exception as e:
        print(f"✗ Error in Phase 2 tests: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_integration():
    """Test MCP integration with mock data."""
    print("\n" + "="*60)
    print("INTEGRATION TEST: MCP with Mock Data")
    print("="*60 + "\n")

    try:
        # Setup test database
        print("Setting up test database...")
        db = Database("data/test_sessions.db")
        db.init_db()

        # Create test sessions
        test_sessions = [
            Session(
                id="session-1",
                pid=11111,
                type=SessionType.CLAUDE_CODE,
                status=SessionStatus.ACTIVE,
                working_directory=str(Path.cwd()),
                token_count=50000,
                token_limit=200000,
                health_score=85.0,
                tags=["backend", "api"],
                project_name="Web App",
                description="Working on REST API implementation"
            ),
            Session(
                id="session-2",
                pid=22222,
                type=SessionType.CURSOR_CLI,
                status=SessionStatus.IDLE,
                working_directory=str(Path.cwd()),
                token_count=150000,
                token_limit=200000,
                health_score=45.0,
                tags=["frontend", "react"],
                project_name="Web App",
                description="Building user interface components"
            ),
        ]

        for session in test_sessions:
            try:
                db.add_session(session)
                print(f"✓ Added test session: {session.id}")
            except Exception as e:
                print(f"  Session already exists: {session.id}")

        print()

        # Test memory system
        print("Testing memory system...")
        memory_mgr = MemoryManager("data/test_memories")
        if memory_mgr.is_available():
            print("✓ Memory system available")

            # Add test memories
            memory_mgr.add_memory(
                "session-1",
                "Implemented JWT authentication using jose library with refresh tokens",
                tags=["auth", "jwt", "backend"]
            )
            print("✓ Added test memory")

            # Search memories
            results = memory_mgr.search_memories("authentication", limit=3)
            print(f"✓ Memory search returned {len(results)} results")
        else:
            print("✗ Memory system not available (ChromaDB not installed)")

        print()

        # Now test MCP server with this data
        from llm_session_manager.mcp.server import MCPServer

        print("Testing MCP server with mock data...")
        server = MCPServer(
            db_path="data/test_sessions.db",
            memory_path="data/test_memories"
        )

        # Test finding sessions
        print("\nTest: Find sessions by tag...")
        result = await server.server._call_tool_handler(
            "find_session",
            {"tag": "backend"}
        )
        data = json.loads(result[0].text)
        print(f"✓ Found {data.get('count', 0)} sessions with tag 'backend'")

        # Test recommendations
        print("\nTest: Get recommendations...")
        result = await server.server._call_tool_handler(
            "recommend_session",
            {"context": "working on authentication"}
        )
        data = json.loads(result[0].text)
        print(f"✓ Generated {len(data.get('recommendations', []))} recommendations")

        # Test export
        print("\nTest: Export session...")
        result = await server.server._call_tool_handler(
            "export_session",
            {"session_id": "session-1", "format": "json"}
        )
        print(f"✓ Exported session successfully")

        print("\n[SUCCESS] Integration tests completed!\n")
        return True

    except Exception as e:
        print(f"✗ Error in integration tests: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all MCP tests."""
    print("\n" + "="*60)
    print("MCP INTEGRATION TEST SUITE")
    print("="*60)

    results = []

    # Phase 1 tests
    result1 = await test_main_mcp_server()
    results.append(("Phase 1: Main MCP Server", result1))

    # Phase 2 tests
    result2 = await test_session_mcp_server()
    results.append(("Phase 2: Session Wrapper Server", result2))

    # Integration tests
    result3 = await test_mcp_integration()
    results.append(("Integration Tests", result3))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    all_passed = all(r for _, r in results)
    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
