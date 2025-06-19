# Terraform Linting Rules - Modular Architecture

This directory contains all the linting rules for the Terraform Scripts Lint Tool, organized in a modular architecture for better maintainability, extensibility, and testability.

## Architecture Overview

The rules are organized into three main categories, each implemented as a separate package:

- **ST Rules** (`st_rules/`): Style and Format rules
- **DC Rules** (`dc_rules/`): Documentation and Comments rules
- **IO Rules** (`io_rules/`): Input/Output definition rules

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
│   ├── rule_010.py             # ST.010 - Quote usage check
│   └── [future rule modules]   # Additional ST rules as separate modules
├── dc_rules/                   # DC rules modular package
│   ├── __init__.py             # Package initialization
│   ├── reference.py            # Main DCRules coordinator class
│   ├── rule_001.py             # DC.001 - Comment format check
│   ├── README.md               # Detailed DC rules documentation
│   └── [future rule modules]   # Additional DC rules as separate modules
└── io_rules/                   # IO rules modular package
    ├── __init__.py             # Package initialization
    ├── reference.py            # Main IORules coordinator class
    └── [future rule modules]   # Additional IO rules as separate modules
```

## Package Design Pattern

Each rule package follows a consistent design pattern:

### 1. Package Initialization (`__init__.py`)
- Provides package-level documentation
- Exports the main coordinator class
- Lists all available rules in the package

### 2. Reference Coordinator (`reference.py`)
- Main coordinator class (e.g., `STRules`, `DCRules`, `IORules`)
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
| ST.008 | Different Parameter Spacing | Exactly 1 empty line between different parameter blocks | ✅ Modular |
| ST.009 | Variable Order | Variable definition order matches usage order | ✅ Modular |
| ST.010 | Quote Usage | Double quotes around resource type and name | ✅ Modular |

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
from rules import STRules, DCRules, IORules

st_rules = STRules()
dc_rules = DCRules()
io_rules = IORules()
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

### 2. Update Reference Coordinator

Add the rule to the coordinator class in `reference.py`:

```python
# Import the new rule
from .rule_XXX import check_{rule_function}

# Add to rules registry in __init__
self.rules["{RULE_ID}"] = {
    "name": "{Rule Name}",
    "description": "Rule description",
    "category": "{Category}",
    "enabled": True
}

# Add to run_all_checks method
if self.rules["{RULE_ID}"]["enabled"]:
    check_{rule_function}(file_path, content, log_error_func)
```

### 3. Update Documentation

- Update the rules table in this README
- Add rule documentation to package-specific README files
- Update rule count in package `__init__.py` files

## Migration Status

The modular architecture migration is **complete**:

- ✅ **DC Rules**: Fully migrated to modular structure (1/1 rules)
- ✅ **IO Rules**: Fully migrated to modular structure (8/8 rules)
- ✅ **ST Rules**: Fully migrated to modular structure (10/10 rules)

All rules have been successfully migrated to individual module files with consistent patterns and interfaces.

## Benefits of Modular Architecture

### 1. **Maintainability**
- Each rule is isolated in its own module
- Changes to one rule don't affect others
- Clear separation of concerns

### 2. **Extensibility**
- Easy to add new rules without modifying existing code
- Consistent patterns for rule implementation
- Plugin-like architecture

### 3. **Testability**
- Individual rules can be tested in isolation
- Mock dependencies easily
- Better test coverage

### 4. **Documentation**
- Each rule has comprehensive documentation
- Examples and usage patterns included
- Metadata for automated documentation generation

### 5. **Backward Compatibility**
- Existing code continues to work unchanged
- Gradual migration path
- No breaking changes

## Performance Considerations

The modular architecture maintains performance through:

- **Lazy Loading**: Rules are only loaded when needed
- **Efficient Imports**: Minimal import overhead
- **Shared Utilities**: Common functions shared across rules
- **Memory Optimization**: Rule instances created once and reused

## Contributing

When contributing new rules or modifications:

1. Follow the established modular design pattern
2. Include comprehensive documentation and examples
3. Add appropriate tests for new functionality
4. Update this README with new rule information
5. Maintain backward compatibility

## License

Apache 2.0 - See project LICENSE file for details.
