# Terraform configuration example that violates the standards

# ST.001 Error: Data source instance name is not "test"
data "huaweicloud_availability_zones" "myaz" {
  region = var.region
}

# ST.001 Error: Resource instance name is not "test"
resource "huaweicloud_vpc" "myvpc" {
  name= var.vpc_name       # ST.003 Error: Missing space before equals sign
  cidr =  var.vpc_cidr     # ST.003 Error: Multiple spaces after equals sign
  description = "test vpc" # ST.003 Error: Equals signs not aligned
}

# ST.002 Error: Variable used in data source must have default value
data "huaweicloud_compute_flavors" "test" {
  performance_type = "normal"
  cpu_core_count   = var.cpu_cores    # Variable without default used in data source
  memory_size      = var.memory_size  # Variable without default used in data source
}

# Using variable not declared in tfvars
resource "huaweicloud_vpc_subnet" "test" {
  name= var.subnet_name                 # ST.003 Error: Missing space before equals sign and not aligned
  cidr       = var.subnet_cidr
  gateway_ip = var.missing_variable
  vpc_id     = huaweicloud_vpc.myvpc.id
}

# DC.001 Error: Incorrect comment format, missing space
resource "huaweicloud_security_group" "test" {
  name= "test-sg"              # ST.003 Error: Missing space before equals sign
  #DC.001 Error: Incorrect comment format, multiple spaces
  description =var.description # ST.003 Error: Missing space after equals sign and not aligned
}

# ST.006 Error: Missing empty line between resource blocks
resource "huaweicloud_security_group_rule" "test" {
	direction        = "ingress"  # ST.004 Error: This line uses tab instead of spaces
  ethertype        = "IPv4"
	protocol         = "tcp"      # ST.004 Error: This line uses tab instead of spaces
  port_range_min   = 22
  port_range_max   = 22
  remote_ip_prefix = "0.0.0.0/0"
  security_group_id = huaweicloud_security_group.test.id
}
# ST.006 Error: Missing empty line between resource blocks
resource "huaweicloud_compute_instance" "test" {
  name            = "test-instance"
  image_id        = "image-123"
  flavor_id       = data.huaweicloud_compute_flavors.test.flavors[0].id
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
  flavor_id       = data.huaweicloud_compute_flavors.test.flavors[0].id

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }



  network {
    uuid = huaweicloud_vpc_subnet.test.id
    fixed_ip_v4 = "10.0.1.100"
  }
}

# ST.005 Error: Additional indentation level errors
resource "huaweicloud_nat_gateway" "test" {
 name = "test-nat"                                 # ST.005 Error: 1 space instead of 2
   vpc_id = huaweicloud_vpc.myvpc.id               # ST.005 Error: 3 spaces instead of 2
     spec = "1"                                    # ST.005 Error: 5 spaces instead of 2
       subnet_id = huaweicloud_vpc_subnet.test.id  # ST.005 Error: 7 spaces instead of 2
}

# IO.001 Error: Output definition should be in outputs.tf file
output "vpc_id" {
  description = "VPC ID"
  value       = huaweicloud_vpc.myvpc.id
}

# IO.001 Error: Variable definition should be in variables.tf file
variable "test_var" {
  description = "Test variable"
  type        = string
  default     = "test"
}

# ST.010 Error: Missing quotes around data source type
data huaweicloud_images "test" {
  name        = "Ubuntu 20.04"
  most_recent = true
}

# ST.010 Error: Missing quotes around data source name
data "huaweicloud_compute_flavors" test {
  performance_type = "normal"
  cpu_core_count   = 2
  memory_size      = 4
}

# ST.010 Error: Missing quotes around resource type
resource huaweicloud_kms_key "test" {
  key_alias    = "test-key"
  pending_days = "7"
}

# ST.010 Error: Missing quotes around resource name
resource "huaweicloud_obs_bucket" test {
  bucket = "test-bucket-unique-name"
  acl    = "private"
}
