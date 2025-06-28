# Quick Start Guide - Terraform Scripts Lint (Terraform Code Quality Tool)

Welcome to **Terraform Scripts Lint** - the comprehensive Terraform code quality and linting tool! This guide will help
you get started quickly with improving your Terraform configurations.

## 🚀 5-Minute Setup

### Option 1: Local Installation (Recommended)

#### One-Click Installation

**English Version:**
```bash
# Download and run the English installation script
curl -fsSL https://raw.githubusercontent.com/Lance52259/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash
```

**Chinese Version:**
```bash
# Download and run the Chinese installation script
curl -fsSL https://raw.githubusercontent.com/Lance52259/hcbp-scripts-lint/master/tools/zh-cn/quick_install.sh | bash
```

#### Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lance52259/hcbp-scripts-lint.git
   cd hcbp-scripts-lint
   ```

2. **Run the installation script:**
   ```bash
   # English version
   chmod +x tools/en-us/quick_install.sh
   ./tools/en-us/quick_install.sh
   
   # 中文版本
   chmod +x tools/zh-cn/quick_install.sh
   ./tools/zh-cn/quick_install.sh
   ```

3. **Activate the environment:**
   ```bash
   # Reload shell configuration
   source ~/.bashrc
   
   # Test installation
   hcbp-lint --help
   ```

### Option 2: GitHub Actions Integration

1. **Create a workflow file** in your repository:
   ```bash
   mkdir -p .github/workflows
   ```

2. **Add the workflow** (`.github/workflows/hcbp-lint.yml`):
   ```yaml
   name: HCBP Lint - Terraform Code Quality

   on:
     push:
       branches: [ master, develop ]
     pull_request:
       branches: [ master ]

   jobs:
     terraform-lint:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout code
           uses: actions/checkout@v4

         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.8'

         - name: Run HCBP Lint
           run: |
             python3 .github/scripts/terraform_lint.py \
               --directory ./terraform \
               --categories "ST,IO,DC,SC" \
               --report-format both
   ```

## 📁 Example Project Structure

```
your-terraform-project/
├── main.tf                 # Main resources
├── variables.tf            # Variable definitions  
├── outputs.tf              # Output definitions
├── terraform.tfvars        # Variable values
├── modules/
│   └── vpc/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── .github/
    └── workflows/
        └── hcbp-lint.yml   # CI/CD linting
```

## 🎯 Common Use Cases

### 1. Basic Local Linting

```bash
# Check current directory
hcbp-lint

# Check specific directory  
hcbp-lint --directory ./terraform

# Quick check with presets
hcbp-lint-quick
```

### 2. Category-Specific Checks

```bash
# Style checks only
hcbp-lint --categories "ST"

# Input/Output validation
hcbp-lint --categories "IO"

# Documentation checks
hcbp-lint --categories "DC"

# Security checks  
hcbp-lint --categories "SC"

# Combined checks
hcbp-lint --categories "ST,IO,DC,SC"
```

### 3. Advanced Filtering

```bash
# Exclude specific paths - Multiple patterns supported
hcbp-lint --exclude-paths "test/*,examples/*,*.backup"

# Directory exclusion (all formats work)
hcbp-lint --exclude-paths "bad-examples"          # Directory name
hcbp-lint --exclude-paths "./bad-examples"        # Relative path with ./
hcbp-lint --exclude-paths "bad-examples/*"        # Wildcard pattern

# Include only specific paths - Multiple patterns supported
hcbp-lint --include-paths "modules/*,environments/prod/*"
# The include path format is the same as --exclude-paths

# Ignore specific rules
hcbp-lint --ignore-rules "ST.001,ST.003"

# JSON output format
hcbp-lint --report-format json
```

**Path Filtering Tips:**
- Use commas to separate multiple patterns: `"pattern1,pattern2,pattern3"`
- Directory names automatically match subdirectories: `"examples"` excludes `examples/*`
- Glob patterns are supported: `"test/*"`, `"*.backup"`, `"**/*.tmp"`
- Both relative (`"./examples"`) and simple (`"examples"`) formats work

### 4. Git Integration

```bash
# Check only changed files (requires git)
hcbp-lint --changed-files-only

# Check against specific branch
hcbp-lint --changed-files-only --base-ref origin/master
```

### 5. Project Integration Scripts

**Create a project check script** (`scripts/check-terraform.sh`):
```bash
#!/bin/bash

echo "🔍 Running Terraform Code Quality Check..."

hcbp-lint \
  --directory . \
  --exclude-paths ".terraform/*,*.backup,test/*" \
  --categories "ST,IO,DC,SC" \
  --report-format both

if [ $? -eq 0 ]; then
    echo "✅ Code quality check passed!"
else
    echo "❌ Code quality issues found. Please fix before committing."
    exit 1
fi
```

**Git pre-commit hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash

echo "Running HCBP Lint before commit..."

hcbp-lint --changed-files-only --categories "ST,IO"

if [ $? -ne 0 ]; then
    echo "❌ Linting failed. Commit blocked."
    echo "Fix the issues above and try again."
    exit 1
fi

echo "✅ Linting passed. Proceeding with commit."
```

## 🔧 Configuration Reference

### Command Line Options

```bash
hcbp-lint [OPTIONS]

Core Options:
  -d, --directory TEXT          Target directory (default: current)
  --categories TEXT             Rule categories: ST,IO,DC,SC
  --ignore-rules TEXT           Rules to skip (e.g., ST.001,ST.003)
  
Path Filtering:
  --include-paths TEXT          Paths to include (glob patterns)
  --exclude-paths TEXT          Paths to exclude (glob patterns)
  
