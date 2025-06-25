# Terraform Linting Rules - Modular Architecture

This directory contains all the linting rules for the Terraform Scripts Lint Tool, organized in a modular architecture for better maintainability, extensibility, and testability.

## Architecture Overview

The rules are organized into three main categories, each implemented as a separate package:

- **ST Rules** (`st_rules/`): Style and Format rules
- **DC Rules** (`dc_rules/`): Documentation and Comments rules
- **IO Rules** (`io_rules/`): Input/Output definition rules
- **SC Rules** (`sc_rules/`): Security Code rules

Each package follows the same modular design pattern for consistency and ease of maintenance.

## Directory Structure

```
rules/
├── README.md                   # This documentation file
├── rules_manager.py            # Unified rules management system
├── __init__.py                 # Package initialization and exports
├── st_rules/                   # ST rules modular package
│   ├── __init__.py             # Package initialization
│   ├── reference.py            # Main STRules coordinator class
│   ├── rule_001.py             # ST.001 - Naming convention check
|   ├── ...
│   ├── rule_011.py             # ST.011 - Trailing whitespace check
│   └── [future rule modules]   # Additional ST rules as separate modules
├── dc_rules/                   # DC rules modular package
│   ├── __init__.py             # Package initialization
│   ├── reference.py            # Main DCRules coordinator class
│   ├── rule_001.py             # DC.001 - Comment format check
│   ├── [future rule modules]   # Additional DC rules as separate modules
│   └── README.md               # Detailed DC rules documentation
├── io_rules/                   # IO rules modular package
│   ├── __init__.py             # Package initialization
│   ├── reference.py            # Main IORules coordinator class
│   ├── rule_001.py             # IO.001 - Variable File Location
|   ├── ...
│   ├── rule_008.py             # IO.008 - Variable Type Check
│   └── [future rule modules]   # Additional IO rules as separate modules
└── sc_rules/                   # SC rules modular package
    ├── __init__.py             # Package initialization
    ├── reference.py            # Main SCRules coordinator class
    ├── rule_001.py             # SC.001 - Array index access safety check
    └── [future rule modules]   # Additional SC rules as separate modules
```

## Package Design Pattern

Each rule package follows a consistent design pattern:

### 1. Package Initialization (`__init__.py`)
- Provides package-level documentation
- Exports the main coordinator class
- Lists all available rules in the package

### 2. Reference Coordinator (`reference.py`)
- Main coordinator class (e.g., `STRules`, `DCRules`, `IORules`, `SCRules`)
- Rule registry with metadata
- Centralized rule execution coordination
- Common utility methods
- Rule enable/disable functionality

### 3. Individual Rule Modules (`rule_XXX.py`)
- Each rule implemented as a separate module
- Consistent function naming convention
- Comprehensive documentation and examples
- Rule metadata and description functions

### 4. Unified Management (`rules_manager.py`)
- Central coordinator for all rule systems
- Cross-system rule execution and management
- Performance monitoring and analytics
- Unified reporting and configuration

## Available Rules

### ST (Style/Format) Rules

| Rule ID | Name | Description | Status |
|---------|------|-------------|--------|
| ST.001 | Naming Convention | Resource and data source instance names must be 'test' | ✅ Modular |
| ST.002 | Data Source Variable Defaults | Variables used in data sources must have default values | ✅ Modular |
| ST.003 | Parameter Alignment | Proper spacing around equals signs | ✅ Modular |
| ST.004 | Indentation Character | Use spaces only, not tabs | ✅ Modular |
| ST.005 | Indentation Level | Follow 2-space indentation rule | ✅ Modular |
| ST.006 | Resource Spacing | One empty line between resource blocks | ✅ Modular |
| ST.007 | Same Parameter Spacing | ≤1 empty line between same parameter blocks | ✅ Modular |
| ST.008 | Different Parameter Type Spacing | Exactly 1 empty line between basic parameters and parameter blocks | ✅ Modular |
| ST.009 | Variable Order | Variable definition order matches usage order | ✅ Modular |
| ST.010 | Quote Usage | Double quotes around resource, data source, variable, and output names | ✅ Modular |
| ST.011 | Trailing Whitespace | No trailing spaces or tabs at line ends | ✅ Modular |

### DC (Documentation/Comments) Rules

| Rule ID | Name | Description | Status |
|---------|------|-------------|--------|
| DC.001 | Comment Format | Comments must have exactly one space after '#' | ✅ Modular |

### IO (Input/Output) Rules

| Rule ID | Name | Description | Status |
|---------|------|-------------|--------|
| IO.001 | Variable File Location | Variables must be in variables.tf | ✅ Modular |
| IO.002 | Output File Location | Outputs must be in outputs.tf | ✅ Modular |
| IO.003 | Required Variable Declaration Check | Required variables must be declared in terraform.tfvars | ✅ Modular |
| IO.004 | Variable Naming Convention Check | Variable names must use snake_case format | ✅ Modular |
| IO.005 | Output Naming Convention Check | Validates that each output variable name uses only lowercase letters and underscores, and does not start with an underscore | ✅ Modular |
| IO.006 | Variable Description Check | All variables must have non-empty descriptions | ✅ Modular |
| IO.007 | Output Description Check | All outputs must have non-empty descriptions | ✅ Modular |
| IO.008 | Variable Type Check | All variables must have type field defined | ✅ Modular |

### SC (Security Code) Rules

| Rule ID | Name | Description | Status |
|---------|------|-------------|--------|
| SC.001 | Array Index Access Safety Check | Validates that array index access uses try() function for safety | ✅ Modular |

## Usage Examples

### Unified Management (Recommended)

```python
# Import from the unified rules management system
from rules import RulesManager, validate_terraform_file

# Using RulesManager for comprehensive control
manager = RulesManager()
summary = manager.execute_all_rules(file_path, content, log_func)

# Or use convenience function for simple validation
summary = validate_terraform_file(file_path, content, log_func)
```

### Direct Package Import

```python
# Import directly from the rule system packages
from rules import STRules, DCRules, IORules, SCRules

st_rules = STRules()
dc_rules = DCRules()
io_rules = IORules()
sc_rules = SCRules()
```

### Rule Execution

```python
def log_error(file_path, rule_id, message):
    print(f"ERROR: {file_path}: [{rule_id}] {message}")

# Execute all rules for a file
file_path = "main.tf"
content = "# Example Terraform content"

st_rules.run_all_checks(file_path, content, log_error)
dc_rules.run_all_checks(file_path, content, log_error)
io_rules.run_all_checks(file_path, content, log_error)
sc_rules.run_all_checks(file_path, content, log_error)
```

### Rule Management

```python
# Get rule information
rule_info = st_rules.get_rule_info("ST.001")
print(rule_info["description"])

# Enable/disable specific rules
st_rules.disable_rule("ST.002")
st_rules.enable_rule("ST.002")

# Check if rule is enabled
if st_rules.is_rule_enabled("ST.001"):
    print("ST.001 is enabled")
```

## Adding New Rules

### 1. Create Rule Module

Create a new file `rules/{category}_rules/rule_XXX.py`:

```python
#!/usr/bin/env python3
"""
{RULE_ID} - {Rule Name}

Rule description and documentation
"""

def check_{rule_id_lower}_{rule_name}(file_path: str, content: str, log_error_func):
    """
    Rule implementation
    """
    # Implementation logic here
    pass

def get_rule_description() -> dict:
    """
    Return rule metadata
    """
    return {
        "id": "{RULE_ID}",
        "name": "{Rule Name}",
        "description": "Rule description",
        # ... other metadata
    }
```
