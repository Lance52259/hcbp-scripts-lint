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

  type    = string
  default = ""
}

variable "vpc_cidr" {
  description = "The CIDR block of the VPC resource"

  type    = string
  default = ""
}

variable "vpc_description" {
  description = "The description of the VPC resource"

  type    = string
  default = ""
}

variable "vpc_secondary_cidrs" {
  description = "The secondary CIDR blocks of the VPC resource"

  type     = list(string)
  default  = []
}

variable "vpc_tags" {
  description = "The key/value pairs to associte with the VPC resource"

  type     = map(string)
  default  = {}
}

variable "enterprise_project_id" {
  description = "Used to specify whether the resource is created under the enterprise project (this parameter is only valid for enterprise users)"

  type    = string
  default = ""
}
