variable "a" {
  description = "Defined first but first-used second"
  type        = string
  default     = "a"
}

variable "b" {
  description = "Defined second but first-used first in extra.tf"
  type        = string
  default     = "b"
}
