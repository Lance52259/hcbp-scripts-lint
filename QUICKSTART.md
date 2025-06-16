# Quick Start Guide

Get started with Terraform Scripts Lint in under `5` minutes!

## 🚀 Quick Setup

### Option 1: GitHub Actions (Recommended)

Add this to your `.github/workflows/terraform-lint.yml`:

```yaml
name: Terraform Lint

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Terraform Lint
      uses: Lance52259/hcbp-scripts-lint@v1.0.0
      # uses: ./                             # Use for local copy
      with:
        directory: '.'
        fail-on-error: 'true'
```

### Option 2: Local Usage

```bash
# Clone the repository
git clone https://github.com/Lance52259/hcbp-scripts-lint.git
cd hcbp-scripts-lint

# Run on your Terraform files
python3 .github/scripts/terraform_lint.py --directory /path/to/your/terraform/files
```

## 📋 Basic Usage Examples

### Check Current Directory

```bash
python3 .github/scripts/terraform_lint.py
```

### Check Specific Directory

```bash
python3 .github/scripts/terraform_lint.py --directory ./infrastructure
```

### Ignore Specific Rules

```bash
python3 .github/scripts/terraform_lint.py --ignore-rules "ST.001,ST.003"
```

### Filter Paths

```bash
# Only check specific paths
python3 .github/scripts/terraform_lint.py --include-paths "modules/vpc,modules/compute"

# Exclude specific paths
python3 .github/scripts/terraform_lint.py --exclude-paths "examples/*,test/*"
```

### Check Only Changed Files (Recommended for Large Repositories)

```bash
# Check only files changed in current commit
python3 .github/scripts/terraform_lint.py --changed-files-only

# Check files changed compared to specific branch
python3 .github/scripts/terraform_lint.py --changed-files-only --base-ref origin/main

# Combine with other options
python3 .github/scripts/terraform_lint.py --changed-files-only --ignore-rules "ST.001"
```

## 🔧 Common Configurations

### Development Environment (Flexible)

```yaml
- name: Development Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    directory: './dev'
    ignore-rules: 'ST.001,ST.003'  # Allow flexible naming and formatting
    fail-on-error: 'false'         # Don't break the build
```

### Production Environment (Strict)

```yaml
- name: Production Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    directory: './prod'
    fail-on-error: 'true'          # Enforce all rules
```

### Module Validation

```yaml
- name: Module Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    include-paths: './modules'
    exclude-paths: 'modules/*/examples/*'
    fail-on-error: 'true'
```

### Pull Request Workflow (Optimized for Performance)

```yaml
- name: PR Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    changed-files-only: 'true'     # Only check changed files
    base-ref: 'origin/main'        # Compare against main branch
    fail-on-error: 'true'
```

### Large Repository Configuration

```yaml
- name: Large Repo Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    changed-files-only: 'true'     # Performance optimization
    include-paths: 'infrastructure/*,modules/*'
    exclude-paths: 'examples/*,test/*,docs/*'
    ignore-rules: 'ST.003'         # Skip formatting rules for speed
    fail-on-error: 'true'
```

## 📊 Understanding the Output

### Sample Output

```
=== Terraform Scripts Lint Report ===
Total Errors: 3
Total Warnings: 0

ERRORS:
  ERROR: main.tf: [ST.001] Resource 'aws_instance' instance name 'BadName' should be 'test'
  ERROR: main.tf: [ST.002] Variable 'region' must have a default value
  ERROR: main.tf: [IO.001] Variables ['region'] should be defined in variables.tf file
```

### Rule Categories
- **ST (Style/Format)**: Naming conventions, formatting, defaults
- **DC (Documentation/Comments)**: Comment formatting
- **IO (Input/Output)**: File organization, variable definitions

## 🛠️ Quick Fixes

### Fix ST.001 (Naming Convention)

```hcl
# ❌ Bad
resource "aws_instance" "MyServer" {
  # ...
}

# ✅ Good
resource "aws_instance" "test" {
  # ...
}
```

### Fix ST.002 (Variable Defaults)

```hcl
# ❌ Bad
variable "region" {
  description = "AWS region"
  type        = string
}

# ✅ Good
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}
```

### Fix ST.003 (Parameter Alignment)

```hcl
# ❌ Bad
resource "aws_instance" "test" {
  ami= "ami-12345"
  instance_type  ="t2.micro"
}

# ✅ Good
resource "aws_instance" "test" {
  ami           = "ami-12345"
  instance_type = "t2.micro"
}
```

### Fix IO.001 (Variable Organization)

```hcl
# ❌ Bad: Variables in main.tf
variable "region" {
  default = "us-west-2"
}

# ✅ Good: Variables in variables.tf
# Move to variables.tf file
```

### Fix IO.002 (Output Organization)

```hcl
# ❌ Bad: Outputs in main.tf
output "instance_id" {
  value = aws_instance.test.id
}

# ✅ Good: Outputs in outputs.tf
# Move to outputs.tf file
```

## 🎯 Best Practices

### 1. Start with Flexible Rules

Begin with ignored rules and gradually enforce them:

```bash
python3 .github/scripts/terraform_lint.py --ignore-rules "ST.001,ST.003" --fail-on-error false
```

### 2. Use Path Filtering for Large Projects

```bash
# Check only critical modules first
python3 .github/scripts/terraform_lint.py --include-paths "modules/core,modules/security"
```

### 3. Integrate with CI/CD Pipeline

```yaml
# Run on every PR
on:
  pull_request:
    paths:
      - '**/*.tf'
      - '**/*.tfvars'
```

### 4. Generate Reports for Review

```yaml
- name: Upload Lint Report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: terraform-lint-report
    path: terraform-lint-report.txt
```

## 🔍 Troubleshooting

### No .tf Files Found

```bash
# Check if you're in the right directory
ls -la *.tf

# Specify the correct directory
python3 .github/scripts/terraform_lint.py --directory ./terraform
```

### Permission Denied

```bash
# Make sure the script is executable
chmod +x .github/scripts/terraform_lint.py

# Or run with python3 explicitly
python3 .github/scripts/terraform_lint.py
```

### Rule Not Found Error

```bash
# Check available rules
python3 .github/scripts/terraform_lint.py --help

# Valid rule IDs: 
#   ST.001, ST.002, ST.003, ST.004, ST.005, ST.006, ST.007, ST.008, ST.009
#   DC.001
#   IO.001, IO.002, IO.003, IO.004, IO.005, IO.006, IO.007, IO.008
```

## 📚 Next Steps

1. **Read the Full Documentation**: Check `README.md` for comprehensive usage
2. **Explore Examples**: Look at `examples/` directory for real-world usage
3. **Customize Rules**: Review `rules/rule_details.md` for rule explanations
4. **Contribute**: See `CONTRIBUTING.md` for contribution guidelines
5. **Get Support**: Open issues on GitHub for help

## 🎉 You're Ready!

You now have Terraform Scripts Lint running on your project. The tool will help you maintain consistent,
high-quality Terraform code by automatically checking for common issues and enforcing best practices.

### 🚀 Quick Commands Reference

```bash
# Basic usage
python3 .github/scripts/terraform_lint.py --directory ./terraform

# GitHub Actions (add to .github/workflows/terraform-lint.yml)
uses: Lance52259/hcbp-scripts-lint@v1.1.0
```

Happy linting!
