resource "null_resource" "test" {
  triggers = {
    second = var.b
  }
}
