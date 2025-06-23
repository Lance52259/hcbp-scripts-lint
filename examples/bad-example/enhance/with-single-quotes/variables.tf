# Variables definition

# ST.010 Error: Variable name is without quotes
variable 'instance_flavor_performance_type' {
  # ST.003 Error: Equals signs not aligned while variable name is without quotes
  description = "The performance type of the flavor that ECS instance will use"
  type =string
  default = "normal"
}
# ST.006 Error: Missing blank line between variable blocks
variable 'instance_flavor_cpu_core_number' {
  description= "The CPU core number of the flavor that ECS instance will use" # ST.003 Error: Missing space before equals sign
  type       =number  # ST.003 Error: No space after equals sign
  default    =   2    # ST.003 Error: Multiple spaces after equals sign
}


# ST.006 Error: Too many blank lines between variable blocks
variable 'instance_flavor_memory_size' {
  # IO.008 Error: Variable missing type field
  description = "The memory size of the flavor that ECS instance will use"
  default     = 4
}

# ST.002 Error: Variable used in data source must have default value
variable 'instance_image_id' {
  description = "The ID of the image that ECS instance will use"
  type        = string
}

# ST.009 Error: Variable order mismatch - instance_image_os should come after instance_image_visibility based on main.tf usage
variable 'instance_image_os' {
  description = "The operating system of the image that ECS instance will use"
  type        = string
  default     = "Ubuntu"
}

# ST.009 Error: Variable order mismatch - instance_image_visibility should come before instance_image_os based on main.tf usage
variable 'instance_image_visibility' {
  description = "The visibility of the image that ECS instance will use"
  type        = string
  default     = "public"
}

variable 'vpc_name' {
  description = "The name of the VPC"
  type        = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]+$", var.vpc_name))
    error_message = "VPC name must contain only alphanumeric characters, underscores, and hyphens."
  }
}

variable 'vpc_cidr' {
  # IO.006 Error: Variable missing description field
  type = string
}

variable 'subnet_name' {
  description = "The name of the VPC subnet"
  type        = string
}

variable 'security_group_name' {
  description = "The name of the security group"
  type        = string
}

variable 'instance_name' {
  description = "The name of the ECS instance"
  type        = string
}

variable 'custom_tags' {
  description = "The custom tags of the ECS instance"
  type        = map(string)
}

# IO.004 Error: Variable name starts with underscore
variable '_variable_starts_with_underscore' {
  description = "Variable name starts with underscore"
  type        = string
  default     = "incorrect_variable_naming"
}

# IO.004 + IO.006 Error: Variable with uppercase and empty description
variable 'BadVariableName' {
  description = ""
  type        = string
  default     = "incorrect_variable_naming"
}

# IO.004 Error: Variable name contains hyphens  
variable 'invalid-hyphen-var' {
  description = "Variable with hyphens in name"
  type        = string
  default     = "test"
}

# IO.004 Error: Variable name contains uppercase letters
variable 'MixedCaseVariable' {
  description = "Variable with mixed case"
  type        = string
  default     = "test"
}

# IO.006 Error: Variable missing description field completely
variable 'missing_description_completely' {
  type = string
  default = "test"
}

# IO.008 Error: Variable missing type field completely
variable 'missing_type_completely' {
  description = "Variable without type field"
  default = "test"
}
