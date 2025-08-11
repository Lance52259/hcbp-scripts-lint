import {
  for_each = {
    "tf_default_vpc" = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "tf_test_vpc"    = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
  }

  to = huaweicloud_vpc.test[each.key]
  id = each.value
}

resource "huaweicloud_vpc" "test" {
  for_each = { for o in var.vpc_configurations : o.name => o }

  name = each.value.name
  cidr = each.value.cidr
}
