# DC (Documentation/Comments) Rules Package

This package contains all documentation and comment related checking rules for Terraform scripts. The package has been refactored into a modular structure where each rule is implemented in a separate module for better maintainability and extensibility.

## 📁 Package Structure

```
dc_rules/
├── __init__.py  # Package initialization and exports
├── README.md    # This documentation file
├── reference.py # Main DCRules coordinator class
└── rule_001.py  # DC.001 rule implementation
```

## 🎯 Available Rules

| Rule ID | Name | Description | Module |
|---------|------|-------------|---------|
| DC.001 | Comment format check | Validates comment formatting standards | `rule_001.py` |

## 🚀 Usage

### Basic Usage

```python
from rules.dc_rules import DCRules

# Initialize the rules coordinator
dc_rules = DCRules()

# Define error logging function
def log_error(file_path, rule_id, message):
    print(f"ERROR: {file_path}: [{rule_id}] {message}")

# Run all DC checks on file content
file_content = "# Good comment\n#Bad comment"
dc_rules.run_all_checks("example.tf", file_content, log_error)
```

### Advanced Usage

```python
from rules.dc_rules import DCRules

dc_rules = DCRules()

# Check if a rule is enabled
if dc_rules.is_rule_enabled("DC.001"):
    print("DC.001 is enabled")

# Disable a specific rule
dc_rules.disable_rule("DC.001")

# Get rule information
rule_info = dc_rules.get_rule_info("DC.001")
print(f"Rule name: {rule_info['name']}")
print(f"Description: {rule_info['description']}")

# Get all rules
all_rules = dc_rules.get_all_rules()
for rule_id, info in all_rules.items():
    print(f"{rule_id}: {info['name']}")
```

## 🔧 Adding New Rules

To add a new DC rule, follow these steps:

### 1. Create Rule Implementation File

Create a new file `rule_XXX.py` in this directory:

```python
#!/usr/bin/env python3
"""
DC.XXX - Rule Name

Detailed description of what this rule validates.

Author: Lance
License: Apache 2.0
"""

from typing import Callable

def check_dcXXX_rule_name(file_path: str, content: str, log_error_func: Callable[[str, str, str], None]) -> None:
    """
    Validate according to DC.XXX rule specifications.

    Args:
        file_path (str): Path to the file being checked
        content (str): Complete file content
        log_error_func (Callable): Error logging function
    """
    # Implementation here
    pass

def get_rule_description() -> dict:
    """
    Get detailed rule information.

    Returns:
        dict: Rule metadata and examples
    """
    return {
        "id": "DC.XXX",
        "name": "Rule Name",
        "description": "Detailed description",
        "category": "Documentation/Comments",
        "severity": "error",
        "examples": {
            "valid": [],
            "invalid": []
        }
    }
```

### 2. Update Reference Class

Add the new rule to `reference.py`:

```python
# Import the new rule
from rule_XXX import check_dcXXX_rule_name

class DCRules:
    def __init__(self):
        self.rules = {
            # Existing rules...
            "DC.XXX": {
                "name": "Rule Name",
                "description": "Rule description",
                "category": "Documentation/Comments",
                "severity": "error",
                "enabled": True
            }
        }

    def run_all_checks(self, file_path: str, content: str, log_error_func):
        # Existing checks...

        # Add new rule check
        if self.rules["DC.XXX"]["enabled"]:
            check_dcXXX_rule_name(file_path, content, log_error_func)
```

### 3. Update Documentation

Update this README.md file to include the new rule in the Available Rules table.

## 🧪 Testing

The package includes comprehensive testing through the main linting system:

```bash
# Test only DC rules
python3 .github/scripts/terraform_lint.py --directory examples/bad-example \
  --ignore-rules "ST.001,ST.002,ST.003,ST.004,ST.005,ST.006,ST.007,ST.008,ST.009,ST.010,IO.001,IO.002,IO.003,IO.004,IO.005,IO.006,IO.007,IO.008"

# Test all rules including DC
python3 .github/scripts/terraform_lint.py --directory examples/bad-example
```

## 📋 Rule Details

### DC.001 - Comment Format Check

**Purpose**: Ensures consistent comment formatting across Terraform files.

**Validation Criteria**:
- Comments must start with `#` character
- Exactly one space must follow the `#` character
- Empty comments (only `#`) are allowed

**Examples**:

✅ **Valid**:
```hcl
# This is a properly formatted comment
# TODO: Add validation logic
#
```

❌ **Invalid**:
```hcl
#This comment has no space after #
#  This comment has multiple spaces after #
#	This comment has a tab after #
```

## 🔄 Backward Compatibility

The package maintains full backward compatibility with the original `dc_rules.py` module. Existing code will continue to work without modifications:

```python
# This still works
from rules.dc_rules import DCRules
```

## 🏗️ Architecture Benefits

The modular architecture provides several advantages:

1. **Maintainability**: Each rule is isolated in its own module
2. **Extensibility**: New rules can be added without modifying existing code
3. **Testability**: Individual rules can be tested in isolation
4. **Documentation**: Each rule has comprehensive inline documentation
5. **Performance**: Rules can be selectively enabled/disabled
6. **Code Quality**: Detailed type hints and error handling

## 📝 Contributing

When contributing new rules or modifications:

1. Follow the established naming conventions
2. Include comprehensive documentation and examples
3. Add appropriate type hints
4. Test thoroughly with both valid and invalid cases
5. Update this README with new rule information
