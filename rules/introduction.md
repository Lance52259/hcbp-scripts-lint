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

### SC (Security Code) - Security Best Practices Rules
These rules enforce security best practices and prevent common security vulnerabilities in Terraform code. They focus on preventing runtime errors and ensuring safe handling of potentially empty arrays, lists, and other data structures.

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
resource "huaweicloud_vpc" "main" {
  name = "example-vpc"
  cidr = "10.0.0.0/16"
}

data "huaweicloud_availability_zones" "current" {
  region = "cn-north-1"
}

resource "huaweicloud_compute_instance" "example" {
  name      = "test-instance"
  flavor_id = "c6.large.2"
  image_id  = "ba10b6e8-de5d-4d96-b8c0-4d8e1d6c7890"
  vpc_id    = huaweicloud_vpc.main.id
}
```

**Correct Example:**

```hcl
# ✅ Correct: All instance names are "test"
resource "huaweicloud_vpc" "test" {
  name = "example-vpc"
  cidr = "10.0.0.0/16"
}

data "huaweicloud_availability_zones" "test" {
  region = "cn-north-1"
}

resource "huaweicloud_compute_instance" "test" {
  name      = "test-instance"
  flavor_id = "c6.large.2"
  image_id  = "ba10b6e8-de5d-4d96-b8c0-4d8e1d6c7890"
  vpc_id    = huaweicloud_vpc.test.id
}
```

**Best Practices:**
- Use "test" uniformly as instance name in example code and test environments
- Use more descriptive names in production environments
- Consider using variables to manage instance names for easy switching between environments

---

### ST.002 - Data Source Variable Default Value Check

**Rule Description:** All input variables used in data source blocks must be designed as optional parameters (with default values).

**Purpose:**
- Ensure data sources can work properly with minimal configuration
- Prevent runtime errors from undefined variables in data source queries
- Allow resources to use required variables while data sources use optional ones
- Improve configuration management for data source filtering

**Error Example:**

```hcl
# ❌ Error: Variable used in data source without default value
# variables.tf
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  # Missing default value but used in data source
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
  # No default - OK for resource use only
}

# main.tf
data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size    # Uses variable without default
}

resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name         # OK - resource can use required variables
}
```

**Correct Example:**

```hcl
# ✅ Correct: Data source variables have defaults, resource variables can be required
# variables.tf
variable "memory_size" {
  description = "The memory size (GB) for queried ECS flavors"
  type        = number
  default     = 8                  # Required because used in data source
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
  # No default - OK for resource use only
}

# main.tf
data "huaweicloud_compute_flavors" "test" {
  memory_size = var.memory_size    # Uses variable with default
}

resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name         # OK - resource can use required variables
}

# terraform.tfvars
instance_name = "my-instance"      # Required variable declared
```

**Best Practices:**
- Provide default values for all variables used in data source blocks
- Use appropriate default values that make sense for filtering/querying
- Required variables (without defaults) can still be used in resource blocks
- Document the purpose of default values in variable descriptions

---

### ST.003 - Parameter Alignment Format Convention

**Rule Description:** Parameter assignments in code blocks must maintain proper alignment formatting with equals signs
aligned to maintain one space from the longest parameter name.

**Purpose:**
- Improve code readability and aesthetics
- Maintain consistent code formatting with proper alignment
- Facilitate code review and maintenance
- Comply with Terraform community formatting standards

**Format Requirements:**
- Equals signs must be aligned within the same code block
- Aligned equals signs should maintain exactly one space from the longest parameter name in the code block
- Exactly one space after the equals sign and parameter value
- Parameters within the same code block (not separated by blank lines) should follow these alignment rules

**Error Example:**

```hcl
# ❌ Error: Improper alignment
resource "huaweicloud_vpc" "test" {
  name                   = "test-vpc"
  cidr                   = "192.168.0.0/16" # The equal sign is not aligned to the longest parameter name in the current code block
  enterprise_project_id  = "0"
}

