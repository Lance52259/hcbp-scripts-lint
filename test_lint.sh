#!/bin/bash

echo "=== Testing Terraform Lint Tool ==="
echo

echo "1. Testing good example (should pass):"
python3 .github/scripts/terraform_lint.py examples/good-example
good_exit_code=$?

echo
echo "2. Testing bad example (should fail):"
python3 .github/scripts/terraform_lint.py examples/bad-example
bad_exit_code=$?

echo
echo "=== Test Results ==="
if [ $good_exit_code -eq 0 ]; then
    echo "✅ Good example test PASSED (exit code: $good_exit_code)"
else
    echo "❌ Good example test FAILED (exit code: $good_exit_code)"
fi

if [ $bad_exit_code -ne 0 ]; then
    echo "✅ Bad example test PASSED (exit code: $bad_exit_code)"
else
    echo "❌ Bad example test FAILED (exit code: $bad_exit_code)"
fi

echo
if [ $good_exit_code -eq 0 ] && [ $bad_exit_code -ne 0 ]; then
    echo "🎉 All tests PASSED!"
    exit 0
else
    echo "💥 Some tests FAILED!"
    exit 1
fi
