# Error 4: Variable missing default value
variable "region" {
  description = "The region where the resources are located"
  type        = string
}

variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  default     = ""
}

# Error 5: Variable missing default value
variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
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
