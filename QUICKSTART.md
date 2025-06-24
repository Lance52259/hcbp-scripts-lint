# Quick Start Guide - Terraform Scripts Lint

Welcome to the **Terraform Scripts Lint** unified rules management system! This guide will help you get started
quickly with linting your Terraform configurations.

## 🚀 5-Minute Setup

### Option 1: GitHub Actions (Recommended)

1. **Create a workflow file** in your repository:
   ```bash
   mkdir -p .github/workflows
   ```

2. **Add the workflow** (`.github/workflows/terraform-lint.yml`):
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
           uses: Lance52259/hcbp-scripts-lint@v2.0.0
           with:
             directory: './terraform'
             rule-categories: 'ST,IO,DC'
             fail-on-error: 'true'
   ```

3. **Commit and push** - Your linting will run automatically!

### Option 2: Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Lance52259/hcbp-scripts-lint.git
   cd hcbp-scripts-lint
   ```

2. **Run the linter:**
   ```bash
   python3 .github/scripts/terraform_lint.py --directory ./your-terraform-directory
   ```

## 📁 Example Project Structure

```
your-terraform-project/
├── main.tf                 # Main resources
├── variables.tf            # Variable definitions
├── outputs.tf              # Output definitions
├── terraform.tfvars        # Variable values
└── modules/
    └── vpc/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## 🎯 Common Use Cases

### 1. Basic Linting

**GitHub Actions:**
```yaml
- name: Basic Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    directory: './terraform'
```

**Local:**
```bash
python3 .github/scripts/terraform_lint.py --directory ./terraform
```

### 2. Style Checks Only

**GitHub Actions:**
```yaml
- name: Style Check
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    directory: './terraform'
    rule-categories: 'ST'
```

**Local:**
```bash
python3 .github/scripts/terraform_lint.py --directory ./terraform --categories "ST"
```

### 3. Check Only Changed Files (PR Workflow)

```yaml
name: PR Terraform Lint
on:
  pull_request:
    paths: ['terraform/**/*.tf']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Lint Changed Files
        uses: Lance52259/hcbp-scripts-lint@v2.0.0
        with:
          changed-files-only: 'true'
          base-ref: 'origin/main'
```

### 4. Ignore Specific Rules

**GitHub Actions:**
```yaml
- name: Terraform Lint with Rule Exceptions
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    directory: './terraform'
    ignore-rules: 'ST.001,ST.003,DC.001'
```

**Local:**
```bash
python3 .github/scripts/terraform_lint.py \
  --directory ./terraform \
  --ignore-rules "ST.001,ST.003"
```

### 5. Advanced Filtering

**GitHub Actions:**
```yaml
- name: Advanced Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    directory: './infrastructure'
    include-paths: 'modules/*,environments/prod/*'
    exclude-paths: 'examples/*,test/*'
    rule-categories: 'ST,IO'
```

**Local:**
```bash
python3 .github/scripts/terraform_lint.py \
  --directory ./infrastructure \
  --include-paths "modules/*,environments/prod/*" \
  --exclude-paths "examples/*,test/*" \
  --categories "ST,IO"
```

### 6. Customizing Summary Output

**Detailed Summary (Default):**
```yaml
- name: Detailed Summary Report
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    directory: './terraform'
    detailed-summary: 'true'    # Shows detailed error analysis
    report-format: 'both'       # Generate both text and JSON reports
```

**Basic Summary (Minimal):**
```yaml
- name: Basic Summary Report
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    directory: './terraform'
    detailed-summary: 'false'   # Shows only basic metrics
    report-format: 'text'       # Generate text report only
```

**Matrix Strategy with Different Summary Levels:**
```yaml
strategy:
  matrix:
    config:
      - { env: "dev", detailed: "true" }
      - { env: "prod", detailed: "false" }

steps:
  - name: Lint ${{ matrix.config.env }}
    uses: Lance52259/hcbp-scripts-lint@v2.0.0
    with:
      directory: './environments/${{ matrix.config.env }}'
      detailed-summary: ${{ matrix.config.detailed }}
```

## 🔧 Configuration Reference

### GitHub Actions Inputs

| Parameter | Description | Example |
|-----------|-------------|---------|
| `directory` | Target directory | `'./terraform'` |
| `rule-categories` | Categories to run | `'ST,IO,DC'` |
| `ignore-rules` | Rules to skip | `'ST.001,ST.003'` |
| `include-paths` | Paths to include | `'modules/*'` |
| `exclude-paths` | Paths to exclude | `'test/*'` |
| `changed-files-only` | Check only changed files | `'true'` |
| `base-ref` | Git base reference | `'origin/main'` |
| `performance-monitoring` | Enable performance tracking | `'true'` |
| `report-format` | Output format | `'text'`, `'json'`, or `'both'` |
| `detailed-summary` | Show detailed error info in summary | `'true'` |
| `fail-on-error` | Fail on errors | `'true'` |

### Command Line Options

```bash
python3 .github/scripts/terraform_lint.py [OPTIONS]

