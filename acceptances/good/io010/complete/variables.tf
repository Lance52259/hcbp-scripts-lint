variable "vpc_name" {
  description = "The name of the VPC"
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]+$", var.vpc_name))
    error_message = "VPC name must contain only alphanumeric characters, underscores, and hyphens."
  }
}

variable "subnet_name" {
  description = "The name of the subnet"
  type        = string
}
