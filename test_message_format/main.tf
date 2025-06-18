resource "huaweicloud_compute_instance" "web_server" {
	name      = "test-instance"
  flavor_id = "c6.large.2"
  image_id  = "test-image"

  data_disks {
    type = "SAS"
    size = 100
  }


  data_disks {
    type = "SSD"
    size = 200
  }
}

# Good comment
#No space comment
#  Multiple space comment

variable "instance_name" {
  description = "Name of the instance"
  type        = string
}

output "instance_id" {
  value = huaweicloud_compute_instance.web_server.id
} 