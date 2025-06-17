# Error 4: Variable missing default value
variable "region" {
  description = "The region where the resources are located"
  type        = string
}

# ST.009 Error: Variable order mismatch - vpc_cidr should come before vpc_name based on main.tf usage
variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
}

variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  default     = ""
}

variable "subnet_name" {
  description = "The name of the subnet"
  type        = string
  default     = ""
}

# Error 6: Variable missing default value
variable "subnet_cidr" {
  description = "The CIDR block for the subnet"
  type        = string
}

variable "missing_variable" {
  description = "This variable won't be in tfvars"
  type        = string
  default     = "default_value"
}

variable "description" {
  description = "The description of the resource"
  type        = string
  default     = "test description"
}

# IO.006 Error: Variable missing description field
variable "no_description_var" {
  type    = string
  default = "test"
}

# IO.006 Error: Variable with empty description
variable "empty_description_var" {
  description = ""
  type        = string
  default     = "test"
}

# IO.008 Error: Variable missing type field
variable "no_type_var" {
  description = "Variable without type field"
  default     = "test"
}

# IO.004 Error: Variable name contains uppercase letters
variable "BadVariableName" {
  description = "Variable with uppercase letters in name"
  type        = string
  default     = "test"
}

# IO.004 Error: Variable name starts with underscore
variable "_underscore_start" {
  description = "Variable name starts with underscore"
  type        = string
  default     = "test"
}

# ST.002 Error: Variables used in data source must have default values
variable "cpu_cores" {
  description = "CPU core count for compute flavors"
  type        = number
  # Missing default value but used in data source
}

variable "memory_size" {
  description = "Memory size for compute flavors"
  type        = number
  # Missing default value but used in data source
}
