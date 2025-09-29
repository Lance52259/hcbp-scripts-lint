# Cross-Repository Push Configuration Guide

## Problem Scenario

When you push from a personal repository branch to a target repository, GitHub Actions may encounter the following issue:

```
Error: A branch or tag with the name 'your-personal-branch-name' could not be found
```

This situation typically occurs when:
- Pushing from personal fork to upstream repository
- Pushing from temporary branch to main branch
- Branch name doesn't exist in target repository

## Solutions

### 1. Smart Checkout Configuration

Use the following configuration to automatically handle cross-repository pushes:

```yaml
name: Cross-Repository Push

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  cross-repo-push:
    runs-on: ubuntu-latest
    
    steps:
    - name: Smart Checkout
      uses: actions/checkout@v4
      with:
        # Automatically detect and checkout the correct branch
        ref: ${{ github.event.pull_request.head.ref || github.ref_name }}
        # Use the source repository for pull requests
        repository: ${{ github.event.pull_request.head.repo.full_name || github.repository }}
        # Fetch all branches and tags
        fetch-depth: 0
        # Use the correct token
        token: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Dynamic Branch Detection

```yaml
name: Dynamic Branch Detection

on:
  push:
    branches: [ main, develop, 'feature/*' ]
  pull_request:
    branches: [ main ]

jobs:
  dynamic-checkout:
    runs-on: ubuntu-latest
    
    steps:
    - name: Detect Source Branch
      id: detect-branch
      run: |
        if [ "${{ github.event_name }}" = "pull_request" ]; then
          echo "source_branch=${{ github.event.pull_request.head.ref }}" >> $GITHUB_OUTPUT
          echo "source_repo=${{ github.event.pull_request.head.repo.full_name }}" >> $GITHUB_OUTPUT
        else
          echo "source_branch=${{ github.ref_name }}" >> $GITHUB_OUTPUT
          echo "source_repo=${{ github.repository }}" >> $GITHUB_OUTPUT
        fi
    
    - name: Checkout Source Code
      uses: actions/checkout@v4
      with:
        ref: ${{ steps.detect-branch.outputs.source_branch }}
        repository: ${{ steps.detect-branch.outputs.source_repo }}
        token: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Multi-Repository Workflow

```yaml
name: Multi-Repository Workflow

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  multi-repo-checkout:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout Target Repository
      uses: actions/checkout@v4
      with:
        ref: ${{ github.ref_name }}
        repository: ${{ github.repository }}
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Checkout Source Repository (for PRs)
      if: github.event_name == 'pull_request'
      uses: actions/checkout@v4
      with:
        ref: ${{ github.event.pull_request.head.ref }}
        repository: ${{ github.event.pull_request.head.repo.full_name }}
        token: ${{ secrets.GITHUB_TOKEN }}
        path: source-code
    
    - name: Run Analysis
      run: |
        if [ "${{ github.event_name }}" = "pull_request" ]; then
          # Analyze source code
          python main.py --path source-code/
        else
          # Analyze target repository
          python main.py --path ./
        fi
```

### 4. Fork-Specific Configuration

```yaml
name: Fork-Specific Configuration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  fork-handling:
    runs-on: ubuntu-latest
    
    steps:
    - name: Check if Fork
      id: check-fork
      run: |
        if [ "${{ github.repository }}" != "${{ github.event.pull_request.base.repo.full_name }}" ]; then
          echo "is_fork=true" >> $GITHUB_OUTPUT
        else
          echo "is_fork=false" >> $GITHUB_OUTPUT
        fi
    
    - name: Checkout Fork Code
      if: steps.check-fork.outputs.is_fork == 'true'
      uses: actions/checkout@v4
      with:
        ref: ${{ github.event.pull_request.head.ref }}
        repository: ${{ github.event.pull_request.head.repo.full_name }}
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Checkout Main Repository
      if: steps.check-fork.outputs.is_fork == 'false'
      uses: actions/checkout@v4
      with:
        ref: ${{ github.ref_name }}
        repository: ${{ github.repository }}
        token: ${{ secrets.GITHUB_TOKEN }}
```

## Advanced Solutions

### 1. Branch Mapping Configuration

