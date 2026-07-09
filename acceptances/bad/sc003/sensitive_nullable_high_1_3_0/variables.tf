variable "region_name" {
  description = "The region name"
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

variable "enterprise_project_id" {
  description = "The enterprise project ID"
  type        = string
  default     = ""
  nullable    = false
}