Options:
  -d, --directory TEXT          Target directory
  --categories TEXT             Rule categories (ST,IO,DC)
  --ignore-rules TEXT           Rules to ignore
  --include-paths TEXT          Paths to include
  --exclude-paths TEXT          Paths to exclude
  --changed-files-only          Check only changed files
  --base-ref TEXT               Base reference for git diff
  --performance-monitoring      Enable performance monitoring
  --report-format [text|json]   Output format
  --help                        Show help
```

## 📊 Understanding Output

### GitHub Actions Summary (Enhanced)

When using GitHub Actions, you'll see a detailed summary with visual indicators:

#### ✅ Success Summary
```markdown
# 🎉 Terraform Lint Analysis - PASSED

✅ **Result**: SUCCESS  
📁 **Files Processed**: 15  
⏱️ **Execution Time**: 1.2s  

## 📋 Summary
All Terraform files passed the linting checks successfully!
```

#### ❌ Detailed Error Summary (with `detailed-summary: true`)
```markdown
# ❌ Terraform Lint Analysis - FAILED

❌ **Result**: FAILED  
🚨 **Errors**: 2  
⚠️ **Warnings**: 1  
📁 **Files Processed**: 15  

## 🔍 Detailed Error Analysis

### 🚨 Errors Found (2)
| File | Line | Rule | Description |
|------|------|------|-------------|
| main.tf | 5 | ST.001 | Resource name should use underscores |
| variables.tf | 12 | IO.006 | Variable missing description |

## 🔧 Quick Fix Suggestions
- **ST.001**: Use snake_case for resource names
- **IO.006**: Add descriptions to all variables
```

#### Basic Summary (with `detailed-summary: false`)
```markdown
# Terraform Lint Analysis

❌ **Result**: FAILED  
🚨 **Errors**: 2  
⚠️ **Warnings**: 1  

Download detailed reports from action artifacts.
```

### Terminal Output

## 🚨 Common Issues & Solutions

### Issue 1: "No Terraform files found"
**Solution:** Check your directory path and ensure `.tf` files exist.
```bash
# Verify files exist
find ./terraform -name "*.tf" -type f
```

### Issue 2: "Permission denied"
**Solution:** Ensure the script has execution permissions.
```bash
chmod +x .github/scripts/terraform_lint.py
```

### Issue 3: "Git diff failed"
**Solution:** When using `changed-files-only`, ensure git history is available.
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Important for git diff
```

### Issue 4: "Module not found"
**Solution:** Ensure Python 3.6+ is installed with required modules.
```bash
python3 --version
python3 -c "import sys; print(sys.path)"
```

## 🎓 Rule Categories Explained

### ST (Style/Format) Rules
Focus on code formatting and consistency:
- Naming conventions
- Indentation standards
- Spacing requirements
- Code organization

### IO (Input/Output) Rules
Validate variables and outputs:
- Variable definitions
- Output specifications
- File organization
- Documentation requirements

### DC (Documentation/Comments) Rules
Ensure proper documentation:
- Comment formatting
- Module documentation
- Inline comments

## 📈 Performance Tips

### For Large Repositories
1. **Use `changed-files-only`** for PR workflows
2. **Filter paths** with `include-paths` and `exclude-paths`
3. **Select specific categories** instead of running all rules
4. **Enable performance monitoring** to track execution times

### Example Optimized Workflow
```yaml
- name: Optimized Terraform Lint
  uses: Lance52259/hcbp-scripts-lint@v2.0.0
  with:
    changed-files-only: 'true'
    rule-categories: 'ST,IO'  # Skip DC for faster execution
    exclude-paths: 'examples/*,test/*,*.backup'
    performance-monitoring: 'true'
```

## 🔄 Migration from v1.x

If you're upgrading from v1.x:

1. **Update the action version:**
   ```yaml
   # Old
   uses: Lance52259/hcbp-scripts-lint@v1.1.0
   
   # New
   uses: Lance52259/hcbp-scripts-lint@v2.0.0
   ```

2. **Add new parameters** (optional):
   ```yaml
   with:
     rule-categories: 'ST,IO,DC'  # New parameter
     performance-monitoring: 'true'  # New parameter
   ```

3. **Check new outputs** in your workflows:
   ```yaml
   - name: Process Results
     run: |
       echo "Files processed: ${{ steps.lint.outputs.files-processed }}"
       echo "Execution time: ${{ steps.lint.outputs.execution-time }}"
   ```

## 🎯 Next Steps

1. **Explore Advanced Features:** Check out the full [README.md](README.md) for advanced configurations
2. **Customize Rules:** Learn about rule customization in [rules/README.md](rules/README.md)
3. **Contribute:** See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute to the project
4. **Get Support:** Visit [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues) for help

## 📞 Need Help?

- 📖 **Full Documentation:** [README.md](README.md)
- 🐛 **Report Issues:** [GitHub Issues](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)
- 📚 **Rule Details:** [rules/introduction.md](rules/introduction.md)

---

**Happy Linting!** 🎉 Your Terraform code quality journey starts here.
