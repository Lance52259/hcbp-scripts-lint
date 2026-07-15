variable "max_count" {
  description = "Validation references undeclared min_count"
  type        = number
  default     = 3

  validation {
    condition     = var.max_count >= var.min_count
    error_message = "max_count must be greater than or equal to min_count"
  }
}
