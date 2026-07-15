variable "access_key" {
  description = "Empty default is allowed"
  type        = string
  sensitive   = true
  default     = ""
}

variable "secret_key" {
  description = "Null default is allowed"
  type        = string
  sensitive   = true
  default     = null
}
