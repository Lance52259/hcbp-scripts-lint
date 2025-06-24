# Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. "Enhanced lint check completed with exit code: 1" Error

#### Problem Description
GitHub Action shows exit code 1, indicating that the linting check found code errors.

#### Solutions

**Option 1: View and fix detected errors**
```yaml
# Add debug step to your workflow
- name: Show Lint Results
  if: always()
  run: |
    echo "=== Lint Report ==="
    cat terraform-lint-report.txt || echo "Report file not found"
    echo "=================="
```

**Option 2: Temporarily allow errors without failing workflow**
```yaml
- name: Terraform Scripts Lint
  uses: ./
  with:
    directory: 'path/to/your/terraform'
    fail-on-error: false  # Set to false to allow errors without breaking workflow
    report-format: 'text'
```

**Option 3: Ignore specific rules**
```yaml
- name: Terraform Scripts Lint
  uses: ./
  with:
    directory: 'path/to/your/terraform'
    ignore-rules: 'ST.008,ST.001'  # Ignore specific rules
```

### 2. "Provided artifact name input during validation is empty" Error

#### Problem Description
Artifact name is empty during upload, causing upload failure.

#### Solution
The updated Action has fixed this issue with the following improvements:

1. **Enhanced name generation logic**
2. **Fallback mechanisms**
3. **Debug output**
4. **Validation checks**

If you still encounter issues, add debugging steps to your workflow:

```yaml
- name: Debug Environment
  run: |
    echo "GitHub Context:"
    echo "  Run ID: ${{ github.run_id }}"
    echo "  Run Number: ${{ github.run_number }}"
    echo "  Job: ${{ github.job }}"
    echo "  Artifact Name: ${{ env.ARTIFACT_NAME }}"
    env
```

### 3. Matrix Job Issues

#### Problem Description
Possible artifact name conflicts in matrix jobs.

#### Solution
Use matrix-specific configuration:

```yaml
strategy:
  matrix:
    terraform-version: ['1.0', '1.1', '1.2']
    directory: ['module1', 'module2']

steps:
  - name: Terraform Scripts Lint
    uses: ./
    with:
      directory: ${{ matrix.directory }}
      report-format: 'both'
```

The Action automatically handles unique naming for matrix jobs.

### 4. Permission Issues

#### Problem Description
Action cannot read files or upload artifacts.

#### Solution
Ensure your workflow has the correct permissions:

```yaml
permissions:
  contents: read
  actions: write    # For uploading artifacts
  checks: write     # For creating check status
```

### 5. Large File Processing

#### Problem Description
Processing large Terraform projects may timeout or run out of memory.

#### Solutions

**Option 1: Batch processing**
```yaml
- name: Lint Module 1
  uses: ./
  with:
    directory: 'modules/module1'
    
- name: Lint Module 2
  uses: ./
  with:
    directory: 'modules/module2'
```

**Option 2: Increase timeout**
```yaml
- name: Terraform Scripts Lint
  uses: ./
  timeout-minutes: 30  # Increase timeout
  with:
    directory: 'large-project'
```

## 🔧 Debugging Tips

### Enable Verbose Output
```yaml
- name: Terraform Scripts Lint
  uses: ./
  with:
    directory: 'path/to/terraform'
    report-format: 'both'
  env:
    RUNNER_DEBUG: 1  # Enable GitHub Actions debugging
```

### Check Generated Reports
```yaml
- name: Show Detailed Report
  if: always()
  run: |
    echo "=== Text Report ==="
    cat terraform-lint-report.txt || echo "Text report not found"
    echo ""
    echo "=== JSON Report ==="
    cat terraform-lint-report.json || echo "JSON report not found"
```

### Validate Input Parameters
```yaml
- name: Validate Inputs
  run: |
    echo "Directory: ${{ inputs.directory }}"
    echo "Report Format: ${{ inputs.report-format }}"
    echo "Fail on Error: ${{ inputs.fail-on-error }}"
    echo "Directory exists: $(test -d '${{ inputs.directory }}' && echo 'Yes' || echo 'No')"
    ls -la "${{ inputs.directory }}" || echo "Cannot list directory"
```

## 📊 Performance Optimization

### Cache Dependencies
```yaml
- name: Cache Python Dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### Parallel Processing
```yaml
strategy:
  matrix:
    module: [module1, module2, module3]
  max-parallel: 3

steps:
  - name: Lint ${{ matrix.module }}
    uses: ./
    with:
      directory: ${{ matrix.module }}
```

## 🆘 Getting Help

If none of the above solutions resolve your issue:

1. **Check Action Logs**: Review the complete GitHub Actions logs
2. **Create an Issue**: Create a detailed issue in the project repository
3. **Provide Information**: Include error messages, workflow configuration, and relevant code

### Issue Template
```markdown
## Problem Description
[Detailed description of the issue encountered]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[Description of expected correct behavior]

## Actual Behavior
[Description of what actually happened]

## Environment Information
- GitHub Actions Runner: [ubuntu-latest/windows-latest/etc]
- Terraform Version: [version number]
- Project Structure: [brief description]

## Related Configuration
```yaml
[paste relevant workflow configuration]
```

## Error Logs
```
[paste complete error information]
```
```

## 🎯 Best Practices

1. **Always use `if: always()`** to ensure report uploads
2. **Set reasonable timeout periods**
3. **Use appropriate permission configuration**
4. **Test on development branches before production**
5. **Regularly update Action to latest version**
