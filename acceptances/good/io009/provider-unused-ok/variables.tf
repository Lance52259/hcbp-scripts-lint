variable "region_name" {
  description = "Provider region; may be unused in module body"
  type        = string
}

variable "project_id" {
  description = "Provider project id; may be unused in module body"
  type        = string
}

variable "access_key" {
  description = "Provider access key; may be unused in module body"
  type        = string
  sensitive   = true
}
