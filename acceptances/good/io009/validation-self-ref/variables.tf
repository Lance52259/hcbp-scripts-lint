variable "vpc_name" {
  description = "Used in main.tf and self-referenced in validation"
  type        = string
  default     = "demo"

  validation {
    condition     = length(var.vpc_name) > 0
    error_message = "vpc_name must not be empty"
  }
}
