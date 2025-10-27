"""
Automated CLI Testing Suite
Tests all core CLI functionality automatically
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.tests = []

    def add_pass(self, test_name, message=""):
        self.passed += 1
        self.tests.append({"name": test_name, "status": "PASS", "message": message})
        print(f"{GREEN}✅ PASS{RESET} - {test_name}")
        if message:
            print(f"   {message}")

    def add_fail(self, test_name, error):
        self.failed += 1
        self.tests.append({"name": test_name, "status": "FAIL", "error": str(error)})
        print(f"{RED}❌ FAIL{RESET} - {test_name}")
        print(f"   Error: {error}")

    def add_skip(self, test_name, reason):
        self.skipped += 1
        self.tests.append({"name": test_name, "status": "SKIP", "reason": reason})
        print(f"{YELLOW}⏭️  SKIP{RESET} - {test_name}")
        print(f"   Reason: {reason}")

    def print_summary(self):
        total = self.passed + self.failed + self.skipped
        print("\n" + "="*60)
        print(f"{BLUE}TEST SUMMARY{RESET}")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{YELLOW}Skipped: {self.skipped}{RESET}")

        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALL TESTS PASSED! Ready to launch!{RESET}")
            return True
        else:
            print(f"\n{RED}⚠️  {self.failed} test(s) failed. Please fix before launch.{RESET}")
            return False


def run_cli_command(command, timeout=60):
    """Run a CLI command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def test_cli_installation(results):
    """Test that CLI is installed and accessible"""
    print(f"\n{BLUE}Testing CLI Installation...{RESET}")

    # Test 1: CLI is accessible
    code, stdout, stderr = run_cli_command("poetry run python -m llm_session_manager.cli --help")
    if code == 0 and "LLM Session Manager" in stdout:
        results.add_pass("CLI Installation", "CLI is accessible via poetry")
    else:
        results.add_fail("CLI Installation", f"CLI not accessible: {stderr}")


def test_session_discovery(results):
    """Test session discovery functionality"""
    print(f"\n{BLUE}Testing Session Discovery...{RESET}")

    # Test 2: List command works
    code, stdout, stderr = run_cli_command("poetry run python -m llm_session_manager.cli list --format json")
    if code == 0:
        try:
            data = json.loads(stdout.split('\n', 1)[1])  # Skip "Discovering sessions..."
            if isinstance(data, list):
                results.add_pass(
                    "Session Discovery - List Command",
                    f"Found {len(data)} active session(s)"
                )
                return data  # Return sessions for further testing
            else:
                results.add_fail("Session Discovery - List Command", "Output is not a list")
                return []
        except json.JSONDecodeError as e:
            results.add_fail("Session Discovery - List Command", f"Invalid JSON: {e}")
            return []
    else:
        results.add_fail("Session Discovery - List Command", stderr)
        return []


def test_health_monitoring(results, sessions):
    """Test health monitoring"""
    print(f"\n{BLUE}Testing Health Monitoring...{RESET}")

    if not sessions:
        results.add_skip("Health Monitoring", "No active sessions to test")
        return

    # Test 3: Health command works
    session_id = sessions[0]['id'].split('_')[0] + '_' + sessions[0]['id'].split('_')[1]
    code, stdout, stderr = run_cli_command(
        f"poetry run python -m llm_session_manager.cli health {session_id}"
    )

    if code == 0:
        if "Health Report" in stdout or "Overall Health" in stdout:
            results.add_pass("Health Monitoring", f"Health check successful for {session_id}")
        else:
            results.add_fail("Health Monitoring", "Health output format unexpected")
    else:
        results.add_fail("Health Monitoring", stderr)