# ❌ Error: Improper alignment and formatting
resource "huaweicloud_compute_instance" "test" {
  name="test-instance"                    # No spaces around equals
  flavor_id =c6.large.2                  # No space after equals, not aligned
  image_id            =  "ba10b6e8-de5d-4d96-b8c0-4d8e1d6c7890"  # Multiple spaces after equals, not aligned
  vpc_id        =    huaweicloud_vpc.test.id         # Inconsistent spacing, not aligned
  availability_zone="cn-north-1a"        # No spaces around equals, not aligned
}
```

**Correct Example:**

```hcl
# ✅ Correct: Proper alignment and formatting
resource "huaweicloud_compute_instance" "test" {
  name              = "test-instance"
  flavor_id         = "c6.large.2"
  image_id          = "ba10b6e8-de5d-4d96-b8c0-4d8e1d6c7890"
  vpc_id            = huaweicloud_vpc.test.id
  availability_zone = "cn-north-1a"

  tags = {
    Environment = "test"
    Purpose     = "example"
  }
}
```

**Alignment Rules:**
- Find the longest parameter name in the code block (e.g., "availability_zone" = 17 characters)
- All equals signs should align at position: base_indent + longest_parameter_name + 1 space
- In the example above: 2 spaces (indent) + 17 characters (longest name) + 1 space = column 20
- Shorter parameter names are padded with spaces to align their equals signs

**Best Practices:**
- Use `terraform fmt` command to automatically format code
- Configure Terraform formatting plugins in IDE
- Add format checking steps in CI/CD pipeline
- Use consistent formatting tools and configurations within the team
- Ensure proper alignment within each code block section

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

### ST.008 - Different Parameter Type Spacing Convention

**Rule Description:** There must be exactly one empty line between different types of parameters within the same resource or data source block.

**Purpose:**
- Provides clear visual separation between different parameter types
- Improves code structure and readability
- Maintains consistent parameter organization
- Ensures proper spacing between basic parameters and parameter blocks
- Ensures proper spacing between different-named parameter blocks

**Parameter Types:**
- **Basic Parameters**: Simple key-value assignments (e.g., `name = "value"`, `flavor_id = "c6.large.2"`)
- **Parameter Blocks**: Nested structures with braces (e.g., `data_disks { ... }`, `tags { ... }`)

**Spacing Requirements:**
1. Exactly one empty line between basic parameters and parameter blocks
2. Exactly one empty line between parameter blocks and basic parameters
3. Exactly one empty line between different-named parameter blocks
4. Comment lines do not count as empty lines

**Good Example:**
```hcl
resource "huaweicloud_compute_instance" "test" {
  name              = "test-instance"
  flavor_id         = "c6.large.2"
  image_id          = "image-123"
  system_disk_size  = 40

  data_disks {
    size = 40
    type = "SAS"
  }

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }

  tags = {
    Environment = "test"
  }
}
```

**Bad Example:**
```hcl
resource "huaweicloud_compute_instance" "test" {
  name              = "test-instance"
  flavor_id         = "c6.large.2"
  image_id          = "image-123"
  system_disk_size  = 40
  data_disks {      # Missing blank line between basic parameter and parameter block
    size = 40
    type = "SAS"
  }

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }
  tags = {          # Missing blank line between parameter block and basic parameter
    Environment = "test"
  }
}
```

**Additional Examples:**

*Missing blank line between basic parameters and parameter blocks:*
```hcl
resource "huaweicloud_compute_instance" "test" {
  name              = var.instance_name
  flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  system_disk_type  = "SAS"
  system_disk_size  = 40
  data_disks {        # ❌ Error: Missing blank line between basic parameter and parameter block
    size = 40
    type = "SAS"
  }

  tags = {
    "key" = "value"
  }
}
```

*Missing blank line between parameter blocks and basic parameters:*
```hcl
resource "huaweicloud_compute_instance" "test" {
  name              = var.instance_name
  flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  system_disk_type  = "SAS"
  system_disk_size  = 40

  data_disks {
    size = 40
    type = "SAS"
  }
  tags = {            # ❌ Error: Missing blank line between parameter block and basic parameter
    "key" = "value"
  }
}
```

*Comment lines handling:*
```hcl
resource "huaweicloud_compute_instance" "test" {
  name              = var.instance_name
  flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  system_disk_type  = "SAS"
  system_disk_size  = 40
  # This is a comment line - does not count as blank line
  data_disks {        # ❌ Error: Missing blank line (comment lines don't count as blank lines)
    size = 40
    type = "SAS"
  }
}
```

**Best Practices:**
- Always separate different parameter types with exactly one empty line
- Group related basic parameters together before parameter blocks
- Use consistent spacing throughout the resource definition
- Remember that comment lines do not count as blank lines for spacing purposes
- Consider the logical flow when organizing parameters: basic configuration first, then complex nested structures

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
  default     = "cn-north-1"
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
  default     = "cn-north-1"
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

### ST.010 - Resource, Data Source, Variable, and Output Quote Check

**Rule Description:** All data sources, resources, variables, and outputs must have their type and name (or just name
for variables/outputs) enclosed in double quotes.

**Purpose:**
- Ensures consistent Terraform syntax across all configurations
- Prevents syntax errors and improves code readability
- Maintains compatibility with Terraform formatting tools
- Follows Terraform community standards for all block declarations

**Error Example:**

```hcl
# ❌ Error: Missing quotes around various declaration types
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

