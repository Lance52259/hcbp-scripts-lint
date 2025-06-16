# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-6-13

### Added
- **Changed Files Only Mode**: New `changed-files-only` parameter to check only files modified in current commit/PR
  - Significantly improves performance for large repositories
  - Supports multiple Git comparison modes (PR, staged, unstaged changes)
  - Configurable base reference with `base-ref` parameter (default: `origin/main`)
- **Enhanced GitHub Actions Integration**:
  - New input parameters: `changed-files-only` and `base-ref`
  - Optimized for Pull Request workflows with `fetch-depth: 0` requirement
  - Improved command building logic in action execution
- **Performance Optimizations**:
  - Smart file detection using Git diff commands
  - Fallback mechanism when Git operations fail
  - Python 3.6+ compatibility improvements

### Changed
- **Action Configuration**: Updated `action.yml` with new input parameters
- **Documentation Updates**:
  - Enhanced README.md with Pull Request workflow examples
  - Updated QUICKSTART.md with changed-files-only usage examples
  - Added large repository configuration templates
  - Improved parameter descriptions and examples
- **Code Quality**: Fixed subprocess compatibility issues for older Python versions

### Fixed
- **Python 3.6 Compatibility**: Replaced `capture_output` and `text` parameters with compatible alternatives
- **Error Handling**: Improved Git command error handling with graceful fallbacks
- **Documentation Formatting**: Removed trailing spaces and ensured consistent line endings

### Performance
- **Large Repository Support**: Checking only changed files can reduce execution time from minutes to seconds
- **CI/CD Optimization**: Particularly beneficial for Pull Request workflows in large codebases

## [1.0.0] - 2025-6-13

### Added
- **Core Linting Engine**: Comprehensive Terraform scripts linting tool
  - Multi-category rule system (Style/Format, Documentation/Comments, Input/Output)
  - Modular architecture supporting rule extension and maintenance
  - Performance optimized for large codebases

- **Rule Categories**:
  - **ST (Style/Format) Rules**:
    - ST.001: Resource and data source naming convention validation
    - ST.002: Variable default value requirement
    - ST.003: Parameter alignment formatting
    - ST.004: Indentation character validation (spaces only)
    - ST.005: Indentation level consistency (2 spaces per level)
    - ST.006: Resource and data source block spacing (exactly 1 empty line)
    - ST.007: Same parameter block spacing (≤1 empty line)
    - ST.008: Different parameter block spacing (exactly 1 empty line)
  - **DC (Documentation/Comments) Rules**:
    - DC.001: Comment formatting standards
  - **IO (Input/Output) Rules**:
    - IO.001: Variable definition file organization
    - IO.002: Output definition file organization
    - IO.003: Required variable declaration in tfvars
    - IO.004: Variable naming conventions
    - IO.005: Output naming conventions
    - IO.006: Variable description validation (non-empty descriptions required)
    - IO.007: Output description validation (non-empty descriptions required)
    - IO.008: Variable type validation (type field required)

- **GitHub Actions Integration**:
  - Complete GitHub Action with composite run steps
  - Configurable input parameters for flexible usage
  - Automated report generation and artifact upload
  - Support for failing workflows on errors

- **Advanced Filtering System**:
  - Rule ignoring with `ignore-rules` parameter
  - Path inclusion with `include-paths` parameter
  - Path exclusion with `exclude-paths` parameter
  - Glob pattern support for flexible path matching

- **Comprehensive Reporting**:
  - Detailed error and warning reporting with line numbers
  - Performance metrics tracking
  - Text-based report generation
  - GitHub Actions artifact integration

- **Command Line Interface**:
  - Full-featured CLI with argparse integration
  - Backward compatibility with deprecated positional arguments
  - Comprehensive help documentation with examples
  - Multiple output formats and configuration options

### Security
- **Local Processing Only**: No network requests or data transmission
- **Read-Only Operations**: No file modifications, only analysis
- **Minimal Permissions**: Requires only read access to target files
- **No Data Collection**: Complete privacy with local-only processing

### Performance
- **Intelligent File Discovery**: Optimized directory traversal with hidden directory skipping
- **Memory Optimization**: File-by-file processing to avoid high memory usage
- **Encoding Handling**: Multiple encoding support with fallback mechanisms
- **Efficient Parsing**: Incremental content parsing for better performance

### Documentation
- **Comprehensive Guides**:
  - README.md with detailed usage instructions and examples
  - QUICKSTART.md for rapid setup and common configurations
  - CONTRIBUTING.md with development guidelines
  - SECURITY.md with security policies and best practices
- **Rule Documentation**:
  - Detailed rule descriptions in rules/introduction.md
  - Technical implementation guide in rules/README.md
  - Complete rule catalog with examples and fixes

### Examples and Testing
- **Real-World Examples**: Comprehensive test cases in examples directory
- **Validation Scripts**: Tools for testing linter functionality
- **CI/CD Templates**: Ready-to-use GitHub Actions workflow examples

### Architecture
- **Modular Design**: Separate rule modules for easy extension
- **Error Handling**: Robust error handling with detailed logging
- **Cross-Platform**: Compatible with Windows, macOS, and Linux
- **Python 3.6+ Support**: Wide compatibility across Python versions

---

## Release Notes

### v1.1.0 Highlights
This release focuses on **performance optimization** for large repositories and **enhanced CI/CD integration**. The new `changed-files-only` mode can reduce linting time from minutes to seconds in large codebases by checking only modified files.

**Recommended for**: Large Terraform projects, frequent Pull Request workflows, and performance-sensitive CI/CD pipelines.

### v1.0.0 Highlights
The initial release provides a **complete Terraform linting solution** with comprehensive rule coverage, flexible configuration options, and seamless GitHub Actions integration.

**Key Features**: Multi-category rule system, advanced filtering, detailed reporting, and production-ready GitHub Action.

---

## Migration Guide

### Upgrading from v1.0.0 to v1.1.0

No breaking changes. All existing configurations remain compatible.

**Optional Enhancements**:
```yaml
# Add to existing workflows for better performance
- name: Terraform Scripts Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.0
  with:
    changed-files-only: 'true'  # New feature
    base-ref: 'origin/main'     # New feature
    # ... existing parameters remain the same
```

**For Pull Request workflows**, add `fetch-depth: 0` to checkout step:
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Required for changed-files-only mode
```

---

## Support and Feedback

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)
- 📖 **Documentation**: [Project README](README.md)
- 🚀 **Quick Start**: [QUICKSTART.md](QUICKSTART.md)