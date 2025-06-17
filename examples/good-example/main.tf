# Terraform configuration example that follows the standards
# ST.010 Compliance: All data sources and resources use proper double quotes around type and name

# Data source definition - instance name is test
data "huaweicloud_availability_zones" "test" {
  region = var.region
}

# VPC resource definition - instance name is test
resource "huaweicloud_vpc" "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr
  # Tag configuration
  tags = {
    "Environment" = var.environment
  }
}

# Subnet resource definition - instance name is test
resource "huaweicloud_vpc_subnet" "test" {
  name       = var.subnet_name
  cidr       = var.subnet_cidr
  gateway_ip = var.gateway_ip
  vpc_id     = huaweicloud_vpc.test.id
} 