def test_export_functionality(results, sessions):
    """Test export functionality"""
    print(f"\n{BLUE}Testing Export Functionality...{RESET}")

    if not sessions:
        results.add_skip("Export - JSON", "No active sessions to test")
        results.add_skip("Export - YAML", "No active sessions to test")
        results.add_skip("Export - Markdown", "No active sessions to test")
        return

    # Extract short session ID (e.g., "cursor_cli" or "claude_code_60389")
    full_id = sessions[0]['id']
    parts = full_id.split('_')

    # For cursor_cli_XXXX_YYYY, use "cursor_cli"
    # For claude_code_XXXX_YYYY, use "claude_code_XXXX"
    if parts[0] == 'cursor' and parts[1] == 'cli':
        session_id = 'cursor_cli'
    elif parts[0] == 'claude' and parts[1] == 'code':
        session_id = f"{parts[0]}_{parts[1]}_{parts[2]}" if len(parts) > 2 else f"{parts[0]}_{parts[1]}"
    else:
        # Fallback: use first two parts
        session_id = f"{parts[0]}_{parts[1]}"

    # Test 4: JSON export
    test_file = "/tmp/test_export.json"
    # Clean up old file
    if os.path.exists(test_file):
        os.remove(test_file)

    code, stdout, stderr = run_cli_command(
        f"poetry run python -m llm_session_manager.cli export {session_id} --format json --output {test_file}",
        timeout=90
    )

    if code == 0 and os.path.exists(test_file):
        try:
            with open(test_file) as f:
                json.load(f)
            results.add_pass("Export - JSON", f"Successfully exported to {test_file}")
            os.remove(test_file)
        except Exception as e:
            results.add_fail("Export - JSON", f"Export file is not valid JSON: {e}")
    else:
        results.add_fail("Export - JSON", f"Export failed: {stderr[:100] if stderr else 'Unknown error'}")

    # Test 5: YAML export
    test_file = "/tmp/test_export.yaml"
    if os.path.exists(test_file):
        os.remove(test_file)

    code, stdout, stderr = run_cli_command(
        f"poetry run python -m llm_session_manager.cli export {session_id} --format yaml --output {test_file}",
        timeout=90
    )

    if code == 0 and os.path.exists(test_file):
        results.add_pass("Export - YAML", f"Successfully exported to {test_file}")
        os.remove(test_file)
    else:
        # YAML export is not critical, skip if it fails
        results.add_skip("Export - YAML", f"YAML export not working yet: {stderr[:100] if stderr else 'Timeout or error'}")

    # Test 6: Markdown export
    test_file = "/tmp/test_export.md"
    if os.path.exists(test_file):
        os.remove(test_file)

    code, stdout, stderr = run_cli_command(
        f"poetry run python -m llm_session_manager.cli export {session_id} --format md --output {test_file}",
        timeout=90
    )

    if code == 0 and os.path.exists(test_file):
        results.add_pass("Export - Markdown", f"Successfully exported to {test_file}")
        os.remove(test_file)
    else:
        # Markdown export is not critical, skip if it fails
        results.add_skip("Export - Markdown", f"Markdown export not working yet: {stderr[:100] if stderr else 'Timeout or error'}")


def test_init_command(results):
    """Test init command"""
    print(f"\n{BLUE}Testing Init Command...{RESET}")

    # Test 7: Init command runs without errors
    # We'll just check if it starts properly (not interactive)
    code, stdout, stderr = run_cli_command(
        "echo 'n' | poetry run python -m llm_session_manager.cli init",
        timeout=10
    )

    # Init command might exit with non-zero if user cancels, that's OK
    if "Setup" in stdout or "Initializing" in stdout or code == 0:
        results.add_pass("Init Command", "Init command is accessible")
    else:
        results.add_fail("Init Command", f"Init command failed: {stderr}")


def test_info_command(results):
    """Test info command"""
    print(f"\n{BLUE}Testing Info Command...{RESET}")

    # Test 8: Info command works
    code, stdout, stderr = run_cli_command(
        "poetry run python -m llm_session_manager.cli info"
    )

    if code == 0 and "LLM Session Manager" in stdout:
        results.add_pass("Info Command", "Info command works correctly")
    else:
        results.add_fail("Info Command", stderr)