# variables.tf - Variable quoting violations
variable test_var {
  description = "Variable without quotes"
  type        = string
  default     = "test"
}

variable 'single_quote_var' {
  description = "Variable with single quotes"
  type        = string
  default     = "test"
}

# outputs.tf - Output quoting violations
output test_output {
  description = "Output without quotes"
  value       = "test_value"
}

output 'single_quote_output' {
  description = "Output with single quotes"
  value       = "test_value"
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

# variables.tf - Proper variable quoting
variable "test_var" {
  description = "Variable with proper quotes"
  type        = string
  default     = "test"
}

variable "correct_var" {
  description = "Another variable with proper quotes"
  type        = string
  default     = "test"
}

# outputs.tf - Proper output quoting
output "test_output" {
  description = "Output with proper quotes"
  value       = "test_value"
}

output "correct_output" {
  description = "Another output with proper quotes"
  value       = "test_value"
}
```

**Best Practices:**
- Always use double quotes for resource/data source types and names
- Always use double quotes for variable and output names
- Maintain consistent quoting style throughout all Terraform files
- Use automated formatting tools like `terraform fmt` to ensure compliance
- Configure IDE/editor to highlight syntax violations

**Cross-references**: Works with [ST.001](#st001---resource-and-data-source-naming-convention),
                      [ST.003](#st003---parameter-assignment-formatting)

### ST.011 - Trailing Whitespace Check

**Rule Description:** All lines in Terraform files must not contain trailing whitespace characters (spaces, tabs, or
other whitespace) at the end of lines.

**Purpose:**
- Prevents unnecessary diff noise in version control systems
- Maintains clean and consistent code formatting
- Follows general coding best practices for all languages
- Ensures compatibility with automated formatting tools
- Reduces merge conflicts caused by inconsistent whitespace

**Error Example:**

```hcl
# ❌ Error: Lines with trailing whitespace
resource "huaweicloud_compute_instance" "test" { 
  name                 = "example"  
  instance_type        = "s6.large.2"	
  availability_zone    = "cn-north-4a"

  network {
    uuid = data.huaweicloud_vpc_subnet.test.id
  }
}

variable "region" {  
  description = "The region where resources will be created"
  type        = string
  default     = "cn-north-4"   
} 
```

**Correct Example:**

```hcl
# ✅ Correct: No trailing whitespace
resource "huaweicloud_compute_instance" "test" {
  name                 = "example"
  instance_type        = "s6.large.2"
  availability_zone    = "cn-north-4a"

  network {
    uuid = data.huaweicloud_vpc_subnet.test.id
  }
}

variable "region" {
  description = "The region where resources will be created"
  type        = string
  default     = "cn-north-4"
}
```

**Best Practices:**
- Configure your editor to automatically trim trailing whitespace on save
- Use `.editorconfig` files to standardize whitespace handling across team members
- Enable editor settings to visualize trailing whitespace
- Use automated formatting tools like `terraform fmt` which removes trailing whitespace
- Set up pre-commit hooks to prevent trailing whitespace from being committed

**Cross-references**: Works with [ST.004](#st004---indentation-character-check),
                      [ST.005](#st005---indentation-level-check)

### ST.012 - File Header and Footer Whitespace Check

**Rule Description:** Terraform files should not have empty lines before the first non-empty line and should have exactly one empty line after the last non-empty line.

**Purpose:**
- Ensures consistent file formatting across all Terraform files
- Prevents unnecessary leading whitespace that can affect readability
- Maintains proper file endings for version control systems
- Follows professional code formatting standards
- Reduces merge conflicts caused by inconsistent file formatting

**Error Example:**

```hcl
# ❌ Error: File has empty lines before first non-empty line
# ❌ Error: File has no empty line after last non-empty line

resource "huaweicloud_vpc" "test" {
  name = "example-vpc"
  cidr = "192.168.0.0/16"
}

# This is the last line without proper trailing empty line
```

**Correct Example:**

```hcl
# ✅ Correct: No empty lines before first non-empty line
resource "huaweicloud_vpc" "test" {
  name = "example-vpc"
  cidr = "192.168.0.0/16"
}

# This is the last line
[empty line]
```

**Best Practices:**
- Configure your editor to automatically add/remove leading/trailing empty lines
- Use `.editorconfig` files to standardize file formatting across team members
- Set up pre-commit hooks to ensure proper file formatting
- Use automated formatting tools that handle file whitespace consistently
- Maintain consistent file formatting across all Terraform files in the project

**Cross-references**: Works with [ST.011](#st011---trailing-whitespace-check)

---

## DC (Documentation/Comments) Rule Details

### DC.001 - Comment Format Convention

**Rule Description:** All comments must start with `#` character and maintain one English space between the `#` and the
                      comment text. Comments within HCL heredoc blocks (<<EOT, <<EOF, etc.) are excluded from validation.

**Purpose:**
- Ensure comment format consistency and readability
- Comply with Terraform community comment standards
- Improve code professionalism and maintainability
- Facilitate automated tool processing of comment content
- Avoid false positives when validating embedded scripts or configuration files in heredoc blocks

**Error Example:**

```hcl
# ❌ Error: Improper comment formatting
#This is an incorrect comment format              # No space
#  This comment has multiple spaces               # Multiple spaces
resource "huaweicloud_resource_group" "test" {
  name     = "example-resources"
  location = "cn-north-1"                         #No space in inline comment
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
resource "huaweicloud_resource_group" "test" {
  name     = "example-resources"
  location = "cn-north-1"              # Resource group location
}

# Define example variable
# Used to demonstrate proper variable definition
variable "example" {
  description = "An example variable"
  type        = string
  default     = "test"                 # Default value for test environment
}
```

**HCL Heredoc Example (comments inside are excluded from validation):**

```hcl
# ✅ Correct: Comments in heredoc blocks are excluded from DC.001 validation
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

**Best Practices:**
- Add explanatory comments for complex resource configurations
- Use comments in variable and output definitions to explain purposes
- Use comments to document important configuration decisions and limitations
- Keep comment content accurate and up-to-date
- Avoid over-commenting obvious code
- Comments within heredoc blocks (<<EOT, <<EOF, etc.) are automatically excluded from validation

---

## IO (Input/Output) Rule Details

### IO.001 - Variable Definition File Convention

**Rule Description:** Validates that each input variable is properly defined in the `variables.tf` file and not in other
files. Each variable definition found in non-`variables.tf` files will be reported as a separate violation with specific
line numbers.

**Purpose:**
- Maintain project structure consistency and clarity
- Facilitate centralized variable management and maintenance
- Improve code readability and maintainability
- Comply with Terraform community best practices
- Ensure precise error reporting for each misplaced variable

**Project Structure Example:**

```
terraform-project/
├── main.tf             # Main resource definitions (For best practice required)
├── variables.tf        # All variable definitions (For best practice required if variables are difined)
├── outputs.tf          # All output definitions (For best practice required if outputs are difined)
├── terraform.tfvars    # Variable value definitions (For best practice required if optional variables are difined)
└── versions.tf         # Provider version constraints
```

**Error Example:**

```hcl
# ❌ Error: Defining variables in main.tf
# main.tf
variable "resource_group_name" {    # Line 3: Variables should be in variables.tf
  description = "Name of the resource group"
  type        = string
  default     = "example-rg"
}

resource "huaweicloud_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}

variable "location" {               # Line 12: Variables should be in variables.tf
  description = "Huawei Cloud region"
  type        = string
  default     = "cn-north-1"
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
  description = "Huawei Cloud region for resources"
  type        = string
  default     = "cn-north-1"
}

# main.tf
resource "huaweicloud_resource_group" "test" {
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

### IO.002 - Output Definition File Organization Convention

**Rule Description:** Validates that each output variable is properly defined in the `outputs.tf` file and not in other
files. Each output definition found in non-`outputs.tf` files will be reported as a separate violation with specific
line numbers.

**Purpose:**
- Maintain project structure clarity and consistency within each directory
- Facilitate centralized output management and documentation
- Improve module interface readability
- Comply with Terraform community best practices
- Ensure outputs are organized at the appropriate directory level
- Provide precise error reporting for each misplaced output

**Error Example:**

```hcl
# ❌ Error: Outputs defined in main.tf instead of outputs.tf
# main.tf
resource "huaweicloud_resource_group" "test" {
  name     = var.resource_group_name
  location = var.location
}

output "resource_group_id" {          # Line 6: Should be in outputs.tf
  description = "The ID of the created resource group"
  value       = huaweicloud_resource_group.test.id
}

output "resource_group_name" {        # Line 11: Should be in outputs.tf
  description = "The name of the created resource group"
  value       = huaweicloud_resource_group.test.name
}

# outputs.tf
# No output definitions - outputs incorrectly placed in main.tf
```

**Correct Example:**

```hcl
# ✅ Correct: Outputs defined in outputs.tf
# outputs.tf
output "resource_group_id" {
  description = "The ID of the created resource group"
  value       = huaweicloud_resource_group.test.id
}

output "resource_group_name" {
  description = "The name of the created resource group"
  value       = huaweicloud_resource_group.test.name
}

# main.tf
resource "huaweicloud_resource_group" "test" {
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

### IO.003 - Required Variable Declaration Check in terraform.tfvars

**Rule Description:** Validates that all required variables (variables without default values) are declared in the
`terraform.tfvars` file. Each missing variable declaration is reported individually with precise line numbers.

**Purpose:**
- Ensure all required variables have explicit value definitions
- Provide clear configuration entry points
- Facilitate configuration management for different environments
- Avoid runtime variable undefined errors
- Ensure precise error reporting for each missing variable declaration

**Error Example:**

```hcl
# ❌ Error: Missing required variable values in terraform.tfvars
# main.tf
variable "cpu_cores" {            # Line 2: Required variable missing from tfvars
  description = "Number of CPU cores"
  type        = number
  # No default value, this is a required variable
}

variable "memory_size" {          # Line 8: Required variable missing from tfvars
  description = "Memory size in GB"
  type        = number
  # No default value, this is a required variable
}

variable "flavor_id" {            # Line 14: Optional variable
  description = "The flavor ID"
  type        = string
  default     = "c6.2xlarge.4"   # Has default - optional
}

# terraform.tfvars
# Missing declarations for required variables cpu_cores and memory_size
flavor_id = "c6.4xlarge.8"       # Optional variable declared (not required)
```

**Correct Example:**

```hcl
# ✅ Correct: All required variables declared in terraform.tfvars
# variables.tf
variable "cpu_cores" {
  description = "Number of CPU cores"
  type        = number
  # No default - required
}

variable "memory_size" {
  description = "Memory size in GB"
  type        = number
  # No default - required
}

variable "flavor_id" {
  description = "The flavor ID"
  type        = string
  default     = "c6.2xlarge.4"   # Has default - optional
}

# terraform.tfvars
cpu_cores = 4                     # Required variable declared
memory_size = 8                   # Required variable declared
# flavor_id is optional, no need to declare (but can be overridden)
```

**Best Practices:**
- Create a `terraform.tfvars` file for all required variables
- Provide example values in `terraform.tfvars.example`
- Use environment-specific `.tfvars` files for different environments
- Document all required variables and their expected values
- Consider using variable validation blocks
- Ensure each required variable is declared individually in `terraform.tfvars`

---

### IO.004 - Variable Naming Convention Check

**Rule Description:** Validates that each input variable name uses only lowercase letters and underscores, and does not
start with an underscore. For each invalid variable definition, an error is reported showing the file where the variable
is defined (e.g., if an invalid variable is defined in main.tf, the error file will show as main.tf).

**Purpose:**
- Ensure consistent variable naming patterns across all input variables
- Improve code readability and maintainability
- Prevent naming conflicts and confusion
- Comply with Terraform community naming standards
- Provide precise error identification for each invalid variable name with accurate file location reporting

**Error Example:**

```hcl
# ❌ Error: Invalid variable naming in main.tf
# main.tf
variable "_invalid_name" {    # Error: Starts with underscore
  description = "Invalid variable name"
  type        = string
}

variable "InvalidName" {      # Error: Contains uppercase letters
  description = "Invalid variable name"
  type        = string
}

variable "invalid-name" {     # Error: Contains hyphen
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

variable "instance_count" {
  description = "Valid variable name with descriptive purpose"
  type        = number
}
```

**Best Practices:**
- Use lowercase letters and underscores only
- Never start variable names with underscores
- Use descriptive but concise names
- Follow consistent naming patterns across the project
- Consider using prefixes for related variables (e.g., `vpc_name`, `vpc_cidr`)
- Each variable naming violation is reported individually for precise error identification
- Error messages show the exact file where the variable is defined

---

### IO.005 - Output Naming Convention Check

**Rule Description:** Validates that each output variable name uses only lowercase letters and underscores, and does not
start with an underscore. For each invalid output definition, an error is reported showing the file where the output
is defined (e.g., if an invalid output is defined in main.tf, the error file will show as main.tf).

**Purpose:**
- Ensure consistent output naming patterns across all output variables
- Improve module interface clarity and readability
- Maintain consistent output naming standards
- Comply with Terraform community naming standards
- Provide precise error identification for each invalid output name with accurate file location reporting

**Error Example:**

```hcl
# ❌ Error: Invalid output naming in main.tf
# main.tf
output "_invalid_output" {    # Error: Starts with underscore
  description = "Invalid output name"
  value       = "test"
}

output "BadOutputName" {      # Error: Contains uppercase letters
  description = "Invalid output name"
  value       = "test"
}

output "invalid-output" {     # Error: Contains hyphen
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

output "instance_id" {
  description = "Valid output name with descriptive purpose"
  value       = "instance-123"
}
```

**Best Practices:**
- Use lowercase letters and underscores only
- Never start output names with underscores
- Use descriptive but concise names
- Follow consistent naming patterns across the project
- Consider using prefixes for related outputs (e.g., `vpc_id`, `vpc_cidr`)
- Each output naming violation is reported individually for precise error identification
- Error messages show the exact file where the output is defined

---

### IO.006 - Variable Description Convention

**Rule Description:** The input variables must have a description field defined and not empty.

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

### IO.007 - Output Description Check

**Rule Description:** All output variables must have a description field defined and not empty.

**Purpose:**
- Improve module documentation and usability
- Ensure outputs are properly documented for users
- Provide clear explanations of output purposes and values
- Enhance code maintainability and team collaboration

**Error Example:**

```hcl
# ❌ Error: Missing or empty description fields
output "instance_id" {
  value = huaweicloud_compute_instance.test.id
  # Missing description field
}

output "vpc_cidr_block" {
  description = ""  # Empty description
  value       = huaweicloud_vpc.test.cidr
}

output "resource_tags" {
  description = "   "  # Whitespace only description
  value       = local.common_tags
}
```

**Correct Example:**

```hcl
# ✅ Correct: Outputs with proper descriptions
output "instance_id" {
  description = "The ID of the created ECS instance"
  value       = huaweicloud_compute_instance.test.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the created VPC"
  value       = huaweicloud_vpc.test.cidr
}

output "resource_tags" {
  description = "Common tags applied to all resources"
  value       = local.common_tags
}
```

**Best Practices:**
- Always include meaningful descriptions for all outputs
- Keep descriptions concise but informative
- Explain what the output represents and its intended use
- Avoid empty or whitespace-only descriptions
- Use consistent description formatting across the module

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

### IO.009 - Unused Variable Detection

**Rule Description:** Detects variables defined in variables.tf but not referenced in any Terraform files within the same directory.

**Purpose:**
- Identifies dead code and unused variable definitions
- Helps maintain clean and efficient variable management
- Reduces configuration file complexity
- Improves code maintainability and readability

**Good Example:**
```hcl
# variables.tf
variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  default     = "test-vpc"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# main.tf
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = var.vpc_name  # ✅ Variable is used
  }
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = var.instance_type  # ✅ Variable is used
  
  tags = {
    Name = "WebServer"
  }
}
```

**Bad Example:**
```hcl
# variables.tf
variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  default     = "test-vpc"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "unused_variable" {
  description = "This variable is never used"
  type        = string
  default     = "unused-value"
}

# main.tf
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = var.vpc_name  # ✅ Variable is used
  }
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = var.instance_type  # ✅ Variable is used
  
  tags = {
    Name = "WebServer"
  }
}

