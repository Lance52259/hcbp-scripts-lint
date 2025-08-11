# ST.001 Disable
resource "huaweicloud_vpc_route" "vpc_route" {
  vpc_id      = huaweicloud_vpc.vpcA.id
  destination = "192.168.0.0/16"
  type        = "peering"
  nexthop     = huaweicloud_vpc_peering_connection.peering.id
}

resource "huaweicloud_vpc_route" "vpc_route_another" {
  vpc_id      = huaweicloud_vpc.vpcB.id
  destination = "192.168.0.0/16"
  type        = "peering"
  nexthop     = huaweicloud_vpc_peering_connection.peering.id
}
# ST.001 Enable

# This should trigger ST.001 error
resource "huaweicloud_vpc_route" "test" {
  vpc_id      = huaweicloud_vpc.vpcC.id
  destination = "192.168.0.0/16"
  type        = "peering"
  nexthop     = huaweicloud_vpc_peering_connection.peering.id
}

# ST.003 Disable
resource "huaweicloud_compute_instance" "test" {
  name = "test-instance"
  flavor_id = "c6.large.2"
  image_id = "test-image"
  system_disk_size = 40
}
# ST.003 Enable

# This should trigger ST.003 error
resource "huaweicloud_compute_instance" "another" {
  name = "test-instance2"
  flavor_id = "c6.large.2"
  image_id = "test-image"
  system_disk_size = 40
}

# Test multiple rule control
# ST.001 Disable
# ST.003 Disable
resource "huaweicloud_vpc_route" "vpc_route_multiple" {
  vpc_id      = huaweicloud_vpc.vpcD.id
  destination = "192.168.0.0/16"
  type        = "peering"
  nexthop     = huaweicloud_vpc_peering_connection.peering.id
}

resource "huaweicloud_compute_instance" "test_multiple" {
  name = "test-instance-multiple"
  flavor_id = "c6.large.2"
  image_id = "test-image"
  system_disk_size = 40
}
# ST.001 Enable
# ST.003 Enable
