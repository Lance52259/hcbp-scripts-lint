# GitHub Setup Guide

This guide provides comprehensive instructions for setting up GitHub authentication and CI/CD pipelines for the
Terraform Scripts Lint Tool, particularly for the SC.004 rule which requires GitHub API access.

## Table of Contents

- [Overview](#overview)
- [GitHub API Setup](#github-api-setup)
- [Token Permissions](#token-permissions)
- [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

The SC.004 rule requires access to GitHub API to fetch HuaweiCloud Provider version information. This guide covers:

- GitHub API authentication setup
- Required token permissions
- CI/CD pipeline configuration
- Rate limit management

## GitHub API Setup

### Problem Description

The SC.004 rule needs to fetch available version lists from GitHub API when checking HuaweiCloud Provider versions.
Unauthenticated GitHub API requests have strict rate limits:

- **Unauthenticated requests**: 60 requests per hour
- **Authenticated requests**: 5000 requests per hour

When rate limits are reached, the following error occurs:
```
[SC.004] Failed to fetch huaweicloud provider versions from GitHub: Failed to fetch versions from GitHub: HTTP Error
403: rate limit exceeded
```

### Solutions

#### Method 1: Personal Access Token (Recommended)

1. **Create Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `public_repo` (or `repo` for private repositories)
   - Set expiration as needed
   - Copy the generated token

2. **Configure in Repository**:
   ```yaml
   env:
     GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # For public repos
     # OR
     GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}  # For private repos
   ```

#### Method 2: GitHub Actions Built-in Token

For public repositories, use the built-in `GITHUB_TOKEN`:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### Method 3: GitHub App (Enterprise)

For enterprise environments:

1. Create a GitHub App with appropriate permissions
2. Install the app on your organization
3. Use the app's installation token

## Token Permissions

### Required Permissions

| Permission | Required | Description | Rate Limit |
|------------|----------|-------------|------------|
| `public_repo` | ✅ **Required** | Access public repository releases information | 5000/hour |
| `repo` | ✅ **Alternative** | Access all repositories (including private) | 5000/hour |
| `read:org` | ⚠️ **Optional** | Read organization information (enterprise environment) | 5000/hour |
| `read:user` | ❌ **Not needed** | Read user information | 5000/hour |

### GitHub App Permissions

| Permission | Required | Description | Purpose |
|------------|----------|-------------|---------|
| `Contents` | ✅ **Read** | Read repository contents | Access release information |
| `Metadata` | ✅ **Read** | Read repository metadata | Basic repository access |
| `Pull requests` | ❌ **Not needed** | Read pull requests | Not required for SC.004 |

## CI/CD Pipeline Configuration

### Environment Requirements

- **Python**: 3.10+
- **Terraform**: 1.9.0+
- **Operating System**: Ubuntu 20.04+ (GitHub Actions default)

### Basic Workflow Configuration

```yaml
name: Terraform Lint with SC.004

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
      with:
        fetch-depth: 0  # Required for SC.004 rule
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v3
      with:
        terraform_version: '1.9.0'
    
    - name: Run Terraform Lint
      uses: Lance52259/hcbp-scripts-lint@v2.3.5
      with:
        directory: '.'
        rule-categories: 'ST,IO,DC,SC'
        fail-on-error: 'true'
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Advanced Configuration

#### With Custom Token

```yaml
- name: Run Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v2.3.5
  with:
    directory: '.'
    rule-categories: 'ST,IO,DC,SC'
    fail-on-error: 'true'
  env:
    GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

#### With Rate Limit Handling

```yaml
- name: Run Terraform Lint with Retry
  uses: Lance52259/hcbp-scripts-lint@v2.3.5
  with:
    directory: '.'
    rule-categories: 'ST,IO,DC,SC'
    fail-on-error: 'true'
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_API_RETRY_COUNT: 3
    GITHUB_API_RETRY_DELAY: 5
```

### Matrix Strategy for Multiple Environments

```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]
    terraform-version: ['1.9.0', '1.10.0']
    
jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v3
      with:
        terraform_version: ${{ matrix.terraform-version }}
    
    - name: Run Terraform Lint for ${{ matrix.environment }}
      uses: Lance52259/hcbp-scripts-lint@v2.3.5
      with:
        directory: './environments/${{ matrix.environment }}'
        rule-categories: 'ST,IO,DC,SC'
        fail-on-error: 'true'
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### Common Issues

#### 1. Rate Limit Exceeded

**Error**: `HTTP Error 403: rate limit exceeded`

**Solutions**:
- Ensure `GITHUB_TOKEN` is properly set
- Check token permissions include `public_repo` or `repo`
- Consider using a Personal Access Token for higher limits
- Implement retry logic with exponential backoff

#### 2. Authentication Failed

**Error**: `HTTP Error 401: Unauthorized`

**Solutions**:
- Verify token is valid and not expired
- Check token has correct permissions
- Ensure token is properly set in environment variables

#### 3. Repository Not Found

**Error**: `HTTP Error 404: Not Found`

**Solutions**:
- Verify repository exists and is accessible
- Check token has access to the repository
- Ensure repository name is correct

### Debug Configuration

Add debug steps to your workflow:

```yaml
- name: Debug GitHub Token
  run: |
    echo "Token length: ${#GITHUB_TOKEN}"
    echo "Token prefix: ${GITHUB_TOKEN:0:10}..."
    
- name: Test GitHub API Access
  run: |
    curl -H "Authorization: token $GITHUB_TOKEN" \
         https://api.github.com/repos/huaweicloud/terraform-provider-huaweicloud/releases \
         | jq '.[0].tag_name'
```

### Performance Optimization

#### Caching

```yaml
- name: Cache Terraform Provider
  uses: actions/cache@v3
  with:
    path: ~/.terraform.d
    key: ${{ runner.os }}-terraform-provider-${{ hashFiles('**/providers.tf') }}
    restore-keys: |
      ${{ runner.os }}-terraform-provider-
```

#### Parallel Execution

```yaml
strategy:
  matrix:
    directory: [modules, environments, examples]
    
jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Run Terraform Lint
      uses: Lance52259/hcbp-scripts-lint@v2.3.5
      with:
        directory: './${{ matrix.directory }}'
        rule-categories: 'ST,IO,DC,SC'
        fail-on-error: 'true'
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Best Practices

1. **Use Built-in Token**: For public repositories, use `GITHUB_TOKEN` when possible
2. **Minimal Permissions**: Only grant necessary permissions to tokens
3. **Token Rotation**: Regularly rotate Personal Access Tokens
4. **Error Handling**: Implement proper error handling and retry logic
5. **Monitoring**: Monitor API usage and rate limits
6. **Security**: Store tokens securely in GitHub Secrets
7. **Documentation**: Document token requirements and setup process

## Support

For additional help:

- Check the [Troubleshooting Guide](../guides/troubleshooting.md)
- Review [GitHub API Documentation](https://docs.github.com/en/rest)
- Open an issue in the [project repository](https://github.com/Lance52259/hcbp-scripts-lint/issues)
