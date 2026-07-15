resource "null_resource" "test" {
  triggers = {
    max = var.max_count
  }
}
