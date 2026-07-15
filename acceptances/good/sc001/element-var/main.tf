resource "null_resource" "test" {
  triggers = {
    item = element(var.items, 0)
  }
}
