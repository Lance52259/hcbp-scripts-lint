# Quick Start Guide - Terraform Scripts Lint (Terraform Code Quality Tool)

Welcome to **Terraform Scripts Lint** - the comprehensive Terraform code quality and linting tool! This guide will help
you get started quickly with improving your Terraform configurations.

## 🚀 5-Minute Setup

### Option 1: Local Installation (Recommended)

#### One-Click Installation

**English Version:**
```bash
# Download and run the English installation script
curl -fsSL https://raw.githubusercontent.com/Lance52259/hcbp-scripts-lint/master/tools/en-us/quick_install.sh | bash
```

**Chinese Version:**
```bash
# Download and run the Chinese installation script
curl -fsSL https://raw.githubusercontent.com/Lance52259/hcbp-scripts-lint/master/tools/zh-cn/quick_install.sh | bash
```

#### Manual Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Lance52259/hcbp-scripts-lint.git
cd hcbp-scripts-lint
```

2. **Install dependencies:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Terraform (if not already installed)
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install terraform

# macOS:
brew install terraform

# Windows:
choco install terraform
```

3. **Verify installation:**
```bash
python main.py --version
```

### Option 2: Docker Installation

```bash
# Pull the Docker image
docker pull lance52259/hcbp-scripts-lint:latest

# Run linting on your Terraform files
docker run -v $(pwd):/workspace lance52259/hcbp-scripts-lint:latest /workspace
```

### Option 3: GitHub Actions Integration

Add this to your `.github/workflows/terraform-lint.yml`:

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
        
    - name: Run Terraform Lint
      uses: Lance52259/hcbp-scripts-lint@v1
      with:
        path: '.'
        rules: 'all'
```

## 📋 Basic Usage

### Command Line Interface

```bash
# Lint all Terraform files in current directory
python main.py

# Lint specific directory
python main.py --path ./terraform/

# Run specific rules only
python main.py --rules ST.001,ST.002,SC.001

# Exclude specific rules
python main.py --exclude-rules ST.003,IO.001

# Output results to file
python main.py --output results.json

# Enable verbose output
python main.py --verbose
```

### Configuration File

Create a `.hcbp-config.yaml` file in your project root:

```yaml
# .hcbp-config.yaml
rules:
  enabled:
    - ST.001  # File naming convention
    - ST.002  # Directory structure
    - SC.001  # Security checks
    - SC.004  # Provider version validation
  
  disabled:
    - IO.001  # Input validation (if not needed)
  
  custom:
    ST.001:
      max_filename_length: 50
      allowed_extensions: ['.tf', '.tfvars']
    
    SC.004:
      github_token: ${GITHUB_TOKEN}
      cache_duration: 24h

paths:
  include:
    - "*.tf"
    - "*.tfvars"
    - "modules/**/*.tf"
  
  exclude:
    - ".terraform/**"
    - "*.auto.tfvars"
    - "examples/**"

output:
  format: json
  file: "lint-results.json"
  verbose: true
```

## 🎯 Rule Categories

### ST Rules (Style/Format)
- **ST.001**: File naming convention check
- **ST.002**: Directory structure validation
- **ST.003**: Resource naming standards
- **ST.004**: Variable naming conventions
- **ST.005**: Output naming standards
- **ST.006**: Data source naming
- **ST.007**: Module naming conventions
- **ST.008**: Provider configuration standards
- **ST.009**: Locals naming conventions
- **ST.010**: Terraform block validation
- **ST.011**: Comment formatting standards
- **ST.012**: Indentation and spacing
- **ST.013**: Directory naming convention check
- **ST.014**: File naming convention check

### IO Rules (Input/Output)
- **IO.001**: Input validation
- **IO.002**: Output validation
- **IO.003**: Variable type checking
- **IO.004**: Default value validation
- **IO.005**: Sensitive data handling

### DC Rules (Documentation/Comments)
- **DC.001**: Resource documentation
- **DC.002**: Variable documentation
- **DC.003**: Module documentation
- **DC.004**: Comment quality check
- **DC.005**: README validation

### SC Rules (Security Code)
- **SC.001**: Security best practices
- **SC.002**: Provider version constraints
- **SC.003**: Terraform version compatibility
- **SC.004**: Provider version validation
- **SC.005**: Sensitive data exposure
- **SC.006**: Access control validation

## 🔧 Advanced Configuration

### Custom Rules

Create custom rules by extending the base rule class:

```python
# custom_rules/my_rule.py
from rules.base_rule import BaseRule

