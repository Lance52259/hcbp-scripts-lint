# Terraform Lint Rules - Detailed Documentation

This document contains detailed descriptions, examples, and implementation principles for all Terraform script checking
rules.

## Rule Categories

### ST (Style/Format) - Code Formatting Rules
These rules primarily check code formatting, naming conventions, and structural consistency to ensure code has good
readability and maintainability.

### DC (Documentation/Comments) - Comment and Description Rules
These rules check comment formatting and quality to ensure code has good documentation.

### IO (Input/Output) - Input and Output Definition Rules
These rules check variable and output definition and usage standards to ensure module interface clarity and consistency.

---

## ST (Style/Format) Rule Details

### ST.001 - Resource and Data Source Instance Naming Convention

**Rule Description:** All data source and resource code block instance names must be defined as "test".

**Purpose:**
- Ensure resource naming consistency in test environments
- Avoid using production environment naming in example code
- Improve code readability and standardization

**Error Example:**

```hcl
# ❌ Error: Instance name is not "test"
resource "azurerm_resource_group" "main" {
  name     = "example-resources"
  location = "West Europe"
}

data "azurerm_client_config" "current" {}

resource "azurerm_storage_account" "example" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

**Correct Example:**

```hcl
# ✅ Correct: All instance names are "test"
resource "azurerm_resource_group" "test" {
  name     = "example-resources"
  location = "West Europe"
}

data "azurerm_client_config" "test" {}

resource "azurerm_storage_account" "test" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.test.name
  location                 = azurerm_resource_group.test.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

**Best Practices:**
- Use "test" uniformly as instance name in example code and test environments
- Use more descriptive names in production environments
- Consider using variables to manage instance names for easy switching between environments

---

### ST.002 - Variable Default Value Convention

**Rule Description:** All input variables must be designed as optional parameters (with default values).

**Purpose:**
- Improve module usability and flexibility
- Reduce configuration complexity for users
- Ensure modules work properly with minimal configuration
- Provide reasonable default behavior

**Error Example:**

```hcl
# ❌ Error: Variables without default values
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}
```

**Correct Example:**

```hcl
# ✅ Correct: All variables have default values
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "example-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# Even null or empty values are valid defaults
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "optional_config" {
  description = "Optional configuration"
  type        = string
  default     = null
}
```

**Best Practices:**
- Provide reasonable default values for all variables
- Use `null` as default for optional configurations
- Use empty collections (`{}`, `[]`) as defaults for optional lists/maps
- Explain the meaning and impact of default values in variable descriptions
- Consider using `validation` blocks to validate variable values

---

### ST.003 - Parameter Alignment Format Convention

**Rule Description:** Parameter assignments in code blocks must maintain proper alignment formatting.

**Purpose:**
- Improve code readability and aesthetics
- Maintain consistent code formatting
- Facilitate code review and maintenance
- Comply with Terraform community formatting standards

**Format Requirements:**
- At least one space before the equals sign
- Exactly one space after the equals sign
- Consistent parameter alignment within the same code block

**Error Example:**

```hcl
# ❌ Error: Improper formatting
resource "azurerm_storage_account" "test" {
  name="storageaccountname"                    # No spaces around equals
  resource_group_name =azurerm_resource_group.test.name  # No space after equals
  location            =  "East US"            # Multiple spaces after equals
  account_tier        =    "Standard"         # Inconsistent spacing
  account_replication_type="LRS"              # No spaces around equals
}
```

**Correct Example:**

```hcl
# ✅ Correct: Proper formatting
resource "azurerm_storage_account" "test" {
  name                     = "storageaccountname"
  resource_group_name      = azurerm_resource_group.test.name
  location                 = "East US"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    Environment = "test"
    Purpose     = "example"
  }
}
```

**Best Practices:**
- Use `terraform fmt` command to automatically format code
- Configure Terraform formatting plugins in IDE
- Add format checking steps in CI/CD pipeline
- Use consistent formatting tools and configurations within the team

---

### ST.004 - Indentation Character Convention

**Rule Description:** All indentation must use spaces only, not tabs.

