variable "api_token" {
  description = "API access token"
  type        = string
}

variable "private_key_pem" {
  description = "TLS private key in PEM format"
  type        = string
}

variable "db_credentials" {
  description = "Database credentials"
  type        = string
}

variable "iam_auth_key" {
  description = "IAM authentication key"
  type        = string
}

variable "email" {
  description = "User email address"
  type        = string
}
