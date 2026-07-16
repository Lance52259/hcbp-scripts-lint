provider "huaweicloud" {
  region = "cn-north-4"
}

provider "huaweicloud" {
  alias  = "test"
  region = "cn-east-3"
}

resource "null_resource" "test" {
  triggers = {
    ok = "true"
  }
}
