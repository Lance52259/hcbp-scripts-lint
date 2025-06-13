# Terraform Scripts Lint

A comprehensive linting tool for Terraform configuration files, designed to enforce best practices and maintain code quality.

- **Comprehensive Rule Coverage**: Supports multiple rule categories including Style/Format (ST),
  Documentation/Comments (DC), and Input/Output (IO) rules
- **GitHub Actions Integration**: Seamlessly integrates with CI/CD pipelines
- **Detailed Reporting**: Provides clear, actionable feedback with line-by-line error reporting
- **Extensible Architecture**: Easy to add new rules and customize existing ones

## Features

### Rule Categories

#### 🎨 Style/Format Rules (ST)
- **ST.001**: Resource and data source instance naming convention (must be "test")
- **ST.002**: Variable default value requirement (all variables must have defaults)
- **ST.003**: Parameter alignment formatting convention

#### 📝 Documentation/Comments Rules (DC)
- **DC.001**: Comment formatting standards (proper spacing after #)

#### 🔧 Input/Output Rules (IO)
- **IO.001**: Variable definition file organization (variables must be in variables.tf)
- **IO.002**: Output definition file organization (outputs must be in outputs.tf)
- **IO.003**: Required variable declaration in tfvars (all required variables must be declared)
- **IO.004**: Variable naming convention (lowercase and underscores only)
- **IO.005**: Output naming convention (lowercase and underscores only)

### Quick Links

📖 **Detailed Rule Descriptions**: See [rules/introduction.md](rules/introduction.md) for detailed descriptions,
examples, and best practices for each rule.

🔧 **Rule Implementation**: See [rules/README.md](rules/README.md) for technical implementation and extension
guidelines.

## Quick Start

### Using as GitHub Action

Add this to your `.github/workflows/terraform-lint.yml`:

```yaml
name: Terraform Lint

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Terraform Scripts Lint
        uses: Lance52259/hcbp-scripts-lint@v1.1.0
        with:
          directory: './terraform'  # Path to your Terraform files
```

### Local Usage

```bash
# Clone the repository
git clone https://github.com/Lance52259/hcbp-scripts-lint.git
cd hcbp-scripts-lint

# Run the linter
python3 .github/scripts/terraform_lint.py --directory /path/to/terraform/files

# With specific output format
python3 .github/scripts/terraform_lint.py --directory ./terraform --output-format json
```

## Configuration

### Action Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `directory` | Directory containing Terraform files to lint | No | `./` |
| `fail-on-error` | Whether to fail the action on lint errors | No | `true` |
| `ignore-rules` | Comma-separated list of rule IDs to ignore (e.g., ST.001,ST.003) | No | - |
| `include-paths` | Comma-separated list of path patterns to include (e.g., modules/*,environments/*) | No | - |
| `exclude-paths` | Comma-separated list of path patterns to exclude (e.g., examples/*,test/*) | No | - |
| `changed-files-only` | If set to true, only check files changed in current commit/PR | No | `false` |
| `base-ref` | Base reference for git diff when checking changed files (e.g., origin/main, HEAD~1) | No | `origin/main` |

### Example Configuration

#### Basic Usage

```yaml
- name: Terraform Scripts Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    directory: './infrastructure'
    fail-on-error: 'true'
```

#### Advanced Configuration with Rule Control

```yaml
- name: Terraform Scripts Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    directory: './terraform'
    ignore-rules: 'ST.001,DC.001'
    include-paths: 'modules/*,environments/prod/*'
    exclude-paths: 'examples/*,test/*'
    fail-on-error: 'true'
```

#### Check Only Changed Files (Recommended for Large Repositories)

```yaml
- name: Terraform Scripts Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    changed-files-only: 'true'
    base-ref: 'origin/main'
    fail-on-error: 'true'
```

#### Pull Request Workflow Example

```yaml
name: Terraform Lint on PR
on:
  pull_request:
    branches: [ main ]
    paths: ['**/*.tf', '**/*.tfvars']

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for changed-files-only mode

      - name: Terraform Scripts Lint
        uses: Lance52259/hcbp-scripts-lint@v1.1.0
        with:
          changed-files-only: 'true'
          base-ref: 'origin/main'
          ignore-rules: 'ST.002'  # Ignore specific rules if needed
          fail-on-error: 'true'
```

## Output

### Text Format (Default)

```
Checking file: ./terraform/main.tf
❌ ST.001: Variable name 'myVar' should use snake_case (line 1)
❌ DC.001: Variable 'environment' is missing description (line 5)
✅ ST.003: Resource naming follows convention

Summary:
- Files checked: 3
- Total errors: 2
- Rules passed: 15
- Rules failed: 2
```

### JSON Format

```json
{
  "summary": {
    "files_checked": 3,
    "total_errors": 2,
    "rules_passed": 15,
    "rules_failed": 2
  },
  "files": [
    {
      "file": "./terraform/main.tf",
      "errors": [
        {
          "rule": "ST.001",
          "message": "Variable name 'myVar' should use snake_case",
          "line": 1,
          "severity": "error"
        }
      ]
    }
  ]
}
```

### GitHub Actions Integration

If errors are found during checking, the GitHub Actions workflow will fail and upload the check report as a
workflow artifact for detailed review.

## Performance

The tool is optimized for performance and can handle large Terraform codebases efficiently:

- **Small Projects** (1-50 files): ~1-3 seconds
- **Medium Projects** (50-200 files): ~5-15 seconds
- **Large Projects** (200+ files): ~15-30 seconds

Performance may vary based on file size, complexity, and system specifications.

## Examples

The tool includes comprehensive test examples in the `examples/` directory. You can validate the tool's
functionality by running it against these examples:

```bash
# Test with valid Terraform files
python3 .github/scripts/terraform_lint.py --directory examples/valid

# Test with files containing violations
python3 .github/scripts/terraform_lint.py --directory examples/violations
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up the development environment
- Adding new rules
- Running tests
- Submitting pull requests

## Security

Security is a top priority. Please see our [Security Policy](SECURITY.md) for:

- Reporting security vulnerabilities
- Security best practices
- Supported versions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 **Documentation**: Check the [rules documentation](rules/) for detailed information
- 🐛 **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- 💬 **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)

## Publishing to GitHub Marketplace

If you want to publish your own version to GitHub Marketplace, please refer to the
[GitHub Actions documentation](https://docs.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace).
