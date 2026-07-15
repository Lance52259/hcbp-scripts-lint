resource "null_resource" "test" {
  triggers = {
    x = var.a
    y = var.b
  }
}
