terraform {
  required_version = ">= 1.9.0"

  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = ">= 1.57.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 1.6.2"
    }
  }
}
# ST.006 Error: Missing blank line between provider block and terraform block
provider "huaweicloud" {
region       = var.region_name # ST.005 Error: 0 space found, not 2 spaces
	access_key = var.access_key  # ST.004 Error: This line uses tab instead of spaces
  secret_key = var.secret_key
}


# ST.006 Error: Too many empty lines between provider blocks
# ST.010 Error: Missing quotes around provider type
provider kubernetes {
  host = "https://${var.eip_address}:5443"
}
