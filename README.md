# Terraform Scripts Lint

A comprehensive linting tool for Terraform scripts with advanced rule management and comment-based control.

## Features

- **Multi-Category Rules**: 22 rules across ST (Style/Format), IO (Input/Output), DC (Documentation/Comments), and SC (Security Code) categories
- **Comment Control**: Enable/disable specific rules using inline comments
- **Flexible Configuration**: Path filtering, rule exclusion, and performance monitoring
- **GitHub Actions Integration**: Seamless CI/CD integration with artifact support
- **Changed Files Mode**: Optimized for large repositories with selective file checking
- **Comprehensive Reporting**: Detailed error reporting with line numbers and suggestions

## Comment Control

You can control rule execution using inline comments in your Terraform files:

```hcl
# ST.001 Disable
resource "huaweicloud_vpc_route" "vpc_route" {
  vpc_id      = huaweicloud_vpc.vpcA.id
  destination = "192.168.0.0/16"
  type        = "peering"
  nexthop     = huaweicloud_vpc_peering_connection.peering.id
}
# ST.001 Enable
```

### Supported Comment Formats

- `# ST.001 Disable` - Disables ST.001 rule from this line onwards in the current file
- `# ST.001 Enable` - Re-enables ST.001 rule from this line onwards in the current file

### Features

- **File-scoped control**: Comments only affect the current file
- **Line-based control**: Rules are disabled/enabled from the comment line onwards
- **Support for all rule categories**: ST, IO, DC, SC
- **Multiple rule control**: You can disable/enable multiple rules with separate comments

### Example Usage

```hcl
# Disable naming convention check for this section
# ST.001 Disable
resource "huaweicloud_vpc_route" "custom_name" {
  vpc_id      = huaweicloud_vpc.vpcA.id
  destination = "192.168.0.0/16"
  type        = "peering"
  nexthop     = huaweicloud_vpc_peering_connection.peering.id
}
# ST.001 Enable

# Disable parameter alignment check for this section
# ST.003 Disable
resource "huaweicloud_compute_instance" "test" {
  name = "test-instance"
  flavor_id = "c6.large.2"
  image_id = "test-image"
  system_disk_size = 40
}
# ST.003 Enable
```

## Quick Start

### Local Usage

```bash
# Basic usage
python3 .github/scripts/terraform_lint.py /path/to/terraform/files

# With specific rules excluded
python3 .github/scripts/terraform_lint.py /path/to/terraform/files --ignore-rules ST.001,ST.002

# Check only changed files
python3 .github/scripts/terraform_lint.py /path/to/terraform/files --changed-files-only
```

### GitHub Actions

```yaml
name: Terraform Lint

on:
  pull_request:
    paths:
      - '**.tf'
      - '**.tfvars'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for changed-files-only mode
      
      - name: Terraform Scripts Lint
        uses: Lance52259/hcbp-scripts-lint@v2.3.3
        with:
          directory: '.'
          changed-files-only: 'true'
          fail-on-error: 'true'
```

## Rule Categories

### ST (Style/Format) Rules - 11 Rules
- **ST.001**: Resource and data source naming convention check
- **ST.002**: Variable default value requirement for data sources
- **ST.003**: Parameter alignment with equals signs
- **ST.004**: Indentation character validation (spaces only)
- **ST.005**: Indentation level validation (2 spaces per level)
- **ST.006**: Resource and data source spacing check
- **ST.007**: Same parameter block spacing validation
- **ST.008**: Different parameter block spacing validation
- **ST.009**: Variable definition order validation
- **ST.010**: Quote usage consistency check
- **ST.011**: Trailing whitespace detection

### IO (Input/Output) Rules - 9 Rules
- **IO.001**: Variable definition file organization
- **IO.002**: Output definition file organization
- **IO.003**: Required variable declaration in tfvars
- **IO.004**: Variable naming convention check
- **IO.005**: Output naming convention check
- **IO.006**: Variable description requirement
- **IO.007**: Output description requirement
- **IO.008**: Variable type definition requirement
- **IO.009**: Variable validation block check

### DC (Documentation/Comments) Rules - 1 Rule
- **DC.001**: Comment formatting standards

### SC (Security Code) Rules - 1 Rule
- **SC.001**: Unsafe array index access detection

## Configuration Options

### Command Line Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--directory` | Directory to lint | Current directory |
| `--ignore-rules` | Comma-separated list of rules to ignore | None |
| `--include-paths` | Comma-separated list of paths to include | All .tf files |
| `--exclude-paths` | Comma-separated list of paths to exclude | None |
| `--changed-files-only` | Check only changed files | false |
| `--base-ref` | Base reference for changed files | origin/main |
| `--rule-categories` | Comma-separated list of rule categories | ST,IO,DC,SC |
| `--report-format` | Output format (text, json, or both) | text |
| `--performance-monitoring` | Enable performance monitoring | true |
| `--fail-on-error` | Exit with error code on violations | true |

### GitHub Actions Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `directory` | Directory to lint | . |
| `ignore-rules` | Comma-separated list of rules to ignore | None |
| `include-paths` | Comma-separated list of paths to include | All .tf files |
| `exclude-paths` | Comma-separated list of paths to exclude | None |
| `changed-files-only` | Check only changed files | false |
| `base-ref` | Base reference for changed files | origin/main |
| `rule-categories` | Comma-separated list of rule categories | ST,IO,DC,SC |
| `report-format` | Output format (text, json, or both) | text |
| `performance-monitoring` | Enable performance monitoring | true |
| `fail-on-error` | Exit with error code on violations | true |

## Examples

### Basic Usage

```bash
# Lint current directory
python3 .github/scripts/terraform_lint.py .

# Lint specific directory
python3 .github/scripts/terraform_lint.py /path/to/terraform

# Exclude specific rules
python3 .github/scripts/terraform_lint.py . --ignore-rules ST.001,ST.002

# Check only changed files
python3 .github/scripts/terraform_lint.py . --changed-files-only
```

### Advanced Configuration

```bash
# Include only specific paths
python3 .github/scripts/terraform_lint.py . --include-paths "modules/**,examples/**"

# Exclude specific paths
python3 .github/scripts/terraform_lint.py . --exclude-paths "**/test/**"

# Use specific rule categories
python3 .github/scripts/terraform_lint.py . --rule-categories ST,IO

# Generate JSON report
python3 .github/scripts/terraform_lint.py . --report-format json
```

### GitHub Actions Examples

```yaml
# Basic workflow
- name: Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v2.3.3
  with:
    directory: '.'
    fail-on-error: 'true'

# Advanced workflow with filtering
- name: Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v2.3.3
  with:
    directory: '.'
    changed-files-only: 'true'
    ignore-rules: 'ST.001,ST.002'
    include-paths: 'modules/**,examples/**'
    exclude-paths: '**/test/**'
    rule-categories: 'ST,IO'
    report-format: 'both'
    performance-monitoring: 'true'
```

## Performance

- **Large Repository Support**: Optimized for repositories with 500+ Terraform files
- **Changed Files Mode**: Reduces execution time from minutes to seconds in large codebases
- **Parallel Processing**: Efficient rule execution with intelligent scheduling
- **Memory Optimization**: Stream-based processing maintains low memory usage

## Security

- **Local Processing Only**: No network requests or data transmission
- **Read-Only Operations**: No file modifications, only analysis
- **Minimal Permissions**: Requires only read access to target files
- **No Data Collection**: Complete privacy with local-only processing

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and contribution instructions.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)
- 📖 **Documentation**: [Project README](README.md)
- 🚀 **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
