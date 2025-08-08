# Terraform configuration example that follows the standards
# ST.010 Compliance: All data sources, resources, variables, and outputs use proper double quotes around names

# Data source definition - instance name is test
data "huaweicloud_availability_zones" "test" {}

# Resource definition - instance name is test
resource "huaweicloud_vpc" "test" {
  name = var.vpc_name
  cidr = var.vpc_cidr

  # Tag configuration
  tags = {
    "foo"         = "bar"
    "environment" = var.environment
  }
}

resource "huaweicloud_vpc_subnet" "test" {
  name       = var.subnet_name
  cidr       = cidrsubnet(var.vpc_cidr, 4, 1)
  gateway_ip = cidrhost(cidrsubnet(var.vpc_cidr, 4, 1), 1)
  vpc_id     = huaweicloud_vpc.test.id
}

data "huaweicloud_compute_flavors" "test" {
  performance_type = "normal"
  cpu_core_count   = 2
  memory_size      = 4
}

data "huaweicloud_images_images" "test" {
  flavor_id  = try(data.huaweicloud_compute_flavors.test.flavors[0].id, null)
  visibility = "public"
  os         = "Ubuntu"
}

resource "huaweicloud_networking_secgroup" "test" {
  name                 = var.security_group_name
  delete_default_rules = true
}

resource "huaweicloud_compute_instance" "test" {
  name               = var.instance_name
  availability_zone  = try(data.huaweicloud_availability_zones.test.names[0], null)                # null is correct and safe
  flavor_id          = try(data.huaweicloud_compute_flavors.test.flavors[0].id, "c6.2xlarge.4")    # fixed value is correct and safe
  image_id           = try(data.huaweicloud_images_images.test.images[0].id, "")                   # empty string is correct and safe
  user_data          = base64encode(var.instance_user_data)
  security_group_ids = [
    huaweicloud_networking_secgroup.test.id
  ]

  network {
    uuid = huaweicloud_vpc_subnet.test.id
  }

  dynamic "data_disks" {
    for_each = var.data_disk_configurations

    content {
      type = data_disks.value.type
      size = data_disks.value.size
    }
  }

  system_disk_type = var.system_disk_type
  system_disk_size = var.system_disk_size
}

resource "huaweicloud_obs_bucket" "test" {
  bucket        = var.bucket_name
  storage_class = var.bucket_storage_class
  acl           = var.bucket_acl
  encryption    = var.bucket_encryption
  sse_algorithm = var.bucket_encryption ? var.bucket_sse_algorithm : null
  kms_key_id    = var.bucket_encryption ? var.bucket_encryption_key_id != "" ? var.bucket_encryption_key_id : huaweicloud_kms_key.test[0].id : null
  force_destroy = var.bucket_force_destroy
  tags          = var.bucket_tags

  lifecycle {
    ignore_changes = [
      sse_algorithm
    ]
  }
}

resource "huaweicloud_obs_bucket_object" "test" {
  bucket       = huaweicloud_obs_bucket.test.id
  key          = var.object_extension_name != "" ? format("%s%s", var.object_name, var.object_extension_name) : var.object_name
  content_type = "application/xml"
  content      = var.object_upload_content
}

resource "huaweicloud_obs_bucket_policy" "test" {
  bucket = huaweicloud_obs_bucket.test.id
  policy = <<POLICY
{
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {"ID": "*"},
            "Action": ["GetObject"],
            "Resource": "${huaweicloud_obs_bucket.test.id}/*"
        }
    ]
}
POLICY
}
