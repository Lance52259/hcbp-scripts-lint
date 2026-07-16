# IO.013 bad: provider configuration belongs in providers.tf
provider "huaweicloud" {
  region = "cn-north-4"
}

resource "null_resource" "test" {
  triggers = {
    region = "cn-north-4"
  }
}
