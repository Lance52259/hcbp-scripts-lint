# Terraform Linting Rules - Complete Guide

This document provides comprehensive documentation for all Terraform script checking rules, including detailed
descriptions, examples, and implementation principles.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Rule Categories](#rule-categories)
- [ST (Style/Format) Rules](#st-styleformat-rules)
- [IO (Input/Output) Rules](#io-inputoutput-rules)
- [DC (Documentation/Comments) Rules](#dc-documentationcomments-rules)
- [SC (Security Code) Rules](#sc-security-code-rules)
- [Rule Implementation](#rule-implementation)
- [Adding New Rules](#adding-new-rules)

## Architecture Overview

The rules are organized into four main categories, each implemented as a separate package:

- **ST Rules** (`st_rules/`): Style and Format rules
- **DC Rules** (`dc_rules/`): Documentation and Comments rules
- **IO Rules** (`io_rules/`): Input/Output definition rules
- **SC Rules** (`sc_rules/`): Security Code rules

Each package follows the same modular design pattern for consistency and ease of maintenance.

## Directory Structure

```
rules/
├── rules_manager.py            # Unified rules management system
├── __init__.py                 # Package initialization and exports
├── st_rules/                   # ST rules modular package
│   ├── __init__.py             # Package initialization
│   ├── reference.py            # Main STRules coordinator class
│   ├── rule_001.py             # ST.001 - Naming convention check
│   ├── rule_002.py             # ST.002 - Variable default value check
│   ├── rule_003.py             # ST.003 - Parameter alignment check
│   ├── rule_004.py             # ST.004 - Indentation character check
│   ├── rule_005.py             # ST.005 - Indentation level check
│   ├── rule_006.py             # ST.006 - Resource spacing check
│   ├── rule_007.py             # ST.007 - Same parameter block spacing
│   ├── rule_008.py             # ST.008 - Different parameter block spacing
│   ├── rule_009.py             # ST.009 - Variable definition order check
│   ├── rule_010.py             # ST.010 - Quote usage consistency check
│   ├── rule_011.py             # ST.011 - Trailing whitespace check
│   ├── rule_012.py             # ST.012 - File header and footer whitespace check
│   ├── rule_013.py             # ST.013 - Directory naming convention check
│   ├── rule_014.py             # ST.014 - File naming convention check
│   └── README.md               # Detailed ST rules documentation
├── dc_rules/                   # DC rules modular package
│   ├── __init__.py             # Package initialization
│   ├── reference.py            # Main DCRules coordinator class
│   ├── rule_001.py             # DC.001 - Comment format check
│   └── README.md               # Detailed DC rules documentation
├── io_rules/                   # IO rules modular package
│   ├── __init__.py             # Package initialization
│   ├── reference.py            # Main IORules coordinator class
│   ├── rule_001.py             # IO.001 - Variable File Location
│   ├── rule_002.py             # IO.002 - Output File Location
│   ├── rule_003.py             # IO.003 - Required Variable Declaration
│   ├── rule_004.py             # IO.004 - Variable Naming Convention
│   ├── rule_005.py             # IO.005 - Output Naming Convention
│   ├── rule_006.py             # IO.006 - Variable Description Check
│   ├── rule_007.py             # IO.007 - Output Description Check
│   ├── rule_008.py             # IO.008 - Variable Type Check
│   ├── rule_009.py             # IO.009 - Variable Validation Check
│   └── README.md               # Detailed IO rules documentation
└── sc_rules/                   # SC rules modular package
    ├── __init__.py             # Package initialization
    ├── reference.py            # Main SCRules coordinator class
    ├── rule_001.py             # SC.001 - Array index access safety check
    ├── rule_002.py             # SC.002 - Terraform required version declaration check
    ├── rule_003.py             # SC.003 - Terraform version compatibility check
    ├── rule_004.py             # SC.004 - HuaweiCloud provider version validity check
    ├── rule_005.py             # SC.005 - Sensitive variable declaration check
    └── README.md               # Detailed SC rules documentation
```

## Rule Categories

### ST (Style/Format) - Code Formatting Rules

These rules primarily check code formatting, naming conventions, and structural consistency to ensure code has good
readability and maintainability.

### DC (Documentation/Comments) - Comment and Description Rules

These rules check comment formatting and quality to ensure code has good documentation.

### IO (Input/Output) - Input and Output Definition Rules

These rules check variable and output definition and usage standards to ensure module interface clarity and consistency.

### SC (Security Code) - Security Best Practices Rules

These rules enforce security best practices and prevent common security vulnerabilities in Terraform code. They focus on
preventing runtime errors and ensuring safe handling of potentially empty arrays, lists, and other data structures.

## ST (Style/Format) Rules

### ST.001 - Resource and Data Source Instance Naming Convention

**Rule Description:** All data source and resource code block instance names must be defined as "test".

**Purpose:**
- Ensure resource naming consistency in test environments
- Avoid using production environment naming in example code
- Improve code readability and standardization

**Error Example:**
```hcl
# ❌ Error: Instance name is not "test"
resource "huaweicloud_vpc" "main" {
  name = "example-vpc"
  cidr = "10.0.0.0/16"
}

data "huaweicloud_availability_zones" "current" {
  region = "cn-north-1"
}
```

**Correct Example:**
```hcl
# ✅ Correct: Instance name is "test"
resource "huaweicloud_vpc" "test" {
  name = "example-vpc"
  cidr = "10.0.0.0/16"
}

data "huaweicloud_availability_zones" "test" {
  region = "cn-north-1"
}
```

### ST.002 - Data Source Variable Default Value Check

**Rule Description:** Validates that all input variables used in data source blocks have default values.
This ensures data sources can work properly with minimal configuration while allowing resources to use required
variables.

**Purpose:**
- Ensure data sources can function independently
- Prevent runtime errors in data source lookups
- Maintain clear separation between required and optional variables

**Error Example:**
```hcl
# ❌ Error: Variable used in data source without default value
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  # Missing default value
}

data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size  # This will cause error
}
```

**Correct Example:**
```hcl
# ✅ Correct: Variable has default value
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  default     = 8  # Default value provided
}

data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size  # Works correctly
}
```

### ST.003 - Parameter Alignment with Equals Signs

**Rule Description:** Validates that parameter assignments within resource, data source, provider, locals, terraform,
and variable blocks have properly aligned equals signs. Also supports terraform.tfvars files for variable assignment
alignment checking.  
All equals signs must align at the same column position for optimal readability.

**Purpose:**
- Improve code visual consistency
- Enhance readability of parameter assignments
- Enforce professional formatting standards
- Support all Terraform block types including provider, locals, terraform, and variable blocks
- Support terraform.tfvars files for variable assignment alignment
- Intelligently handle nested object structures for proper parameter grouping
- Provide comprehensive error reporting for all alignment issues
- Properly filter out comment lines in all supported file types

**Error Example:**
```hcl
# ❌ Error: Equals signs not aligned
resource "huaweicloud_vpc_subnet" "test" {
  name = var.subnet_name
  cidr = cidrsubnet(var.vpc_cidr, 4, 1)
  gateway_ip = cidrhost(cidrsubnet(var.vpc_cidr, 4, 1), 1)
  vpc_id = huaweicloud_vpc.test.id
}
```

**Correct Example:**
```hcl
# ✅ Correct: Equals signs properly aligned
resource "huaweicloud_vpc_subnet" "test" {
  name       = var.subnet_name
  cidr       = cidrsubnet(var.vpc_cidr, 4, 1)
  gateway_ip = cidrhost(cidrsubnet(var.vpc_cidr, 4, 1), 1)
  vpc_id     = huaweicloud_vpc.test.id
}
```

### ST.004 - Indentation Character Validation

**Rule Description:** Validates that only spaces are used for indentation, no tabs are allowed.

**Purpose:**
- Ensure consistent indentation across all files
- Prevent mixed indentation issues
- Improve code portability

### ST.005 - Indentation Level Validation

**Rule Description:** Validates that indentation levels follow the correct nesting pattern where each level uses exactly
current_level * 2 spaces. Heredoc blocks (<<EOT, <<EOF, <<POLICY, etc.) are excluded from validation across all file
types. Top-level variable declarations in terraform.tfvars files are properly recognized and excluded from indentation
requirements. Error messages display the actual expected level based on context, not the incorrect indentation level.
Properly handles complex data structures including arrays and objects in terraform.tfvars files.

**Purpose:**
- Enforce consistent indentation standards
- Prevent indentation-related errors
- Support various content types appropriately
- Provide accurate error reporting with correct level information
- Skip tab character detection to avoid duplicate error reporting with ST.004 rule
- Detect missing indentation for block structure elements in complex data structures

### ST.006 - Block Spacing Check

**Rule Description:** Validates that there is exactly one empty line between different Terraform blocks (resource,
data source, variable, output, locals, terraform, provider). Comment lines between blocks do not count as
spacing - blank lines are still required even when comments are present.

**Purpose:**
- Improve code readability
- Create clear visual separation between blocks
- Enforce consistent spacing standards
- Require blank lines between blocks regardless of comment presence
- Support all Terraform block types including terraform and provider blocks

**Comment Line Handling:**
- Comment lines (starting with '#') are ignored during block extraction
- Blank lines are required between blocks even when comment lines are present
- Supports all quote format combinations (quoted/unquoted type and name)
- Comment lines do not count toward the required blank line count

### ST.007 - Parameter Block Spacing Check

**Rule Description:** Validates parameter block spacing within Terraform resource and data source blocks.  
This rule combines functionality from the original ST.007 and ST.008 rules to ensure consistent spacing between
different types of parameters: basic parameters, structure blocks, and dynamic blocks.

**Validation Criteria:**
- **Different parameter types**: Exactly 1 blank line required between basic parameters, structure blocks, and dynamic
  blocks
- **Same-name structure blocks**: 0-1 blank lines allowed between blocks with the same name (compact or single spacing)
- **Adjacent dynamic blocks**: Exactly 1 blank line required between dynamic blocks
- **Same-type basic parameters**: At most 1 blank line between basic parameters
- **Structure and dynamic blocks with same name**: Exactly 1 blank line required

**Parameter Types:**
- **Basic parameters**: Simple key-value assignments (e.g., `name = "value"`)
- **Structure blocks**: Nested parameter blocks (e.g., `data_disks { ... }`)
- **Dynamic blocks**: Dynamic parameter blocks (e.g., `dynamic "data_disks" { ... }`)

**Purpose:**
- Improve code readability by creating clear visual separation between different parameter types
- Maintain logical grouping of related parameters
- Enforce consistent spacing standards within resource definitions
- Support all parameter types including basic parameters, structure blocks, and dynamic blocks

### ST.009 - Variable Definition Order Validation

**Rule Description:** Validates that variable definitions in variables.tf follow the same order as their usage in
main.tf. Provider-related variables (access_key, secret_key, region_name) are excluded from ordering validation to
avoid interference with authentication and region configuration patterns.

**Purpose:**
- Ensure logical variable organization
- Improve code maintainability
- Support provider configuration patterns

### ST.010 - Resource, Data Source, Variable, Output, and Provider Quote Check

**Rule Description:** Validates that all resource, data source, variable, output, and provider declarations use proper
double quotes around their type and name declarations.

**Purpose:**
- Enforce proper double quote usage for all Terraform block declarations
- Ensure consistent syntax and prevent parsing errors
- Support all Terraform block types including provider blocks

### ST.011 - Trailing Whitespace Detection

**Rule Description:** Detects and reports trailing whitespace at the end of lines.

**Purpose:**
- Clean up unnecessary whitespace
- Prevent version control noise
- Improve code cleanliness

### ST.012 - File Header and Footer Whitespace Check

**Rule Description:** Validates that Terraform files have proper whitespace formatting at the beginning and end.

**Purpose:**
- Ensure consistent file formatting
- Improve file readability
- Standardize file structure

### ST.013 - Directory Naming Convention Check

**Rule Description:** Validates that directory names follow proper naming conventions.

**Purpose:**
- Enforce consistent directory naming
- Improve project organization
- Support cross-platform compatibility

### ST.014 - File Naming Convention Check

**Rule Description:** Validates that file names follow proper naming conventions. Excludes Terraform state files
(terraform.tfstate and variations) and log files (*.log).

**Purpose:**
- Enforce consistent file naming
- Improve project organization
- Support cross-platform compatibility

## IO (Input/Output) Rules

### IO.001 - Variable Definition File Organization

**Rule Description:** Validates that variable definitions are placed in the appropriate files (variables.tf).

**Purpose:**
- Ensure proper file organization
- Improve code maintainability
- Enforce modular structure

### IO.002 - Output Definition File Organization

**Rule Description:** Validates that output definitions are placed in the appropriate files (outputs.tf).

**Purpose:**
- Ensure proper file organization
- Improve code maintainability
- Enforce modular structure

### IO.003 - Required Variable Declaration Check

**Rule Description:** Validates that each required variable used in resources must be declared in terraform.tfvars,
excluding provider-related variables like region_*, access_key, secret_key, domain_name.

**Purpose:**
- Ensure all required variables are properly declared
- Prevent runtime errors
- Support provider configuration patterns

### IO.004 - Variable Naming Convention Check

**Rule Description:** Validates that each input variable name uses only lowercase letters and underscores, and does
not start with an underscore.

**Purpose:**
- Enforce consistent variable naming
- Improve code readability
- Follow Terraform best practices

### IO.005 - Output Naming Convention Check

**Rule Description:** Validates that each output variable name uses only lowercase letters and underscores, and does not
start with an underscore.

**Purpose:**
- Enforce consistent output naming
- Improve code readability
- Follow Terraform best practices

### IO.006 - Variable Description Requirement

**Rule Description:** Validates that all input variables have non-empty description fields.

**Purpose:**
- Ensure proper documentation
- Improve code maintainability
- Enforce documentation standards

### IO.007 - Output Description Requirement

**Rule Description:** Validates that all output variables have non-empty description fields.

**Purpose:**
- Ensure proper documentation
- Improve code maintainability
- Enforce documentation standards

### IO.008 - Variable Type Definition Requirement

**Rule Description:** Validates that all input variables have type field defined.

**Purpose:**
- Ensure type safety
- Improve code reliability
- Enforce best practices

### IO.009 - Variable Validation Block Check

**Rule Description:** Validates that variables have appropriate validation blocks where needed.

**Purpose:**
- Ensure data validation
- Improve code reliability
- Enforce best practices

## DC (Documentation/Comments) Rules

### DC.001 - Comment Formatting Standards

**Rule Description:** Validates that comments follow proper formatting standards. Comments must start with '#' character
and maintain one space. Comments within HCL heredoc blocks are excluded from validation.

**Purpose:**
- Ensure consistent comment formatting
- Improve code readability
- Support various content types

## SC (Security Code) Rules

### SC.001 - Unsafe Array Index Access Detection

**Rule Description:** Detects unsafe array index access patterns that could cause runtime errors.

**Purpose:**
- Prevent runtime errors
- Ensure safe array access
- Improve code reliability

### SC.002 - Terraform Required Version Declaration Check

**Rule Description:** Validates that `providers.tf` files contain proper `terraform` block with `required_version`
declaration.

**Purpose:**
- Ensure version consistency
- Prevent compatibility issues
- Enforce version management

### SC.003 - Terraform Version Compatibility Check

**Rule Description:** Analyzes Terraform configuration to determine minimum required version and validates that declared
`required_version` is compatible with used features.

**Purpose:**
- Ensure version compatibility
- Prevent feature incompatibility
- Enforce proper version management

### SC.004 - HuaweiCloud Provider Version Validity Check

**Rule Description:** Validates that the declared HuaweiCloud provider version is valid and available.

**Purpose:**
- Ensure provider version validity
- Prevent deployment failures
- Enforce proper provider management

### SC.005 - Sensitive Variable Declaration Check

**Rule Description:** Validates that sensitive variables are properly declared with `sensitive = true` to prevent data
exposure in state files and logs.

**Purpose:**
- Protect sensitive data
- Enforce security best practices
- Prevent data exposure

## Rule Implementation

### Modular Architecture

Each rule is implemented as a separate Python module with the following structure:

```python
def check_rule_xxx(file_path: str, content: str, log_error_func: Callable) -> None:
    """Main rule checking function."""
    # Rule implementation logic
    pass

def get_rule_description() -> dict:
    """Return rule metadata and description."""
    return {
        "name": "Rule Name",
        "description": "Rule description",
        "category": "ST|IO|DC|SC",
        "status": "modular"
    }
```

### Rule Registration

Rules are registered in their respective `reference.py` files:

```python
_rules_registry = {
    "RULE_ID": {
        "check_function": check_rule_xxx,
        "description_function": get_rule_description,
        "name": "Rule Name",
        "status": "modular"
    }
}
```

### Error Reporting

Rules report errors using the provided `log_error_func`:

```python
log_error_func(file_path, "RULE_ID", "Error message", line_number)
```

## Adding New Rules

### 1. Create Rule Module

Create a new Python file in the appropriate rules directory:

```python
# rules/st_rules/rule_015.py
def check_st015_new_rule(file_path: str, content: str, log_error_func: Callable) -> None:
    """Check for new rule violations."""
    # Implementation logic
    pass

def get_rule_description() -> dict:
    """Return rule metadata."""
    return {
        "name": "New Rule Name",
        "description": "Rule description",
        "category": "ST",
        "status": "modular"
    }
```

### 2. Register Rule

Add the rule to the appropriate `reference.py` file:

```python
from .rule_015 import check_st015_new_rule, get_rule_description as get_st015_description

_rules_registry = {
    # ... existing rules ...
    "ST.015": {
        "check_function": check_st015_new_rule,
        "description_function": get_st015_description,
        "name": "New Rule Name",
        "status": "modular"
    }
}
```

### 3. Update Documentation

Update the relevant documentation files:
- `docs/rules/overview.md` - Add rule description
- `README.md` - Update rule count and list
- `rules/README.md` - Add to rule table

### 4. Add Tests

Create test cases in the examples directory to validate the rule works correctly.

## Best Practices

1. **Consistent Naming**: Use consistent naming conventions for rule functions and files
2. **Clear Error Messages**: Provide clear, actionable error messages
3. **Performance**: Ensure rules are efficient and don't significantly impact performance
4. **Documentation**: Document all rules thoroughly with examples
5. **Testing**: Create comprehensive test cases for each rule
6. **Backward Compatibility**: Ensure new rules don't break existing functionality

## Support

For questions about rules or adding new rules:

- Check the [Troubleshooting Guide](../guides/troubleshooting.md)
- Review existing rule implementations
- Open an issue in the [project repository](https://github.com/Lance52259/hcbp-scripts-lint/issues)
