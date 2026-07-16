resource "null_resource" "test" {
  triggers = {
    has_tags = tostring(var.tags != null)
  }
}
