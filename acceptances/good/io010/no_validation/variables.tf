variable "subnet_name" {
  description = "The name of the subnet"
  type        = string
}

variable "instance_name" {
  description = "The name of the ECS instance"
  type        = string
  default     = "example"
}
