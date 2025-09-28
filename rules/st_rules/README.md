# ST (Style/Format) Rules Package

This package contains all style and format related checking rules for Terraform scripts.  
The package has been refactored into a modular structure where each rule is implemented in a separate module for better
maintainability and extensibility.

## 📁 Package Structure

```
st_rules/
├── __init__.py   # Package initialization and exports
├── README.md     # This documentation file
├── reference.py  # Main STRules coordinator class
├── rule_001.py   # ST.001 - Resource and data source naming convention check
├── rule_002.py   # ST.002 - Variable default value check
├── rule_003.py   # ST.003 - Parameter alignment check
├── rule_004.py   # ST.004 - Indentation character check
├── rule_005.py   # ST.005 - Indentation level check
├── rule_006.py   # ST.006 - Resource and data source spacing check
├── rule_007.py   # ST.007 - Same parameter block spacing check
├── rule_008.py   # ST.008 - Different parameter block spacing check
├── rule_009.py   # ST.009 - Variable definition order check
├── rule_010.py   # ST.010 - Resource, data source, variable, and output quote check
├── rule_011.py   # ST.011 - Trailing whitespace check
├── rule_012.py   # ST.012 - File header and footer whitespace check
└── rule_013.py   # ST.013 - Directory naming convention check
```

## 🎯 Available Rules

| Rule ID | Name | Description | Module |
|---------|------|-------------|---------|
| ST.001 | Resource and data source naming convention check | Validates naming conventions for resources and data sources | `rule_001.py` |
| ST.002 | Variable default value check | Ensures variables used in data sources have default values | `rule_002.py` |
| ST.003 | Parameter alignment check | Validates proper parameter alignment and formatting with equals signs aligned to maintain one space from the longest parameter name. | `rule_003.py` |
| ST.004 | Indentation character check | Ensures only spaces are used for indentation (no tabs) | `rule_004.py` |
| ST.005 | Indentation level check | Validates consistent 2-space indentation levels. For terraform.tfvars files, heredoc blocks (<<EOT, <<EOF, etc.) are excluded from validation | `rule_005.py` |
| ST.006 | Resource and data source spacing check | Ensures exactly 1 empty line between resource/data blocks | `rule_006.py` |
| ST.007 | Same parameter block spacing check | Validates spacing between same-named parameter blocks | `rule_007.py` |
| ST.008 | Different parameter block spacing check | Ensures proper spacing between different parameter types | `rule_008.py` |
| ST.009 | Variable definition order check | Validates variable order consistency between files | `rule_009.py` |
| ST.010 | Resource, data source, variable, and output quote check | Ensures double quotes around resource/data source names | `rule_010.py` |
| ST.011 | Trailing whitespace check | Removes trailing spaces and tabs from line endings | `rule_011.py` |
| ST.012 | File header and footer whitespace check | Ensures no extra whitespace at the beginning or end of the file | `rule_012.py` |
| ST.013 | Directory naming convention check | Validates directory names contain only letters, numbers, and hyphens, and start/end with letters | `rule_013.py` |

## 🚀 Usage

### Basic Usage

```python
from rules.st_rules import STRules

# Initialize the rules coordinator
st_rules = STRules()

# Define error logging function (note the Optional[int] parameter for line number)
def log_error(file_path, rule_id, message, line_number=None):
    if line_number:
        print(f"ERROR: {file_path} ({line_number}): [{rule_id}] {message}")
    else:
        print(f"ERROR: {file_path}: [{rule_id}] {message}")

# Execute all ST rules on file content
file_content = '''resource "aws_instance" "example" {
    ami = "ami-12345"
}'''
st_rules.execute_all_rules("example.tf", file_content, log_error)

# Execute a specific rule
st_rules.execute_rule("ST.001", "example.tf", file_content, log_error)

# For backward compatibility, you can also use the legacy method
st_rules.run_all_checks("example.tf", file_content, log_error)
```

### Advanced Usage

```python
from rules.st_rules import STRules

st_rules = STRules()

# Get rule information
rule_info = st_rules.get_rule_info("ST.001")
if rule_info:
    print(f"Rule name: {rule_info['name']}")
    print(f"Description: {rule_info['description']}")
    print(f"Category: {rule_info['category']}")

# Get all available rules
all_rules = st_rules.get_available_rules()
print(f"Available ST rules: {all_rules}")

# Execute rules with exclusions
excluded_rules = ["ST.009"]  # Example: exclude cross-file analysis
results = st_rules.execute_all_rules("example.tf", file_content, log_error, excluded_rules)

# Get rules summary
summary = st_rules.get_rules_summary()
print(f"Total ST rules: {summary['total']}")
print(f"Modular rules: {summary['modular']}")

# Legacy methods (for backward compatibility)
if st_rules.is_rule_enabled("ST.001"):
    print("ST.001 is available")

# Note: enable_rule() and disable_rule() are legacy methods
# Use excluded_rules parameter in execute_all_rules() instead
```

## 🔧 Adding New Rules

To add a new ST rule, follow these steps:

### 1. Create Rule Implementation File

Create a new file `rule_XXX.py` in this directory:

