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
