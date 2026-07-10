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
variable "vpc_configurations" {
  description = "The configuration for the VPC resources"
  type        = list(object({
    name = string
    cidr = string
  }))
  default     = [
    {
      name = "tf_default_vpc"
      cidr = "192.168.0.0/16"
    },
    {
      name = "tf_test_vpc"
      cidr = "192.168.1.0/16"
    }
  ]
}
