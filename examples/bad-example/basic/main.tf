# Terraform configuration example that violates the standards

locals {
  system_tags = {
    "Environment" = "Development"
  }
}
# ST.001 Error: Data source name is not "test"
# ST.006 Error: Missing blank line between local variable block and data source block
# ST.010 Error: Missing quotes around data source type
data huaweicloud_availability_zones "myaz" {}
# ST.006 Error: Missing blank line between data source blocks
data "huaweicloud_availability_zones" test {}


# ST.006 Error: Too many blank lines between data source blocks
data "huaweicloud_compute_flavors" test {
  count = var.instance_flavor_id == "" ? 1 : 0

  # ST.003 Error: Equals signs not aligned
  performance_type = var.instance_flavor_performance_type
  cpu_core_count   = var.instance_flavor_cpu_core_number
  memory_size      = var.instance_flavor_memory_size
}

data "huaweicloud_images_images" "test" {
  count = var.instance_image_id == "" ? 1 : 0

  # ST.003 Error: Missing space before equals sign
  flavor_id= var.instance_flavor_id == "" ? try(data.huaweicloud_compute_flavors.test.flavors[0].id, null) : var.instance_flavor_id
  visibility =var.instance_image_visibility    # ST.003 Error: No space after equals sign
  os         =   var.instance_image_os         # ST.003 Error: Multiple spaces after equals sign
}
# ST.001 Error: Resource name is not "test"
# ST.006 Error: Missing blank line between data source block and resource block
# ST.010 Error: Missing quotes around resource type
resource huaweicloud_vpc "incorrect_resource_name" {
  name        = var.incorrect_vpc_name    # IO.001 Error: Missing variable definition in variables.tf file
  cidr        = var.vpc_cidr
  description = "The resource name is incorrect, should be 'test'"
}
# ST.006 Error: Missing blank line between resource blocks
resource huaweicloud_vpc "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr
}


# ST.006 Error: Too many empty lines between resource blocks
# ST.010 Error: Missing quotes around resource name
#The subnet resource definition (DC.001 Error: Incorrect comment format, missing space after # character)
resource "huaweicloud_vpc_subnet" test {
	vpc_id     = huaweicloud_vpc.incorrect_resource_name.id    # ST.004 Error: This line uses tab instead of spaces
  name       = var.subnet_name                               # IO.003 Error: Using required variable and the value is not declared in tfvars file
  cidr       = cidrsubnet(var.vpc_cidr, 4, 1)	               # ST.011 Error: Tab exist in the end of line
  # ST.011 Error: White spaces exist in the end of line
  gateway_ip = cidrhost(cidrsubnet(var.vpc_cidr, 4, 1), 1)  
}


# ST.006 Error: Too many blank lines between resource block and data source block
data "huaweicloud_vpc_subnets" "test" {
  name = var.subnet_name
  depends_on = [huaweicloud_vpc_subnet.test]
}


# ST.006 Error: Too many blank lines between data source block and local variable block
locals {
  queried_availability_zones = data.huaweicloud_availability_zones.test.names
}


# ST.006 Error: Too many blank lines between local variable block and resource block
resource "huaweicloud_networking_secgroup" "test" {
  name                 = var.security_group_name
  delete_default_rules = true
}

#  The security group rule resource definition and open the SSH port 22 access from anywhere (DC.001 Error: Incorrect comment format, Too many spaces
#  after # character)
resource "huaweicloud_networking_secgroup_rule" "test" {
  security_group_id = huaweicloud_networking_secgroup.test.id
  direction        = "ingress"
  ethertype        = "IPv4"
  protocol         = "tcp"
  ports            = "22"
  remote_ip_prefix = "0.0.0.0/0"
}

resource "huaweicloud_compute_instance" "test" {
  # Indentation level 1 is not a multiple of 2 spaces, 2 spaces is expected
 name               = var.instance_name                                            # ST.005 Error: 2 space instead of 1
    image_id        = try(data.huaweicloud_images_images.test.images[0].id, "")    # ST.005 Error: 2 space instead of 4
  flavor_id         = data.huaweicloud_compute_flavors.test.flavors[0].id          # SC.001 Error: Array index access is unsafe
  security_groups   = [huaweicloud_security_group.test.name]
  availability_zone = local.queried_availability_zones[0]                          # SC.001 Error: Array index access is unsafe


  # ST.008 Error: Too many empty lines between different parameter blocks
  system_disk_type = "SSD"
  system_disk_size = 40
  # ST.008 Error: Missing blank lines between difference parameter blocks even they are basic parameters and blocks (1 blank line is expected)
  data_disks {
    # Indentation level 2 is not a multiple of 2 spaces, 4 spaces is expected
     type = "SAS"    # ST.005 Error: 4 space instead of 5
  size = "10"        # ST.005 Error: 4 space instead of 2
  }


  # ST.007 Error: Too many blank lines between data disks blocks (Maximum 1 blank line)
  data_disks {
    type = "SSD"
    size = "20"
  }


  # ST.007 Error: Too many blank lines between network block and data disks block (Maximum 1 blank line)
  network {
    uuid        = huaweicloud_vpc_subnet.test.id
    fixed_ip_v4 = "10.0.1.100"
  }


  # ST.008 Error: Too many empty lines between different parameter blocks
  tags = merge(local.system_tags, var.custom_tags)
}

# IO.001 Error: Variable definition should be in variables.tf file
variable "instance_flavor_id" {
  description = "The ID of the flavor that ECS instance will use"
  type        = string
  default     = ""
}

# IO.002 Error: Output definition should be in outputs.tf file
output "vpc_id" {
  description = "The ID of the created VPC"
  value       = huaweicloud_vpc.myvpc.id
}
