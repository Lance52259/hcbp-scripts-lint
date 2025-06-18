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
#DC.001 Error: Incorrect comment format, missing space
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

# ST.006 Error: Missing empty line between resource blocks (data source and resource)
data "huaweicloud_images" "test_image" {
  name        = "Ubuntu 20.04"
  most_recent = true
}
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


# ST.006 Error: Too many blank lines between data source blocks
data "huaweicloud_compute_flavors" "test_flavors" {
  performance_type = "normal"
  cpu_core_count   = 2
  memory_size      = 4
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
# ST.006 Error: Missing blank line between output blocks
output "subnet_id" {
  description = "Subnet ID"
  value       = huaweicloud_vpc_subnet.test.id
}

# IO.001 Error: Variable definition should be in variables.tf file
variable "test_var" {
  description = "Test variable"
  type        = string
  default     = "test"
}
# ST.006 Error: Missing blank line between variable blocks
variable "another_test_var" {
  description = "Another test variable"
  type        = string
  default     = "test2"
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

# ========================================================================
# ST.006 Comprehensive Test Cases - All Block Type Combinations
# ========================================================================

# ST.006 Error: Missing blank line between data source blocks
data "huaweicloud_vpc" "test" {
  name = "tf_test_vpc"
}
data "huaweicloud_subnet" "test" {
  name = "tf_test_subnet"
}

# ST.006 Error: Too many blank lines between variable and data source


variable "test_missing_blank" {
  description = "Test variable before data source"
  type        = string
}


data "huaweicloud_kms_key" "test" {
  key_alias = "tf_test_key"
}

# ST.006 Error: Missing blank line between variable and output
variable "test_var_before_output" {
  description = "Test variable before output"
  type        = string
}
output "test_output_after_var" {
  description = "Test output after variable"
  value       = "test"
}

# ST.006 Error: Too many blank lines between output and variable


output "test_output_before_var" {
  description = "Test output before variable"
  value       = "test"
}


variable "test_var_after_output" {
  description = "Test variable after output"
  type        = string
}

# ST.006 Error: Missing blank line between output and resource
output "test_output_before_resource" {
  description = "Test output before resource"
  value       = "test"
}
resource "huaweicloud_dns_zone" "test" {
  name = "test.com."
  zone_type = "public"
}

# ST.006 Error: Too many blank lines between resource and variable


resource "huaweicloud_ces_alarmrule" "test" {
  alarm_name = "test-alarm"

  metric {
    namespace = "SYS.VPC"
    metric_name = "network_incoming_bytes_rate_inband"
  }
}


variable "test_var_after_resource" {
  description = "Test variable after resource"
  type        = string
}

# ST.006 Error: Missing blank line between data source and variable
data "huaweicloud_networking_secgroup" "test" {
  name = "tf_test_secgroup"
}
variable "test_var_after_data" {
  description = "Test variable after data source"
  type        = string
}

# ST.006 Error: Too many blank lines between variable and resource


variable "test_var_before_resource" {
  description = "Test variable before resource"
  type        = string
}


resource "huaweicloud_vpc_eip" "test" {
  publicip {
    type = "5_bgp"
  }

  bandwidth {
    name       = "test"
    size       = 8
    share_type = "PER"
  }
}

# ST.006 Error: Missing blank line between data source and output
data "huaweicloud_workspace_flavors" "test" {}
output "test_output_after_data" {
  description = "Test output after data source"
  value       = data.huaweicloud_workspace_flavors.test.flavors[0].id
}

# ST.006 Error: Too many blank lines between output and data source


output "test_output_before_data" {
  description = "Test output before data source"
  value       = "test"
}


data "huaweicloud_rds_flavors" "test" {
  db_type = "MySQL"
  db_version = "8.0"
}

# ========================================================================
# Locals Block Test Cases
# ========================================================================

# ST.006 Error: Missing blank line between resource and locals
resource "huaweicloud_identity_group" "test" {
  name        = "test-group"
  description = "Test group"
}
locals {
  common_tags = {
    Environment = "test"
    Project     = "terraform-lint"
  }
}

# ST.006 Error: Too many blank lines between locals and resource


locals {
  vpc_config = {
    name = "test-vpc"
    cidr = "10.0.0.0/16"
  }
}


resource "huaweicloud_identity_role" "test" {
  name        = "tf_test_role"
  description = "Test role"
  type        = "XA"
  policy      = jsonencode({
    Version = "1.1"
    Statement = [
      {
        Effect = "Allow"
        Action = ["iam:*"]
      }
    ]
  })
}

# ST.006 Error: Missing blank line between locals and data source
locals {
  subnet_config = {
    name = "test-subnet"
    cidr = "10.0.1.0/24"
  }
}
data "huaweicloud_enterprise_project" "test" {
  name = "default"
}

# ST.006 Error: Too many blank lines between data source and locals


data "huaweicloud_identity_role" "test" {
  name = "tf_test_admin"
}


locals {
  security_config = {
    ssh_port = 22
    http_port = 80
    https_port = 443
  }
}

# ST.006 Error: Missing blank line between locals and variable
locals {
  database_config = {
    engine = "mysql"
    version = "8.0"
  }
}
variable "test_var_after_locals" {
  description = "Test variable after locals"
  type        = string
}

# ST.006 Error: Too many blank lines between variable and locals


variable "test_var_before_locals" {
  description = "Test variable before locals"
  type        = string
}


locals {
  network_config = {
    vpc_cidr    = "192.168.0.0/16"
    subnet_cidr = "192.168.1.0/24"
  }
}

# ST.006 Error: Missing blank line between locals and output
locals {
  output_config = {
    format   = "json"
    detailed = true
  }
}
output "test_output_after_locals" {
  description = "Test output after locals"
  value       = local.output_config
}

# ST.006 Error: Too many blank lines between output and locals


output "test_output_before_locals" {
  description = "Test output before locals"
  value       = "test"
}


locals {
  final_config = {
    deployment = "complete"
    status     = "ready"
  }
}

# ST.006 Error: Missing blank line between locals blocks
locals {
  first_locals = {
    key1 = "value1"
  }
}
locals {
  second_locals = {
    key2 = "value2"
  }
}

# ST.006 Error: Too many blank lines between locals blocks


locals {
  third_locals = {
    key3 = "value3"
  }
}


locals {
  fourth_locals = {
    key4 = "value4"
  }
}
