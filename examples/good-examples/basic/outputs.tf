# Output definitions file

# VPC ID output
output "vpc_id" {
  description = "The ID of the VPC"
  value       = huaweicloud_vpc.test.id
}

# Subnet ID output
output "subnet_id" {
  description = "The ID of the subnet"
  value       = huaweicloud_vpc_subnet.test.id
}

# Availability zones output
output "availability_zones" {
  description = "Available zones"
  value       = data.huaweicloud_availability_zones.test.names
}
