resource "null_resource" "test" {
  triggers = {
    region = "cn-north-4"
  }
}
