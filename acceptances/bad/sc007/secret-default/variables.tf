variable "api_token" {
  description = "Dangerous non-empty default"
  type        = string
  sensitive   = true
  default     = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake"
}
