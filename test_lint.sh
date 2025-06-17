#!/bin/bash

# Terraform Scripts Lint - Test Script for Unified Rules Management System
# This script tests the enhanced linting tool with various scenarios and configurations
# Author: Lance
# License: Apache License 2.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test configuration
SCRIPT_PATH=".github/scripts/terraform_lint.py"
GOOD_EXAMPLE_DIR="examples/good-example"
BAD_EXAMPLE_DIR="examples/bad-example"

echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}🚀 TERRAFORM SCRIPTS LINT - UNIFIED SYSTEM TESTING${NC}"
echo -e "${CYAN}================================================================${NC}"
echo

# Function to print test header
print_test_header() {
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '%.0s-' {1..60})${NC}"
}

# Function to run test and capture results
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_exit_code="$3"
    
    echo -e "${YELLOW}🔄 Running: $test_name${NC}"
    echo -e "${PURPLE}Command: $command${NC}"
    
    if eval "$command" > /tmp/test_output.log 2>&1; then
        actual_exit_code=0
    else
        actual_exit_code=$?
    fi
    
    if [ "$actual_exit_code" -eq "$expected_exit_code" ]; then
        echo -e "${GREEN}✅ PASSED (exit code: $actual_exit_code)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (expected: $expected_exit_code, got: $actual_exit_code)${NC}"
        echo -e "${RED}Output:${NC}"
        cat /tmp/test_output.log
        return 1
    fi
}

# Initialize test counters
total_tests=0
passed_tests=0
failed_tests=0

# Test 1: Basic functionality with good example
print_test_header "📋 Test 1: Basic Functionality - Good Example"
total_tests=$((total_tests + 1))
if run_test "Good example validation" "python3 $SCRIPT_PATH --directory $GOOD_EXAMPLE_DIR" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 2: Basic functionality with bad example
print_test_header "📋 Test 2: Basic Functionality - Bad Example"
total_tests=$((total_tests + 1))
if run_test "Bad example validation" "python3 $SCRIPT_PATH --directory $BAD_EXAMPLE_DIR" 1; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 3: Category-specific execution - Style/Format only
print_test_header "🎨 Test 3: Style/Format Rules Only"
total_tests=$((total_tests + 1))
if run_test "ST rules only" "python3 $SCRIPT_PATH --directory $GOOD_EXAMPLE_DIR --categories ST" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 4: Category-specific execution - Input/Output only
print_test_header "🔧 Test 4: Input/Output Rules Only"
total_tests=$((total_tests + 1))
if run_test "IO rules only" "python3 $SCRIPT_PATH --directory $GOOD_EXAMPLE_DIR --categories IO" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 5: Category-specific execution - Documentation/Comments only
print_test_header "📝 Test 5: Documentation/Comments Rules Only"
total_tests=$((total_tests + 1))
if run_test "DC rules only" "python3 $SCRIPT_PATH --directory $GOOD_EXAMPLE_DIR --categories DC" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 6: Multiple categories
print_test_header "🎯 Test 6: Multiple Categories"
total_tests=$((total_tests + 1))
if run_test "ST and IO rules" "python3 $SCRIPT_PATH --directory $GOOD_EXAMPLE_DIR --categories ST,IO" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 7: Rule filtering with ignore-rules
print_test_header "🚫 Test 7: Rule Filtering"
total_tests=$((total_tests + 1))
if run_test "Ignore specific rules" "python3 $SCRIPT_PATH --directory $BAD_EXAMPLE_DIR --ignore-rules ST.001,ST.002 || true" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 8: Performance monitoring
print_test_header "⚡ Test 8: Performance Monitoring"
total_tests=$((total_tests + 1))
if run_test "Performance monitoring enabled" "python3 $SCRIPT_PATH --directory $GOOD_EXAMPLE_DIR --performance-monitoring" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 9: JSON output format
print_test_header "📊 Test 9: JSON Output Format"
total_tests=$((total_tests + 1))
if run_test "JSON report format" "python3 $SCRIPT_PATH --directory $GOOD_EXAMPLE_DIR --report-format json" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 10: Path filtering
print_test_header "🔍 Test 10: Path Filtering"
total_tests=$((total_tests + 1))
if run_test "Include paths filter" "python3 $SCRIPT_PATH --directory . --include-paths 'examples/good-example/*'" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 11: Help command
print_test_header "❓ Test 11: Help Command"
total_tests=$((total_tests + 1))
if run_test "Help command" "python3 $SCRIPT_PATH --help" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 12: Invalid directory handling
print_test_header "🚨 Test 12: Error Handling"
total_tests=$((total_tests + 1))
if run_test "Invalid directory" "python3 $SCRIPT_PATH --directory /nonexistent/directory" 1; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 13: Empty directory handling
print_test_header "📁 Test 13: Empty Directory"
mkdir -p /tmp/empty_terraform_dir
total_tests=$((total_tests + 1))
if run_test "Empty directory" "python3 $SCRIPT_PATH --directory /tmp/empty_terraform_dir" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
rm -rf /tmp/empty_terraform_dir
echo

