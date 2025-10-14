#!/bin/bash

# LLM Session Manager - Quick Test Suite
# Runs all component tests in sequence

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   LLM Session Manager - Automated Test Suite              ║"
echo "╔════════════════════════════════════════════════════════════╗"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 Test: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if eval "$test_command" > /tmp/test_output.txt 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "Error output:"
        tail -20 /tmp/test_output.txt
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Change to project directory
cd /Users/gagan/llm-session-manager

echo "Phase 1: Component Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Session Discovery
run_test "Session Discovery" "python test_discovery.py"

# Test 2: Token Estimation
run_test "Token Estimation" "python test_token_estimator.py"

# Test 3: Health Monitor
run_test "Health Monitor" "python test_health_monitor.py"

# Test 4: Dashboard (Single Refresh)
run_test "Dashboard Rendering" "python test_dashboard.py"

echo ""
echo "Phase 2: CLI Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 5: CLI Help
run_test "CLI Help" "python -m llm_session_manager.cli --help"

# Test 6: CLI Info
run_test "CLI Info" "python -m llm_session_manager.cli info"

# Test 7: CLI List (Table)
run_test "CLI List (Table)" "python -m llm_session_manager.cli list"

# Test 8: CLI List (JSON)
run_test "CLI List (JSON)" "python -m llm_session_manager.cli list --format json"

echo ""
echo "Phase 3: Export/Import Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get first session ID for testing
SESSION_ID=$(python -m llm_session_manager.cli list --format json 2>/dev/null | python -c "import sys, json; sessions = json.load(sys.stdin); print(sessions[0]['id'][:20] if sessions else '')" 2>/dev/null)

if [ -n "$SESSION_ID" ]; then
    # Test 9: CLI Export
    run_test "CLI Export" "python -m llm_session_manager.cli export $SESSION_ID --output test_auto_export.json"

    # Test 10: CLI Import
    if [ -f test_auto_export.json ]; then
        run_test "CLI Import" "python -m llm_session_manager.cli import-context test_auto_export.json"

        # Test 11: CLI Health
        run_test "CLI Health" "python -m llm_session_manager.cli health $SESSION_ID"
    else
        echo -e "${YELLOW}⚠️  SKIPPED: Export/Import/Health tests (export failed)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  SKIPPED: Export/Import/Health tests (no sessions found)${NC}"
fi

echo ""
echo "Phase 4: Error Handling Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 12: Invalid Session ID (should fail gracefully)
echo "🧪 Test: Invalid Session ID (Expected to fail gracefully)"
python -m llm_session_manager.cli export invalid_session_12345 2>&1 | grep -q "not found"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED (Error handled correctly)${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAILED (Error not handled correctly)${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Test 13: Invalid JSON Import
echo "🧪 Test: Invalid JSON Import (Expected to fail gracefully)"
echo "{ invalid json }" > /tmp/invalid_test.json
python -m llm_session_manager.cli import-context /tmp/invalid_test.json 2>&1 | grep -q "Invalid JSON"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED (Error handled correctly)${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAILED (Error not handled correctly)${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Test 14: Missing File
echo "🧪 Test: Missing File (Expected to fail gracefully)"
python -m llm_session_manager.cli import-context /nonexistent/file.json 2>&1 | grep -q "not found"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED (Error handled correctly)${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAILED (Error not handled correctly)${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Summary
TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                            ║"
echo "╠════════════════════════════════════════════════════════════╣"
printf "║  Total Tests:    %-5d                                    ║\n" $TOTAL_TESTS
printf "║  ${GREEN}Passed:${NC}          %-5d                                    ║\n" $TESTS_PASSED
printf "║  ${RED}Failed:${NC}          %-5d                                    ║\n" $TESTS_FAILED

if [ $TESTS_FAILED -eq 0 ]; then
    echo "╠════════════════════════════════════════════════════════════╣"
    echo -e "║  ${GREEN}✅ ALL TESTS PASSED!${NC}                                    ║"
else
    echo "╠════════════════════════════════════════════════════════════╣"
    echo -e "║  ${RED}❌ SOME TESTS FAILED${NC}                                     ║"
fi
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Cleanup
rm -f /tmp/test_output.txt /tmp/invalid_test.json test_auto_export.json

# Exit with appropriate code
if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
