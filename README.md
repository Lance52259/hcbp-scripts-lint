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
- **Three Rule Categories**: ST (Style/Format), IO (Input/Output), DC (Documentation/Comments)
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

Through the **unified rules management system**, all rules are organized into three main categories, each managed by a
dedicated coordinator:

### ST (Style/Format) Rules
Code formatting and style consistency rules, managed by the `STRules` coordinator:
- **ST.001**: Resource and data source naming conventions
- **ST.002**: Default value checking convention
- **ST.003**: Parameter alignment and formatting
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

### DC (Documentation/Comments) Rules
Documentation and comment standard rules, managed by the `DCRules` coordinator:
- **DC.001**: Comment formatting and style standards

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
    rule-categories: 'ST,IO,DC'
    ignore-rules: 'ST.001,ST.003'
    fail-on-error: 'true'
    performance-monitoring: 'true'
```

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
| `rule-categories` | Rule categories to execute (ST,IO,DC) | `ST,IO,DC` | No |
| `ignore-rules` | Comma-separated list of rules to ignore | `` | No |
| `include-paths` | Path patterns to include | `` | No |
| `exclude-paths` | Path patterns to exclude | `` | No |
| `changed-files-only` | Check only changed files | `false` | No |
| `base-ref` | Base reference for git diff | `origin/main` | No |
| `performance-monitoring` | Enable performance analytics | `true` | No |
| `report-format` | Output format (text/json) | `text` | No |
| `fail-on-error` | Fail workflow on errors | `true` | No |

### Command Line Options

```bash
python3 .github/scripts/terraform_lint.py [OPTIONS]

Options:
  -d, --directory TEXT          Target directory to check
  --categories TEXT             Rule categories (ST,IO,DC)
  --ignore-rules TEXT           Rules to ignore (comma-separated)
  --include-paths TEXT          Paths to include (comma-separated)
  --exclude-paths TEXT          Paths to exclude (comma-separated)
  --changed-files-only          Check only changed files
  --base-ref TEXT               Base reference for git diff
  --performance-monitoring      Enable performance monitoring
  --report-format [text|json]   Output report format
  --help                        Show help message
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

### 1. Comprehensive Workflow

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
          rule-categories: 'ST,IO,DC'
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

### 2. Multi-Environment Validation

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

### 3. Selective Rule Execution

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
 ┌─────────────────────────────────────┐
 │         RulesManager                │
 │  (Central Unified Coordinator)      │
 ├─────────────────────────────────────┤
 │ • Rule Discovery & Registration     │
 │ • Cross-System Execution            │
 │ • Performance Monitoring            │
 │ • Unified Reporting & Analytics     │
 │ • Configuration Management          │
 └─────────────────────────────────────┘
                    │
     ┌──────────────┼──────────────┐
     │              │              │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│ST Rules │    │IO Rules │    │DC Rules │
│Package  │    │Package  │    │Package  │
├─────────┤    ├─────────┤    ├─────────┤
│reference│    │reference│    │reference│
│.py      │    │.py      │    │.py      │
└─────────┘    └─────────┘    └─────────┘
```

### Key Components

1. **RulesManager**: Central coordinator for all rule systems with unified API
2. **Rule Packages**: Independent packages (st_rules/, io_rules/, dc_rules/) with their own coordinators
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
│   └── dc_rules/                   # Documentation rules package
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
