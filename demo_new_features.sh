#!/bin/bash

echo "🚀 Terraform Lint Tool - New Features Demo"
echo "=========================================="

echo ""
echo "📋 Feature List:"
echo "1. Ignore specific rules (ignore-rules)"
echo "2. Specify check paths (include-paths)"
echo "3. Exclude specific paths (exclude-paths)"
echo "4. Combine multiple features"
echo ""

# Demo 1: Ignore specific rules
echo "🔧 Demo 1: Ignore Specific Rules"
echo "Command: python3 .github/scripts/terraform_lint.py --include-paths 'examples/bad-example' --ignore-rules 'ST.001,ST.003'"
echo "Description: Check bad-example but ignore ST.001 and ST.003 rules"
echo "Result:"
python3 .github/scripts/terraform_lint.py --include-paths "examples/bad-example" --ignore-rules "ST.001,ST.003" | grep -E "(Ignoring|Total|ERROR.*\[DC|ERROR.*\[IO|ERROR.*\[ST\.002\])"
echo ""

# Demo 2: Exclude specific paths
echo "🚫 Demo 2: Exclude Specific Paths"
echo "Command: python3 .github/scripts/terraform_lint.py --exclude-paths 'examples/*'"
echo "Description: Check entire project but exclude examples directory"
echo "Result:"
python3 .github/scripts/terraform_lint.py --exclude-paths "examples/*" | grep -E "(Excluding|Total|No .tf files)"
echo ""

# Demo 3: Specify check paths
echo "🎯 Demo 3: Specify Check Paths"
echo "Command: python3 .github/scripts/terraform_lint.py --include-paths 'examples/good-example'"
echo "Description: Only check good-example directory"
echo "Result:"
python3 .github/scripts/terraform_lint.py --include-paths "examples/good-example" | grep -E "(Checking|Total)"
echo ""

# Demo 4: Combine multiple features
echo "🔄 Demo 4: Combine Multiple Features"
echo "Command: python3 .github/scripts/terraform_lint.py --include-paths 'examples' --exclude-paths 'examples/bad-example/*' --ignore-rules 'ST.002'"
echo "Description: Check examples directory, exclude bad-example, ignore ST.002 rule"
echo "Result:"
python3 .github/scripts/terraform_lint.py --include-paths "examples" --exclude-paths "examples/bad-example/*" --ignore-rules "ST.002" | grep -E "(Ignoring|Excluding|Total)"
echo ""

# Demo 5: Help information
echo "❓ Demo 5: View Help Information"
echo "Command: python3 .github/scripts/terraform_lint.py --help"
echo "Result:"
python3 .github/scripts/terraform_lint.py --help | head -15
echo ""

echo "✅ Demo Complete!"
echo ""
echo "💡 GitHub Actions Usage Example:"
echo "```yaml"
echo "- name: Run Terraform Lint"
echo "  uses: Lance52259/hcbp-scripts-lint@v1"
echo "  with:"
echo "    exclude-paths: 'examples/*,test/*'"
echo "    ignore-rules: 'ST.001,DC.001'"
echo "    fail-on-error: 'false'"
echo "```"
