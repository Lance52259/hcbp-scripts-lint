terraform {
  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.70.1"
    }
  }
}

provider "huaweicloud" {
  region = "cn-north-4"
}
