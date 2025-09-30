# SC (Security Code) Rules Package

> 📖 **For detailed SC rules documentation, see [docs/rules/sc-rules.md](../../docs/rules/sc-rules.md)**

This package contains all security-related checking rules for Terraform scripts.  
The package has been refactored into a modular structure where each rule is implemented in a separate module for better
maintainability and extensibility.

## 📁 Package Structure

```
sc_rules/
├── __init__.py   # Package initialization and exports
├── README.md     # This documentation file
├── reference.py  # Main SCRules coordinator class
├── rule_001.py   # SC.001 - Array index access safety check
├── rule_002.py   # SC.002 - Terraform required version declaration check
├── rule_003.py   # SC.003 - Terraform version compatibility check
├── rule_004.py   # SC.004 - HuaweiCloud provider version validity check
└── rule_005.py   # SC.005 - Sensitive variable declaration check
```

## 🎯 Available Rules

| Rule ID | Name | Description | Module |
|---------|------|-------------|---------|
| SC.001 | Array index access safety check | Enforce safe array access using try() function | `rule_001.py` |
| SC.002 | Terraform required version declaration check | Validates that providers.tf files contain terraform block with required_version declaration | `rule_002.py` |
| SC.003 | Terraform version compatibility check | Validates that declared required_version is compatible with features used | `rule_003.py` |
| SC.004 | HuaweiCloud provider version validity check | Validates huaweicloud provider version constraints by testing with current and previous versions | `rule_004.py` |
| SC.005 | Sensitive variable declaration check | Validates that sensitive variables are properly declared with Sensitive=true | `rule_005.py` |


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

### SC.002 - Terraform Required Version Declaration Check

**Purpose**: Validates that `providers.tf` files contain proper `terraform` block with `required_version` declaration.

**Validation Criteria**:
- Ensures consistent Terraform version usage across the project
- Prevents version compatibility issues
- Supports multiple version constraint formats (`>= 1.3.0`, `~> 1.0`, `>= 0.14.0, < 2.0.0`, etc.)
- Intelligent detection of terraform block structure and required_version declaration

**Examples**:

**✅ Valid**:
```hcl
terraform {
  required_version = ">= 1.3.0"
  
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.72.1"
    }
  }
}
```

**❌ Invalid**:
```hcl
# Missing required_version declaration
terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.72.1"
    }
  }
}
```

### SC.003 - Terraform Version Compatibility Check

**Purpose**: Analyzes Terraform configuration to determine minimum required version and validates that declared `required_version` is compatible with used features.

**Version Requirements Detection**:
- `variable/output sensitive = "true"` requires >= 0.14.0
- `variable nullable = "true"` requires >= 1.1.0
- `variable type with optional()` requires >= 1.3.0
- `resource lifecycle precondition` requires >= 1.2.0
- `variable validation with other variable references` requires >= 1.9.0
- `import block with for_each` requires >= 1.7.0
- Default minimum version: 0.12.0

**Examples**:

**✅ Compatible Version**:
```hcl
terraform {
  required_version = ">= 1.9.0"  # Compatible with validation.condition referencing other variables
}

variable "workspace_name" {
  type        = string
  description = "Workspace name"
  
  validation {
    condition     = var.workspace_id != "" || var.workspace_name != ""
    error_message = "At least one must be provided."
  }
}
```

**❌ Incompatible Version**:
```hcl
terraform {
  required_version = ">= 1.0.0"  # Too low for validation.condition with other variable references
}

variable "workspace_name" {
  type        = string
  description = "Workspace name"
  
  validation {
    condition     = var.workspace_id != "" || var.workspace_name != ""
    error_message = "At least one must be provided."
  }
}
```

### SC.004 - HuaweiCloud Provider Version Validity Check

**Purpose**: Validates huaweicloud provider version constraints by testing with current and previous versions to ensure proper version boundaries.

**Scenarios Covered**:
- Version constraint is too permissive (previous version also works)
- Version constraint is too restrictive (current version doesn't work)
- Version constraint points to non-existent version
- Version constraint syntax is invalid

**Validation Criteria**:
- Fetches real version data from GitHub releases
- Finds the previous available version (excluding known problematic versions)
- Executes terraform validate with current version (should pass)
- Executes terraform validate with previous version (should fail)

**Examples**:

**❌ Too Permissive (Previous Version Also Works)**:
```hcl
# Version constraint too permissive - previous version also works
terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.76.0"  # Previous version 1.75.x also works
    }
  }
}
```

**✅ Properly Set (Only Current Version Works)**:
```hcl
# Properly set version constraint - only current version works
terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.77.1"  # Previous version 1.76.5 fails validation
    }
  }
}
```

**❌ Non-existent Version**:
```hcl
# Version doesn't exist in GitHub releases
terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 99.0.0"  # Non-existent version
    }
  }
}
```

**❌ Invalid Syntax**:
```hcl
# Invalid version constraint syntax
terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "invalid-version"  # Invalid syntax
    }
  }
}
```

**Best Practices**:
1. Use semantic versioning constraints (>=, ~>, etc.)
2. Test version constraints in development environment
3. Check GitHub releases for available versions
4. Exclude known problematic versions (1.63.0-1.63.2, 1.64.0-1.64.2, 1.77.0)
5. Ensure current version passes terraform validate
6. Verify previous version fails terraform validate

**Technical Details**:
- Fetches versions from GitHub API with pagination support
- Excludes known problematic versions automatically
- Executes actual terraform commands for validation
- Provides detailed error messages with suggestions

### SC.005 - Sensitive Variable Declaration Check

**Purpose**: Validates that sensitive variables are properly declared with Sensitive=true to prevent sensitive data exposure in Terraform state files and logs.

**Sensitive Variable Patterns**:
- **Exact Match**: email, age, access_key, secret_key, sex, signature
- **Fuzzy Match**: phone (contains "phone"), password (contains "password"), pwd (contains "pwd")

**Validation Criteria**:
- Variables matching sensitive patterns must have `sensitive = true` declaration
- Supports various spacing formats: `sensitive = true`, `sensitive=true`, `sensitive  =  true`
- Ignores comments and only validates actual declarations
- Prevents sensitive data from appearing in Terraform state and logs

**Examples**:

**❌ Missing Sensitive Declaration**:
```hcl
variable "email" {
  type        = string
  description = "User email address"
  # Missing sensitive = true - will trigger error
}

variable "user_password" {
  type        = string
  description = "User password"
  # Missing sensitive = true - will trigger error (fuzzy match)
}
```

**✅ Proper Sensitive Declaration**:
```hcl
variable "email" {
  type        = string
  description = "User email address"
  sensitive   = true
}

variable "user_password" {
  type        = string
  description = "User password"
  sensitive   = true
}

variable "access_key" {
  type        = string
  description = "API access key"
  sensitive   = true
}
```

**Best Practices**:
1. Always declare sensitive variables with `sensitive = true`
2. Review variable names against sensitive patterns list
3. Use descriptive variable names for non-sensitive data
4. Regularly audit variable declarations for sensitive data exposure
5. Consider using more specific variable names to avoid false positives

**Security Impact**:
- **Risk Level**: High
- **Exposure Points**: Terraform state files, Terraform plan output, Terraform apply logs, CI/CD pipeline logs
- **Mitigation**: Declaring sensitive variables prevents their values from being displayed in logs and state files

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