class MyCustomRule(BaseRule):
    def check(self, file_path: str, content: str) -> List[Dict]:
        # Your custom logic here
        pass
    
    def get_rule_description(self) -> Dict:
        return {
            "rule_id": "CUSTOM.001",
            "title": "My Custom Rule",
            "description": "Custom validation logic"
        }
```

### Rule Dependencies

Some rules depend on others. Configure dependencies:

```yaml
# .hcbp-config.yaml
rule_dependencies:
  SC.004:  # Provider version validation
    requires:
      - SC.002  # Provider version constraints
    provides:
      - version_info
```

### Performance Optimization

```yaml
# .hcbp-config.yaml
performance:
  parallel_execution: true
  max_workers: 4
  cache_enabled: true
  cache_ttl: 3600  # 1 hour
```

## 🐛 Troubleshooting

### Common Issues

1. **ImportError: No module named 'rules'**
   ```bash
   # Solution: Add the project root to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Terraform not found**
   ```bash
   # Solution: Install Terraform
   # Ubuntu/Debian:
   sudo apt-get install terraform
   
   # macOS:
   brew install terraform
   ```

3. **Permission denied errors**
   ```bash
   # Solution: Check file permissions
   chmod +x main.py
   ```

4. **GitHub API rate limit exceeded**
   ```bash
   # Solution: Set GitHub token
   export GITHUB_TOKEN="your_token_here"
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
python main.py --debug --verbose
```

### Log Files

Check log files for detailed error information:

```bash
# Default log location
tail -f ~/.hcbp-scripts-lint/logs/lint.log

# Custom log location
python main.py --log-file /path/to/custom.log
```

## 📊 Output Formats

### JSON Output

```json
{
  "summary": {
    "total_files": 15,
    "total_issues": 3,
    "rules_executed": 25,
    "execution_time": "2.3s"
  },
  "results": [
    {
      "file": "main.tf",
      "line": 5,
      "rule": "ST.001",
      "severity": "error",
      "message": "File name should follow naming convention"
    }
  ]
}
```

### CSV Output

```bash
python main.py --output-format csv --output results.csv
```

### HTML Report

```bash
python main.py --output-format html --output report.html
```

## 🔗 Integration Examples

### Pre-commit Hook

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: terraform-lint
        name: Terraform Lint
        entry: python main.py
        language: system
        files: \.tf$
```

### CI/CD Pipeline

```yaml
# .github/workflows/terraform-lint.yml
name: Terraform Lint

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run Terraform Lint
        run: python main.py --path . --output lint-results.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: lint-results
          path: lint-results.json
```

## 📚 Additional Resources

- [Complete Rule Reference](rules/README.md)
- [Configuration Guide](docs/configuration.md)
- [API Documentation](docs/api.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

## 🆘 Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/Lance52259/hcbp-scripts-lint/issues)
- **Discussions**: [Community discussions](https://github.com/Lance52259/hcbp-scripts-lint/discussions)
- **Documentation**: [Complete documentation](https://github.com/Lance52259/hcbp-scripts-lint/wiki)

## 🎉 What's Next?

1. **Explore Rules**: Check out the [complete rule list](rules/README.md)
2. **Customize**: Create your own [configuration file](docs/configuration.md)
3. **Integrate**: Set up [CI/CD integration](docs/ci-cd.md)
4. **Contribute**: Help improve the tool by [contributing](CONTRIBUTING.md)

Happy linting! 🚀