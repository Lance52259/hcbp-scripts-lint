# Variable definitions for authentication
variable "region_name" {
  description = "The region where the ECS instance is located"
  type        = string
}

variable "access_key" {
  description = "The access key of the IAM user"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "The secret key of the IAM user"
  type        = string
  sensitive   = true
}

# Variable definitions for resources/data sources
variable "vpc_name" {
  description = "The name of the VPC resource"

  type     = string
  default  = ""
  nullable = false
}

variable "vpc_cidr" {
  description = "The CIDR block of the VPC resource"

  type    = string
  default = "192.168.0.0/16"
  nullable = false
}
