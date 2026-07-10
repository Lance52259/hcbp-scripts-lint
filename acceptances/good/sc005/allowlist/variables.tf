variable "auth_type" {
  description = "Authentication type"
  type        = string
  default     = "token"
}

variable "authorization_mode" {
  description = "Authorization mode"
  type        = string
  default     = "iam"
}
