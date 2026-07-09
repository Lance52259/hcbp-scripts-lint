resource "huaweicloud_compute_instance" "test" {
  name = var.instance_name

  data_disks {
    type = "SSD"
    size = 20
  }
  data_disks {
    type = "SAS"
    size = 40
  }
}