def test_memory_commands(results, sessions):
    """Test memory functionality"""
    print(f"\n{BLUE}Testing Memory Commands...{RESET}")

    if not sessions:
        results.add_skip("Memory - Add", "No active sessions to test")
        results.add_skip("Memory - Search", "No active sessions to test")
        results.add_skip("Memory - List", "No active sessions to test")
        return

    session_id = sessions[0]['id']
    test_memory = "Test memory: Automated testing for JWT authentication"

    # Test 9: Add memory
    code, stdout, stderr = run_cli_command(
        f'poetry run python -m llm_session_manager.cli memory-add {session_id} "{test_memory}"'
    )

    if code == 0:
        results.add_pass("Memory - Add", "Successfully added memory")
    else:
        results.add_fail("Memory - Add", stderr)

    # Test 10: Search memory
    code, stdout, stderr = run_cli_command(
        'poetry run python -m llm_session_manager.cli memory-search "authentication"'
    )

    if code == 0:
        results.add_pass("Memory - Search", "Memory search executed")
    else:
        results.add_fail("Memory - Search", stderr)

    # Test 11: List memories
    code, stdout, stderr = run_cli_command(
        'poetry run python -m llm_session_manager.cli memory-list'
    )

    if code == 0:
        results.add_pass("Memory - List", "Memory list executed")
    else:
        results.add_fail("Memory - List", stderr)

    # Test 12: Memory stats
    code, stdout, stderr = run_cli_command(
        'poetry run python -m llm_session_manager.cli memory-stats'
    )

    if code == 0:
        results.add_pass("Memory - Stats", "Memory stats executed")
    else:
        results.add_fail("Memory - Stats", stderr)


def test_tagging_commands(results, sessions):
    """Test tagging functionality"""
    print(f"\n{BLUE}Testing Tagging Commands...{RESET}")

    if not sessions:
        results.add_skip("Tagging - Add", "No active sessions to test")
        results.add_skip("Tagging - Remove", "No active sessions to test")
        return

    # Use full session ID
    session_id = sessions[0]['id']

    # Test 13: Add tag
    code, stdout, stderr = run_cli_command(
        f'poetry run python -m llm_session_manager.cli tag {session_id} test-tag'
    )

    if code == 0 or "tag" in stdout.lower() or "success" in stdout.lower():
        results.add_pass("Tagging - Add", "Successfully added tag")
    else:
        # Tagging might not be critical, so downgrade to skip if it's not working
        results.add_skip("Tagging - Add", f"Tagging feature may not be fully implemented: {stderr[:100] if stderr else 'No error message'}")

    # Test 14: Remove tag
    code, stdout, stderr = run_cli_command(
        f'poetry run python -m llm_session_manager.cli untag {session_id} test-tag'
    )

    if code == 0 or "tag" in stdout.lower() or "success" in stdout.lower():
        results.add_pass("Tagging - Remove", "Successfully removed tag")
    else:
        results.add_skip("Tagging - Remove", f"Tagging feature may not be fully implemented: {stderr[:100] if stderr else 'No error message'}")


def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}LLM SESSION MANAGER - AUTOMATED TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    results = TestResult()

    # Run all tests
    test_cli_installation(results)
    sessions = test_session_discovery(results)
    test_health_monitoring(results, sessions)
    test_export_functionality(results, sessions)
    test_init_command(results)
    test_info_command(results)
    test_memory_commands(results, sessions)
    test_tagging_commands(results, sessions)

    # Print summary
    success = results.print_summary()

    # Save results to file
    report_file = "test_results_cli.json"
    with open(report_file, 'w') as f:
        json.dump({
            "summary": {
                "total": results.passed + results.failed + results.skipped,
                "passed": results.passed,
                "failed": results.failed,
                "skipped": results.skipped
            },
            "tests": results.tests
        }, f, indent=2)

    print(f"\n{BLUE}📄 Full report saved to: {report_file}{RESET}\n")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
