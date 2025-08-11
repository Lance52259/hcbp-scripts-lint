resource "huaweicloud_vpc" "test" {
  name = var.name_prefix != "" ? var.vpc_name != "" ? format("%s-%s", var.name_prefix, var.vpc_name) : format("%s-default", var.name_prefix) : var.vpc_name
  cidr = var.vpc_cidr
}