**Purpose:**
- Ensures consistent formatting across different editors and environments
- Prevents indentation-related parsing issues
- Maintains uniform code appearance

**Good Example:**
```hcl
resource "huaweicloud_vpc" "test" {
  name = "test-vpc"
  cidr = "10.0.0.0/16"

  tags = {
    Environment = "test"
  }
}
```

**Bad Example:**
```hcl
resource "huaweicloud_vpc" "test" {
	name = "test-vpc"    # Uses tab character
	cidr = "10.0.0.0/16" # Uses tab character
}
```

**Best Practices:**
- Configure your editor to show whitespace characters
- Set up automatic tab-to-space conversion
- Use consistent indentation settings across the team

---

### ST.005 - Indentation Level Convention

**Rule Description:** Indentation must follow the rule of 2 spaces per nesting level.

**Purpose:**
- Ensures consistent code structure
- Improves readability and maintainability
- Follows Terraform community standards

**Good Example:**
```hcl
resource "huaweicloud_vpc" "test" {
  name = "test-vpc"
  cidr = "10.0.0.0/16"

  tags = {
    Environment = "test"
    Project     = "demo"
  }
}
```

**Bad Example:**
```hcl
resource "huaweicloud_vpc" "test" {
    name = "test-vpc"    # 4 spaces instead of 2
cidr = "10.0.0.0/16"     # No indentation

      tags = {           # 6 spaces instead of 2
    Environment = "test" # Inconsistent indentation
  }
}
```

**Best Practices:**
- Configure editor to use 2 spaces for indentation
- Use automatic formatting tools
- Maintain consistent indentation throughout the file

---

### ST.006 - Resource and Data Source Spacing Convention

**Rule Description:** There must be exactly one empty line between resource and data source blocks.

**Purpose:**
- Improves code organization and visual separation
- Maintains consistent block spacing standards
- Enhances code readability

**Good Example:**
```hcl
data "huaweicloud_availability_zones" "test" {
  region = var.region
}

resource "huaweicloud_vpc" "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr
}

resource "huaweicloud_vpc_subnet" "test" {
  name   = var.subnet_name
  vpc_id = huaweicloud_vpc.test.id
}
```

**Bad Example:**
```hcl
data "huaweicloud_availability_zones" "test" {
  region = var.region
}
resource "huaweicloud_vpc" "test" {  # Missing empty line
  name = var.vpc_name
}


resource "huaweicloud_vpc_subnet" "test" {  # Too many empty lines
  name = var.subnet_name
}
```

**Best Practices:**
- Always separate blocks with exactly one empty line
- Use consistent spacing throughout the file
- Consider using automated formatting tools

---

### ST.007 - Same Parameter Block Spacing Convention

**Rule Description:** Empty lines between same-name parameter blocks should be less than or equal to 1.

**Purpose:**
- Prevents excessive whitespace in parameter definitions
- Maintains clean and readable parameter organization
- Ensures consistent formatting within blocks

**Good Example:**
```hcl
resource "huaweicloud_compute_instance" "test" {
  name = "test-instance"

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }

  network {
    uuid = huaweicloud_vpc_subnet.test2.id
  }
}
```

**Bad Example:**
```hcl
resource "huaweicloud_compute_instance" "test" {
  name = "test-instance"

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }


  network {  # Too many empty lines between same parameter blocks
    uuid = huaweicloud_vpc_subnet.test2.id
  }
}
```

**Best Practices:**
- Use at most one empty line between same-name parameter blocks
- Consider grouping related parameters together
- Maintain consistent spacing patterns

---

### ST.008 - Different Parameter Block Spacing Convention

**Rule Description:** There must be exactly one empty line between different-name parameter blocks.

**Purpose:**
- Provides clear visual separation between different parameter types
- Improves code structure and readability
- Maintains consistent parameter organization

**Good Example:**
```hcl
resource "huaweicloud_compute_instance" "test" {
  name     = "test-instance"
  image_id = "image-123"

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }

  tags {
    Environment = "test"
  }
}
```

