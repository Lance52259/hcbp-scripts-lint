variable "example_e" {
  description = "Example variable with trivial error_message"
  type        = string

  validation {
    condition     = length(var.example_e) > 0
    error_message = "example_e"
  }
}
