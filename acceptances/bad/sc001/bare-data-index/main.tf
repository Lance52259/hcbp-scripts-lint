data "huaweicloud_compute_flavors" "test" {
  availability_zone = "cn-north-4a"
}

resource "null_resource" "test" {
  triggers = {
    flavor = data.huaweicloud_compute_flavors.test.flavors[0].id
  }
}