Git Integration:
  --changed-files-only          Check only modified files
  --base-ref TEXT               Base reference for git diff
  
Output Control:
  --report-format [text|json|both]  Output format
  --performance-monitoring      Show performance metrics
  --help                        Show detailed help
```

### Configuration File

The installer creates `~/.hcbp-lint.conf` with default settings:

```ini
# HCBP Lint Configuration File

# Common configuration options
DEFAULT_CATEGORIES="ST,IO,DC,SC"
DEFAULT_REPORT_FORMAT="text"  
DEFAULT_EXCLUDE_PATHS="*.backup,.terraform/*,test/*"

# Usage examples:
# hcbp-lint --directory ./terraform
# hcbp-lint --categories "ST,IO"
# hcbp-lint --exclude-paths "test/*,examples/*"
```

## 📊 Understanding Output

### Success Output
```
🎉 HCBP Lint Analysis - PASSED

✅ Result: SUCCESS
📁 Files Processed: 15
⏱️  Execution Time: 1.2s
🔍 Rules Applied: 21 (ST:11, IO:8, DC:1, SC:1)

All Terraform files passed the quality checks!
```

### Error Output  
```
❌ HCBP Lint Analysis - FAILED

❌ Result: FAILED
🚨 Errors: 3  
⚠️  Warnings: 1
📁 Files Processed: 15

Errors Found:
  main.tf:5    [ST.001] Resource name should use underscores
  variables.tf:12 [IO.006] Variable missing description  
  outputs.tf:8    [DC.001] Output missing description

Quick Fix Suggestions:
- ST.001: Use snake_case for resource names
- IO.006: Add descriptions to all variables
- DC.001: Add descriptions to all outputs
```

## 🚨 Common Issues & Solutions

### Issue 1: Command not found after installation
```bash
# Solution: Reload shell configuration
source ~/.bashrc

# Or restart your terminal
# Alternative: Use full path temporarily
~/.local/bin/hcbp-lint --help
```

### Issue 2: "No Terraform files found"
```bash
# Check if .tf files exist
find . -name "*.tf" -type f

# Specify correct directory
hcbp-lint --directory ./infrastructure
```

### Issue 3: Git diff errors with changed-files-only
```bash
# Ensure git repository is properly initialized
git status

# For GitHub Actions, ensure fetch-depth: 0
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

### Issue 4: Python version issues
```bash
# Check Python version (requires 3.6+)
python3 --version

# Update Python if needed (Ubuntu/Debian)
sudo apt update && sudo apt install python3.8
```

## 🎓 Rule Categories Explained

### 🎨 ST (Style/Format) - 11 Rules
- **Purpose**: Code formatting and consistency
- **Examples**: Naming conventions, indentation, spacing
- **Usage**: `hcbp-lint --categories "ST"`

### 📝 IO (Input/Output) - 8 Rules  
- **Purpose**: Variable and output management
- **Examples**: Variable descriptions, output definitions
- **Usage**: `hcbp-lint --categories "IO"`

### 📚 DC (Documentation/Comments) - 1 Rule
- **Purpose**: Documentation standards
- **Examples**: Comment formatting, inline documentation
- **Usage**: `hcbp-lint --categories "DC"`

### 🔒 SC (Security Code) - 1 Rule
- **Purpose**: Security best practices
- **Examples**: Sensitive data handling, secure configurations
- **Usage**: `hcbp-lint --categories "SC"`

## 📈 Performance Tips

### For Large Repositories
```bash
# Use changed-files-only for PR workflows
hcbp-lint --changed-files-only

# Filter specific paths
hcbp-lint --include-paths "src/*" --exclude-paths "test/*"

# Run specific categories for faster execution
hcbp-lint --categories "ST,IO"  # Skip DC and SC

# Enable performance monitoring
hcbp-lint --performance-monitoring
```

### Example Optimized Workflow
```yaml
name: Fast PR Check
on:
  pull_request:
    paths: ['**.tf']

jobs:
  quick-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          
      - name: Quick Style Check
        run: |
          python3 .github/scripts/terraform_lint.py \
            --changed-files-only \
            --categories "ST" \
            --performance-monitoring
```

## 🔄 Updating HCBP Lint

```bash
# Re-run the installation script to update
./tools/en-us/quick_install.sh

# Or for Chinese version
./tools/zh-cn/quick_install.sh

# The script will automatically update to the latest version
```

## 🌍 Multi-Language Support

HCBP Lint provides installation scripts in multiple languages:

- **English**: `tools/en-us/quick_install.sh`
- **中文**: `tools/zh-cn/quick_install.sh`

Both scripts provide identical functionality with localized user interface.

## 🎯 Next Steps

1. **📖 Read Full Documentation**: [README.md](README.md) for advanced features
2. **🔍 Explore Rules**: [rules/introduction.md](rules/introduction.md) for detailed rule explanations  
3. **🤝 Contribute**: [CONTRIBUTING.md](CONTRIBUTING.md) to help improve the project
4. **💬 Get Support**: [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues) for questions

## 📞 Need Help?

- 📖 **Full Documentation**: [README.md](README.md)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- 💭 **Discussions**: [GitHub Discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)
- 📚 **Rule Details**: [rules/introduction.md](rules/introduction.md)

## 🚀 Quick Test

After installation, test with the provided examples:

```bash
# Test with good example (should pass)
hcbp-lint --directory ~/.local/share/terraform-linter/examples/good-example

# Test with bad example (should show errors)  
hcbp-lint --directory ~/.local/share/terraform-linter/examples/bad-example
```

---

**Happy Linting!** 🎉 Start improving your Terraform code quality today with HCBP Lint!
