# Variable definitions for authentication
variable "region_name" {
  description = "The region where the ECS instance is located"
  type        = string
}

variable "access_key" {
  description = "The access key of the IAM user"
  type        = string
}

variable "secret_key" {
  description = "The secret key of the IAM user"
  type        = string
}

# Variable definitions for resources/data sources
variable "vpc_name" {
  description = "The name of the VPC"
  type        = string

  validation {
    condition = can(regex("^[a-zA-Z0-9_-]+$", var.vpc_name))
    error_message = "VPC name must contain only alphanumeric characters, underscores, and hyphens."
  }
}

# Optional variable and using supported default value
variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "192.168.0.0/16"
}

# Optional variable and supports default value (do not use default value in production)
variable "environment" {
  description = "The environment where the resources are located"
  type        = string
  default     = "dev"
}

variable "subnet_name" {
  description = "The name of the subnet"
  type        = string
}

variable "security_group_name" {
  description = "The name of the security group"
  type        = string
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
}

variable "instance_user_data" {
  description = "The user data for the ECS instance"
  type        = string
  default     = ""
}