# ❌ Error: Variable 'unused_variable' is defined but never used
```

**Smart Exclusions:**
The rule automatically excludes common provider-related variables that may be used by the provider but not explicitly referenced in configuration files:
- Provider configuration variables (e.g., `region`, `access_key`, `secret_key`)
- Authentication-related variables (e.g., `token`, `key_file`, `tenant_id`)
- Environment-specific variables (e.g., `endpoint`, `domain_id`, `project_id`)

**Best Practices:**
- Regularly review and remove unused variable definitions
- Keep variable definitions focused on actual usage requirements
- Use descriptive variable names to indicate their purpose
- Consider moving rarely-used variables to separate configuration files
- Document variables that may appear unused but serve specific purposes

**Error Output Format:**
```
ERROR: variables.tf (15): [IO.009] Variable 'unused_variable' is defined but not used in any Terraform files
```

---

## SC (Security Code) Rule Details

### SC.001 - Array Index Access Safety Check

**Rule Description:** Validates that array index access operations use try() function to prevent index out of bounds errors in specific scenarios.

**Purpose:**
- Prevent runtime errors from array index out of bounds
- Ensure safe handling of data source query results
- Promote defensive programming practices for list variable access
- Validate safe usage of HCL for expressions with array indexing
- Improve Terraform configuration reliability

**Scenarios Covered:**
1. **Data Source List Attribute References**: Data source returns empty list when no matching resources found
2. **Optional List Parameter Element References**: Optional input variables might be empty lists
3. **For Expressions in Local Variables**: For expressions generating dynamic lists that could be empty

**Error Example:**

```hcl
# ❌ Error: Unsafe array index access
# variables.tf
variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
  default     = []  # Could be empty
}

