variable "api_token" {
  description = "API access token"
  type        = string
  sensitive   = true
}

variable "access_key" {
  description = "The access key of the IAM user"
  type        = string
  sensitive   = true
}

variable "user_password" {
  description = "User password"
  type        = string
  sensitive   = true
}
