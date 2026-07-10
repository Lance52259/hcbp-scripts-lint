variable "example_a" {
  description = "Example variable missing condition"
  type        = string

  validation {
    error_message = "Value is invalid because condition is missing."
  }
}