**Bad Example:**
```hcl
resource "huaweicloud_compute_instance" "test" {
  name     = "test-instance"
  image_id = "image-123"

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }
  tags {  # Missing empty line between different parameter blocks
    Environment = "test"
  }
}
```

**Best Practices:**
- Always separate different parameter types with exactly one empty line
- Group related parameters together
- Use consistent spacing throughout the resource definition

---

### ST.009 - Variable Definition Order Convention

**Rule Description:** Variable definition order in `variables.tf` must match the usage order in `main.tf`.

**Purpose:**
- Improves code readability and logical flow
- Makes it easier to understand variable dependencies
- Facilitates code review and maintenance
- Ensures consistent variable organization across projects

**Error Example:**

```hcl
# ❌ Error: Variable definition order doesn't match usage order
# main.tf - Variables used in this order: region, vpc_name, vpc_cidr, subnet_name
resource "huaweicloud_vpc" "test" {
  name   = var.vpc_name      # Second variable used
  cidr   = var.vpc_cidr      # Third variable used
  region = var.region        # First variable used
}

resource "huaweicloud_vpc_subnet" "test" {
  name   = var.subnet_name   # Fourth variable used
  vpc_id = huaweicloud_vpc.test.id
}

# variables.tf - Variables defined in wrong order
variable "vpc_cidr" {        # Should be third, but defined second
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "region" {          # Should be first, but defined first (correct)
  description = "The region where resources are located"
  type        = string
  default     = "us-east-1"
}

variable "vpc_name" {        # Should be second, but defined third
  description = "The name of the VPC"
  type        = string
  default     = "test-vpc"
}

variable "subnet_name" {     # Should be fourth, defined fourth (correct)
  description = "The name of the subnet"
  type        = string
  default     = "test-subnet"
}
```

**Correct Example:**

```hcl
# ✅ Correct: Variable definition order matches usage order
# main.tf - Variables used in this order: region, vpc_name, vpc_cidr, subnet_name
resource "huaweicloud_vpc" "test" {
  name   = var.vpc_name      # Second variable used
  cidr   = var.vpc_cidr      # Third variable used
  region = var.region        # First variable used
}

resource "huaweicloud_vpc_subnet" "test" {
  name   = var.subnet_name   # Fourth variable used
  vpc_id = huaweicloud_vpc.test.id
}

# variables.tf - Variables defined in correct order
variable "region" {          # First variable used in main.tf
  description = "The region where resources are located"
  type        = string
  default     = "us-east-1"
}

variable "vpc_name" {        # Second variable used in main.tf
  description = "The name of the VPC"
  type        = string
  default     = "test-vpc"
}

variable "vpc_cidr" {        # Third variable used in main.tf
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_name" {     # Fourth variable used in main.tf
  description = "The name of the subnet"
  type        = string
  default     = "test-subnet"
}
```

**Best Practices:**
- Define variables in `variables.tf` in the same order they are first referenced in `main.tf`
- Review variable usage order when adding new variables
- Consider grouping related variables together while maintaining usage order
- Use consistent variable ordering across similar modules
- Document any intentional deviations from usage order with comments

### ST.010 - Resource and Data Source Quote Check

**Rule Description:** All data sources and resources must have their type and name enclosed in double quotes.

**Purpose:**
- Ensures consistent Terraform syntax across all configurations
- Prevents syntax errors and improves code readability
- Maintains compatibility with Terraform formatting tools
- Follows Terraform community standards for resource declarations

**Error Example:**

```hcl
# ❌ Error: Missing quotes around data source type and name
# main.tf - Various quoting violations
data huaweicloud_availability_zones test {
  region = var.region
}

data "huaweicloud_compute_flavors" test_flavor {
  performance_type = "normal"
  cpu_core_count   = 2
}

resource huaweicloud_vpc "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr
}

resource "huaweicloud_vpc_subnet" test_subnet {
  name   = var.subnet_name
  vpc_id = huaweicloud_vpc.test.id
}
```

**Correct Example:**

