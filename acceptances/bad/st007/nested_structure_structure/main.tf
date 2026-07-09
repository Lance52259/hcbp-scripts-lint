resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name

  extend_params {
    network {
      uuid = var.subnet_id
    }
    storage {
      type = "SSD"
      size = 20
    }
  }
}
