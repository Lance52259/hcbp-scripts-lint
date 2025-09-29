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

variable "subnets_configuration" {
  description = "The configuration for the subnet resources to which the VPC belongs"

  type = list(object({
    name         = string
    cidr         = string
    gateway_ip   = optional(string, "")
    description  = optional(string, "")
    ipv6_enabled = optional(bool, null)
    dhcp_enabled = optional(bool, null)
    dns_list     = optional(list(string), [])
    tags         = optional(map(string), {})
  }))
  default  = []
  nullable = false
}