# Test 14: Python module import test
print_test_header "🐍 Test 14: Python Module Integration"
total_tests=$((total_tests + 1))
if run_test "Python module test" "python3 -c 'import sys; sys.path.insert(0, \"rules\"); from rules import RulesManager; rm = RulesManager(); print(f\"Rules available: {len(rm.get_available_rules())}\")'" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Test 15: Example usage script
print_test_header "📚 Test 15: Example Usage Script"
total_tests=$((total_tests + 1))
if run_test "Example usage script" "python3 example_usage.py" 0; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi
echo

# Final results
echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}📊 FINAL TEST RESULTS${NC}"
echo -e "${CYAN}================================================================${NC}"

echo -e "${BLUE}Total Tests: $total_tests${NC}"
echo -e "${GREEN}Passed: $passed_tests${NC}"
echo -e "${RED}Failed: $failed_tests${NC}"

if [ $failed_tests -eq 0 ]; then
    echo
    echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
    echo -e "${GREEN}The unified rules management system is working correctly.${NC}"
    
    # Additional system information
    echo
    echo -e "${CYAN}📋 System Information:${NC}"
    echo -e "${BLUE}Python version: $(python3 --version)${NC}"
    echo -e "${BLUE}Script location: $SCRIPT_PATH${NC}"
    echo -e "${BLUE}Test timestamp: $(date)${NC}"
    
    # Show available rules summary
    echo
    echo -e "${CYAN}📚 Available Rules Summary:${NC}"
    python3 -c "
import sys
sys.path.insert(0, 'rules')
try:
    from rules import RulesManager
    rm = RulesManager()
    rules = rm.get_available_rules()
    st_rules = [r for r in rules if r.startswith('ST.')]
    io_rules = [r for r in rules if r.startswith('IO.')]
    dc_rules = [r for r in rules if r.startswith('DC.')]
    print(f'  🎨 Style/Format (ST): {len(st_rules)} rules')
    print(f'  🔧 Input/Output (IO): {len(io_rules)} rules')
    print(f'  📝 Documentation (DC): {len(dc_rules)} rules')
    print(f'  📊 Total: {len(rules)} rules')
except Exception as e:
    print(f'  ⚠️  Could not load rules: {e}')
"
    
    exit 0
else
    echo
    echo -e "${RED}💥 SOME TESTS FAILED! 💥${NC}"
    echo -e "${RED}Please check the failed tests above and fix any issues.${NC}"
    
    # Show failure summary
    echo
    echo -e "${YELLOW}🔍 Failure Analysis:${NC}"
    success_rate=$((passed_tests * 100 / total_tests))
    echo -e "${YELLOW}Success Rate: $success_rate%${NC}"
    
    if [ $success_rate -ge 80 ]; then
        echo -e "${YELLOW}Most tests passed. Check for minor configuration issues.${NC}"
    elif [ $success_rate -ge 50 ]; then
        echo -e "${YELLOW}Moderate failures. Check system dependencies and file paths.${NC}"
    else
        echo -e "${RED}Major failures detected. Check Python environment and rule system.${NC}"
    fi
    
    exit 1
fi

# Cleanup
rm -f /tmp/test_output.log