```yaml
name: Branch Mapping

on:
  push:
    branches: [ main, develop, 'feature/*' ]
  pull_request:
    branches: [ main ]

jobs:
  branch-mapping:
    runs-on: ubuntu-latest
    
    steps:
    - name: Map Branch Names
      id: map-branch
      run: |
        # Define branch mapping
        case "${{ github.ref_name }}" in
          "main")
            echo "target_branch=main" >> $GITHUB_OUTPUT
            ;;
          "develop")
            echo "target_branch=develop" >> $GITHUB_OUTPUT
            ;;
          "feature/"*)
            echo "target_branch=main" >> $GITHUB_OUTPUT
            ;;
          *)
            echo "target_branch=${{ github.ref_name }}" >> $GITHUB_OUTPUT
            ;;
        esac
    
    - name: Checkout Mapped Branch
      uses: actions/checkout@v4
      with:
        ref: ${{ steps.map-branch.outputs.target_branch }}
        repository: ${{ github.repository }}
        token: ${{ secrets.GITHUB_TOKEN }}
```

### 2. Conditional Checkout Strategy

```yaml
name: Conditional Checkout

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  conditional-checkout:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        include:
          - condition: "push"
            ref: ${{ github.ref_name }}
            repo: ${{ github.repository }}
          - condition: "pull_request"
            ref: ${{ github.event.pull_request.head.ref }}
            repo: ${{ github.event.pull_request.head.repo.full_name }}
    
    steps:
    - name: Checkout Based on Condition
      if: matrix.condition == github.event_name
      uses: actions/checkout@v4
      with:
        ref: ${{ matrix.ref }}
        repository: ${{ matrix.repo }}
        token: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Error Handling and Fallback

```yaml
name: Error Handling Checkout

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  error-handling-checkout:
    runs-on: ubuntu-latest
    
    steps:
    - name: Try Checkout Source Branch
      id: checkout-source
      uses: actions/checkout@v4
      with:
        ref: ${{ github.event.pull_request.head.ref || github.ref_name }}
        repository: ${{ github.event.pull_request.head.repo.full_name || github.repository }}
        token: ${{ secrets.GITHUB_TOKEN }}
      continue-on-error: true
    
    - name: Fallback to Main Branch
      if: steps.checkout-source.outcome == 'failure'
      uses: actions/checkout@v4
      with:
        ref: main
        repository: ${{ github.repository }}
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Continue with Analysis
      run: |
        echo "Checkout completed successfully"
        python main.py --path ./
```

## Best Practices

### 1. Use Appropriate Tokens

```yaml
# Use the correct token for the repository
token: ${{ secrets.GITHUB_TOKEN }}  # For public repositories
# or
token: ${{ secrets.PERSONAL_ACCESS_TOKEN }}  # For private repositories
```

### 2. Handle Different Event Types

```yaml
# Handle both push and pull_request events
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

### 3. Set Appropriate Fetch Depth

```yaml
# For full history (useful for cross-repository operations)
fetch-depth: 0

# For shallow clone (faster, less storage)
fetch-depth: 1
```

### 4. Use Path Parameters

```yaml
# Specify different paths for different repositories
path: source-code  # For source repository
path: target-code  # For target repository
```

## Troubleshooting

### Common Issues

1. **Branch not found error**
   ```
   Error: A branch or tag with the name 'feature-branch' could not be found
   ```
   **Solution**: Use dynamic branch detection or fallback to main branch

2. **Permission denied**
   ```
   Error: Permission denied (publickey)
   ```
   **Solution**: Ensure correct token permissions and repository access

3. **Repository not found**
   ```
   Error: Repository not found
   ```
   **Solution**: Check repository name and ensure it exists

4. **Token expired**
   ```
   Error: Bad credentials
   ```
   **Solution**: Update token or use fresh token

### Debug Steps

1. **Check event context**
   ```yaml
   - name: Debug Event Context
     run: |
       echo "Event name: ${{ github.event_name }}"
       echo "Ref name: ${{ github.ref_name }}"
       echo "Repository: ${{ github.repository }}"
       if [ "${{ github.event_name }}" = "pull_request" ]; then
         echo "PR head ref: ${{ github.event.pull_request.head.ref }}"
         echo "PR head repo: ${{ github.event.pull_request.head.repo.full_name }}"
       fi
   ```

2. **Verify branch existence**
   ```yaml
   - name: List Available Branches
     run: |
       git branch -a
       git ls-remote --heads origin
   ```

3. **Test checkout manually**
   ```yaml
   - name: Test Manual Checkout
     run: |
       git checkout ${{ github.ref_name }}
       git status
   ```

## Related Resources

- [GitHub Actions Checkout Action](https://github.com/actions/checkout)
- [GitHub Actions Context](https://docs.github.com/en/actions/learn-github-actions/contexts)
- [GitHub Actions Events](https://docs.github.com/en/actions/learn-github-actions/events-that-trigger-workflows)
- [Cross-Repository Workflows](https://docs.github.com/en/actions/learn-github-actions/contexts#github-context)