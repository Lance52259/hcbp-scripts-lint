locals {
  zones = ["cn-north-4a", "cn-north-4b"]
}

resource "null_resource" "test" {
  triggers = {
    zone = local.zones[0]
  }
}
