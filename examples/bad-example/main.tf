# Terraform configuration example that violates the standards

# Error 1: Data source instance name is not "test"
data "huaweicloud_availability_zones" "myaz" {
  region = var.region
}

# Error 2: Resource instance name is not "test"
resource "huaweicloud_vpc" "myvpc" {
  name= var.vpc_name       # ST.003 error: Missing space before equals sign
  cidr =  var.vpc_cidr     # ST.003 error: Multiple spaces after equals sign
  description = "test vpc" # ST.003 error: Equals signs not aligned
}

# Error 3: Using variable not declared in tfvars
resource "huaweicloud_vpc_subnet" "test" {
  name= var.subnet_name                 # ST.003 error: Missing space before equals sign and not aligned
  cidr       = var.subnet_cidr
  gateway_ip = var.missing_variable
  vpc_id     = huaweicloud_vpc.myvpc.id
}

# Error 4: Incorrect comment format, missing space
resource "huaweicloud_security_group" "test" {
  name= "test-sg"              # ST.003 error: Missing space before equals sign
  #  Error 5: Incorrect comment format, multiple spaces
  description =var.description # ST.003 error: Missing space after equals sign and not aligned
}

# ST.006 Error: Missing empty line between resource blocks
resource "huaweicloud_security_group_rule" "test" {
	direction        = "ingress"  # This line uses tab instead of spaces
  ethertype        = "IPv4"
	protocol         = "tcp"      # This line uses tab instead of spaces
  port_range_min   = 22
  port_range_max   = 22
  remote_ip_prefix = "0.0.0.0/0"
  security_group_id = huaweicloud_security_group.test.id
}
# ST.006 Error: Missing empty line between resource blocks
resource "huaweicloud_compute_instance" "test" {
  name            = "test-instance"
  image_id        = "image-123"
  flavor_id       = "flavor-456"
  security_groups = [huaweicloud_security_group.test.name]
  availability_zone = data.huaweicloud_availability_zones.myaz.names[0]

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }


  # ST.008 Error: Too many empty lines between different parameter blocks
  tags {
    Environment = "test"
  }
}

# ST.007 Error: Too many empty lines between same parameter blocks
resource "huaweicloud_compute_instance" "test2" {
  name            = "test-instance-2"
  image_id        = "image-123"
  flavor_id       = "flavor-456"

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }



  network {
    uuid = huaweicloud_vpc_subnet.test.id
    fixed_ip_v4 = "10.0.1.100"
  }
}

# Error 6: Output definition should be in outputs.tf file
output "vpc_id" {
  description = "VPC ID"
  value       = huaweicloud_vpc.myvpc.id
}

# Error 7: Variable definition should be in variables.tf file
variable "test_var" {
  description = "Test variable"
  type        = string
  default     = "test"
}
