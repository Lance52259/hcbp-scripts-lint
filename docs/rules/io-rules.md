# IO (Input/Output) Rules Package

This package contains all input/output related checking rules for Terraform scripts.  
The package has been refactored into a modular structure where each rule is implemented in a separate module for better
maintainability and extensibility.

## 📁 Package Structure

```
io_rules/
├── __init__.py   # Package initialization and exports
├── README.md     # This documentation file
├── reference.py  # Main IORules coordinator class
├── rule_001.py   # IO.001 - Variable definition file location check
├── rule_002.py   # IO.002 - Output definition file location check
├── rule_003.py   # IO.003 - Required variable declaration check in terraform.tfvars
├── rule_004.py   # IO.004 - Variable naming convention check
├── rule_005.py   # IO.005 - Output naming convention check
├── rule_006.py   # IO.006 - Variable description field check
├── rule_007.py   # IO.007 - Output description field check
├── rule_008.py   # IO.008 - Variable type definition check
└── rule_009.py   # IO.009 - Unused variable detection check
```

## 🎯 Available Rules

| Rule ID | Name | Description | Module |
|---------|------|-------------|---------|
| IO.001 | Variable definition file location check | Variables must be defined in variables.tf | `rule_001.py` |
| IO.002 | Output definition file location check | Outputs must be defined in outputs.tf | `rule_002.py` |
| IO.003 | Required variable declaration check | Required variables must be declared in terraform.tfvars | `rule_003.py` |
| IO.004 | Variable naming convention check | Variable names must use snake_case format | `rule_004.py` |
| IO.005 | Output naming convention check | Output names must use snake_case format | `rule_005.py` |
| IO.006 | Variable description field check | All variables must have non-empty descriptions | `rule_006.py` |
| IO.007 | Output description field check | All outputs must have non-empty descriptions | `rule_007.py` |
| IO.008 | Variable type definition check | All variables must have type field defined | `rule_008.py` |
| IO.009 | Unused variable detection check | Detects variables defined in variables.tf but not referenced in any Terraform files within the same directory. | `rule_009.py` |

## 🚀 Usage

### Basic Usage

```python
from rules.io_rules import IORules

# Initialize the rules coordinator
io_rules = IORules()

# Define error logging function (note the Optional[int] parameter for line number)
def log_error(file_path, rule_id, message, line_number=None):
    if line_number:
        print(f"ERROR: {file_path} ({line_number}): [{rule_id}] {message}")
    else:
        print(f"ERROR: {file_path}: [{rule_id}] {message}")

# Execute all IO rules on file content
file_content = '''variable "example" {
  description = "Example variable"
  type        = string
}'''
io_rules.execute_all_rules("variables.tf", file_content, log_error)

# Execute a specific rule
io_rules.execute_rule("IO.001", "main.tf", file_content, log_error)

# For backward compatibility, you can also use the legacy method
io_rules.run_all_checks("variables.tf", file_content, log_error)
```

### Advanced Usage

```python
from rules.io_rules import IORules

io_rules = IORules()

# Get rule information
rule_info = io_rules.get_rule_info("IO.001")
if rule_info:
    print(f"Rule name: {rule_info['name']}")
    print(f"Description: {rule_info['description']}")
    print(f"Category: {rule_info['category']}")

# Get all available rules
all_rules = io_rules.get_available_rules()
print(f"Available IO rules: {all_rules}")

# Execute rules with exclusions
excluded_rules = ["IO.003"]  # Example: exclude terraform.tfvars validation
results = io_rules.execute_all_rules("variables.tf", file_content, log_error, excluded_rules)

# Get rules summary
summary = io_rules.get_rules_summary()
print(f"Total IO rules: {summary['total']}")
print(f"Modular rules: {summary['modular']}")

# Legacy methods (for backward compatibility)
if io_rules.is_rule_enabled("IO.001"):
    print("IO.001 is available")

# Note: enable_rule() and disable_rule() are legacy methods
# Use excluded_rules parameter in execute_all_rules() instead
```

## 🔧 Adding New Rules

To add a new IO rule, follow these steps:

### 1. Create Rule Implementation File

Create a new file `rule_XXX.py` in this directory:

