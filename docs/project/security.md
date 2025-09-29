# Security Policy

## Security Philosophy

The Terraform Scripts Lint Tool is designed with security as a fundamental principle. This document outlines our
security practices and how to report security vulnerabilities.

## Security Features

- **Local Processing Only**: All linting operations are performed locally. No data is transmitted to external
  services or third-party APIs.
- **Read-Only Operations**: The tool only reads files and never modifies, creates, or deletes any files in your
  repository.
- **No Network Dependencies**: The tool operates entirely offline and doesn't require internet connectivity.
- **Minimal Permissions**: When used as a GitHub Action, it only requires read permissions on repository contents.

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do Not Create Public Issues**

Please **do not** create public GitHub issues for security vulnerabilities. This helps protect users who may be
using vulnerable versions.

### 2. **Contact Information**

Report security vulnerabilities by emailing: **[security@example.com]** (Replace with actual contact)

Or create a private security advisory on GitHub:
1. Go to the repository's Security tab
2. Click "Report a vulnerability"
3. Fill out the advisory form

### 3. **Information to Include**

When reporting a vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker accomplish?
- **Reproduction**: Step-by-step instructions to reproduce the issue
- **Affected Versions**: Which versions are affected?
- **Suggested Fix**: If you have ideas for how to fix the issue

### 4. **Response Timeline**

We aim to respond to security reports within:

- **Initial Response**: 48 hours
- **Confirmation**: 7 days
- **Fix Development**: 30 days (depending on complexity)
- **Public Disclosure**: After fix is released and users have time to update

## Security Best Practices

### For Users

1. **Keep Updated**: Always use the latest version of the tool
2. **Review Permissions**: When using as a GitHub Action, review the permissions granted
3. **Validate Sources**: Only use the tool from official sources (GitHub releases, GitHub Marketplace)
4. **Monitor Dependencies**: Keep an eye on security advisories for Python dependencies

### For Contributors

1. **Code Review**: All code changes require review before merging
2. **Dependency Management**: Regularly update and audit dependencies
3. **Input Validation**: Validate all user inputs and file contents
4. **Error Handling**: Implement proper error handling to prevent information disclosure

## Security Considerations

### File Processing

- **Path Traversal**: The tool validates file paths to prevent directory traversal attacks
- **File Size Limits**: Large files are handled efficiently to prevent resource exhaustion
- **Content Validation**: File contents are validated before processing

### GitHub Action Security

- **Minimal Permissions**: The action requests only necessary permissions
- **Secure Defaults**: Default configuration follows security best practices
- **Input Sanitization**: All action inputs are properly sanitized

### Dependencies

- **Regular Updates**: Dependencies are regularly updated to address security vulnerabilities
- **Vulnerability Scanning**: Automated scanning for known vulnerabilities in dependencies
- **Minimal Dependencies**: We keep the dependency tree as small as possible

## Security Testing

We perform regular security testing including:

- **Static Analysis**: Code is analyzed for potential security issues
- **Dependency Scanning**: Regular scans for vulnerable dependencies
- **Input Fuzzing**: Testing with malformed inputs to identify edge cases
- **Permission Testing**: Verifying the tool works with minimal permissions

## Incident Response

In case of a security incident:

1. **Assessment**: Evaluate the scope and impact of the incident
2. **Containment**: Take immediate steps to limit the impact
3. **Communication**: Notify affected users through appropriate channels
4. **Resolution**: Develop and deploy fixes
5. **Post-Incident**: Conduct a post-incident review to improve security

## Security Resources

- **GitHub Security Advisories**: [Repository Security Tab]
- **Python Security**: [Python Security Documentation](https://docs.python.org/3/library/security_warnings.html)
- **Terraform Security**: [Terraform Security Best Practices](https://learn.hashicorp.com/tutorials/terraform/security)

## Acknowledgments

We thank the security community and all contributors who help make this tool more secure.
