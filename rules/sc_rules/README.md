# SC (Security Code) Rules Package

This package contains all security-related checking rules for Terraform scripts.  
The package has been refactored into a modular structure where each rule is implemented in a separate module for better
maintainability and extensibility.

## 📁 Package Structure

```
sc_rules/
├── __init__.py   # Package initialization and exports
├── README.md     # This documentation file
├── reference.py  # Main SCRules coordinator class
└── rule_001.py   # SC.001 - Array index access safety check
```

## 🎯 Available Rules

| Rule ID | Name | Description | Module |
|---------|------|-------------|---------|
| SC.001 | Array index access safety check | Enforce safe array access using try() function | `rule_001.py` |

## 🚀 Usage

### Basic Usage

```python
from rules.sc_rules import SCRules

# Initialize the rules coordinator
sc_rules = SCRules()

# Define error logging function (note the Optional[int] parameter for line number)
def log_error(file_path, rule_id, message, line_number=None):
    if line_number:
        print(f"ERROR: {file_path} ({line_number}): [{rule_id}] {message}")
    else:
        print(f"ERROR: {file_path}: [{rule_id}] {message}")

# Execute all SC rules on file content
file_content = '''resource "aws_instance" "example" {
  ami = data.aws_ami.ubuntu.images[0].image_id
}'''
sc_rules.execute_all_rules("main.tf", file_content, log_error)

# Execute a specific rule
sc_rules.execute_rule("SC.001", "main.tf", file_content, log_error)

# For backward compatibility, you can also use the legacy method
sc_rules.run_all_checks("main.tf", file_content, log_error)
```

### Advanced Usage

```python
from rules.sc_rules import SCRules

sc_rules = SCRules()

# Get rule information
rule_info = sc_rules.get_rule_info("SC.001")
if rule_info:
    print(f"Rule name: {rule_info['name']}")
    print(f"Description: {rule_info['description']}")
    print(f"Category: {rule_info['category']}")

# Get all available rules
all_rules = sc_rules.get_available_rules()
print(f"Available SC rules: {all_rules}")

# Execute rules with exclusions
excluded_rules = ["SC.001"]  # Example: skip array safety checks
results = sc_rules.execute_all_rules("main.tf", file_content, log_error, excluded_rules)

# Get rules summary
summary = sc_rules.get_rules_summary()
print(f"Total SC rules: {summary['total']}")
print(f"Modular rules: {summary['modular']}")

# Legacy methods (for backward compatibility)
if sc_rules.is_rule_enabled("SC.001"):
    print("SC.001 is available")

# Note: enable_rule() and disable_rule() are legacy methods
# Use excluded_rules parameter in execute_all_rules() instead
```

## 🔧 Adding New Rules

To add a new SC rule, follow these steps:

### 1. Create Rule Implementation File

Create a new file `rule_XXX.py` in this directory:

```python
#!/usr/bin/env python3
"""
SC.XXX - Rule Name

Detailed description of what this security rule validates.

Author: Lance
License: Apache 2.0
"""

from typing import Callable, Optional, Dict, Any

def check_scXXX_rule_name(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate according to SC.XXX rule specifications.

    Args:
        file_path (str): Path to the file being checked
        content (str): Complete file content
        log_error_func (Callable): Error logging function with signature:
                                 (file_path, rule_id, message, line_number)
    """
    # Implementation here
    pass

def get_rule_description() -> Dict[str, Any]:
    """
    Get detailed rule information.

    Returns:
        Dict[str, Any]: Rule metadata and examples
    """
    return {
        "id": "SC.XXX",
        "name": "Rule Name",
        "description": "Detailed description",
        "category": "Security Code",
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
from .rule_XXX import check_scXXX_rule_name, get_rule_description as get_scXXX_description

class SCRules:
    def _build_rules_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            # Existing rules...
            "SC.XXX": {
                "check_function": check_scXXX_rule_name,
                "description_function": get_scXXX_description,
                "name": "Rule Name",
                "status": "modular"
            }
        }
```

### 3. Update Documentation

Update this README.md file to include the new rule in the Available Rules table.

