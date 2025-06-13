# Variable definitions

variable "region" {
  description = "The region where the resources are located"
  type        = string
  default     = "cn-north-1"
}

variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  default     = "test-vpc"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "environment" {
  description = "The environment where the resources are located"
  type        = string
  default     = "dev"
}

variable "subnet_name" {
  description = "The name of the subnet"
  type        = string
  default     = "test-subnet"
}

variable "subnet_cidr" {
  description = "The CIDR block for the subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "gateway_ip" {
  description = "The IP address of the gateway"
  type        = string
  default     = "10.0.1.1"
}
