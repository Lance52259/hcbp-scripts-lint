variable "example_d" {
  description = "Example variable with multiple validation blocks"
  type        = string

  validation {
    condition     = length(var.example_d) > 0
    error_message = "The example_d value must not be an empty string."
  }

  validation {
    error_message = "Second validation block is missing condition field."
  }
}
