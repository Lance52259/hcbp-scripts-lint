# Terraform configuration example that follows the standards
# ST.010 Compliance: All data sources, resources, variables, and outputs use proper double quotes around names

# Data source definition - instance name is test
data "huaweicloud_availability_zones" "test" {}

# Resource definition - instance name is test
resource "huaweicloud_vpc" "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr

  # Tag configuration
  tags = {
    "foo"         = "bar"
    "environment" = var.environment
  }
}

resource "huaweicloud_vpc_subnet" "test" {
  name       = var.subnet_name
  cidr       = cidrsubnet(var.vpc_cidr, 4, 1)
  gateway_ip = cidrhost(cidrsubnet(var.vpc_cidr, 4, 1), 1)
  vpc_id     = huaweicloud_vpc.test.id
}

data "huaweicloud_compute_flavors" "test" {
  performance_type = "normal"
  cpu_core_count   = 2
  memory_size      = 4
}

data "huaweicloud_images_images" "test" {
  flavor_id  = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  visibility = "public"
  os         = "Ubuntu"
}

resource "huaweicloud_networking_secgroup" "test" {
  name                 = var.security_group_name
  delete_default_rules = true
}

resource "huaweicloud_compute_instance" "test" {
  name               = var.instance_name
  availability_zone  = try(data.huaweicloud_availability_zones.test.names[0], null)                # null is correct and safe
  flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")    # fixed value is correct and safe
  image_id           = try(data.huaweicloud_images_images.test.images[0].id, "")                   # empty string is correct and safe
  user_data          = base64encode(var.instance_user_data)
  security_group_ids = [
    huaweicloud_networking_secgroup.test.id
  ]

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }
}
