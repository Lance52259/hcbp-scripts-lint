terraform {
  required_version = ">= 1.9.0"


  # ST.007 Error: Too many empty lines between different parameter blocks
  required_providers {
    huaweicloud = {
      source = "huaweicloud/huaweicloud" # ST.003 Error: Equals sign not aligned
      version =">= 1.57.0"               # ST.003 Error: Missing space after equals sign
    }


    # ST.007 Error: Too many empty lines between different parameter blocks
    kubernetes = {
      source= "hashicorp/kubernetes" # ST.003 Error: Missing space before equals sign and missing space before equals sign
      version =  ">= 1.6.2"          # ST.003 Error: Multiple spaces after equals sign
    }

    random = {
      source = "hashicorp/random"
      version = ">= 3.0.0"
    }
    time = {
      source = "hashicorp/time"
      version = ">= 0.9.0"
    }
  }
}
# ST.006 Error: Missing blank line between provider block and terraform block
provider "huaweicloud" {
region           = var.region_name # ST.005 Error: 0 space found, not 2 spaces
  # ST.003 Error: Multiple spaces after equals sign
  # ST.004 Error: This line uses tab instead of spaces
	access_key     =  var.access_key
  # ST.003 Error: Missing space before equals sign
  # ST.003 Error: Equals sign not aligned
  secret_key= var.secret_key
  security_token = var.security_token


  # ST.007 Error: Too many empty lines between different parameter blocks
  endpoints = {
    iam = "https://iam.myhuaweicloud.com"
  }
}


# ST.006 Error: Too many empty lines between provider blocks
provider "huaweicloud" {
  alias          = "test"
  region         = var.region_name
  access_key     = var.access_key
  secret_key     = var.secret_key
  security_token = var.security_token
}
# ST.006 Error: Missing blank line between two provider blocks
# ST.010 Error: Missing quotes around provider type
provider kubernetes {
  host = "https://${var.eip_address}:5443"
}
