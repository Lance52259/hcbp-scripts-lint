# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2025-06-16

### Fixed
- **GitHub Actions Working Directory Issue**: Fixed `changed-files-only` mode execution in GitHub Actions
  - Resolved linter executing in action directory instead of user's repository directory
  - Now properly executes in `$GITHUB_WORKSPACE` while calling scripts from `$GITHUB_ACTION_PATH`
  - Added file existence verification before processing changed files
  - Improved path resolution for changed files detection
- **Enhanced Git Command Handling**: 
  - Added support for multiple base-ref formats (`origin/master`, `master`, `HEAD~1`)
  - Implemented fallback git command strategy for different PR/commit scenarios
  - Better error messages and fallback strategies for various GitHub Actions scenarios
- **Documentation Fixes**:
  - Fixed help documentation to match actual supported rules
  - Updated GitHub Actions configuration examples
  - Added comprehensive debugging information for troubleshooting

### Added
- **Comprehensive Debugging**: Environment information and file verification for easier troubleshooting
- **Path Resolution Improvements**: Better handling of file paths in GitHub Actions context
- **Error Handling Enhancements**: More informative error messages for debugging

### Changed
- **Execution Context**: Linter now properly executes in user's workspace directory
- **Git Command Strategy**: Improved fallback mechanisms for different repository states
- **File Processing**: Added validation steps before processing detected files

### Performance
- **GitHub Actions Optimization**: Restored proper functionality for `changed-files-only` mode
- **Error Recovery**: Better handling of edge cases in CI/CD environments

### Compatibility
- **Backward Compatible**: No breaking changes - all existing workflows continue to work
- **GitHub Actions**: Enhanced compatibility with different GitHub Actions scenarios
- **Multi-Environment**: Improved support for various git repository configurations

### Validation
- ✅ Basic linting functionality verified
- ✅ Path filtering (`--include-paths`, `--exclude-paths`) confirmed working
- ✅ Changed files detection now functional in GitHub Actions
- ✅ All existing workflows remain compatible

## [1.1.1] - 2025-06-16

### Fixed
- **Critical Bug Fix**: Fixed `changed-files-only` functionality not working correctly
  - Resolved incorrect Git command execution order in `get_changed_files` method
  - Completely rewrote Git command logic with proper error handling
  - Improved command ordering and fallback mechanisms for better reliability
- **Enhanced Git Integration**: 
  - Better error handling for Git operations
  - Improved fallback mechanisms when Git commands fail
  - Added detailed logging to help troubleshoot Git-related issues
- **CI/CD Reliability**: Fixed issues affecting Pull Request workflows in large repositories

### Performance
- **Large Repository Support**: Restored proper functionality for checking only changed files
- **CI/CD Optimization**: Fixed performance regression affecting Pull Request workflows

### Technical Details
- **Root Cause**: Incorrect Git command execution order preventing proper file detection
- **Solution**: Complete rewrite of Git command logic with comprehensive error handling
- **Testing**: Verified across multiple Git scenarios and repository configurations
- **Compatibility**: Maintains full backward compatibility with existing configurations

### Upgrade Recommendation
**Strongly recommended** for all users who:
- Use `changed-files-only: true` in their workflows
- Experience performance issues with large repositories  
- Want reliable CI/CD integration with Pull Request workflows
- Encountered issues with v1.1.0's changed-files-only feature

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
  - **DC (Documentation/Comments) Rules**:
    - DC.001: Comment formatting standards
  - **IO (Input/Output) Rules**:
    - IO.001: Variable definition file organization
    - IO.002: Output definition file organization
    - IO.003: Required variable declaration in tfvars
    - IO.004: Variable naming conventions
    - IO.005: Output naming conventions

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

### v1.1.2 Highlights
This **critical fix release** resolves GitHub Actions working directory issues that prevented `changed-files-only` mode from functioning correctly. The linter now properly executes in the user's repository directory while maintaining access to action scripts.

**Key Fix**: Resolved execution context issues in GitHub Actions environments, ensuring `changed-files-only` mode works reliably across different repository configurations.

**Recommended for**: All users experiencing issues with `changed-files-only` mode in GitHub Actions, especially those with complex repository structures.

### v1.1.1 Highlights
This **critical bug fix release** addresses a major issue with the `changed-files-only` functionality introduced in v1.1.0. The feature now works correctly and reliably detects changed Terraform files in CI/CD workflows.

**Critical Fix**: Resolved Git command execution issues that prevented proper file detection in Pull Request workflows.

**Recommended for**: All users using `changed-files-only` mode, especially those experiencing issues with v1.1.0.

### v1.1.0 Highlights
This release focuses on **performance optimization** for large repositories and **enhanced CI/CD integration**. The new `changed-files-only` mode can reduce linting time from minutes to seconds in large codebases by checking only modified files.

**Recommended for**: Large Terraform projects, frequent Pull Request workflows, and performance-sensitive CI/CD pipelines.

### v1.0.0 Highlights
The initial release provides a **complete Terraform linting solution** with comprehensive rule coverage, flexible configuration options, and seamless GitHub Actions integration.

**Key Features**: Multi-category rule system, advanced filtering, detailed reporting, and production-ready GitHub Action.

---

## Migration Guide

### Upgrading from v1.1.1 to v1.1.2

**Critical Update**: This patch fixes GitHub Actions working directory issues. No configuration changes required.

**Simple Update**:
```yaml
# Update version in your workflow
- name: Terraform Scripts Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.2  # Changed from v1.1.1
  with:
    changed-files-only: 'true'  # Now works correctly in all GitHub Actions scenarios
    base-ref: 'origin/main'     # Supports multiple base-ref formats
    # ... existing parameters remain the same
```

### Upgrading from v1.1.0 to v1.1.2

**Critical Updates**: This version includes fixes for both Git command execution and GitHub Actions working directory issues.

**Recommended Update**:
```yaml
# Update version in your workflow
- name: Terraform Scripts Lint
  uses: Lance52259/hcbp-scripts-lint@v1.1.2  # Skip v1.1.1, go directly to v1.1.2
  with:
    changed-files-only: 'true'  # Now fully functional
    base-ref: 'origin/main'     # Enhanced base-ref support
    # ... existing parameters remain the same
```

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