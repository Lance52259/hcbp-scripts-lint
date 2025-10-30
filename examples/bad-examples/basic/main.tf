

# ST.012 Error: This file has multiple empty lines before the first non-empty line
# DC.001 Error: Incorrect comment format, comment must starts with # instead of //
// Terraform configuration example that violates the standards

locals {
  is_instance_flavors_available = data.huaweicloud_compute_flavors.test.flavors[0].id != null


  # ST.003 Error: Equals sign not aligned
  # ST.003 Error: Multiple spaces after equals sign
  # ST.007 Error: Too many empty lines between different parameter blocks
  system_tags=  {
    "Environment" = "Development" # The alignment of this line is correct
    # ST.003 Error: Equals sign not aligned
    # ST.003 Error: Missing space after equals sign
    "Usage"="Tool"


    # ST.003 Error: Equals sign not aligned (blank line ahead of this line, so this line is in the new section)
    # ST.003 Error: Multiple spaces after equals sign
    # ST.007 Error: Too many empty lines between different parameter blocks
    "Owner"       =  "DevOps"
    # ST.003 Error: Equals sign not aligned
    # ST.003 Error: Missing space after equals sign
    "Project"     ="Terraform"
  }

  # ST.003 Error: Equals sign not aligned (blank line ahead of this line, so this line is in the new section)
  sys_eps_id                   = "0"
}
# ST.001 Error: Data source name is not "test"
# ST.006 Error: Missing blank line between local variable block and data source block
# ST.010 Error: Missing quotes around data source type
data huaweicloud_availability_zones "myaz" {

  # ST.008 Error: There is a blank line definition ahead of the count meta-parameter
  count = var.availability_zone == "" ? 1 : 0
}

# ST.006 Error: Missing blank line between data source blocks
data "huaweicloud_availability_zones" test {
  count = anytrue([for v in var.instance_configurations : length(v.availability_zones) == 0]) ? 1 : 0
}


# ST.006 Error: Too many blank lines between data source blocks
data "huaweicloud_compute_flavors" test {
  count            = var.instance_flavor_id == "" ? 1 : 0
  # ST.008 Error: There is no blank line between the Count meta-parameter and other parameters
  performance_type = var.instance_flavor_performance_type
  cpu_core_count   = var.instance_flavor_cpu_core_number
  memory_size      = var.instance_flavor_memory_size
}

data "huaweicloud_images_images" "test" {
  count = var.instance_image_id == "" ? 1 : 0


  # ST.003 Error: Equals sign not aligned (blank line ahead of this line, so this line is in the new section)
  # ST.008 Error: There are too many blank lines between the count meta-parameter and other parameters
  flavor_id= var.instance_flavor_id == "" ? try(data.huaweicloud_compute_flavors.test.flavors[0].id, null) : var.instance_flavor_id
  # ST.003 Error: Missing space after equals sign
  visibility =var.instance_image_visibility
  # ST.003 Error: Multiple spaces after equals sign
  os         =   var.instance_image_os
}
# ST.001 Error: Resource name is not "test"
# ST.006 Error: Missing blank line between data source block and resource block
# ST.010 Error: Missing quotes around resource type
resource huaweicloud_vpc "incorrect_resource_name" {

  # ST.008 Error: There is a blank line definition ahead of the count meta-parameter
  count = var.vpc_id == "" ? 1 : 0
  # ST.008 Error: There is no blank line between the depends_on meta-parameter and count meta-parameter
  depends_on = [data.huaweicloud_availability_zones.test]


  # ST.008 Error: There are too many blank lines between the name meta-parameter and depends_on meta-parameter
  name        = var.incorrect_vpc_name    # IO.001 Error: Missing variable definition in variables.tf file
  cidr        = var.vpc_cidr
  description = "The resource name is incorrect, should be 'test'"
}
# ST.006 Error: Missing blank line between resource blocks
resource huaweicloud_vpc "test" {
  count = var.vpc_id == "" ? 1 : 0


  # ST.008 Error: There are too many blank lines between the name parameter and depends_on meta-parameter
  name = var.vpc_name
  cidr = var.vpc_cidr
}


# ST.006 Error: Too many empty lines between resource blocks
# ST.010 Error: Missing quotes around resource name
#The subnet resource definition (DC.001 Error: Incorrect comment format, missing space after # character)
resource "huaweicloud_vpc_subnet" test {

  # ST.008 Error: There is a blank line definition ahead of the depends_on meta-parameter
  depends_on = [huaweicloud_vpc.test]  # The depends_on meta-parameter is ahead of the other parameters
  # ST.008 Error: There is no blank line between the depends_on meta-parameter and other parameters
	vpc_id     = huaweicloud_vpc.incorrect_resource_name.id    # ST.004 Error: This line uses tab instead of spaces
  name       = var.subnet_name                               # IO.003 Error: Using required variable and the value is not declared in tfvars file
  # ST.011 Error: Tab exist in the end of line
  cidr       = cidrsubnet(var.vpc_cidr, 4, 1)	
  # ST.011 Error: White spaces exist in the end of line
  gateway_ip = cidrhost(cidrsubnet(var.vpc_cidr, 4, 1), 1)  
}


# ST.006 Error: Too many blank lines between resource block and data source block
data "huaweicloud_vpc_subnets" "test" {
  depends_on = [huaweicloud_vpc_subnet.test]  # The depends_on meta-parameter is ahead of the other parameters

  name = var.subnet_name
}


