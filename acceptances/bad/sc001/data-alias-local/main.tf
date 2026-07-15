data "huaweicloud_availability_zones" "test" {
  region = "cn-north-4"
}

locals {
  names = data.huaweicloud_availability_zones.test.names
}

resource "null_resource" "test" {
  triggers = {
    zone = local.names[0]
  }
}
