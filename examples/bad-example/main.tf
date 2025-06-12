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
