#!/bin/bash
# Automated Testing Suite
set -e
clear
echo "🧪 Running Automated Tests..."
echo ""
mkdir -p tests
python3 tests/test_cli_automated.py
echo ""
echo "✅ Testing complete! Check test_results_cli.json for details"
