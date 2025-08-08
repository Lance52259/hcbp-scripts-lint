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

variable "data_disk_configurations" {
  description = "The data disk configurations for the ECS instance"
  type        = list(object({
    type = optional(string, "SSD")
    size = optional(number, 40)
  }))
}

variable "system_disk_type" {
  description = "The type of the system disk"
  type        = string
  default     = "SSD"
}

variable "system_disk_size" {
  description = "The size of the system disk"
  type        = number
  default     = 40
}

variable "bucket_name" {
  description = "The name of the OBS bucket"
  type        = string
}

variable "bucket_storage_class" {
  description = "The storage class of the OBS bucket"
  type        = string
  default     = "STANDARD"
}

variable "bucket_acl" {
  description = "The ACL of the OBS bucket"
  type        = string
  default     = "private"
}

variable "bucket_sse_algorithm" {
  description = "The SSE algorithm of the OBS bucket"
  type        = string
  default     = "kms"
}

variable "bucket_force_destroy" {
  description = "The force destroy of the OBS bucket"
  type        = bool
  default     = true
}

variable "bucket_tags" {
  description = "The tags of the OBS bucket"
  type        = map(string)
  default     = {}
}

variable "object_extension_name" {
  description = "The extension name of the OBS object to be uploaded"
  type        = string
  default     = ".txt"
  nullable    = false
}

variable "object_name" {
  description = "The name of the OBS object to be uploaded"
  type        = string
}

variable "object_upload_content" {
  description = "The content of the OBS object to be uploaded"
  type        = string
}
