variable "b" {
  description = "Second variable in wrong definition order"
  type        = string
  default     = "b"
}

variable "a" {
  description = "First variable by usage order"
  type        = string
  default     = "a"
}
