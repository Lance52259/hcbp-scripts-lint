resource "null_resource" "test" {
  triggers = {
    name = var.vpc_name
  }
}
