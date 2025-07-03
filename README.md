# Terraform Scripts Lint - Unified Rules Management System

[![GitHub Release](https://img.shields.io/github/v/release/Lance52259/hcbp-scripts-lint)](https://github.com/Lance52259/hcbp-scripts-lint/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-compatible-green.svg)](action.yml)

A comprehensive and enhanced linting tool for Terraform scripts that uses a **unified rules management system** to
ensure code quality, consistency, and best practices. This tool provides advanced rule coordination, detailed analytics,
and flexible configuration options for teams of all sizes.

## 🚀 Key Features

### Unified Rules Management System
- **Centralized Coordination**: Single point of control for all linting rules
- **Advanced Rule Discovery**: Automatic detection and organization of available rules
- **Flexible Rule Filtering**: Filter by category, severity, or specific rule IDs
- **Performance Monitoring**: Built-in analytics and execution time tracking
- **Extensible Architecture**: Easy to add new rules and categories

### Enhanced Linting Capabilities
- **Four Rule Categories**: ST (Style/Format), IO (Input/Output), DC (Documentation/Comments), SC (Security Code)
- **Intelligent Path Filtering**: Include/exclude specific directories and files
- **Git Integration**: Check only changed files in commits or pull requests
- **Comprehensive Reporting**: Detailed reports with performance metrics
- **GitHub Actions Ready**: Seamless CI/CD integration with enhanced outputs

### Performance & Reliability
- **Optimized Execution**: Parallel rule processing and efficient file handling
- **Memory Efficient**: Processes files individually to minimize memory usage
- **Error Resilience**: Robust error handling and recovery mechanisms
- **Detailed Logging**: Comprehensive logging for debugging and monitoring

## 📋 Rule Categories

Through the **unified rules management system**, all rules are organized into four main categories, each managed by a
dedicated coordinator:

### ST (Style/Format) Rules
Code formatting and style consistency rules, managed by the `STRules` coordinator:
- **ST.001**: Resource and data source naming conventions
- **ST.002**: Default value checking convention
- **ST.003**: Parameter alignment with equals signs aligned to maintain one space from longest parameter name
- **ST.004**: Indentation character validation (spaces only)
- **ST.005**: Proper indentation level enforcement
- **ST.006**: Resource and data source spacing standards
- **ST.007**: Same parameter block spacing consistency
- **ST.008**: Different parameter type spacing rules (exactly 1 empty line between basic parameters and parameter blocks)
- **ST.009**: Variable order validation
- **ST.010**: Resource, data source, variable, and output quote standards
- **ST.011**: Trailing whitespace check

### IO (Input/Output) Rules
Variable and output definition validation rules, managed by the `IORules` coordinator:
- **IO.001**: Variable definition file organization
- **IO.002**: Output definition file organization
- **IO.003**: Required variable declaration check in terraform.tfvars
- **IO.004**: Variable naming convention check
- **IO.005**: Output naming convention check
- **IO.006**: Variable description validation (non-empty descriptions required)
- **IO.007**: Output description validation (non-empty descriptions required)
- **IO.008**: Variable type validation (type field required)
- **IO.009**: Unused variable detection (variables defined but not used)

### DC (Documentation/Comments) Rules
Documentation and comment standard rules, managed by the `DCRules` coordinator:
- **DC.001**: Comment formatting and style standards

### SC (Security Code) Rules
Security best practices and safety validation rules, managed by the `SCRules` coordinator:
- **SC.001**: Array index access safety check (prevents index out of bounds errors using try() function)

> **Unified Management Advantages**: All rules are coordinated through the `RulesManager`, providing cross-category
  performance monitoring, batch execution, and comprehensive reporting capabilities.

## 🔧 Installation & Usage

### GitHub Actions (Recommended)

Add the following step to your GitHub Actions workflow:

```yaml
- name: Terraform Scripts Lint
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    directory: './terraform'
    rule-categories: 'ST,IO,DC,SC'
    ignore-rules: 'ST.001,ST.003'
    fail-on-error: 'true'
    performance-monitoring: 'true'
```

> ⚠️ **Notes on cross-repository push**: If you push from a personal repository branch to a target repository, you may
  encounter an error that the branch does not exist. Please refer to the [Cross-repository push configuration guide](CROSS_REPO_PUSH.md)
  to learn how to correctly configure the checkout step.

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lance52259/hcbp-scripts-lint.git
   cd hcbp-scripts-lint
   ```

2. **Run the linter:**
   ```bash
   python3 .github/scripts/terraform_lint.py --directory ./terraform
   ```

3. **Advanced usage with filtering:**
   ```bash
   python3 .github/scripts/terraform_lint.py \
     --directory ./infrastructure \
     --categories "ST,IO" \
     --ignore-rules "ST.001,ST.003" \
     --exclude-paths "examples/*,test/*" \
     --performance-monitoring
   ```

## ⚙️ Configuration Options

### GitHub Actions Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `directory` | Target directory to check | `.` | No |
| `rule-categories` | Rule categories to execute (ST,IO,DC,SC) | `ST,IO,DC,SC` | No |
| `ignore-rules` | Comma-separated list of rules to ignore | `` | No |
| `include-paths` | Path patterns to include | `` | No |
| `exclude-paths` | Path patterns to exclude | `` | No |
| `changed-files-only` | Check only changed files | `false` | No |
| `base-ref` | Base reference for git diff | `origin/main` | No |
| `performance-monitoring` | Enable performance analytics (true/false, case-insensitive) | `true` | No |
| `report-format` | Output format (text, json, or both) | `text` | No |
| `detailed-summary` | Show detailed error information in GitHub Actions summary | `true` | No |
| `fail-on-error` | Fail workflow on errors | `true` | No |

### Command Line Options

```bash
python3 .github/scripts/terraform_lint.py [OPTIONS]

Options:
  -d, --directory TEXT          Target directory to check
  --categories TEXT             Rule categories (ST,IO,DC,SC)
  --ignore-rules TEXT           Rules to ignore (comma-separated)
  --include-paths TEXT          Paths to include (comma-separated)
  --exclude-paths TEXT          Paths to exclude (comma-separated)
  --changed-files-only          Check only changed files
  --base-ref TEXT               Base reference for git diff
  --performance-monitoring      Enable performance monitoring (true/false, case-insensitive)
  --report-format [text|json|both]   Output report format
  --help                        Show help message
```

## 📊 Enhanced Summary Reports

### GitHub Actions Summary with Detailed Error Analysis

When `detailed-summary` is enabled (default), the action provides a comprehensive summary in the GitHub Actions interface:

#### ✅ Success Summary
```markdown
# 🎉 Terraform Lint Analysis - PASSED

✅ **Result**: SUCCESS  
📁 **Files Processed**: 15  
⏱️ **Execution Time**: 2.1s  

## 📋 Summary
All Terraform files passed the linting checks successfully!

## 📈 Performance Metrics
- **Processing Speed**: 7.1 files/second
- **Lines Analyzed**: 850 lines (404 lines/second)

## 🔧 Configuration
- **Report Format**: both
- **Rule Categories**: ST, IO, DC, SC
- **Performance Monitoring**: enabled
```

#### ❌ Detailed Error Summary
```markdown
# ❌ Terraform Lint Analysis - FAILED

❌ **Result**: FAILED  
🚨 **Errors**: 5  
⚠️ **Warnings**: 3  
📁 **Files Processed**: 12  
⏱️ **Execution Time**: 1.8s  

## 🔍 Detailed Error Analysis

### 🚨 Errors Found (5)
| File | Line | Rule | Description |
|------|------|------|-------------|
| main.tf | 15 | ST.001 | Resource name 'aws_instance.web-server' should use underscores |
| variables.tf | 8 | IO.006 | Variable 'instance_type' missing description |
| outputs.tf | 12 | IO.007 | Output 'instance_ip' missing description |
| main.tf | 95 | SC.001 | Unsafe array index access detected in data source list attribute |

### ⚠️ Warnings Found (3)
| File | Line | Rule | Description |
|------|------|------|-------------|
| main.tf | 25 | ST.008 | Missing blank line between parameter types |
| variables.tf | 15 | ST.010 | Variable value should use double quotes |
| main.tf | 97 | SC.001 | Unsafe array index access detected in for expression result |

## 📊 Error Categories
- **ST (Style/Format)**: 3 errors, 2 warnings
- **IO (Input/Output)**: 2 errors, 1 warning
- **DC (Documentation)**: 0 errors, 0 warnings
- **SC (Security Code)**: 1 error, 1 warning

### 🔧 Quick Fix Suggestions
- **ST.001**: Use underscores in resource names: `aws_instance.web_server`
- **IO.006/IO.007**: Add descriptions to variables and outputs
- **ST.008**: Add blank lines between different parameter types
- **ST.010**: Use double quotes for string values
- **SC.001**: Use try() function for safe array access: `try(data.source.list[0], "fallback")`

## 🎯 Most Common Issues
1. **ST.001** (Resource Naming): 2 occurrences
2. **IO.006** (Variable Descriptions): 1 occurrence
3. **ST.008** (Parameter Spacing): 1 occurrence
4. **SC.001** (Array Safety): 2 occurrences

## 📂 Affected Files
- `main.tf` (3 issues)
- `variables.tf` (2 issues) 
- `outputs.tf` (1 issue)

## 📈 Performance Metrics
- **Processing Speed**: 6.7 files/second
- **Lines Analyzed**: 720 lines (400 lines/second)

## 🔧 Configuration  
- **Report Format**: both
- **Rule Categories**: ST, IO, DC, SC
- **Performance Monitoring**: enabled

## 📎 Artifacts
- **Text Report**: terraform-lint-report-unified-{timestamp}.txt
- **JSON Report**: terraform-lint-report-unified-{timestamp}.json

> 💡 **Tip**: Download the detailed reports from the action artifacts for complete analysis.
```

### Basic Summary Mode

When `detailed-summary` is set to `false`, a simplified summary is displayed:

```markdown
# Terraform Lint Analysis

❌ **Result**: FAILED  
🚨 **Errors**: 5  
⚠️ **Warnings**: 3  
📁 **Files Processed**: 12  
⏱️ **Execution Time**: 1.8s  

Download the detailed reports from action artifacts for complete analysis.
```

## 📊 Enhanced Outputs

### GitHub Actions Outputs

| Output | Description |
|--------|-------------|
| `result` | Overall result (success/failure) |
| `error-count` | Number of errors found |
| `warning-count` | Number of warnings found |
| `violation-count` | Total violations found |
| `files-processed` | Number of files processed |
| `execution-time` | Total execution time in seconds |
| `rules-executed` | Total number of rules executed |
| `performance-metrics` | JSON with performance data |
| `report-file` | Path to the generated report |

### Performance Metrics

The unified system provides detailed performance analytics:

```json
{
  "files_per_second": 15.2,
  "lines_per_second": 1250,
  "rules_per_second": 45.8,
  "execution_time": 2.34,
  "files_processed": 35,
  "rules_executed": 105
}
```

## 📈 Advanced Usage Examples

### 1. Cross-Repository Push Handling

When pushing from personal forks or branches that don't exist in the target repository, use this configuration:

```yaml
name: Terraform Lint (Cross-Repo Safe)
on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Smart Checkout
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
          fetch-depth: 0
          
      - name: Fallback Checkout
        if: failure()
        uses: actions/checkout@v4
        with:
          ref: 'master'  # or 'main' based on your default branch
          fetch-depth: 0
      
      - name: Terraform Lint with Smart Base-Ref
        uses: Lance52259/hcbp-scripts-lint@v2.0.0
        with:
          directory: '.'
          changed-files-only: 'true'
          base-ref: ${{ 
            github.event_name == 'pull_request' && github.event.pull_request.base.sha ||
            github.event_name == 'push' && github.event.before != '0000000000000000000000000000000000000000' && github.event.before ||
            'HEAD~1'
          }}
          fail-on-error: 'false'
```

> 📖 **Detailed Configuration Guide**: See [CROSS_REPO_PUSH.md](CROSS_REPO_PUSH.md) for a complete cross-repository push
  scenario solution.

### 2. Comprehensive Workflow

```yaml
name: Terraform Quality Gate
on:
  pull_request:
    paths: ['terraform/**']

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Terraform Lint - Full Analysis
        id: lint
        uses: Lance52259/hcbp-scripts-lint@v2.0.0
        with:
          directory: './terraform'
          rule-categories: 'ST,IO,DC,SC'
          changed-files-only: 'true'
          base-ref: 'origin/main'
          performance-monitoring: 'true'
          fail-on-error: 'false'
      
      - name: Process Results
        run: |
          echo "Files processed: ${{ steps.lint.outputs.files-processed }}"
          echo "Execution time: ${{ steps.lint.outputs.execution-time }}s"
          echo "Performance: ${{ steps.lint.outputs.performance-metrics }}"
```

### 3. Multi-Environment Validation

```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]
    
steps:
  - name: Lint ${{ matrix.environment }}
    uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
      directory: './terraform/environments/${{ matrix.environment }}'
      rule-categories: 'ST,IO'
      exclude-paths: '*.backup,test/*'
```

### 4. Selective Rule Execution

```yaml
- name: Style Check Only
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    rule-categories: 'ST'
    ignore-rules: 'ST.001,ST.003'

- name: Documentation Check
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    rule-categories: 'DC'
    include-paths: 'modules/*'
```

## 🏗️ Architecture Overview

### Unified Rules Management System

```
 ┌────────────────────────────────────────────────────┐
 │                  RulesManager                      │
 │           (Central Unified Coordinator)            │
 ├────────────────────────────────────────────────────┤
 │ • Rule Discovery & Registration                    │
 │ • Cross-System Execution                           │
 │ • Performance Monitoring                           │
 │ • Unified Reporting & Analytics                    │
 │ • Configuration Management                         │
 └────────────────────────────────────────────────────┘
                           │
     ┌──────────────┬──────┴───────┬──────────────┐
     │              │              │              │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│ST Rules │    │IO Rules │    │DC Rules │    │SC Rules │
│Package  │    │Package  │    │Package  │    │Package  │
├─────────┤    ├─────────┤    ├─────────┤    ├─────────┤
│reference│    │reference│    │reference│    │reference│
│.py      │    │.py      │    │.py      │    │.py      │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### Key Components

1. **RulesManager**: Central coordinator for all rule systems with unified API
2. **Rule Packages**: Independent packages (st_rules/, io_rules/, dc_rules/, sc_rules/) with their own coordinators
3. **Direct Integration**: No intermediate compatibility layers - direct package imports
4. **Execution Engine**: Optimized rule execution with performance monitoring
5. **Reporting System**: Comprehensive analytics and detailed reporting
6. **Configuration Manager**: Flexible rule and path filtering

## 🔍 Detailed Reports

### Artifact Management

The enhanced system includes robust artifact management to prevent naming conflicts:

- **Unique Naming**: Artifacts are named with timestamp, run ID, job ID, and matrix keys
- **Conflict Resolution**: Automatic fallback naming if primary upload fails
- **Multiple Formats**: Supports both text and JSON report formats
- **Retention**: 30-day artifact retention for historical analysis

### Artifact Naming Convention

```
terraform-lint-report-unified-{run_id}-{run_attempt}-{job_id}-{timestamp}
```

For matrix jobs:
```
terraform-lint-report-unified-{run_id}-{run_attempt}-{job_id}-matrix-{matrix_index}-{timestamp}
```

### Sample Report Output

```
============================================================
TERRAFORM SCRIPTS LINT REPORT (UNIFIED SYSTEM)
============================================================
Generated: 2024-01-15 10:30:45

=== SUMMARY ===
Total Errors: 3
Total Warnings: 7
Total Violations: 10
Files Processed: 25
Total Lines Processed: 1,250
Execution Time: 2.34 seconds

=== RULE EXECUTION STATISTICS ===
Total Rules Executed: 75
Successful Rule Executions: 72
Failed Rule Executions: 3
Success Rate: 96.0%

=== VIOLATIONS BY CATEGORY ===
ST (Style/Format): 4 violations, 2 errors, 2 warnings
IO (Input/Output): 3 violations, 1 errors, 2 warnings
DC (Documentation): 3 violations, 0 errors, 3 warnings
SC (Security Code): 0 violations, 0 errors, 0 warnings

=== PERFORMANCE METRICS ===
Average Lines per File: 50
Files per Second: 10.7
Lines per Second: 534
Rules per Second: 32.1
```

## 🛠️ Development & Contribution

### Project Structure

```
hcbp-scripts-lint/
├── rules/                          # Unified Rules Management System
│   ├── __init__.py                 # Package initialization and API exports
│   ├── rules_manager.py            # Central unified coordinator
│   ├── st_rules/                   # Style/Format rules package
│   ├── io_rules/                   # Input/Output rules package
│   ├── dc_rules/                   # Documentation rules package
│   └── sc_rules/                   # Security Code rules package
├── .github/
│   └── scripts/
│       └── terraform_lint.py       # Enhanced linting script
├── action.yml                      # GitHub Action definition
├── README.md                       # This file
└── QUICKSTART.md                   # Quick start guide
```

### Adding New Rules

1. **Create Rule Module**: Add your rule in the appropriate category directory
2. **Register Rule**: Update the category's reference.py file
3. **Add Tests**: Include comprehensive test cases
4. **Update Documentation**: Add rule description and examples

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run specific category tests
python3 -m pytest tests/test_st_rules.py
python3 -m pytest tests/test_sc_rules.py

# Run with coverage
python3 -m pytest --cov=rules tests/
```

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🏷️ Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions available, see the
[tags on this repository](https://github.com/Lance52259/hcbp-scripts-lint/tags).

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)
- **Documentation**: [Wiki](https://github.com/Lance52259/hcbp-scripts-lint/wiki)

---

**Enhanced by the Unified Rules Management System** - Providing consistent, efficient, and extensible Terraform linting
for teams worldwide.