```hcl
# ✅ Correct: Proper double quotes around all types and names
# main.tf - Consistent quoting style
data "huaweicloud_availability_zones" "test" {
  region = var.region
}

data "huaweicloud_compute_flavors" "test" {
  performance_type = "normal"
  cpu_core_count   = 2
}

resource "huaweicloud_vpc" "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr
}

resource "huaweicloud_vpc_subnet" "test" {
  name   = var.subnet_name
  vpc_id = huaweicloud_vpc.test.id
}
```

**Best Practices:**
- Always use double quotes for both resource type and name
- Maintain consistent quoting style throughout all Terraform files
- Use automated formatting tools like `terraform fmt` to ensure compliance
- Configure IDE/editor to highlight syntax violations

**Cross-references**: Works with [ST.001](#st001---resource-and-data-source-naming-convention), [ST.003](#st003---parameter-assignment-formatting)

---

## DC (Documentation/Comments) Rule Details

### DC.001 - Comment Format Convention

**Rule Description:** All comments must start with `#` character and maintain one English space between the `#` and the
                      comment text.

**Purpose:**
- Ensure comment format consistency and readability
- Comply with Terraform community comment standards
- Improve code professionalism and maintainability
- Facilitate automated tool processing of comment content

**Error Example:**

```hcl
# ❌ Error: Improper comment formatting
#This is an incorrect comment format                    # No space
#  This comment has multiple spaces                      # Multiple spaces
resource "azurerm_resource_group" "test" {
  name     = "example-resources"
  location = "West Europe"              #No space in inline comment
}

#Another incorrect comment
variable "example" {
  description = "An example variable"
  type        = string
  default     = "test"
}
```

**Correct Example:**

```hcl
# ✅ Correct: Proper comment formatting
# This is a correct comment format
# Create resource group to contain all related resources
resource "azurerm_resource_group" "test" {
  name     = "example-resources"
  location = "West Europe"              # Resource group location
}

# Define example variable
# Used to demonstrate proper variable definition
variable "example" {
  description = "An example variable"
  type        = string
  default     = "test"                  # Default value for test environment
}
```

**Best Practices:**
- Add explanatory comments for complex resource configurations
- Use comments in variable and output definitions to explain purposes
- Use comments to document important configuration decisions and limitations
- Keep comment content accurate and up-to-date
- Avoid over-commenting obvious code

---

## IO (Input/Output) Rule Details

### IO.001 - Variable Definition File Convention

**Rule Description:** All input variables must be defined in the `variables.tf` file in the same directory.

**Purpose:**
- Maintain project structure consistency and clarity
- Facilitate centralized variable management and maintenance
- Improve code readability and maintainability
- Comply with Terraform community best practices

**Project Structure Example:**

```
terraform-project/
├── main.tf             # Main resource definitions
├── variables.tf        # All variable definitions
├── outputs.tf          # All output definitions
├── terraform.tfvars    # Variable value definitions
└── versions.tf         # Provider version constraints
```

**Error Example:**

```hcl
# ❌ Error: Defining variables in main.tf
# main.tf
variable "resource_group_name" {    # Variables should be in variables.tf
  description = "Name of the resource group"
  type        = string
  default     = "example-rg"
}

resource "azurerm_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}

variable "location" {               # Variables should be in variables.tf
  description = "Azure region"
  type        = string
  default     = "East US"
}
```

**Correct Example:**

```hcl
# ✅ Correct: Variables defined in variables.tf
# variables.tf
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "example-rg"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

# main.tf
resource "azurerm_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}
```

**Best Practices:**
- Keep all variable definitions in `variables.tf`
- Use descriptive variable names
- Include clear descriptions for all variables
- Consider using variable validation blocks
- Document any special requirements or constraints

---

### IO.002 - Output Definition File Convention

**Rule Description:** All output variables must be defined in the `outputs.tf` file in the same directory.

**Purpose:**
- Maintain project structure clarity and consistency
- Facilitate centralized output management and documentation
- Improve module interface readability
- Comply with Terraform community best practices

**Error Example:**

```hcl
# ❌ Error: Defining outputs in main.tf
# main.tf
resource "azurerm_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}

output "resource_group_id" {        # Outputs should be in outputs.tf
  description = "ID of the resource group"
  value       = azurerm_resource_group.test.id
}
```

**Correct Example:**

```hcl
# ✅ Correct: Outputs defined in outputs.tf
# outputs.tf
output "resource_group_id" {
  description = "The ID of the created resource group"
  value       = azurerm_resource_group.test.id
}

output "resource_group_name" {
  description = "The name of the created resource group"
  value       = azurerm_resource_group.test.name
}

# main.tf
resource "azurerm_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}
```

**Best Practices:**
- Keep all output definitions in `outputs.tf`
- Provide clear descriptions for all outputs
- Mark sensitive outputs appropriately
- Consider using output validation
- Document any special output formats or requirements

---

### IO.003 - Required Parameter Declaration Convention

**Rule Description:** All required variables used in resources must have input values declared in the `terraform.tfvars`
                      file in the same directory.

**Purpose:**
- Ensure all required variables have explicit value definitions
- Provide clear configuration entry points
- Facilitate configuration management for different environments
- Avoid runtime variable undefined errors

**Error Example:**

```hcl
# ❌ Error: Missing required variable values in terraform.tfvars
# variables.tf
variable "storage_account_name" {
  description = "Name of the storage account"
  type        = string
  # No default value, this is a required variable
}

variable "location" {
  description = "Azure region"
  type        = string
  # No default value, this is a required variable
}

# Missing terraform.tfvars file or incomplete variable declarations
```

**Correct Example:**

```hcl
# ✅ Correct: All required variables declared in terraform.tfvars
# terraform.tfvars
storage_account_name = "myuniquestorageacct001"
location            = "East US"
environment         = "development"

# Optional: Override variables with default values
resource_group_name = "my-custom-rg"
```

**Best Practices:**
- Create a `terraform.tfvars` file for all required variables
- Provide example values in `terraform.tfvars.example`
- Use environment-specific `.tfvars` files for different environments
- Document all required variables and their expected values
- Consider using variable validation blocks

---

### IO.004 - Variable Naming Convention

**Rule Description:** All variable names must only contain lowercase letters and underscores, and must not start with an
underscore.

**Purpose:**
- Ensure consistent variable naming patterns
- Improve code readability and maintainability
- Prevent naming conflicts and confusion
- Comply with Terraform community naming standards

**Error Example:**

```hcl
# ❌ Error: Invalid variable naming
variable "_invalid_name" {    # Starts with underscore
  description = "Invalid variable name"
  type        = string
}

variable "InvalidName" {      # Contains uppercase letters
  description = "Invalid variable name"
  type        = string
}

variable "invalid-name" {     # Contains hyphen
  description = "Invalid variable name"
  type        = string
}
```

**Correct Example:**

```hcl
# ✅ Correct: Valid variable naming
variable "valid_name" {
  description = "Valid variable name"
  type        = string
}

variable "another_valid_name" {
  description = "Another valid variable name"
  type        = string
}

variable "validname" {
  description = "Valid variable name without underscores"
  type        = string
}
```

**Best Practices:**
- Use lowercase letters and underscores only
- Avoid starting names with underscores
- Use descriptive but concise names
- Follow consistent naming patterns
- Consider using prefixes for related variables

---

### IO.005 - Output Naming Convention

**Rule Description:** All output names must only contain lowercase letters and underscores, and must not start with an
                      underscore.

**Purpose:**
- Ensure consistent output naming patterns
- Improve module interface clarity
- Maintain consistent output naming standards
- Comply with Terraform community naming standards

**Error Example:**

```hcl
# ❌ Error: Invalid output naming
output "_invalid_output" {    # Starts with underscore
  description = "Invalid output name"
  value       = "test"
}

output "InvalidOutput" {      # Contains uppercase letters
  description = "Invalid output name"
  value       = "test"
}

output "invalid-output" {     # Contains hyphen
  description = "Invalid output name"
  value       = "test"
}
```

**Correct Example:**

```hcl
# ✅ Correct: Valid output naming
output "valid_output" {
  description = "Valid output name"
  value       = "test"
}

output "another_valid_output" {
  description = "Another valid output name"
  value       = "test"
}

output "validoutput" {
  description = "Valid output name without underscores"
  value       = "test"
}
```

**Best Practices:**
- Use lowercase letters and underscores only
- Avoid starting names with underscores
- Use descriptive but concise names
- Follow consistent naming patterns
- Consider using prefixes for related outputs

---

### IO.006 - Variable Description Convention

**Rule Description:** All input variables must have a description field defined and not empty.

**Purpose:**
- Improves code documentation and usability
- Facilitates automated documentation generation
- Helps users understand variable purposes

**Good Example:**
```hcl
variable "vpc_name" {
  description = "The name of the VPC to be created"
  type        = string
  default     = "test-vpc"
}

variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}
```

**Bad Example:**
```hcl
variable "vpc_name" {
  # Missing description field
  type    = string
  default = "test-vpc"
}

variable "environment" {
  description = ""  # Empty description
  type        = string
  default     = "dev"
}
```

**Best Practices:**
- Always provide meaningful descriptions for variables
- Describe the purpose and expected values
- Include examples or constraints when helpful
- Keep descriptions concise but informative

---

### IO.007 - Output Description Convention

**Rule Description:** All output variables must have a description field defined and not empty.

**Purpose:**
- Improves module interface documentation
- Helps users understand output purposes and usage
- Facilitates automated documentation generation

**Good Example:**
```hcl
output "vpc_id" {
  description = "The ID of the created VPC"
  value       = huaweicloud_vpc.test.id
}

output "subnet_ids" {
  description = "List of subnet IDs created in the VPC"
  value       = huaweicloud_vpc_subnet.test[*].id
}
```

**Bad Example:**
```hcl
output "vpc_id" {
  # Missing description field
  value = huaweicloud_vpc.test.id
}

output "subnet_ids" {
  description = ""  # Empty description
  value       = huaweicloud_vpc_subnet.test[*].id
}
```

**Best Practices:**
- Always provide clear descriptions for outputs
- Describe what the output represents and how it can be used
- Include data type information when helpful
- Use consistent description formatting

---

### IO.008 - Variable Type Convention

**Rule Description:** All input variables must have a type field defined.

**Purpose:**
- Improves type safety and validation
- Prevents runtime type-related errors
- Enhances code documentation and clarity

**Good Example:**
```hcl
variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  default     = "test-vpc"
}

variable "subnet_count" {
  description = "Number of subnets to create"
  type        = number
  default     = 2
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
```

**Bad Example:**
```hcl
variable "vpc_name" {
  description = "The name of the VPC"
  # Missing type field
  default     = "test-vpc"
}

variable "subnet_count" {
  description = "Number of subnets to create"
  # Missing type field
  default     = 2
}
```

**Best Practices:**
- Always specify the type for all variables
- Use appropriate Terraform type constraints
- Consider using complex types (list, map, object) when appropriate
- Validate input types to prevent runtime errors

---

## Rule Ignoring and Customization

### Ignoring Specific Rules

In some cases, you may need to ignore specific rules. You can use the following methods:

1. **Command Line Arguments:**

```bash
# Ignore single rule
python3 terraform_lint.py --ignore-rules ST.001

# Ignore multiple rules
python3 terraform_lint.py --ignore-rules ST.001,DC.001,IO.002
```

2. **GitHub Actions Configuration:**

```yaml
- name: Terraform Lint
  uses: ./
  with:
    ignore-rules: 'ST.001,DC.001'
    exclude-paths: 'examples/*,test/*'
```

### Rule Extension

To add custom rules, please refer to the existing rule implementation patterns:

1. Add new check functions in the appropriate rule file
2. Register new check functions in the rule class
3. Update rule documentation and test cases

---

## Summary

These rules aim to improve the quality, consistency, and maintainability of Terraform code. Following these rules can:

- **Improve Code Quality:** Unified formatting and naming conventions
- **Enhance Readability:** Clear structure and comprehensive documentation
- **Facilitate Maintenance:** Modular design and standardized interfaces
- **Reduce Errors:** Strict variable management and validation
- **Team Collaboration:** Consistent code style and best practices

It is recommended to continuously use this checking tool during project development and adjust rule configurations
according to team needs.