# ST.006 Error: Too many blank lines between data source block and local variable block
locals {
  queried_availability_zones = data.huaweicloud_availability_zones.test.names
}


# ST.006 Error: Too many blank lines between local variable block and resource block
resource "huaweicloud_networking_secgroup" "test" {

  # ST.008 Error: There is a blank line definition ahead of the count meta-parameter
  provider             = huaweicloud.test
  # ST.008 Error: There is no blank line between the provider meta-parameter and other parameters
  name                 = var.security_group_name
  delete_default_rules = true

  depends_on = [huaweicloud_vpc.test]  # The depends_on meta-parameter is behind of the other parameters
}

# DC.001 Error: Incorrect comment format, Too many spaces after # character
#  The security group rule resource definition and open the SSH port 22 access from anywhere
resource "huaweicloud_networking_secgroup_rule" "test" {
  provider = huaweicloud.test


  # ST.008 Error: There are too many blank lines between the provider meta-parameter and other parameters
  # ST.003 Error: Equals sign not aligned
  security_group_id  = huaweicloud_networking_secgroup.test.id
  # ST.003 Error: Equals sign not aligned
  direction          = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"

  ports            = "22"
  remote_ip_prefix = "0.0.0.0/0"
}

resource "huaweicloud_compute_instance" "test" {
   # ST.005 Error: 1 space found, not 2 spaces
 name               = var.instance_name
  # ST.005 Error: 4 spaces found, not 2 spaces
  # Equals sign not aligned (This ST.003 error message will not be displayed until the ST.005 problem is fixed)
    image_id        = try(data.huaweicloud_images_images.test.images[0].id, "")
    # SC.001 Error: Array index access is unsafe
  flavor_id         = data.huaweicloud_compute_flavors.test.flavors[0].id
  security_groups   = [huaweicloud_security_group.test.name]
  # SC.001 Error: Array index access is unsafe
  availability_zone = local.queried_availability_zones[0]
  # ST.007 Error: Missing blank lines between difference parameter blocks even they are basic parameters and blocks (1 blank line is expected)
  dynamic "data_disks" {
    for_each = var.data_disks_configurations


  # ST.008 Error: There are too many blank lines between the for_each meta-parameter (in the dynamic block) and other parameters
  # ST.005 Error: Indentation level 2 is not a multiple of 2 spaces, 4 spaces is expected
  content {
       type        = data_disks.value.type # ST.005 Error: 7 spaces found, not 6 spaces
     size          = data_disks.value.size # ST.005 Error: 5 spaces found, not 6 spaces
      extend_param = data_disks.value.extend_param
    }
  }


  # ST.007 Error: Too many blank lines between data disks blocks (Maximum 1 blank line)
  data_disks {
    type = "SSD"
    size = "20"
  }

  system_disk_type = "SSD"
  system_disk_size = 40


  # ST.007 Error: Too many blank lines between data_disks block and parameter (Maximum 1 blank line)
  data_disks {
    type = "SSD"
    size = "20"
  }



  # ST.007 Error: Too many blank lines between network block and data disks block (Maximum 1 blank line)
  network {
    uuid        = huaweicloud_vpc_subnet.test.id
    fixed_ip_v4 = "10.0.1.100"

    extend_param = {
      "dhcp_disabled" = "true"  # Fixed definition
      "access_mode"   = "nat"   # Fixed definition
    }
  }


  # ST.007 Error: Too many empty lines between different parameter blocks
  tags       = merge(local.system_tags, var.custom_tags)
  # ST.008 Error: There is no blank line between the depends_on meta-parameter and other parameters
  depends_on = [huaweicloud_networking_secgroup_rule.test]  # The depends_on meta-parameter is behind of the other parameters
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

resource "huaweicloud_evs_volumes" "test" {

  # ST.008 Error: There is a blank line definition ahead of the for_each meta-parameter
  for_each          = var.volumes_configurations
  # ST.008 Error: There is no blank line between the for_each meta-parameter and other parameters
  volume_type       = each.value.type
  volume_size       = each.value.size
  availability_zone = local.queried_availability_zones[0]


  # ST.008 Error: There are too many blank lines between the depends_on meta-parameter and other parameters
  depends_on = [huaweicloud_compute_instance.test]
  # ST.008 Error: There is no blank line between the lifecycle meta-parameter and depends_on meta-parameter
  lifecycle {
    create_before_destroy = true
    # ST.003 Error: Equals sign not aligned
    ignore_changes = [
      # ST.004 Error: This line uses tab instead of spaces
			volume_size,
    availability_zone  # ST.005 Error: 4 spaces found, not 6 spaces
    ]
  }
}

resource "huaweicloud_compute_volume_attach" "test" {
  depends_on = [
    huaweicloud_compute_instance.test,
    huaweicloud_evs_volumes.test
  ]


  # ST.008 Error: There are too many blank lines between the depends_on meta-parameter and for_each meta-parameter
  for_each = var.volumes_configurations


  # ST.008 Error: There are too many blank lines between the for_each meta-parameter and other parameters
  instance_id = huaweicloud_compute_instance.test.id
  volume_id   = huaweicloud_evs_volumes.test[each.key].id


  # ST.008 Error: There are too many blank lines between the lifecycle meta-parameter and other parameters
  lifecycle {
    create_before_destroy = true
    ignore_changes        = [
      volume_id
    ]
  }
}
# ST.012 Error: This file has multiple empty lines after the last non-empty line