```python
#!/usr/bin/env python3
"""
ST.XXX - Rule Name

Detailed description of what this rule validates.

Author: Lance
License: Apache 2.0
"""

from typing import Callable, Optional, Dict, Any

def check_stXXX_rule_name(file_path: str, content: str, log_error_func: Callable[[str, str, str, Optional[int]], None]) -> None:
    """
    Validate according to ST.XXX rule specifications.

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
        "id": "ST.XXX",
        "name": "Rule Name",
        "description": "Detailed description",
        "category": "Style/Format",
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
from .rule_XXX import check_stXXX_rule_name, get_rule_description as get_stXXX_description

class STRules:
    def _build_rules_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            # Existing rules...
            "ST.XXX": {
                "check_function": check_stXXX_rule_name,
                "description_function": get_stXXX_description,
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
# Test exclude a ST rule
python3 .github/scripts/terraform_lint.py examples/bad-example/basic --ignore-rules "ST.001"

# Test all rules including ST
python3 .github/scripts/terraform_lint.py examples/bad-example/basic
```

## 📋 Rule Details

### ST.001 - Resource and Data Source Naming Convention Check

**Purpose**: Ensures consistent naming conventions for resources and data sources.

**Validation Criteria**:
- Resource and data source names must follow proper naming patterns
- Names should be descriptive and follow team conventions

### ST.002 - Variable Default Value Check  

**Purpose**: Ensures variables used in data sources have default values.

**Validation Criteria**:
- Variables referenced in data source blocks must have default values defined
- Prevents runtime errors from undefined variables

### ST.003 - Parameter Alignment Check

**Purpose**: Validates proper parameter alignment and formatting with equals signs aligned to maintain one space from
the longest parameter name.

**Validation Criteria**:
- Equals signs must be aligned within the same code block
- Aligned equals signs should maintain exactly one space from the longest parameter name in the code block
- Exactly one space after the equals sign and parameter value
- Parameters within the same code block (not separated by blank lines) should follow alignment rules

### ST.004 - Indentation Character Check

**Purpose**: Ensures only spaces are used for indentation.

**Validation Criteria**:
- No tab characters allowed for indentation
- Only space characters should be used

### ST.005 - Indentation Level Check

**Purpose**: Validates consistent 2-space indentation levels.

**Validation Criteria**:
- Each indentation level must use exactly 2 spaces
- Consistent indentation depth throughout the file
- For terraform.tfvars files, heredoc blocks (<<EOT, <<EOF, etc.) are excluded from validation

### ST.006 - Resource and Data Source Spacing Check

**Purpose**: Ensures proper spacing between resource and data source blocks.

**Validation Criteria**:
- Exactly 1 empty line required between different resource/data blocks
- No excessive spacing between blocks

### ST.007 - Same Parameter Block Spacing Check

**Purpose**: Validates spacing between same-named parameter blocks.

**Validation Criteria**:
- Allows 0 or 1 empty line between same-named parameter blocks
- Prevents excessive spacing within similar parameter groups

### ST.008 - Different Parameter Block Spacing Check

**Purpose**: Ensures proper spacing between different parameter types.

**Validation Criteria**:
- Exactly 1 empty line required between basic parameters and parameter blocks
- Consistent spacing between different parameter type combinations

### ST.009 - Variable Definition Order Check

**Purpose**: Validates variable order consistency between main.tf and variables.tf.

**Validation Criteria**:
- Variable definition order in variables.tf must match usage order in main.tf
- Cross-file analysis for maintaining logical organization
- Provider-related variables (access_key, secret_key, region_name) are excluded from ordering validation
- Excludes authentication and region configuration variables to avoid interference with business logic ordering

### ST.010 - Resource, Data Source, Variable, and Output Quote Check

**Purpose**: Ensures double quotes around resource and data source names.

**Validation Criteria**:
- All resource and data source type and name identifiers must use double quotes
- Consistent quoting style across all Terraform files

### ST.011 - Trailing Whitespace Check

**Purpose**: Removes trailing spaces and tabs from line endings.

**Validation Criteria**:
- No trailing whitespace characters at the end of lines
- Clean line endings for better version control

### ST.012 - File Header and Footer Whitespace Check

**Purpose**: Ensures no extra whitespace at the beginning or end of the file.

**Validation Criteria**:
- No leading or trailing whitespace at the beginning of the file
- No leading or trailing whitespace at the end of the file

### ST.013 - Directory Naming Convention Check

**Purpose**: Validates that all directory names follow proper naming conventions.

**Validation Criteria**:
- Directory names must contain only letters, numbers, and hyphens
- Directory names must start and end with a letter
- No consecutive hyphens allowed
- Recursively checks all subdirectories at any depth
- Automatically skips hidden directories and system directories

**Examples**:
- Valid: `my-project`, `terraform-modules`, `test-env-1`, `data-processing`
- Invalid: `_private-dir` (starts with underscore), `my-project-` (ends with hyphen), `123-project` (starts with number)

## 🔄 Backward Compatibility

The package maintains full backward compatibility with the original `st_rules.py` module. Existing code will continue to work without modifications:

```python
# This still works
from rules.st_rules import STRules

# Legacy methods are supported
st_rules = STRules()
st_rules.run_all_checks(file_path, content, log_error_func)
st_rules.is_rule_enabled("ST.001")
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