```python
#!/usr/bin/env python3
"""
IO.XXX - Rule Name

Detailed description of what this rule validates.

Author: Lance
License: Apache 2.0
"""

from typing import Callable, Optional, Dict, Any

def check_ioXXX_rule_name(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate according to IO.XXX rule specifications.

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
        "id": "IO.XXX",
        "name": "Rule Name",
        "description": "Detailed description",
        "category": "Input/Output",
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
from .rule_XXX import check_ioXXX_rule_name, get_rule_description as get_ioXXX_description

class IORules:
    def _build_rules_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            # Existing rules...
            "IO.XXX": {
                "check_function": check_ioXXX_rule_name,
                "description_function": get_ioXXX_description,
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
# Test exclude a IO rule
python3 .github/scripts/terraform_lint.py examples/bad-example/basic --ignore-rules "IO.001"

# Test all rules including IO
python3 .github/scripts/terraform_lint.py examples/bad-example/basic
```

## 📋 Rule Details

### IO.001 - Variable Definition File Location Check

**Purpose**: Ensures all variables are defined in the dedicated variables.tf file.

**Validation Criteria**:
- All variable definitions must be in variables.tf
- No variable definitions allowed in other .tf files
- Promotes consistent file organization

### IO.002 - Output Definition File Location Check

**Purpose**: Ensures all outputs are defined in the dedicated outputs.tf file.

**Validation Criteria**:
- All output definitions must be in outputs.tf
- No output definitions allowed in other .tf files
- Maintains clear separation of concerns

### IO.003 - Required Variable Declaration Check

**Purpose**: Validates that required variables are properly declared in terraform.tfvars.

**Validation Criteria**:
- Variables without default values must be declared in terraform.tfvars
- Prevents runtime errors from missing variable values
- Cross-file validation between .tf and .tfvars files

### IO.004 - Variable Naming Convention Check

**Purpose**: Ensures consistent naming conventions for input variables.

**Validation Criteria**:
- Variable names must use snake_case format (lowercase with underscores)
- Names must not start with underscores
- Consistent naming improves code readability

### IO.005 - Output Naming Convention Check

**Purpose**: Ensures consistent naming conventions for output variables.

**Validation Criteria**:
- Output names must use snake_case format (lowercase with underscores)  
- Names must not start with underscores
- Maintains naming consistency across all Terraform constructs

### IO.006 - Variable Description Field Check

**Purpose**: Ensures all input variables have meaningful descriptions.

**Validation Criteria**:
- All variable blocks must include a description field
- Description field must contain non-empty text
- Improves code documentation and maintainability

### IO.007 - Output Description Field Check

**Purpose**: Ensures all output variables have meaningful descriptions.

**Validation Criteria**:
- All output blocks must include a description field
- Description field must contain non-empty text
- Documents the purpose and usage of each output

### IO.008 - Variable Type Definition Check

**Purpose**: Ensures all input variables have explicit type definitions.

**Validation Criteria**:
- All variable blocks must include a type field
- Type field must specify the expected variable type
- Prevents type-related runtime errors and improves validation

### IO.009 - Unused Variable Detection Check

**Purpose**: Detects variables defined in variables.tf but not referenced in any Terraform files within the same
directory.

**Validation Criteria**:
- Identifies variables declared in variables.tf but never used in the codebase
- Excludes common provider-related variables that may be used internally
- Helps maintain clean and efficient variable definitions
- Reduces configuration complexity and improves maintainability

**Smart Exclusions**:
The rule automatically excludes provider-related variables:
- Authentication variables: `region`, `access_key`, `secret_key`, `token`
- Provider configuration: `endpoint`, `domain_id`, `project_id`, `tenant_id`
- SSL/TLS settings: `insecure`, `cacert_file`, `cert`, `key`

**Examples**:
- ✅ **Valid**: All declared variables are used in the configuration
- ❌ **Invalid**: Variables declared but not referenced in any `.tf` files

## 🔄 Backward Compatibility

The package maintains full backward compatibility with the original `io_rules.py` module. Existing code will continue to
work without modifications:

```python
# This still works
from rules.io_rules import IORules

# Legacy methods are supported
io_rules = IORules()
io_rules.run_all_checks(file_path, content, log_error_func)
io_rules.is_rule_enabled("IO.001")
```

**Note**: While legacy methods like `enable_rule()` and `disable_rule()` are still available, it's recommended to use
the new `execute_all_rules()` method with the `excluded_rules` parameter for better control.

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
6. Ensure error logging function signature matches: `(file_path, rule_id, message, line_number)`
