resource "huaweicloud_vpc" "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr
}

resource "huaweicloud_vpc_subnet" "test" {
  count = length(var.subnets_configuration)

  vpc_id = huaweicloud_vpc.test.id

  name       = lookup(element(var.subnets_configuration, count.index), "name")
  cidr       = lookup(element(var.subnets_configuration, count.index), "cidr")
  gateway_ip = lookup(element(var.subnets_configuration, count.index), "gateway_ip") != "" ? lookup(element(var.subnets_configuration, count.index), "gateway_ip") : cidrhost(lookup(element(var.subnets_configuration, count.index), "cidr"), 1)
}
