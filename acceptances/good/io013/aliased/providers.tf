terraform {
  required_version = ">= 0.12.0"

  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.70.0"
    }
  }
}

provider "huaweicloud" {
  region = "cn-north-4"
}

provider "huaweicloud" {
  alias  = "test"
  region = "cn-east-3"
}
