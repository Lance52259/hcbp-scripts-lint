# Variable definitions

variable "region" {
  description = "The region where the resources are located"
  type        = string
  default     = "cn-north-1"
  validation {
    condition = contains([
      "cn-north-1", "cn-north-4", "cn-east-2", "cn-east-3", 
      "cn-south-1", "cn-southwest-2", "ap-southeast-1", 
      "ap-southeast-2", "ap-southeast-3"
    ], var.region)
    error_message = "Region must be a valid Huawei Cloud region."
  }
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
  validation {
    condition     = contains(["dev", "test", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, staging, prod."
  }
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
