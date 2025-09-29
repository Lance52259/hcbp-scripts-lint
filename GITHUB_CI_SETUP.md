# SC.004 Rule Configuration Guide for GitHub Pipelines

## Overview

The SC.004 rule requires proper configuration of GitHub authentication and Terraform environment to work correctly in GitHub pipeline environments. This guide provides detailed instructions on how to properly configure and run the SC.004 rule in GitHub Actions.

## Environment Requirements

### 1. Basic Environment
- **Python**: 3.10+
- **Terraform**: 1.9.0+
- **Operating System**: Ubuntu 20.04+ (GitHub Actions default)

### 2. GitHub Authentication
The SC.004 rule needs to access GitHub API to fetch HuaweiCloud Provider version information, supporting the following authentication methods:

#### Method 1: GitHub Actions Built-in Token (Recommended)
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Automatically provided
  GITHUB_USERNAME: ${{ github.actor }}       # Automatically provided
```

**Advantages**:
- ✅ No additional configuration required
- ✅ Automatic token lifecycle management
- ✅ Rate limit: 5000 requests/hour
- ✅ Permission: Access current repository

**Disadvantages**:
- ❌ Can only access current repository
- ❌ Cannot access releases from other repositories

#### Method 2: Personal Access Token
```yaml
env:
  GITHUB_PAT: ${{ secrets.GITHUB_PAT }}     # Requires manual configuration
  GITHUB_USERNAME: ${{ github.actor }}       # Automatically provided
```

**Advantages**:
- ✅ Rate limit: 5000 requests/hour
- ✅ Can access multiple repositories
- ✅ Controllable permissions

**Disadvantages**:
- ❌ Requires manual creation and configuration
- ❌ Requires regular token updates

#### Method 3: GitHub App Token
```yaml
env:
  GITHUB_APP_TOKEN: ${{ secrets.GITHUB_APP_TOKEN }}  # Requires manual configuration
  GITHUB_APP_ID: ${{ secrets.GITHUB_APP_ID }}        # Requires manual configuration
  GITHUB_USERNAME: ${{ github.actor }}                # Automatically provided
```

**Advantages**:
- ✅ Enterprise-level permission control
- ✅ Rate limit: 5000 requests/hour
- ✅ Granular permission control

**Disadvantages**:
- ❌ Complex configuration
- ❌ Requires GitHub App setup

## Complete Workflow Configuration

### Basic Configuration Example

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
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install Terraform
      uses: hashicorp/setup-terraform@v3
      with:
        terraform_version: 1.9.0
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        # Install project dependencies
        
    - name: Run Terraform Lint
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_USERNAME: ${{ github.actor }}
      run: |
        echo "Running Terraform Lint check..."
        python main.py --rules SC.004 examples/bad-examples/provider-version/
```

### Advanced Configuration Example

```yaml
name: Advanced Terraform Lint

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  terraform-lint:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
        terraform-version: ['1.9.0', '1.8.0']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install Terraform ${{ matrix.terraform-version }}
      uses: hashicorp/setup-terraform@v3
      with:
        terraform_version: ${{ matrix.terraform-version }}
        
    - name: Cache Python dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
          
    - name: Cache Terraform providers
      uses: actions/cache@v3
      with:
        path: ~/.terraform.d/plugin-cache
        key: ${{ runner.os }}-terraform-${{ matrix.terraform-version }}-${{ hashFiles('**/*.tf') }}
        restore-keys: |
          ${{ runner.os }}-terraform-${{ matrix.terraform-version }}-
          
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Configure GitHub Authentication
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_USERNAME: ${{ github.actor }}
      run: |
        echo "✅ GitHub authentication configured"
        echo "✅ Python version: ${{ matrix.python-version }}"
        echo "✅ Terraform version: ${{ matrix.terraform-version }}"
        echo "✅ GitHub user: $GITHUB_USERNAME"
        
    - name: Run Terraform Lint
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_USERNAME: ${{ github.actor }}
      run: |
        echo "Running Terraform Lint check..."
        python main.py --rules SC.004 examples/bad-examples/provider-version/
        
    - name: Upload lint results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: lint-results-${{ matrix.python-version }}-${{ matrix.terraform-version }}
        path: |
          lint-results/
          *.log
```

## Environment Variable Priority

The SC.004 rule checks environment variables in the following priority:

1. **GITHUB_TOKEN** (Highest priority)
2. **GITHUB_PAT** 
3. **GITHUB_APP_TOKEN** (Lowest priority)

```python
# Authentication configuration priority
if os.getenv('GITHUB_TOKEN'):
    # Use GITHUB_TOKEN
elif os.getenv('GITHUB_PAT'):
    # Use GITHUB_PAT
elif os.getenv('GITHUB_APP_TOKEN'):
    # Use GITHUB_APP_TOKEN
else:
    # No authentication, use 60 requests/hour limit
```

## Caching and Performance Optimization

### 1. GitHub Version Cache
- ✅ **Location**: `/tmp/hcbp_github_versions_cache.json`
- ✅ **Validity**: 24 hours
- ✅ **Effect**: Reduces API calls, improves execution speed

### 2. Terraform Provider Cache
- ✅ **Location**: `~/.terraform.d/plugin-cache`
- ✅ **Effect**: Avoids repeated provider downloads

### 3. Python Dependencies Cache
- ✅ **Location**: `~/.cache/pip`
- ✅ **Effect**: Accelerates dependency installation

## Potential Issues and Solutions

### 1. Rate Limit Issues
**Problem**: Only 60 requests/hour without authentication
**Solution**: Use `GITHUB_TOKEN` environment variable

### 2. Network Timeout Issues
**Problem**: `terraform init` may timeout
**Solution**: Optimized timeout to 120 seconds

### 3. Permission Issues
**Problem**: Insufficient token permissions
**Solution**: Ensure token has `public_repo` permission

## Environment Variable Priority

SC.004 rule checks authentication in the following priority:

1. **GITHUB_TOKEN** (Highest priority)
2. **GITHUB_PAT**
3. **GITHUB_APP_TOKEN** (Lowest priority)

## Conclusion

**✅ GitHub Pipeline Fully Supports SC.004 Rule**:

1. **Provider Loading**: ✅ Fully supported, can normally download and validate HuaweiCloud Provider
2. **TOKEN Access**: ✅ Fully supported, multiple authentication methods available
3. **API Access**: ✅ Fully supported, 5000 requests/hour rate limit
4. **Caching Mechanism**: ✅ Fully supported, 24-hour version cache
5. **Error Handling**: ✅ Fully supported, includes retry and fallback mechanisms

**Recommended Configuration**:
- Use GitHub Actions built-in `GITHUB_TOKEN`
- Set `GITHUB_USERNAME` to `${{ github.actor }}`
- Enable caching mechanism for better performance
- Use appropriate timeout settings

The SC.004 rule can run stably in GitHub pipeline environments, correctly detecting HuaweiCloud Provider version constraint issues and providing accurate error information and suggestions.
