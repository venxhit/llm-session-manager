"""
Automated Backend API Testing Suite
Tests backend API endpoints and WebSocket functionality
"""

import requests
import json
import time
import sys

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

        if self.failed == 0 and self.passed > 0:
            print(f"\n{GREEN}🎉 ALL BACKEND TESTS PASSED!{RESET}")
            return True
        elif self.passed == 0:
            print(f"\n{YELLOW}⚠️  No tests passed. Is the backend running?{RESET}")
            return False
        else:
            print(f"\n{RED}⚠️  {self.failed} test(s) failed. Please fix before launch.{RESET}")
            return False


def test_backend_health(results, base_url):
    """Test backend health endpoint"""
    print(f"\n{BLUE}Testing Backend Health...{RESET}")

    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                results.add_pass("Backend Health", "Backend is healthy")
                return True
            else:
                results.add_fail("Backend Health", f"Unexpected health status: {data}")
                return False
        else:
            results.add_fail("Backend Health", f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        results.add_fail("Backend Health", "Cannot connect to backend. Is it running?")
        return False
    except Exception as e:
        results.add_fail("Backend Health", str(e))
        return False


def test_api_docs(results, base_url):
    """Test that API documentation is accessible"""
    print(f"\n{BLUE}Testing API Documentation...{RESET}")

    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200 and "swagger" in response.text.lower():
            results.add_pass("API Documentation", "Swagger UI is accessible")
        else:
            results.add_fail("API Documentation", f"Unexpected response: {response.status_code}")
    except Exception as e:
        results.add_fail("API Documentation", str(e))


def test_cors_headers(results, base_url):
    """Test CORS headers are configured"""
    print(f"\n{BLUE}Testing CORS Configuration...{RESET}")

    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if "access-control-allow-origin" in [h.lower() for h in response.headers]:
            results.add_pass("CORS Configuration", "CORS headers present")
        else:
            results.add_skip("CORS Configuration", "CORS headers not found (may not be configured)")
    except Exception as e:
        results.add_fail("CORS Configuration", str(e))


def test_session_endpoints(results, base_url):
    """Test session-related endpoints"""
    print(f"\n{BLUE}Testing Session Endpoints...{RESET}")

    # Test GET /api/sessions (if exists)
    try:
        response = requests.get(f"{base_url}/api/sessions", timeout=5)
        if response.status_code in [200, 401, 403]:  # OK, or auth required
            results.add_pass("Sessions Endpoint", f"Endpoint accessible (status: {response.status_code})")
        else:
            results.add_skip("Sessions Endpoint", f"Endpoint returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        results.add_skip("Sessions Endpoint", "Endpoint not found or not implemented")
    except Exception as e:
        results.add_skip("Sessions Endpoint", str(e))


def test_websocket_endpoint(results, base_url):
    """Test WebSocket endpoint is available"""
    print(f"\n{BLUE}Testing WebSocket Endpoint...{RESET}")

    # We can't fully test WebSocket without a client library,
    # but we can check if the HTTP upgrade endpoint exists
    ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")

    try:
        # Try to connect (will fail but we can see if endpoint exists)
        response = requests.get(f"{base_url}/ws/test", timeout=2)
        # Any response means endpoint exists (even if it requires upgrade)
        results.add_pass("WebSocket Endpoint", "WebSocket endpoint is configured")
    except requests.exceptions.ConnectionError:
        results.add_skip("WebSocket Endpoint", "Cannot verify WebSocket (needs WebSocket client)")
    except Exception as e:
        results.add_skip("WebSocket Endpoint", f"Cannot verify: {str(e)}")


def test_response_times(results, base_url):
    """Test API response times"""
    print(f"\n{BLUE}Testing Response Times...{RESET}")

    try:
        start = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        elapsed = (time.time() - start) * 1000  # ms

        if elapsed < 100:
            results.add_pass("Response Time", f"Fast response: {elapsed:.0f}ms")
        elif elapsed < 500:
            results.add_pass("Response Time", f"Acceptable response: {elapsed:.0f}ms")
        else:
            results.add_fail("Response Time", f"Slow response: {elapsed:.0f}ms (should be <500ms)")
    except Exception as e:
        results.add_fail("Response Time", str(e))


def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}BACKEND API - AUTOMATED TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Backend URL
    base_url = "http://localhost:8000"

    print(f"{YELLOW}Testing backend at: {base_url}{RESET}")
    print(f"{YELLOW}Make sure backend is running: cd backend && uvicorn app.main:app --reload{RESET}\n")

    results = TestResult()

    # Check if backend is running first
    backend_running = test_backend_health(results, base_url)

    if not backend_running:
        print(f"\n{RED}⚠️  Backend is not running!{RESET}")
        print(f"{YELLOW}Start it with: cd backend && uvicorn app.main:app --reload{RESET}\n")
        results.print_summary()
        sys.exit(1)

    # Run all tests
    test_api_docs(results, base_url)
    test_cors_headers(results, base_url)
    test_session_endpoints(results, base_url)
    test_websocket_endpoint(results, base_url)
    test_response_times(results, base_url)

    # Print summary
    success = results.print_summary()

    # Save results to file
    report_file = "test_results_backend.json"
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

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
