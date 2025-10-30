
# ST.012 Error: This file has a empty line before the first non-empty line
# Variables definition
variable "availability_zone" {
  description = "The availability zone where the resources will be created"
  type        = string
  default     = ""
}

# ST.010 Error: Variable name is without quotes
variable instance_flavor_performance_type {
  description = "The performance type of the flavor that ECS instance will use"
  # ST.003 Error: Missing space after equals sign
  # ST.003 Error: Equals sign not aligned
  type =string
  # ST.003 Error: Equals sign not aligned
  default = "normal"
}
# ST.006 Error: Missing blank line between variable blocks
# ST.010 Error: Variable name is with single quotes
variable "instance_flavor_cpu_core_number" {
  # ST.003 Error: Equals sign not aligned
  description= "The CPU core number of the flavor that ECS instance will use" # Only fixed space error, the equals sign alignment error will be reported in the next line
  # ST.003 Error: Missing space after equals sign
  # ST.003 Error: Equals sign not aligned
  type       =number
  # ST.003 Error: Multiple spaces after equals sign
  # ST.003 Error: Equals sign not aligned
  default    =   2
}


# ST.006 Error: Too many blank lines between variable blocks
variable "instance_flavor_memory_size" {
  # IO.008 Error: Variable missing type field
  description = "The memory size of the flavor that ECS instance will use"
  default     = 4
}

# ST.002 Error: Variable used in data source must have default value
variable "instance_image_id" {
  description = "The ID of the image that ECS instance will use"
  type        = string
}

# ST.009 Error: Variable order mismatch - instance_image_os should come after instance_image_visibility based on main.tf usage
variable "instance_image_os" {
  description = "The operating system of the image that ECS instance will use"
  type        = string
  default     = "Ubuntu"
}

# ST.009 Error: Variable order mismatch - instance_image_visibility should come before instance_image_os based on main.tf usage
variable "instance_image_visibility" {
  description = "The visibility of the image that ECS instance will use"
  type        = string
  default     = "public"
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
  default     = ""
}

variable "vpc_name" {
  description = "The name of the VPC"
  type        = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]+$", var.vpc_name))
    error_message = "VPC name must contain only alphanumeric characters, underscores, and hyphens."
  }
}

variable "vpc_cidr" {
  description = "The CIDR of the VPC"
  type        = string
}

variable "subnet_name" {
  description = "The name of the VPC subnet"
  type        = string
}

variable "security_group_name" {
  description = "The name of the security group"
  type        = string
}

variable "instance_name" {
  description = "The name of the ECS instance"
  # ST.004 Error: This line uses tab instead of spaces
	type        = string
}

variable "data_disks_configurations" {
  # ST.003 Error: Missing space after equals sign
  description ="The data disk configurations for the ECS instance"
  # ST.003 Error: Equals sign not aligned
  type       = list(object({
    # ST.003 Error: Missing space after equals sign
    # ST.003 Error: Equals sign not aligned
    type=optional(string, "SSD")
    # ST.003 Error: Too many spaces after equals sign
    size         =  optional(number, 40)
    extend_param = optional(map(string), {})
  }))
  # ST.003 Error: Equals sign not aligned
  default = [
    {
      type = "SATA"
      size = 40

      extend_param = {
        # ST.003 Error: Equals sign not aligned
        "format" = "ext4"
        "partition_size" = 10
      }
    },
    {
      type = "SSD"
     size  = 40 # ST.005 Error: 5 spaces found, not 6 spaces
    },
    {
      # ST.003 Error: Equals sign not aligned
      type= "SAS"
      # ST.003 Error: Missing space after equals sign
      size =80
    },
    {
      # ST.003 Error: Equals sign not aligned
      type = "SSD"
      # ST.003 Error: Equals sign not aligned
      size = 120
      extend_param = {
        "format"         = "ext4"
        "partition_size" = 10
      }
    }
  ]
}

variable "custom_tags" {
  description = "The custom tags of the ECS instance"
  type        = map(string)
}

variable "volumes_configurations" {
  description = "The volumes configurations for the ECS instance"
  type        = list(object({
    type = string
    size = number
  }))

  default = [
    {
      type = "SSD"
      size = 40
    }
  ]
}

# IO.004 Error: Variable name starts with underscore
variable "_variable_starts_with_underscore" {
# IO.006 Error: Variable block without description
  type    = string
  default = "incorrect_variable_naming"
}

variable "BadVariableName" {
# IO.006 Error: Variable block has an empty description
  description = ""
  type        = string
  default     = "incorrect_variable_naming"
}
# ST.012 Error: This file has multiple empty lines after the last non-empty line

variable "eip_address" {
  description = "The address of the EIP"
  type        = string
}

variable "instance_configurations" {
  description = "The list of configurations for multiple Kafka instances"

  type = list(object({
    name               = string
    availability_zones = optional(list(string), [])
    engine_version     = optional(string, "3.x")
    flavor_id          = optional(string, "")
    flavor_type        = optional(string, "cluster")

    optional = optional(object({
      private_ip  = optional(string, "")
      eip_address = optional(string, "")

      sub_optional = optional(object({
        private_ip  = optional(string, "")
        eip_address = optional(string, "")
      }), {})
    }), {})
  }))

  default = [
    {
      name               = "instance_1"
      availability_zones = ["cn-north-1a", "cn-north-1b"]
      engine_version     = "3.x"
      flavor_id          = "c6.large.4"
      flavor_type        = "cluster"
    }
  ]
}
