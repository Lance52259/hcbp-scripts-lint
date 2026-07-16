resource "null_resource" "test" {
  provider = huaweicloud.test

  triggers = {
    ok = "true"
  }
}
