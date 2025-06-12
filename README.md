# Terraform Scripts Lint Tool

A comprehensive linting tool for Terraform scripts with flexible rule control and path filtering capabilities.

## Features

- **Comprehensive Rule Coverage**: Supports multiple rule categories including Style/Format (ST), 
  Documentation/Comments (DC), and Input/Output (IO)
- **Flexible Rule Control**: Use `ignore-rules` parameter to ignore specific rule IDs
- **Precise Path Control**: Use `include-paths` and `exclude-paths` to specify which paths to check or exclude
- **GitHub Actions Integration**: Easy integration with CI/CD pipelines
- **Detailed Reporting**: Generate comprehensive lint reports with error details and suggestions
- **Performance Optimized**: Efficient processing for large codebases with intelligent path filtering

## Quick Start

### Local Usage

```bash
# Check current directory
python3 .github/scripts/terraform_lint.py

# Check specific directory
python3 .github/scripts/terraform_lint.py --directory ./terraform

# Ignore specific rules
python3 .github/scripts/terraform_lint.py --ignore-rules "ST.001,DC.001"

# Include only specific paths
python3 .github/scripts/terraform_lint.py --include-paths "src/,modules/"

# Exclude specific paths
python3 .github/scripts/terraform_lint.py --exclude-paths "examples/,test/"
```

### GitHub Actions Usage

```yaml
name: Terraform Lint
on: [push, pull_request]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Terraform Scripts Lint
        uses: Lance52259/hcbp-scripts-lint@v1.1.0
        with:
          directory: './terraform'
          ignore-rules: 'ST.001,DC.001'
          include-paths: 'src/,modules/'
          exclude-paths: 'examples/,test/'
```

## Rule Categories

### Style/Format Rules (ST)
- **ST.001**: Resource and data source instance name specification
- **ST.002**: Variable default value specification  
- **ST.003**: Parameter alignment format specification

### Documentation/Comments Rules (DC)
- **DC.001**: Comment format specification

### Input/Output Rules (IO)
- **IO.001**: Variable definition file specification
- **IO.002**: Output definition file specification
- **IO.003**: Required variable value declaration specification

## Documentation

📖 **Detailed Rule Descriptions**: See [rules/rule_details.md](rules/rule_details.md) for detailed descriptions, 
examples, and implementation principles of each rule.

🔧 **Rule Implementation**: See [rules/README.md](rules/README.md) for technical implementation and extension 
methods of rules.

## Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `directory` | Target directory to check | Current directory | `./terraform` |
| `ignore-rules` | Comma-separated rule IDs to ignore | None | `ST.001,DC.001` |
| `include-paths` | Comma-separated paths to include | None | `src/,modules/` |
| `exclude-paths` | Comma-separated path patterns to exclude | None | `examples/,test/` |

## Advanced Usage

### Rule Management

```bash
# Ignore multiple rules
python3 .github/scripts/terraform_lint.py --ignore-rules "ST.001,ST.002,DC.001"

# Check only specific paths
python3 .github/scripts/terraform_lint.py --include-paths "production/,staging/"

# Exclude test and example directories
python3 .github/scripts/terraform_lint.py --exclude-paths "test/,examples/,docs/"
```

### CI/CD Integration

#### Basic Integration

```yaml
- name: Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    directory: './infrastructure'
```

#### Advanced Integration with Custom Rules

```yaml
- name: Terraform Lint with Custom Rules
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    directory: './terraform'
    ignore-rules: 'ST.001'  # Ignore resource naming rules for legacy code
    include-paths: 'modules/,environments/'
    exclude-paths: 'examples/,deprecated/'
```

#### Integration with Artifact Upload

```yaml
- name: Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    directory: './terraform'
  continue-on-error: true

- name: Upload Lint Report
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: terraform-lint-report
    path: terraform-lint-report.txt
```

If errors are found during checking, the GitHub Actions workflow will fail and upload the check report as a 
build artifact.

## Performance Considerations

### Optimization Features
- **Intelligent Path Filtering**: Only processes relevant Terraform files (*.tf, *.tfvars)
- **Incremental Parsing**: Optimized parsing for large files with streaming processing
- **Memory Optimization**: Efficient memory usage through lazy loading and garbage collection
- **Concurrency-Friendly**: Designed to work well in parallel CI/CD environments

### Performance Metrics
- **Small Projects** (< 50 files): ~2-5 seconds
- **Medium Projects** (50-200 files): ~5-15 seconds  
- **Large Projects** (200+ files): ~15-30 seconds

### Performance Tips
- Use `exclude-paths` to skip unnecessary directories (examples, tests, documentation)
- Use `include-paths` for targeted checking of specific modules
- Consider ignoring non-critical rules in large legacy codebases during initial adoption

## Security

### Data Security
- **Local Processing**: All linting operations are performed locally. No data is transmitted to external services
- **Read-Only Operations**: The tool only reads files and never modifies, creates, or deletes files
- **No Network Dependencies**: No external API calls or network requests during operation
- **No Data Collection**: No telemetry, analytics, or user data collection

### Permission Requirements
- **File System Access**: Read access to Terraform files in the specified directory
- **Report Generation**: Write access to create lint report files
- **Minimal Permissions**: No elevated privileges or system-level access required

### GitHub Actions Security
- **Sandbox Execution**: Runs in GitHub's secure runner environment
- **No Secrets Required**: Does not require access to secrets or sensitive environment variables
- **Isolated Processing**: Each run is isolated and does not persist data between runs

### Best Practices
- **Regular Updates**: Keep the action updated to the latest version for security patches
- **Version Pinning**: Use specific version tags (e.g., `@v1.1.0`) instead of `@main` for production
- **Code Review**: Review configuration changes and rule modifications through pull requests

## Testing

The tool includes comprehensive test examples in the `examples/` directory. You can validate the tool's 
correctness by running:

```bash
python3 .github/scripts/terraform_lint.py --directory examples/
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Reporting Issues
- Use GitHub Issues to report bugs or request features
- Provide detailed information including error messages and example code
- Include your environment details (OS, Python version, etc.)

### Contributing Code
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Ensure all tests pass and code follows style guidelines
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Adding New Rules
1. Define the rule in the appropriate category file (`st_rules.py`, `dc_rules.py`, or `io_rules.py`)
2. Add comprehensive tests for the new rule
3. Update documentation in `rules/rule_details.md`
4. Add examples demonstrating correct and incorrect usage

### Coding Standards
- Follow PEP 8 style guidelines for Python code
- Include comprehensive docstrings for all functions and classes
- Add type hints where appropriate
- Ensure all code is well-tested with appropriate test coverage

## Publishing to GitHub Marketplace

If you want to publish your own version to GitHub Marketplace, please refer to the 
[RELEASE.md](RELEASE.md) documentation.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Support

- **Maintainer**: Lance52259
- **Issues**: [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version updates and new features.