## 🧪 Testing

The package includes comprehensive testing through the main linting system:

```bash
# Test exclude a SC rule
python3 .github/scripts/terraform_lint.py examples/bad-example/basic --ignore-rules "SC.001"

# Test all rules including SC
python3 .github/scripts/terraform_lint.py examples/bad-example/basic
```

## 📋 Rule Details

### SC.001 - Array Index Access Safety Check

**Purpose**: Enforces safe array access patterns to prevent index out of bounds errors.

**Scenarios Covered**:
- Data source list attribute references
- Optional list parameter element references
- Complex nested list access patterns

**Validation Criteria**:
- Array access expressions must use `try()` function for safety
- Direct array indexing `[0]`, `[1]`, etc. should be wrapped in try() calls
- Prevents runtime errors from accessing non-existent array elements

**Examples**:

**❌ Unsafe (Direct Index Access)**:
```hcl
# Direct array access - can cause errors if index doesn't exist
resource "aws_instance" "example" {
  ami = data.aws_ami.ubuntu.images[0].image_id
}

# Direct access to optional list elements
resource "aws_security_group" "example" {
  ingress {
    cidr_blocks = var.allowed_cidr_blocks[0]
  }
}
```

**✅ Safe (Using try() Function)**:
```hcl
# Safe array access with try() and fallback
resource "aws_instance" "example" {
  ami = try(data.aws_ami.ubuntu.images[0].image_id, "ami-default")
}

# Safe access with null fallback
resource "aws_security_group" "example" {
  ingress {
    cidr_blocks = try(var.allowed_cidr_blocks[0], null)
  }
}

# Using length() check for safety
locals {
  first_cidr = length(var.allowed_cidr_blocks) > 0 ? var.allowed_cidr_blocks[0] : null
}
```

**Best Practices**:
1. Always use `try()` function when accessing array elements by index
2. Provide meaningful fallback values appropriate for the context
3. Consider using `length()` checks for complex validation logic
4. Document expected array structures in variable descriptions

**Alternative Safe Patterns**:
- Use `for_each` instead of direct indexing when possible
- Use `coalesce()` for multiple fallback options
- Implement proper validation in variable definitions

## 🔄 Backward Compatibility

The package maintains full backward compatibility with the original `sc_rules.py` module. Existing code will continue to work without modifications:

```python
# This still works
from rules.sc_rules import SCRules

# Legacy methods are supported
sc_rules = SCRules()
sc_rules.run_all_checks(file_path, content, log_error_func)
sc_rules.is_rule_enabled("SC.001")
```

**Note**: While legacy methods like `enable_rule()` and `disable_rule()` are still available, it's recommended to use
the new `execute_all_rules()` method with the `excluded_rules` parameter for better control.

## 🏗️ Architecture Benefits

The modular architecture provides several advantages:

1. **Maintainability**: Each rule is isolated in its own module
2. **Extensibility**: New security rules can be added without modifying existing code
3. **Testability**: Individual rules can be tested in isolation
4. **Documentation**: Each rule has comprehensive inline documentation
5. **Performance**: Rules can be selectively enabled/disabled
6. **Security Focus**: Dedicated security rule validation with clear examples

## 📝 Contributing

When contributing new security rules or modifications:

1. Follow the established naming conventions
2. Include comprehensive documentation and security examples
3. Add appropriate type hints
4. Test thoroughly with both safe and unsafe code patterns
5. Update this README with new rule information
6. Consider security implications and provide clear mitigation strategies
7. Ensure error logging function signature matches: `(file_path, rule_id, message, line_number)`

## 🔒 Security Considerations

Security rules in this package focus on:

- **Runtime Safety**: Preventing index out of bounds and null reference errors
- **Error Handling**: Ensuring graceful degradation when resources are unavailable
- **Best Practices**: Promoting secure coding patterns in Terraform
- **Defensive Programming**: Encouraging protective measures against common vulnerabilities

When adding new security rules, consider:
- Impact on infrastructure reliability
- Common attack vectors in cloud environments
- Terraform-specific security anti-patterns
- Integration with security scanning tools
