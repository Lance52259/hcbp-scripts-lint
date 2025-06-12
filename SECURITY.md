# Security Policy

## Overview

The Terraform Scripts Lint Tool is designed with security as a fundamental principle. This document outlines our 
security practices, how to report security vulnerabilities, and the security features built into the tool.

## Security Features

### Data Security
- **Local Processing Only**: All linting operations are performed locally. No data is transmitted to external 
  services or servers.
- **Read-Only Operations**: The tool only reads files and never modifies, creates, or deletes any files in your 
  repository.
- **No Network Dependencies**: The tool operates entirely offline and makes no network requests during execution.
- **No Data Collection**: We do not collect, store, or transmit any user data, code, or analytics.

### Permission Requirements
- **Minimal File System Access**: Only requires read access to Terraform files in the specified directory
- **Report Generation**: Write access only for creating lint report files in the working directory
- **No Elevated Privileges**: Does not require administrator or root privileges
- **No System Modifications**: Does not modify system settings, environment variables, or installed software

### GitHub Actions Security
- **Sandbox Execution**: Runs in GitHub's secure, isolated runner environment
- **No Secrets Access**: Does not require or access repository secrets or environment variables
- **Isolated Processing**: Each workflow run is completely isolated from other runs
- **Minimal Permissions**: Only requires `contents: read` permission for repository access

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it responsibly:

### Private Reporting
1. **Email**: Send details to [security@example.com] (replace with actual email)
2. **GitHub Security**: Use GitHub's private vulnerability reporting feature
3. **Include**: Detailed description, steps to reproduce, and potential impact

Please **do not** create public GitHub issues for security vulnerabilities. This helps protect users who may be 
affected.

### What to Include
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact and severity assessment
- Any suggested fixes or mitigations
- Your contact information for follow-up

### Response Timeline
- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix Development**: Within 2 weeks for critical issues
- **Public Disclosure**: After fix is released and users have time to update

## Security Best Practices

### For Users
- **Use Official Releases**: Always use official releases from the GitHub repository
- **Verify Checksums**: Verify file integrity when downloading releases
- **Regular Updates**: Keep the tool updated to the latest version
- **Review Changes**: Review configuration changes through pull requests
- **Principle of Least Privilege**: Run with minimal required permissions

### For Contributors
- **Code Review**: All code changes require review before merging
- **Security Testing**: Test for potential security issues before submitting
- **Dependency Management**: Keep dependencies updated and secure
- **Input Validation**: Validate all user inputs and file contents
- **Error Handling**: Implement proper error handling to prevent information disclosure

## Security Configuration Examples

### Minimal GitHub Actions Setup

```yaml
name: Terraform Lint
on: [push, pull_request]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    permissions:
      contents: read  # Minimal required permission
    steps:
      - uses: actions/checkout@v3
      - name: Terraform Scripts Lint
        uses: Lance52259/hcbp-scripts-lint@v1.1.0  # Use specific version
        with:
          directory: './terraform'
```

### Secure Local Usage

```bash
# Run with restricted permissions (Unix/Linux)
chmod 755 .github/scripts/terraform_lint.py
python3 .github/scripts/terraform_lint.py --directory ./terraform

# Verify no network connections are made
strace -e trace=network python3 .github/scripts/terraform_lint.py 2>&1 | grep -E "(connect|socket)"
```

## Threat Model

### In Scope
- **Code Injection**: Malicious code execution through crafted Terraform files
- **Path Traversal**: Unauthorized file access outside specified directories
- **Information Disclosure**: Leaking sensitive information through error messages or logs
- **Denial of Service**: Resource exhaustion through malicious input files

### Out of Scope
- **Physical Security**: Physical access to systems running the tool
- **Social Engineering**: Attacks targeting users rather than the tool itself
- **Network Security**: Network-level attacks (tool operates offline)
- **Operating System**: Vulnerabilities in the underlying OS or runtime

## Security Testing

### Automated Security Checks
- **Static Analysis**: Code is analyzed for security vulnerabilities
- **Dependency Scanning**: Dependencies are scanned for known vulnerabilities
- **Input Validation Testing**: Malformed inputs are tested for proper handling
- **Permission Testing**: Verification that minimal permissions are sufficient

### Manual Security Review
- **Code Review**: All changes undergo security-focused code review
- **Threat Modeling**: Regular assessment of potential attack vectors
- **Penetration Testing**: Periodic testing by security professionals

## Compliance and Standards

### Security Standards
- **OWASP Top 10**: Adherence to OWASP security guidelines
- **CWE/SANS Top 25**: Protection against common software weaknesses
- **NIST Cybersecurity Framework**: Alignment with cybersecurity best practices

### Privacy Compliance
- **No Personal Data**: Tool does not process personal or sensitive data
- **GDPR Compliant**: No data collection means automatic GDPR compliance
- **SOC 2 Ready**: Security controls suitable for SOC 2 environments

## Security Changelog

### Version 1.1.0
- Enhanced input validation for path parameters
- Improved error handling to prevent information disclosure
- Added security-focused unit tests

### Version 1.0.0
- Initial security implementation
- Basic input validation and sanitization
- Secure file handling practices

## Contact Information

### Security Team
- **Primary Contact**: Lance52259
- **Security Email**: [security@example.com] (replace with actual email)
- **Response Time**: `48` hours for security issues

### Reporting Channels
- **GitHub Security Advisories**: Preferred for vulnerability reports
- **Email**: For sensitive security communications
- **Issues**: For general security questions (non-sensitive)

## Acknowledgments

We thank the security community and all contributors who help make this tool more secure.  
If you've reported a security issue, we'd be happy to acknowledge your contribution (with your permission) in our
security acknowledgments.

**Note**: This security policy is regularly reviewed and updated. Please check back periodically for the latest
information.
