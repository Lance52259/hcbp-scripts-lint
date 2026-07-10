variable "example_b" {
  description = "Example variable missing error_message"
  type        = string

  validation {
    condition = length(var.example_b) > 0
  }
}
