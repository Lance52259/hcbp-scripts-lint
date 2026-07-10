resource "huaweicloud_vpc" "test" {
  name = var.name_prefix != "" ? var.vpc_name != "" ? format("%s-%s", var.name_prefix, var.vpc_name) : format("%s-default", var.name_prefix) : var.vpc_name
  cidr = var.vpc_cidr
}

resource "huaweicloud_vpc_subnet" "test" {
  count = length(var.subnets_configuration)

  vpc_id = huaweicloud_vpc.test.id

  name        = lookup(element(var.subnets_configuration, count.index), "name")
  cidr        = lookup(element(var.subnets_configuration, count.index), "cidr")
  gateway_ip  = lookup(element(var.subnets_configuration, count.index), "gateway_ip") != "" ? lookup(element(var.subnets_configuration, count.index), "gateway_ip") : cidrhost(lookup(element(var.subnets_configuration, count.index), "cidr"), 1)
  description = lookup(element(var.subnets_configuration, count.index), "description") != "" ? lookup(element(var.subnets_configuration, count.index), "description") : null
  ipv6_enable = lookup(element(var.subnets_configuration, count.index), "ipv6_enabled")
  dhcp_enable = lookup(element(var.subnets_configuration, count.index), "dhcp_enabled")
  dns_list    = try(length(lookup(element(var.subnets_configuration, count.index), "dns_list")), 0) > 0 ? lookup(element(var.subnets_configuration, count.index), "dns_list") : null

  tags = try(length(lookup(element(var.subnets_configuration, count.index), "tags")), 0) > 0 ? lookup(element(var.subnets_configuration, count.index), "tags") : null
}
