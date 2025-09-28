terraform {
  # SC.002 Error: Version constraint required_version is missing
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.52.1" # SC.004 Error: Version constraint is too permissive
    }
  }
}

provider "huaweicloud" {
  region     = var.region_name
  access_key = var.access_key
  secret_key = var.secret_key
}
