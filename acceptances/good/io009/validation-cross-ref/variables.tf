variable "min_count" {
  description = "Lower bound; only referenced from max_count validation"
  type        = number
  default     = 1
}

variable "max_count" {
  description = "Upper bound used by main.tf and validated against min_count"
  type        = number
  default     = 3

  validation {
    condition     = var.max_count >= var.min_count
    error_message = "max_count must be greater than or equal to min_count"
  }
}
