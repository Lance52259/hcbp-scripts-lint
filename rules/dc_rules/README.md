# DC (Documentation/Comments) Rules Package

> 📖 **For detailed DC rules documentation, see [docs/rules/dc-rules.md](../../docs/rules/dc-rules.md)**

This package contains all documentation and comment related checking rules for Terraform scripts.  
The package has been refactored into a modular structure where each rule is implemented in a separate module for better
maintainability and extensibility.

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


## 📋 Rule Details

### DC.001 - Comment Format Check

**Purpose**: Ensures consistent comment formatting across Terraform files. Comments within HCL heredoc blocks (<<EOT, <<EOF, etc.) are excluded from validation.

**Validation Criteria**:
- Comments must start with `#` character
- Exactly one space must follow the `#` character
- Empty comments (only `#`) are allowed
- Comments within HCL heredoc blocks are excluded from validation

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

**HCL Heredoc Example (comments inside are excluded from validation)**:
```hcl
# ✅ Comments in heredoc blocks are excluded from DC.001 validation
locals = <<EOT
#! /bin/bash
echo "hello world!"
# This comment in heredoc block is not validated
EOT

resource "aws_instance" "test" {
  user_data = <<EOF
#!/bin/bash
# This comment is also excluded from validation
echo "Starting application..."
EOF
}
```

## 🔄 Backward Compatibility

The package maintains full backward compatibility with the original `dc_rules.py` module. Existing code will continue to work without modifications:

```python
# This still works
from rules.dc_rules import DCRules

# Legacy methods are supported
dc_rules = DCRules()
dc_rules.run_all_checks(file_path, content, log_error_func)
dc_rules.is_rule_enabled("DC.001")
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
