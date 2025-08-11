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
variable "name_prefix" {
  description = "The prefix of the VPC name"
  type        = string
  default     = ""
}

variable "vpc_name" {
  description = "The name of the VPC resource"

  type    = string
  default = ""

  validation {
    condition     = !(var.vpc_name == "" && var.name_prefix == "")
    error_message = "Either vpc_name or name_prefix must be provided."
  }
}

variable "vpc_cidr" {
  description = "The CIDR block of the VPC resource"

  type    = string
  default = ""
}