# main.tf
data "huaweicloud_compute_flavors" "test" {
  vcpus = 2
}

locals {
  queried_availability_zones = [for az in data.huaweicloud_availability_zones.test.names : az if az != "cn-north-1c"]
}

resource "huaweicloud_compute_instance" "test" {
  name              = "test-instance"
  flavor_id         = data.huaweicloud_compute_flavors.test.flavors[0].id          # Unsafe: might be empty
  subnet_id         = var.subnet_ids[0]                                            # Unsafe: variable might be empty
  availability_zone = local.queried_availability_zones[0]                          # Unsafe: for expression might be empty
}
```

**Correct Example:**

```hcl
# ✅ Correct: Safe array index access with try() function
# variables.tf
variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
  default     = []  # Could be empty
}

variable "default_subnet_id" {
  description = "Default subnet ID when subnet_ids is empty"
  type        = string
  default     = "default-subnet-123"
}

# main.tf
data "huaweicloud_compute_flavors" "test" {
  vcpus = 2
}

locals {
  queried_availability_zones = [for az in data.huaweicloud_availability_zones.test.names : az if az != "cn-north-1c"]
}

resource "huaweicloud_compute_instance" "test" {
  name              = "test-instance"
  flavor_id         = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.large.2")          # Safe with fallback
  subnet_id         = try(var.subnet_ids[0], var.default_subnet_id)                                   # Safe with fallback
  availability_zone = try(local.queried_availability_zones[0], "cn-north-1a")                         # Safe with fallback
}
```

**Best Practices:**
- Always use try() function when accessing array elements that might not exist
- Provide meaningful fallback values for try() functions
- Consider using length() function to check array size before accessing elements
- Design data structures to avoid empty array scenarios when possible
- Use conditional expressions combined with try() for complex scenarios

**Alternative Safe Patterns:**

```hcl
# Pattern 1: Length check before access
resource "huaweicloud_compute_instance" "test" {
  flavor_id = length(data.huaweicloud_compute_flavors.test.flavors) > 0 ? 
              data.huaweicloud_compute_flavors.test.flavors[0].id : 
              "c6.large.2"
}

# Pattern 2: Using coalescelist for array handling
resource "huaweicloud_compute_instance" "test" {
  subnet_id = coalescelist(var.subnet_ids, [var.default_subnet_id])[0]
}

# Pattern 3: Using try() with multiple fallbacks
resource "huaweicloud_compute_instance" "test" {
  availability_zone = try(
    local.queried_availability_zones[0],
    data.huaweicloud_availability_zones.test.names[0],
    "cn-north-1a"
  )
}
```

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
